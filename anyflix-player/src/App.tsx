import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SWRConfig } from "swr";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Home from "./pages/Home";
import Auth from "./pages/Auth";
import NotFound from "./pages/NotFound";
import Aniworld from "./pages/Aniworld";
import { RemoteControlDev } from "./components/RemoteControlDev";
import { KeyRemoteNavigationProvider } from "./hooks/KeyRemoteNavigationProvider";

const queryClient = new QueryClient();

// SWR configuration
const swrConfig = {
  revalidateOnFocus: false,
  revalidateOnReconnect: true,
  shouldRetryOnError: true,
  errorRetryCount: 3,
  errorRetryInterval: 1000,
  dedupingInterval: 2000,
};

const App = () => (
  <KeyRemoteNavigationProvider>
    <QueryClientProvider client={queryClient}>
      <SWRConfig value={swrConfig}>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <div className="min-h-screen bg-background">
              <Navbar />
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/auth" element={<Auth />} />
                <Route
                  path="/tv-shows"
                  element={
                    <div className="pt-16 text-white text-center">
                      TV Shows - Coming Soon
                    </div>
                  }
                />
                <Route path="/aniworld" element={<Aniworld />} />
                <Route path="/test" element={<RemoteControlDev />} />

                {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </div>
          </BrowserRouter>
        </TooltipProvider>
      </SWRConfig>
    </QueryClientProvider>
  </KeyRemoteNavigationProvider>
);

export default App;
