import { useEffect, useState } from "react";
import { useLocalAuth } from "@/hooks/useLocalAuth";
import { CaosEntry } from "@/components/CaosEntry";
import { SyncStatus } from "@/components/SyncStatus";
import AIOnShell from "@/components/AIOnShell";

type Profile = {
  ai_name: string | null;
  voice_id: string | null;
  onboarded: boolean;
};

const Index = () => {
  const { user: localUser, isAuthenticated, createLocalUser } = useLocalAuth();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [currentUser, setCurrentUser] = useState<{
    id: string;
    name?: string;
    isLocal?: boolean;
  } | null>(null);

  const isDemoMode =
    import.meta.env.VITE_DEMO_MODE === "true" ||
    window.location.search.includes("demo=true");

  useEffect(() => {
    if (isDemoMode) {
      setCurrentUser({ id: "demo_user", name: "Caos" });
      setProfile({ ai_name: "Caos", voice_id: "pt-female", onboarded: true });
      return;
    }

    if (localUser?.isLocal) {
      setCurrentUser(localUser);
      setProfile({
        ai_name: localUser.name || "Caos",
        voice_id: "pt-female",
        onboarded: true,
      });
      return;
    }

    setCurrentUser(null);
    setProfile(null);
  }, [isAuthenticated, localUser, isDemoMode]);

  const handleEnter = () => {
    const user = createLocalUser("Caos");
    setCurrentUser(user);
    setProfile({ ai_name: "Caos", voice_id: "pt-female", onboarded: true });
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setProfile(null);
  };

  if (!currentUser && !isDemoMode) {
    return <CaosEntry onEnter={handleEnter} />;
  }

  if (!profile) {
    return <CaosEntry onEnter={handleEnter} />;
  }

  return (
    <div className="min-h-[100dvh] flex flex-col">
      {isDemoMode && (
        <div className="flex justify-between items-center p-4 border-b bg-black/80 backdrop-blur-sm">
          <h1 className="text-lg font-semibold">Caos — Modo Demo</h1>
          <SyncStatus />
        </div>
      )}
      <div className="flex-1">
        <AIOnShell
          userId={currentUser!.id}
          aiName={profile.ai_name ?? "Caos"}
          voiceId={
            (profile.voice_id as "pt-female" | "pt-male" | "en-female") ??
            "pt-female"
          }
          onLogout={handleLogout}
        />
      </div>
    </div>
  );
};

export default Index;
