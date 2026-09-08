import Navbar from './Navbar';
import Hero from './Hero';
import Services from './Services';
import OrderForm from './OrderForm';
import FAQ from './FAQ';
import Footer from './Footer';
import { LanguageProvider } from './LanguageContext';

function App() {
  return (
    <LanguageProvider>
      <Navbar />
      <main>
        <Hero />
        <Services />
        <OrderForm />
        <FAQ />
      </main>
      <Footer />
    </LanguageProvider>
  )
}

export default App
