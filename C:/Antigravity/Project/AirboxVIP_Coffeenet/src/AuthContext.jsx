import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext(null);

const DEFAULT_USERS = [
  {
    id: 'USR-DEMO-01',
    name: 'علی محمدی',
    phone: '09121112233',
    email: 'client@airboxvip.top',
    password: 'password123',
    role: 'client',
    agencyName: '',
    createdAt: '2026-08-01T10:00:00.000Z'
  },
  {
    id: 'USR-DEMO-02',
    name: 'آژانس دیجیتال پارس',
    phone: '09129998877',
    email: 'agency@airboxvip.top',
    password: 'agency123',
    role: 'agency',
    agencyName: 'کانون تبلیغات و خدمات دیجیتال پارس',
    createdAt: '2026-08-05T12:00:00.000Z'
  }
];

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('airbox_auth_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authModalTab, setAuthModalTab] = useState('signin'); // 'signin' | 'signup'

  useEffect(() => {
    try {
      const existing = localStorage.getItem('airbox_users_db');
      if (!existing) {
        localStorage.setItem('airbox_users_db', JSON.stringify(DEFAULT_USERS));
      }
    } catch {
      // Ignore
    }
  }, []);

  const getUsersFromDb = () => {
    try {
      const data = localStorage.getItem('airbox_users_db');
      if (data) {
        return JSON.parse(data);
      }
    } catch {
      // fallback
    }
    return DEFAULT_USERS;
  };

  const saveUsersToDb = (users) => {
    try {
      localStorage.setItem('airbox_users_db', JSON.stringify(users));
    } catch {
      // Ignore
    }
  };

  const openAuthModal = (tab = 'signin') => {
    setAuthModalTab(tab);
    setAuthModalOpen(true);
  };

  const closeAuthModal = () => {
    setAuthModalOpen(false);
  };

  const login = ({ identifier, password, rememberMe = true }) => {
    const trimmedId = (identifier || '').trim().toLowerCase();
    const cleanPass = (password || '').trim();

    const users = getUsersFromDb();
    const foundUser = users.find(u => 
      (u.email?.toLowerCase() === trimmedId || u.phone?.replace(/\s+/g, '') === trimmedId) &&
      u.password === cleanPass
    );

    if (!foundUser) {
      return { success: false, error: 'invalid_credentials' };
    }

    const sessionUser = {
      id: foundUser.id,
      name: foundUser.name,
      email: foundUser.email,
      phone: foundUser.phone,
      role: foundUser.role || 'client',
      agencyName: foundUser.agencyName || ''
    };

    setUser(sessionUser);

    if (rememberMe) {
      try {
        localStorage.setItem('airbox_auth_user', JSON.stringify(sessionUser));
      } catch {
        // Ignore
      }
    }

    closeAuthModal();
    return { success: true, user: sessionUser };
  };

  const signup = ({ name, phone, email, password, role = 'client', agencyName = '', rememberMe = true }) => {
    const trimmedName = (name || '').trim();
    const trimmedPhone = (phone || '').trim();
    const trimmedEmail = (email || '').trim().toLowerCase();
    const cleanPass = (password || '').trim();
    const trimmedAgency = (agencyName || '').trim();

    const users = getUsersFromDb();
    const exists = users.some(u => 
      (trimmedEmail && u.email?.toLowerCase() === trimmedEmail) ||
      (trimmedPhone && u.phone?.replace(/\s+/g, '') === trimmedPhone.replace(/\s+/g, ''))
    );

    if (exists) {
      return { success: false, error: 'user_exists' };
    }

    const newUser = {
      id: 'USR-' + Date.now(),
      name: trimmedName,
      phone: trimmedPhone,
      email: trimmedEmail,
      password: cleanPass,
      role: role || 'client',
      agencyName: role === 'agency' ? trimmedAgency : '',
      createdAt: new Date().toISOString()
    };

    const updatedUsers = [...users, newUser];
    saveUsersToDb(updatedUsers);

    const sessionUser = {
      id: newUser.id,
      name: newUser.name,
      email: newUser.email,
      phone: newUser.phone,
      role: newUser.role,
      agencyName: newUser.agencyName
    };

    setUser(sessionUser);

    if (rememberMe) {
      try {
        localStorage.setItem('airbox_auth_user', JSON.stringify(sessionUser));
      } catch {
        // Ignore
      }
    }

    closeAuthModal();
    return { success: true, user: sessionUser };
  };

  const logout = () => {
    setUser(null);
    try {
      localStorage.removeItem('airbox_auth_user');
    } catch {
      // Ignore
    }
  };

  const value = {
    user,
    isAuthenticated: Boolean(user),
    authModalOpen,
    authModalTab,
    openAuthModal,
    closeAuthModal,
    setAuthModalTab,
    login,
    signup,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
