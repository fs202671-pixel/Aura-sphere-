import React, { useState, useEffect } from 'react';

interface MiniOverlayProps {
  onClick: () => void;
  isMinimized: boolean;
}

export function MiniOverlay({ onClick, isMinimized }: MiniOverlayProps) {
  const [particles, setParticles] = useState<Array<{id: number, x: number, y: number, vx: number, vy: number, connections: number[]}>>([]);

  useEffect(() => {
    if (!isMinimized) return;

    // Criar partículas da rede neural
    const newParticles = Array.from({ length: 8 }, (_, i) => ({
      id: i,
      x: Math.random() * 60 + 20, // Dentro da bolinha pequena
      y: Math.random() * 60 + 20,
      vx: (Math.random() - 0.5) * 0.5, // Movimento lento
      vy: (Math.random() - 0.5) * 0.5,
      connections: []
    }));

    // Criar conexões entre partículas próximas
    newParticles.forEach(particle => {
      particle.connections = newParticles
        .filter(p => p.id !== particle.id)
        .filter(p => Math.sqrt((p.x - particle.x) ** 2 + (p.y - particle.y) ** 2) < 40)
        .map(p => p.id);
    });

    setParticles(newParticles);

    // Animação das partículas
    const interval = setInterval(() => {
      setParticles(prev => prev.map(particle => {
        let newX = particle.x + particle.vx;
        let newY = particle.y + particle.vy;

        // Bater nas bordas e ricochetear
        if (newX <= 10 || newX >= 70) {
          particle.vx *= -1;
          newX = Math.max(10, Math.min(70, newX));
        }
        if (newY <= 10 || newY >= 70) {
          particle.vy *= -1;
          newY = Math.max(10, Math.min(70, newY));
        }

        return { ...particle, x: newX, y: newY };
      }));
    }, 50);

    return () => clearInterval(interval);
  }, [isMinimized]);

  if (!isMinimized) return null;

  return (
    <div
      onClick={onClick}
      className="fixed bottom-4 right-4 w-20 h-20 bg-gradient-to-br from-blue-500/20 to-purple-500/20 backdrop-blur-md rounded-full border border-white/20 cursor-pointer hover:scale-110 transition-transform duration-300 z-50 shadow-2xl"
      style={{
        background: 'radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, rgba(147, 51, 234, 0.1) 100%)',
        boxShadow: '0 0 30px rgba(59, 130, 246, 0.3), inset 0 0 30px rgba(59, 130, 246, 0.1)'
      }}
    >
      {/* Partículas animadas */}
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 80 80">
        {/* Conexões */}
        {particles.map(particle =>
          particle.connections.map(targetId => {
            const target = particles.find(p => p.id === targetId);
            if (!target) return null;
            return (
              <line
                key={`${particle.id}-${targetId}`}
                x1={particle.x}
                y1={particle.y}
                x2={target.x}
                y2={target.y}
                stroke="rgba(59, 130, 246, 0.3)"
                strokeWidth="0.5"
                className="animate-pulse"
              />
            );
          })
        )}

        {/* Partículas */}
        {particles.map(particle => (
          <circle
            key={particle.id}
            cx={particle.x}
            cy={particle.y}
            r="2"
            fill="rgba(59, 130, 246, 0.8)"
            className="animate-pulse"
          />
        ))}
      </svg>

      {/* Centro pulsante */}
      <div className="absolute inset-1/2 transform -translate-x-1/2 -translate-y-1/2 w-3 h-3 bg-blue-400 rounded-full animate-ping opacity-75"></div>
      <div className="absolute inset-1/2 transform -translate-x-1/2 -translate-y-1/2 w-2 h-2 bg-blue-500 rounded-full"></div>
    </div>
  );
}