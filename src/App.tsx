import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import PatientAuth from "./pages/PatientAuth";
import HospitalAuth from "./pages/HospitalAuth";
import PharmacyAuth from "./pages/PharmacyAuth";
import PatientDashboard from "./pages/PatientDashboard";
import HospitalDashboard from "./pages/HospitalDashboard";
import PharmacyDashboard from "./pages/PharmacyDashboard";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/auth/patient" element={<PatientAuth />} />
          <Route path="/auth/hospital" element={<HospitalAuth />} />
          <Route path="/auth/pharmacy" element={<PharmacyAuth />} />
          <Route path="/patient/dashboard" element={<PatientDashboard />} />
          <Route path="/hospital/dashboard" element={<HospitalDashboard />} />
          <Route path="/pharmacy/dashboard" element={<PharmacyDashboard />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
