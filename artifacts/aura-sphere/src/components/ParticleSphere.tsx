import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import type { SphereState, ParticleShape } from "@/lib/types";
import { generateShape } from "@/lib/shapes";

function CssFallbackSphere({ className }: { className?: string }) {
  return (
    <div className={className ?? "w-full h-full"} aria-hidden="true">
      <div
        className="relative w-full h-full flex items-center justify-center"
        style={{ perspective: "600px" }}
      >
        {Array.from({ length: 32 }).map((_, i) => {
          const theta = Math.acos(-1 + (2 * i) / 32);
          const phi = Math.sqrt(32 * Math.PI) * theta;
          const x = 50 + 40 * Math.sin(theta) * Math.cos(phi);
          const y = 50 + 40 * Math.sin(theta) * Math.sin(phi);
          const delay = (i * 0.12) % 2;
          return (
            <span
              key={i}
              style={{
                position: "absolute",
                left: `${x}%`,
                top: `${y}%`,
                width: "4px",
                height: "4px",
                borderRadius: "50%",
                background: "white",
                opacity: 0.6,
                transform: "translate(-50%,-50%)",
                animation: `cssDot 2.8s ease-in-out ${delay}s infinite alternate`,
              }}
            />
          );
        })}
        <style>{`
          @keyframes cssDot {
            0%   { transform: translate(-50%,-50%) scale(1);   opacity: 0.5; }
            50%  { transform: translate(-50%,-50%) scale(1.6); opacity: 1;   }
            100% { transform: translate(-50%,-50%) scale(0.8); opacity: 0.3; }
          }
        `}</style>
      </div>
    </div>
  );
}

const STATE_PARAMS: Record<
  SphereState,
  {
    speed: number;
    scale: number;
    jitter: number;
    ringIntensity: number;
    opacity: number;
    density: number;
    pulseRate: number;
    burstFactor: number;
  }
> = {
  idle:       { speed: 0.0010, scale: 0.98, jitter: 0.002, ringIntensity: 0.08, opacity: 0.55, density: 0.030, pulseRate: 0.6,  burstFactor: 1.2 },
  listening:  { speed: 0.006,  scale: 1.04, jitter: 0.020, ringIntensity: 0.85, opacity: 0.95, density: 0.038, pulseRate: 1.6,  burstFactor: 2.2 },
  thinking:   { speed: 0.015,  scale: 1.08, jitter: 0.035, ringIntensity: 0.45, opacity: 0.85, density: 0.034, pulseRate: 2.4,  burstFactor: 1.8 },
  responding: { speed: 0.010,  scale: 1.06, jitter: 0.024, ringIntensity: 1.00, opacity: 1.00, density: 0.040, pulseRate: 2.0,  burstFactor: 2.5 },
};

