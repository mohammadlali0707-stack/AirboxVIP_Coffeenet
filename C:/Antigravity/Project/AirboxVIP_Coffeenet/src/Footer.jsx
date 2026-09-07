import { useLanguage } from './LanguageContext';
import useScrollAnimation from './useScrollAnimation';

export default function Footer() {
  const { t } = useLanguage();
  const footerRef = useScrollAnimation();

  return (
    <footer className="footer-section">
      <div ref={footerRef} className="footer-content glass fade-in slide-up">
        <div className="brand-info">
          <h2>{t.footer.title}</h2>
          <p>{t.footer.desc}</p>
        </div>
        <div className="contact-links">
          <a href="https://t.me/airboxvipcoffeenet" target="_blank" rel="noreferrer">{t.footer.telegram}</a>
          <a href="http://t.me/airboxvip_admin" target="_blank" rel="noreferrer">{t.footer.email}</a>
        </div>
        <div className="copyright">
          <p>{t.footer.rights}</p>
        </div>
      </div>
    </footer>
  );
}

