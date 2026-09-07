import { useLanguage } from './LanguageContext';
import useScrollAnimation from './useScrollAnimation';

export default function Services() {
  const { t } = useLanguage();
  const servicesRef = useScrollAnimation();

  return (
    <section id="services" className="services-section">
      <h2>{t.services.title}</h2>
      <p className="no-print-notice">{t.services.note}</p>
      <div ref={servicesRef} className="services-grid fade-in slide-up">
        {t.services.items.map((s, idx) => (
          <div key={idx} className="service-card glass">
            <span className="icon">{s.icon}</span>
            <h3>{s.title}</h3>
            <p>{s.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

