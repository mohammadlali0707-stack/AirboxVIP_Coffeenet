import { useLanguage } from './LanguageContext';
import { useScrollAnimation } from './useScrollAnimation';

export default function Hero() {
  const { t } = useLanguage();
  const heroRef = useScrollAnimation();

  return (
    <section className="hero">
      <div ref={heroRef} className="hero-content fade-in slide-up">
        <h1 className="hero-title">{t.hero.title} <span className="highlight">{t.hero.highlight}</span></h1>
        <p className="hero-subtitle">{t.hero.subtitle}</p>
        <div className="hero-actions">
          <a href="#services" className="btn primary" style={{ display: 'inline-block', textDecoration: 'none' }}>{t.hero.explore}</a>
          <a href="#order" className="btn secondary" style={{ display: 'inline-block', textDecoration: 'none' }}>{t.hero.viewPlans}</a>
        </div>
      </div>
      <div className="hero-glow"></div>
    </section>
  );
}
