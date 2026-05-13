import { useState, useEffect } from "react";
import { Switch, Route, Router as WouterRouter } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppLayout } from "@/components/layout";
import { OnboardingModal, useOnboarding, skipOnboarding } from "@/components/onboarding";
import { FloatingSphere } from "@/components/floating-sphere";
import { AnimatePresence } from "framer-motion";
import { loadSavedTheme } from "@/lib/themes";

import Home from "@/pages/home";
import Shell from "@/pages/shell";
import Dashboard from "@/pages/dashboard";
import Skills from "@/pages/skills";
import Study from "@/pages/study";
import Fuse from "@/pages/fuse";
import Chat from "@/pages/chat";
import Profile from "@/pages/profile";
import Settings from "@/pages/settings";
import Builder from "@/pages/builder";
import Security from "@/pages/security";
import Professor from "@/pages/professor";
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
  loadSavedTheme();
}

function AppRouter() {
  useOnboarding();
  const [showOnboarding, _setShowOnboarding] = useState(false);

  return (
    <>
      <AppLayout>
        <Switch>
          <Route path="/" component={Shell} />
          <Route path="/shell" component={Shell} />
          <Route path="/builder" component={Builder} />
          <Route path="/professor" component={Professor} />
          <Route path="/seguranca" component={Security} />
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

      <FloatingSphere />
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
