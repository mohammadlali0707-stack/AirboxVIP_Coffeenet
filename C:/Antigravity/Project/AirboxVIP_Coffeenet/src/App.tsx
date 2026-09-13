import Navbar from './Navbar';
import Hero from './Hero';
import Services from './Services';
import OrderForm from './OrderForm';
import FAQ from './FAQ';
import Footer from './Footer';
import AuthModal from './AuthModal';
import { LanguageProvider } from './LanguageContext';
import { AuthProvider } from './AuthContext';

function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <Navbar />
        <main>
          <Hero />
          <Services />
          <OrderForm />
          <FAQ />
        </main>
        <Footer />
        <AuthModal />
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;
