import { useState } from "react";
import { Switch, Route, Router as WouterRouter } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppLayout } from "@/components/layout";
import { OnboardingModal, useOnboarding } from "@/components/onboarding";
import { AnimatePresence } from "framer-motion";

import Home from "@/pages/home";
import Shell from "@/pages/shell";
import Dashboard from "@/pages/dashboard";
import Skills from "@/pages/skills";
import Study from "@/pages/study";
import Fuse from "@/pages/fuse";
import Chat from "@/pages/chat";
import Profile from "@/pages/profile";
import Settings from "@/pages/settings";
import StudioHome from "@/pages/studio/index";
import Arsenal from "@/pages/studio/arsenal";
import Agents from "@/pages/studio/agents";
import Themes from "@/pages/studio/themes";
import Missions from "@/pages/studio/missions";
import ItemDetail from "@/pages/studio/item-detail";
import NotFound from "@/pages/not-found";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

if (typeof document !== "undefined") {
  document.documentElement.classList.add("dark");
}

function AppRouter() {
  const { needsOnboarding } = useOnboarding();
  const [showOnboarding, setShowOnboarding] = useState(needsOnboarding);

  return (
    <>
      <AppLayout>
        <Switch>
          <Route path="/" component={Home} />
          <Route path="/shell" component={Shell} />
          <Route path="/caos" component={Dashboard} />
          <Route path="/caos/habilidades" component={Skills} />
          <Route path="/caos/estudar" component={Study} />
          <Route path="/caos/fusao" component={Fuse} />
          <Route path="/caos/terminal" component={Chat} />
          <Route path="/caos/perfil" component={Profile} />
          <Route path="/studio" component={StudioHome} />
          <Route path="/studio/arsenal" component={Arsenal} />
          <Route path="/studio/entidades" component={Agents} />
          <Route path="/studio/fragmentos" component={Themes} />
          <Route path="/studio/missoes" component={Missions} />
          <Route path="/studio/itens/:id" component={ItemDetail} />
          <Route path="/configuracoes" component={Settings} />
          <Route component={NotFound} />
        </Switch>
      </AppLayout>

      <AnimatePresence>
        {showOnboarding && (
          <OnboardingModal onComplete={() => setShowOnboarding(false)} />
        )}
      </AnimatePresence>
    </>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
          <AppRouter />
        </WouterRouter>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
