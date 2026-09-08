import { useState } from 'react';
import { useLanguage } from './LanguageContext';
import useScrollAnimation from './useScrollAnimation';

export default function FAQ() {
  const { t } = useLanguage();
  const faqRef = useScrollAnimation();
  const [openIndex, setOpenIndex] = useState(null);

  const toggleFAQ = (idx) => {
    setOpenIndex(openIndex === idx ? null : idx);
  };

  return (
    <section id="faq" className="faq-section">
      <h2>{t.faq.title}</h2>
      <div ref={faqRef} className="faq-list fade-in slide-up">
        {t.faq.items.map((f, idx) => {
          const isOpen = openIndex === idx;
          return (
            <div 
              key={idx} 
              className={`faq-item glass accordion-item ${isOpen ? 'active' : ''}`}
              onClick={() => toggleFAQ(idx)}
            >
              <div className="faq-header">
                <h4>{f.q}</h4>
                <span className="faq-toggle-icon">{isOpen ? '−' : '+'}</span>
              </div>
              {isOpen && <p className="faq-body">{f.a}</p>}
            </div>
          );
        })}
      </div>
    </section>
  );
}
