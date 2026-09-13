import { useState, useEffect } from 'react';
import { useLanguage } from './LanguageContext';
import { useAuth } from './AuthContext';
import { FiGlobe, FiMenu, FiX, FiUser, FiLogOut, FiLogIn, FiBriefcase } from 'react-icons/fi';
import useScrollAnimation from './useScrollAnimation';

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { lang, toggleLanguage, t } = useLanguage();
  const { user, isAuthenticated, openAuthModal, logout } = useAuth();
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
          
          <button onClick={toggleLanguage} className="lang-toggle" aria-label="Toggle language">
            <FiGlobe /> {lang === 'en' ? 'FA' : 'EN'}
          </button>

          {!isAuthenticated ? (
            <div className="auth-nav-actions">
              <button 
                type="button" 
                onClick={() => openAuthModal('signin')} 
                className="nav-auth-btn"
              >
                <FiLogIn /> {t.auth?.navSignIn || 'Sign In'}
              </button>
              <button 
                type="button" 
                onClick={() => openAuthModal('signup')} 
                className="cta-btn"
              >
                {t.auth?.navSignUp || 'Sign Up'}
              </button>
            </div>
          ) : (
            <div className="auth-nav-user-group">
              <div className="auth-user-chip">
                <span className="auth-user-avatar">
                  {user.role === 'agency' ? <FiBriefcase /> : <FiUser />}
                </span>
                <span className="auth-user-name">{user.name}</span>
                <span className="auth-role-badge">
                  {user.role === 'agency' ? (t.auth?.roleAgency || 'Agency') : (t.auth?.roleClient || 'Client')}
                </span>
              </div>
              <button 
                type="button" 
                onClick={logout} 
                className="auth-logout-btn" 
                title={t.auth?.logout || 'Logout'}
                aria-label="Log out"
              >
                <FiLogOut /> <span>{t.auth?.logout || 'Logout'}</span>
              </button>
            </div>
          )}
        </div>

        {/* Mobile Actions & Hamburger Toggle */}
        <div className="mobile-actions">
          <button onClick={toggleLanguage} className="lang-toggle mobile-lang-btn" aria-label="Toggle language">
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

          {!isAuthenticated ? (
            <div className="mobile-auth-section">
              <button 
                type="button" 
                onClick={() => { closeMobileMenu(); openAuthModal('signin'); }} 
                className="nav-auth-btn mobile-auth-btn"
              >
                <FiLogIn /> {t.auth?.navSignIn || 'Sign In'}
              </button>
              <button 
                type="button" 
                onClick={() => { closeMobileMenu(); openAuthModal('signup'); }} 
                className="cta-btn mobile-cta"
              >
                {t.auth?.navSignUp || 'Sign Up'}
              </button>
            </div>
          ) : (
            <div className="mobile-user-box">
              <div className="auth-user-chip">
                <span className="auth-user-avatar">
                  {user.role === 'agency' ? <FiBriefcase /> : <FiUser />}
                </span>
                <span className="auth-user-name">{user.name}</span>
                <span className="auth-role-badge">
                  {user.role === 'agency' ? (t.auth?.roleAgency || 'Agency') : (t.auth?.roleClient || 'Client')}
                </span>
              </div>
              <button 
                type="button" 
                onClick={() => { logout(); closeMobileMenu(); }} 
                className="auth-logout-btn mobile-logout-btn"
              >
                <FiLogOut /> {t.auth?.logout || 'Logout'}
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
