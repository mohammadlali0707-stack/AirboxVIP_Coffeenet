import { useState, useEffect } from 'react';
import { useLanguage } from './LanguageContext';
import { FiGlobe, FiMenu, FiX } from 'react-icons/fi';
import useScrollAnimation from './useScrollAnimation';

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { lang, toggleLanguage, t } = useLanguage();
  const navContainerRef = useScrollAnimation();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const closeMobileMenu = () => setMobileMenuOpen(false);

  return (
    <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
      <div ref={navContainerRef} className="nav-container fade-in">
        <div className="brand">
          <span className="logo-icon">💠</span>
          <h1>AirboxVIP</h1>
        </div>

        {/* Desktop Links */}
        <div className="nav-links desktop-only">
          <a href="#services">{t.nav.services}</a>
          <a href="#order">{t.nav.order}</a>
          <a href="#faq">{t.nav.faq}</a>
          <button onClick={toggleLanguage} className="lang-toggle">
            <FiGlobe /> {lang === 'en' ? 'FA' : 'EN'}
          </button>
          <a href="#order" className="cta-btn" style={{ display: 'inline-block', textDecoration: 'none' }}>
            {t.nav.accessVIP}
          </a>
        </div>

        {/* Mobile Actions & Hamburger Toggle */}
        <div className="mobile-actions">
          <button onClick={toggleLanguage} className="lang-toggle mobile-lang-btn">
            <FiGlobe /> {lang === 'en' ? 'FA' : 'EN'}
          </button>
          <button
            className="hamburger-btn"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle Navigation Menu"
          >
            {mobileMenuOpen ? <FiX size={26} /> : <FiMenu size={26} />}
          </button>
        </div>

        {/* Mobile Drawer Overlay */}
        <div className={`mobile-drawer ${mobileMenuOpen ? 'open' : ''}`}>
          <a href="#services" onClick={closeMobileMenu}>{t.nav.services}</a>
          <a href="#order" onClick={closeMobileMenu}>{t.nav.order}</a>
          <a href="#faq" onClick={closeMobileMenu}>{t.nav.faq}</a>
          <a href="#order" className="cta-btn mobile-cta" onClick={closeMobileMenu}>
            {t.nav.accessVIP}
          </a>
        </div>
      </div>
    </nav>
  );
}
