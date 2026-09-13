import { useState } from 'react';
import { useLanguage } from './LanguageContext';
import { useAuth } from './AuthContext';
import useScrollAnimation from './useScrollAnimation';

export default function OrderForm() {
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const { t } = useLanguage();
  const { user, isAuthenticated } = useAuth();
  const formRef = useScrollAnimation();
  const [formData, setFormData] = useState(() => ({
    name: user?.name || '',
    phone: user?.phone || user?.email || '',
    service: '',
    details: '',
    fileName: ''
  }));

  const serviceLabels = {
    university: t.order.servicesList?.university || 'ثبت‌نام دانشگاهی و آزمون‌ها',
    tax: t.order.servicesList?.tax || 'اظهارنامه و امور مالیاتی',
    translation: t.order.servicesList?.translation || 'ترجمه آنلاین و رسمی',
    visa: t.order.servicesList?.visa || 'درخواست ویزا و وقت سفارت',
    insurance: t.order.servicesList?.insurance || 'امور بیمه و تامین اجتماعی',
    business: t.order.servicesList?.business || 'ثبت شرکت و برند تجاری',
    legal: t.order.servicesList?.legal || 'امور ثبتی و استعلامات قانونی',
    other: t.order.servicesList?.other || 'سایر موارد (توضیح در بخش توضیحات)'
  };

  const getTelegramUrl = () => {
    const serviceName = serviceLabels[formData.service] || formData.service || 'سایر';
    const clientTypeStr = user?.role === 'agency' ? ` (آژانس: ${user.agencyName || user.name})` : '';
    const message = `سلام، درخواست جدید خدمات VIP:

👤 نام: ${formData.name}${clientTypeStr}
📱 تماس/آیدی: ${formData.phone}
📋 نوع خدمت: ${serviceName}${formData.details ? `
📝 توضیحات: ${formData.details}` : ''}`;
    return `https://t.me/airboxvip_admin?text=${encodeURIComponent(message)}`;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    const newOrder = {
      id: 'ORD-' + Date.now(),
      ...formData,
      userId: user?.id || null,
      userRole: user?.role || 'guest',
      createdAt: new Date().toISOString()
    };
    
    // Save locally
    try {
      const existingOrders = JSON.parse(localStorage.getItem('airbox_orders') || '[]');
      localStorage.setItem('airbox_orders', JSON.stringify([...existingOrders, newOrder]));
    } catch {
      // Ignore
    }

    const tgUrl = getTelegramUrl();
    window.open(tgUrl, '_blank');
    setSubmitted(true);
    setLoading(false);
  };

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    if (name === 'file' && files && files[0]) {
      setFormData(prev => ({ ...prev, fileName: files[0].name }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleReset = () => {
    setFormData({
      name: user?.name || '',
      phone: user?.phone || user?.email || '',
      service: '',
      details: '',
      fileName: ''
    });
    setSubmitted(false);
  };

  return (
    <section id="order" className="order-section">
      <div ref={formRef} className="form-container glass fade-in slide-up">
        <h2>{t.order.title}</h2>

        {/* Authenticated user status banner */}
        {isAuthenticated && !submitted && (
          <div className="auth-order-banner">
            <span className="auth-order-banner-icon">💠</span>
            <div className="auth-order-banner-text">
              <span>{t.auth?.orderBanner || 'Ordering as:'} </span>
              <strong>{user.name}</strong> ({user.phone || user.email})
              {user.role === 'agency' && (
                <span className="auth-agency-tag"> 🏢 {user.agencyName || (t.auth?.roleAgency || 'Agency')}</span>
              )}
            </div>
          </div>
        )}

        {submitted ? (
          <div className="success-message">
            <span className="success-icon">✨</span>
            <h3>{t.order.successTitle}</h3>
            <p style={{ marginBottom: '1.5rem' }}>{t.order.successMessage}</p>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
              <a 
                href={getTelegramUrl()} 
                target="_blank" 
                rel="noreferrer" 
                className="submit-btn" 
                style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', width: 'auto', padding: '0.8rem 1.5rem' }}
              >
                📱 ارسال نهایی در تلگرام
              </a>
              <button onClick={handleReset} className="btn secondary">{t.order.title}</button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="input-group">
              <label>{t.order.name}</label>
              <input type="text" name="name" required placeholder="John Doe" value={formData.name} onChange={handleChange} />
            </div>
            <div className="input-group">
              <label>{t.order.phone}</label>
              <input type="text" name="phone" required placeholder="0912... / @telegram" value={formData.phone} onChange={handleChange} />
            </div>
            <div className="input-group">
              <label>{t.order.service}</label>
              <select name="service" required value={formData.service} onChange={handleChange}>
                <option value="">{t.order.servicesList.select}</option>
                <option value="university">{t.order.servicesList.university}</option>
                <option value="tax">{t.order.servicesList.tax}</option>
                <option value="translation">{t.order.servicesList.translation}</option>
                <option value="visa">{t.order.servicesList.visa}</option>
                <option value="insurance">{t.order.servicesList.insurance}</option>
                <option value="business">{t.order.servicesList.business}</option>
                <option value="legal">{t.order.servicesList.legal}</option>
                <option value="other">{t.order.servicesList.other}</option>
              </select>
            </div>
            <div className="input-group">
              <label>{t.order.details}</label>
              <textarea name="details" rows="3" placeholder="..." value={formData.details} onChange={handleChange}></textarea>
            </div>
            <div className="input-group">
              <label>{t.order.secureUpload}</label>
              <input type="file" name="file" onChange={handleChange} />
            </div>
            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? '...' : t.order.submit}
            </button>
          </form>
        )}
      </div>
    </section>
  );
}
