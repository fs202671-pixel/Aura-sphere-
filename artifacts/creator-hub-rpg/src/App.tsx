import { Switch, Route, Router as WouterRouter } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppLayout } from "@/components/layout";

import Dashboard from "@/pages/dashboard";
import Library from "@/pages/library";
import Themes from "@/pages/themes";
import Agents from "@/pages/agents";
import Skills from "@/pages/skills";
import Projects from "@/pages/projects";
import ItemDetail from "@/pages/item-detail";
import NotFound from "@/pages/not-found";

const queryClient = new QueryClient();

function Router() {
  return (
    <AppLayout>
      <Switch>
        <Route path="/" component={Dashboard} />
        <Route path="/arsenal" component={Library} />
        <Route path="/fragmentos" component={Themes} />
        <Route path="/entidades" component={Agents} />
        <Route path="/protocolos" component={Skills} />
        <Route path="/missoes" component={Projects} />
        <Route path="/itens/:id" component={ItemDetail} />
        <Route component={NotFound} />
      </Switch>
    </AppLayout>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
          <Router />
        </WouterRouter>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
