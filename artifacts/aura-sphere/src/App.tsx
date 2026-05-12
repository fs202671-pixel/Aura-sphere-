import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { ThemeProvider } from "next-themes";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import Index from "./pages/Index.tsx";
import NotFound from "./pages/NotFound.tsx";
import { AIOnShellTabs } from "./components/AIOnShellTabs.tsx";
import { useDynamicStyles } from "@/hooks/useVisualCustomization";

const queryClient = new QueryClient();
const basePath = import.meta.env.BASE_URL?.replace(/\/$/, "") || "";

const DynamicStylesProvider = ({ children }: { children: React.ReactNode }) => {
  useDynamicStyles();
  return <>{children}</>;
};

function AppRoutes() {
  return (
    <QueryClientProvider client={queryClient}>
      <DynamicStylesProvider>
        <Toaster />
        <Sonner />
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/shell" element={<AIOnShellTabs />} />
          <Route path="/control-panel" element={<AIOnShellTabs />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </DynamicStylesProvider>
    </QueryClientProvider>
  );
}

const App = () => (
  <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
    <TooltipProvider>
      <BrowserRouter basename={basePath}>
        <AppRoutes />
      </BrowserRouter>
    </TooltipProvider>
  </ThemeProvider>
);

export default App;