export function ParticleSphere({
  state,
  shape = "sphere",
  volume = 0,
  className,
}: {
  state: SphereState;
  shape?: ParticleShape;
  volume?: number;
  className?: string;
}) {
  const [webglFailed, setWebglFailed] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const stateRef = useRef<SphereState>(state);
  const shapeRef = useRef<ParticleShape>(shape);
  const volumeRef = useRef<number>(volume);
  const morphRef = useRef<{
    from: Float32Array;
    to: Float32Array;
    t: number;
    active: boolean;
  } | null>(null);

  useEffect(() => { stateRef.current = state; }, [state]);
  useEffect(() => { shapeRef.current = shape; }, [shape]);
  useEffect(() => { volumeRef.current = volume; }, [volume]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, 1, 0.1, 100);
    camera.position.z = 3.2;

    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    } catch {
      setWebglFailed(true);
      return;
    }
    if (!renderer.getContext()) {
      renderer.dispose();
      setWebglFailed(true);
      return;
    }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);
    renderer.domElement.style.display = "block";
    renderer.domElement.style.width = "100%";
    renderer.domElement.style.height = "100%";
    renderer.domElement.style.touchAction = "none";

    const COUNT = 480;
    const positions = new Float32Array(COUNT * 3);
    const basePositions = new Float32Array(COUNT * 3);
    const initial = generateShape(shapeRef.current, COUNT);
    positions.set(initial);
    basePositions.set(initial);
    let currentShape: ParticleShape = shapeRef.current;

    // Per-particle explosion data — each particle has its own burst phase and amplitude
    const burstPhase = new Float32Array(COUNT);
    const burstAmp = new Float32Array(COUNT);
    const burstSpeed = new Float32Array(COUNT);
    for (let i = 0; i < COUNT; i++) {
      burstPhase[i] = Math.random() * Math.PI * 2;
      burstAmp[i]   = 0.2 + Math.random() * 0.9; // 0.2..1.1 × burstFactor scaling
      burstSpeed[i] = 0.25 + Math.random() * 0.55; // individual oscillation speed
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));

    const material = new THREE.PointsMaterial({
      size: 0.038,
      sizeAttenuation: true,
      color: new THREE.Color(0xffffff),
      transparent: true,
      opacity: 0.55,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });

    const points = new THREE.Points(geometry, material);
    scene.add(points);

    const buildRing = (radius: number, particles: number, yOffset = 0) => {
      const arr = new Float32Array(particles * 3);
      for (let i = 0; i < particles; i++) {
        const a = (i / particles) * Math.PI * 2;
        arr[i * 3]     = Math.cos(a) * radius;
        arr[i * 3 + 1] = yOffset;
        arr[i * 3 + 2] = Math.sin(a) * radius;
      }
      const g = new THREE.BufferGeometry();
      g.setAttribute("position", new THREE.BufferAttribute(arr, 3));
      const m = new THREE.PointsMaterial({
        size: 0.028,
        color: 0xffffff,
        transparent: true,
        opacity: 0.0,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
      });
      return new THREE.Points(g, m);
    };
    const ringEquator  = buildRing(1.0, 90,  0);
    const ringTop      = buildRing(0.55, 60,  0.82);
    const ringTop2     = buildRing(0.30, 40,  0.95);
    const ringBottom   = buildRing(0.55, 60, -0.82);
    const ringBottom2  = buildRing(0.30, 40, -0.95);
    const rings = [ringEquator, ringTop, ringTop2, ringBottom, ringBottom2];
    rings.forEach((r) => scene.add(r));

    const resize = () => {
      const w = container.clientWidth;
      const h = container.clientHeight;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(container);

    let isDown = false;
    let lastX = 0, lastY = 0;
    let velX = 0, velY = 0;
    const onDown = (e: PointerEvent) => {
      isDown = true; lastX = e.clientX; lastY = e.clientY;
      (e.target as Element).setPointerCapture?.(e.pointerId);
    };
    const onMove = (e: PointerEvent) => {
      if (!isDown) return;
      velX = (e.clientY - lastY) * 0.005;
      velY = (e.clientX - lastX) * 0.005;
      points.rotation.x += velX;
      points.rotation.y += velY;
      lastX = e.clientX; lastY = e.clientY;
    };
    const onUp = () => { isDown = false; };
    const dom = renderer.domElement;
    dom.addEventListener("pointerdown", onDown);
    dom.addEventListener("pointermove", onMove);
    dom.addEventListener("pointerup", onUp);
    dom.addEventListener("pointercancel", onUp);

    let currentScale = 1;
    let ringOpacity = 0;
    let currentDensity = 0.038;
    let currentOpacity = 0.55;
    let t = 0;
    let raf = 0;

    const animate = () => {
      raf = requestAnimationFrame(animate);
      const s = stateRef.current;
      const params = STATE_PARAMS[s];
      const vol = volumeRef.current;
      const volBoost = Math.min(1, vol * 4);

      const targetScale = params.scale + volBoost * 0.06;
      currentScale += (targetScale - currentScale) * 0.05;
      points.scale.setScalar(currentScale);

      const targetOpacity = params.opacity + volBoost * 0.1;
      currentOpacity += (targetOpacity - currentOpacity) * 0.05;
      material.opacity = currentOpacity;

      const breath = 1 + Math.sin(t * params.pulseRate) * 0.12;
      const targetDensity = params.density * breath + volBoost * 0.012;
      currentDensity += (targetDensity - currentDensity) * 0.08;
      material.size = currentDensity;

      const targetRing = params.ringIntensity + volBoost * 0.4;
      ringOpacity += (targetRing - ringOpacity) * 0.04;
      rings.forEach((r, i) => {
        const mat = r.material as THREE.PointsMaterial;
        const pulse = 0.7 + Math.sin(t * params.pulseRate + i * 0.8) * 0.3;
        mat.opacity = ringOpacity * pulse;
        mat.size = 0.026 + currentDensity * 0.2;
        r.scale.setScalar(currentScale);
      });
      const ringSpeedScale = 0.3 + ringOpacity;
      ringEquator.rotation.y  += (0.010 + params.speed) * ringSpeedScale;
      ringTop.rotation.y      -= 0.018 * ringSpeedScale;
      ringTop2.rotation.y     -= 0.030 * ringSpeedScale;
      ringBottom.rotation.y   -= 0.018 * ringSpeedScale;
      ringBottom2.rotation.y  -= 0.030 * ringSpeedScale;

      if (shapeRef.current !== currentShape) {
        currentShape = shapeRef.current;
        morphRef.current = {
          from: new Float32Array(basePositions),
          to: generateShape(currentShape, COUNT),
          t: 0,
          active: true,
        };
      }

      if (morphRef.current?.active) {
        const m = morphRef.current;
        m.t = Math.min(1, m.t + 0.018);
        const e = m.t < 0.5 ? 2 * m.t * m.t : 1 - Math.pow(-2 * m.t + 2, 2) / 2;
        for (let i = 0; i < COUNT * 3; i++) {
          basePositions[i] = m.from[i] + (m.to[i] - m.from[i]) * e;
        }
        if (m.t >= 1) m.active = false;
      }

      if (!isDown) {
        velX *= 0.95; velY *= 0.95;
        points.rotation.x += velX;
        points.rotation.y += velY + params.speed;
      } else {
        points.rotation.y += params.speed;
      }

      // ── Particle burst/retraction ─────────────────────────────────────
      // Each particle oscillates individually along its radial direction,
      // going outside the sphere boundary and coming back in.
      t += 0.016;
      const pos = geometry.getAttribute("position") as THREE.BufferAttribute;
      const jitter = params.jitter + volBoost * 0.04;
      const burst = params.burstFactor + volBoost * 0.6;

      for (let i = 0; i < COUNT; i++) {
        const ix = i * 3;
        let bx = basePositions[ix];
        let by = basePositions[ix + 1];
        let bz = basePositions[ix + 2];

        // Base radius from sphere centre
        const dist = Math.sqrt(bx * bx + by * by + bz * bz) || 1;

        // Jitter in tangential directions
        const wave = Math.sin(t * (1.5 + params.pulseRate) + i * 0.35) * jitter;
        bx *= (1 + wave);
        by *= (1 + wave);
        bz *= (1 + wave);

        // Radial burst: positive half of sine → particle flies outward
        const sinVal = Math.sin(t * burstSpeed[i] + burstPhase[i]);
        const outFactor = Math.max(0, sinVal);   // 0 when returning, >0 when exploding
        const radialExtra = outFactor * burstAmp[i] * burst * 0.35;

        const nx = bx / dist;
        const ny = by / dist;
        const nz = bz / dist;

        pos.array[ix]     = bx + nx * radialExtra;
        pos.array[ix + 1] = by + ny * radialExtra;
        pos.array[ix + 2] = bz + nz * radialExtra;
      }
      pos.needsUpdate = true;

      renderer.render(scene, camera);
    };
    animate();

    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
      dom.removeEventListener("pointerdown", onDown);
      dom.removeEventListener("pointermove", onMove);
      dom.removeEventListener("pointerup", onUp);
      dom.removeEventListener("pointercancel", onUp);
      geometry.dispose();
      material.dispose();
      rings.forEach((r) => {
        r.geometry.dispose();
        (r.material as THREE.PointsMaterial).dispose();
      });
      renderer.dispose();
      if (dom.parentNode) dom.parentNode.removeChild(dom);
    };
  }, []);

  if (webglFailed) {
    return <CssFallbackSphere className={className} />;
  }

  return (
    <div
      ref={containerRef}
      className={className ?? "w-full h-full"}
      aria-hidden="true"
    />
  );
}
