import { Routes, Route, Navigate } from "react-router-dom";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { ScrollToTop } from "@/components/common/ScrollToTop";
import { Home } from "@/pages/Home";
import { About } from "@/pages/About";
import { Services } from "@/pages/Services";
import { Gallery } from "@/pages/Gallery";
import { AISizeFinder } from "@/pages/AISizeFinder";
import { FAQ } from "@/pages/FAQ";
import { Contact } from "@/pages/Contact";
import { Booking } from "@/pages/Booking";
import { NotFound } from "@/pages/NotFound";

export function App() {
  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground">
      <ScrollToTop />
      <Header />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/services" element={<Services />} />
          <Route path="/gallery" element={<Gallery />} />
          <Route path="/ai-nail-size-finder" element={<AISizeFinder />} />
          <Route path="/ai-size-finder" element={<Navigate to="/ai-nail-size-finder" replace />} />
          <Route path="/faq" element={<FAQ />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/booking" element={<Booking />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;
