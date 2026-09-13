import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { useLanguage } from './LanguageContext';
import { 
  FiX, 
  FiUser, 
  FiMail, 
  FiPhone, 
  FiLock, 
  FiEye, 
  FiEyeOff, 
  FiBriefcase, 
  FiCheckCircle, 
  FiAlertCircle,
  FiArrowRight,
  FiArrowLeft
} from 'react-icons/fi';

export default function AuthModal() {
  const { 
    authModalOpen, 
    closeAuthModal, 
    authModalTab, 
    setAuthModalTab, 
    login, 
    signup 
  } = useAuth();
  
  const { t, lang } = useLanguage();
  const isRtl = lang === 'fa';

  // Sign In State
  const [signInIdentifier, setSignInIdentifier] = useState('');
  const [signInPassword, setSignInPassword] = useState('');
  const [showSignInPassword, setShowSignInPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [showForgotHelp, setShowForgotHelp] = useState(false);

  // Sign Up State
  const [signUpRole, setSignUpRole] = useState('client'); // 'client' | 'agency'
  const [signUpName, setSignUpName] = useState('');
  const [signUpPhone, setSignUpPhone] = useState('');
  const [signUpEmail, setSignUpEmail] = useState('');
  const [signUpAgencyName, setSignUpAgencyName] = useState('');
  const [signUpPassword, setSignUpPassword] = useState('');
  const [signUpConfirmPassword, setSignUpConfirmPassword] = useState('');
  const [showSignUpPassword, setShowSignUpPassword] = useState(false);
  const [agreeTerms, setAgreeTerms] = useState(false);

  // Status & Feedback State
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Close on ESC key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && authModalOpen) {
        closeAuthModal();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [authModalOpen, closeAuthModal]);

  const handleTabSwitch = (tab) => {
    setErrorMsg('');
    setSuccessMsg('');
    setShowForgotHelp(false);
    setAuthModalTab(tab);
  };

  if (!authModalOpen) return null;

  const handleSignInSubmit = (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    if (!signInIdentifier.trim() || !signInPassword.trim()) {
      setErrorMsg(t.auth?.errors?.missingFields || 'Please fill in all fields.');
      return;
    }

    setLoading(true);
    const result = login({
      identifier: signInIdentifier,
      password: signInPassword,
      rememberMe
    });

    setLoading(false);
    if (!result.success) {
      setErrorMsg(t.auth?.errors?.invalidCredentials || 'Invalid username or password.');
    } else {
      setSuccessMsg(t.auth?.success?.welcomeBack || 'Logged in successfully!');
    }
  };

  const handleSignUpSubmit = (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    if (!signUpName.trim() || !signUpPhone.trim() || !signUpEmail.trim() || !signUpPassword.trim()) {
      setErrorMsg(t.auth?.errors?.missingFields || 'Please fill in all fields.');
      return;
    }

    if (signUpRole === 'agency' && !signUpAgencyName.trim()) {
      setErrorMsg(t.auth?.errors?.missingFields || 'Please enter your agency name.');
      return;
    }

    if (signUpPassword.length < 6) {
      setErrorMsg(t.auth?.errors?.shortPassword || 'Password must be at least 6 characters.');
      return;
    }

    if (signUpPassword !== signUpConfirmPassword) {
      setErrorMsg(t.auth?.errors?.passwordMismatch || 'Passwords do not match.');
      return;
    }

    if (!agreeTerms) {
      setErrorMsg(t.auth?.errors?.agreeRequired || 'You must agree to the terms.');
      return;
    }

    setLoading(true);
    const result = signup({
      name: signUpName,
      phone: signUpPhone,
      email: signUpEmail,
      password: signUpPassword,
      role: signUpRole,
      agencyName: signUpAgencyName,
      rememberMe: true
    });

    setLoading(false);
    if (!result.success) {
      if (result.error === 'user_exists') {
        setErrorMsg(t.auth?.errors?.userExists || 'An account with this email or phone already exists.');
      } else {
        setErrorMsg(t.auth?.errors?.generalError || 'Registration failed.');
      }
    } else {
      setSuccessMsg(t.auth?.success?.accountCreated || 'Account created successfully!');
    }
  };

  const handleQuickDemo = (role) => {
    setErrorMsg('');
    setSuccessMsg('');
    if (role === 'client') {
      setSignInIdentifier('client@airboxvip.top');
      setSignInPassword('password123');
      login({ identifier: 'client@airboxvip.top', password: 'password123', rememberMe: true });
    } else {
      setSignInIdentifier('agency@airboxvip.top');
      setSignInPassword('agency123');
      login({ identifier: 'agency@airboxvip.top', password: 'agency123', rememberMe: true });
    }
  };

  return (
    <div className="auth-modal-overlay" onClick={closeAuthModal}>
      <div 
        className="auth-modal glass" 
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        {/* Header */}
        <div className="auth-modal-header">
          <div className="auth-modal-title-group">
            <span className="auth-badge">💠 {t.auth?.portalBadge || 'AirboxVIP Online Agency'}</span>
            <h3>{authModalTab === 'signin' ? t.auth?.signInTab : t.auth?.signUpTab}</h3>
          </div>
          <button 
            className="auth-close-btn" 
            onClick={closeAuthModal}
            aria-label="Close modal"
          >
            <FiX size={20} />
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="auth-tabs">
          <button 
            type="button"
            className={`auth-tab ${authModalTab === 'signin' ? 'active' : ''}`}
            onClick={() => handleTabSwitch('signin')}
          >
            {t.auth?.signInTab}
          </button>
          <button 
            type="button"
            className={`auth-tab ${authModalTab === 'signup' ? 'active' : ''}`}
            onClick={() => handleTabSwitch('signup')}
          >
            {t.auth?.signUpTab}
          </button>
        </div>

        {/* Error / Success Feedback */}
        {errorMsg && (
          <div className="auth-alert-box error">
            <FiAlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
        )}
        {successMsg && (
          <div className="auth-alert-box success">
            <FiCheckCircle size={18} />
            <span>{successMsg}</span>
          </div>
        )}

        {/* Tab 1: Sign In Form */}
        {authModalTab === 'signin' && (
          <form onSubmit={handleSignInSubmit} className="auth-form">
            <div className="input-group">
              <label>{t.auth?.identifier}</label>
              <div className="auth-input-wrapper">
                <FiUser className="auth-input-icon" />
                <input 
                  type="text"
                  required
                  placeholder={t.auth?.identifierPlaceholder}
                  value={signInIdentifier}
                  onChange={(e) => setSignInIdentifier(e.target.value)}
                  autoFocus
                />
              </div>
            </div>

            <div className="input-group">
              <label>{t.auth?.password}</label>
              <div className="auth-input-wrapper">
                <FiLock className="auth-input-icon" />
                <input 
                  type={showSignInPassword ? 'text' : 'password'}
                  required
                  placeholder="••••••••"
                  value={signInPassword}
                  onChange={(e) => setSignInPassword(e.target.value)}
                />
                <button 
                  type="button" 
                  className="auth-eye-btn"
                  onClick={() => setShowSignInPassword(!showSignInPassword)}
                  aria-label="Toggle password visibility"
                >
                  {showSignInPassword ? <FiEyeOff size={16} /> : <FiEye size={16} />}
                </button>
              </div>
            </div>

            <div className="auth-row-between">
              <label className="auth-checkbox-label">
                <input 
                  type="checkbox" 
                  checked={rememberMe} 
                  onChange={(e) => setRememberMe(e.target.checked)} 
                />
                <span>{t.auth?.rememberMe}</span>
              </label>

              <button 
                type="button" 
                className="auth-text-link"
                onClick={() => setShowForgotHelp(!showForgotHelp)}
              >
                {t.auth?.forgotPassword}
              </button>
            </div>

            {showForgotHelp && (
              <div className="auth-helper-card">
                <p>{t.auth?.forgotPasswordHint}</p>
                <a 
                  href="https://t.me/airboxvip_admin" 
                  target="_blank" 
                  rel="noreferrer"
                  className="auth-tg-link"
                >
                  📱 @airboxvip_admin
                </a>
              </div>
            )}

            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? '...' : t.auth?.signInBtn}
            </button>

            {/* Quick Demo Section */}
            <div className="auth-demo-section">
              <span className="auth-demo-title">⚡ {t.auth?.quickDemo}</span>
              <div className="auth-demo-buttons">
                <button 
                  type="button" 
                  className="auth-demo-btn"
                  onClick={() => handleQuickDemo('client')}
                >
                  👤 {t.auth?.demoClient}
                </button>
                <button 
                  type="button" 
                  className="auth-demo-btn agency"
                  onClick={() => handleQuickDemo('agency')}
                >
                  🏢 {t.auth?.demoAgency}
                </button>
              </div>
            </div>

            {/* Switch to Sign Up */}
            <div className="auth-switch-prompt">
              <span>{t.auth?.noAccount}</span>
              <button 
                type="button" 
                className="auth-text-link-accent"
                onClick={() => handleTabSwitch('signup')}
              >
                {t.auth?.signUpTab} {isRtl ? <FiArrowLeft /> : <FiArrowRight />}
              </button>
            </div>
          </form>
        )}

        {/* Tab 2: Sign Up Form */}
        {authModalTab === 'signup' && (
          <form onSubmit={handleSignUpSubmit} className="auth-form">
            {/* Account Role Selector */}
            <div className="auth-role-group">
              <label>{t.auth?.accountType}</label>
              <div className="auth-role-selector">
                <button 
                  type="button"
                  className={`auth-role-btn ${signUpRole === 'client' ? 'active' : ''}`}
                  onClick={() => setSignUpRole('client')}
                >
                  <FiUser size={16} />
                  <span>{t.auth?.clientType}</span>
                </button>
                <button 
                  type="button"
                  className={`auth-role-btn ${signUpRole === 'agency' ? 'active' : ''}`}
                  onClick={() => setSignUpRole('agency')}
                >
                  <FiBriefcase size={16} />
                  <span>{t.auth?.agencyType}</span>
                </button>
              </div>
            </div>

            {/* Agency Name (Conditional) */}
            {signUpRole === 'agency' && (
              <div className="input-group">
                <label>{t.auth?.agencyName} *</label>
                <div className="auth-input-wrapper">
                  <FiBriefcase className="auth-input-icon" />
                  <input 
                    type="text"
                    required
                    placeholder={t.auth?.agencyNamePlaceholder}
                    value={signUpAgencyName}
                    onChange={(e) => setSignUpAgencyName(e.target.value)}
                  />
                </div>
              </div>
            )}

            <div className="input-group">
              <label>{t.auth?.fullName} *</label>
              <div className="auth-input-wrapper">
                <FiUser className="auth-input-icon" />
                <input 
                  type="text"
                  required
                  placeholder={t.auth?.fullNamePlaceholder}
                  value={signUpName}
                  onChange={(e) => setSignUpName(e.target.value)}
                />
              </div>
            </div>

            <div className="input-group">
              <label>{t.auth?.phone} *</label>
              <div className="auth-input-wrapper">
                <FiPhone className="auth-input-icon" />
                <input 
                  type="text"
                  required
                  placeholder={t.auth?.phonePlaceholder}
                  value={signUpPhone}
                  onChange={(e) => setSignUpPhone(e.target.value)}
                />
              </div>
            </div>

            <div className="input-group">
              <label>{t.auth?.email} *</label>
              <div className="auth-input-wrapper">
                <FiMail className="auth-input-icon" />
                <input 
                  type="email"
                  required
                  placeholder={t.auth?.emailPlaceholder}
                  value={signUpEmail}
                  onChange={(e) => setSignUpEmail(e.target.value)}
                />
              </div>
            </div>

            <div className="input-group">
              <label>{t.auth?.password} *</label>
              <div className="auth-input-wrapper">
                <FiLock className="auth-input-icon" />
                <input 
                  type={showSignUpPassword ? 'text' : 'password'}
                  required
                  placeholder="••••••••"
                  value={signUpPassword}
                  onChange={(e) => setSignUpPassword(e.target.value)}
                />
                <button 
                  type="button" 
                  className="auth-eye-btn"
                  onClick={() => setShowSignUpPassword(!showSignUpPassword)}
                  aria-label="Toggle password visibility"
                >
                  {showSignUpPassword ? <FiEyeOff size={16} /> : <FiEye size={16} />}
                </button>
              </div>
            </div>

            <div className="input-group">
              <label>{t.auth?.confirmPassword} *</label>
              <div className="auth-input-wrapper">
                <FiLock className="auth-input-icon" />
                <input 
                  type={showSignUpPassword ? 'text' : 'password'}
                  required
                  placeholder="••••••••"
                  value={signUpConfirmPassword}
                  onChange={(e) => setSignUpConfirmPassword(e.target.value)}
                />
              </div>
            </div>

            <div className="input-group">
              <label className="auth-checkbox-label terms">
                <input 
                  type="checkbox" 
                  required
                  checked={agreeTerms}
                  onChange={(e) => setAgreeTerms(e.target.checked)}
                />
                <span>{t.auth?.agreeTerms}</span>
              </label>
            </div>

            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? '...' : t.auth?.signUpBtn}
            </button>

            {/* Switch to Sign In */}
            <div className="auth-switch-prompt">
              <span>{t.auth?.hasAccount}</span>
              <button 
                type="button" 
                className="auth-text-link-accent"
                onClick={() => handleTabSwitch('signin')}
              >
                {t.auth?.signInTab} {isRtl ? <FiArrowLeft /> : <FiArrowRight />}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
