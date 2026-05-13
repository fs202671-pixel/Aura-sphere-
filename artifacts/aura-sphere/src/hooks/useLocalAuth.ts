import { useState, useEffect, useCallback } from 'react';
import type { ChatMessage } from '@/lib/types';

interface LocalUser {
  id: string;
  name: string;
  email?: string;
  avatar?: string;
  createdAt: string;
  isLocal: true;
}

type LocalStoredMessage = ChatMessage & {
  status?: 'pending' | 'sent' | 'failed';
  timestamp?: string;
};

interface LocalAuthState {
  user: LocalUser | null;
  isAuthenticated: boolean;
  isOnline: boolean;
}

const LOCAL_USER_KEY = 'caos_local_user';
const LOCAL_MESSAGES_KEY = 'caos_local_messages';

// One-time key migration (runs synchronously at module load, before any React render)
if (typeof window !== 'undefined') {
  const oldUser = localStorage.getItem('caos_local_user');
  if (oldUser && !localStorage.getItem(LOCAL_USER_KEY)) {
    localStorage.setItem(LOCAL_USER_KEY, oldUser);
    localStorage.removeItem('caos_local_user');
  }
  const oldMsgs = localStorage.getItem('caos_local_messages');
  if (oldMsgs && !localStorage.getItem(LOCAL_MESSAGES_KEY)) {
    localStorage.setItem(LOCAL_MESSAGES_KEY, oldMsgs);
    localStorage.removeItem('caos_local_messages');
  }
}

function readSavedUser(): LocalUser | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = localStorage.getItem(LOCAL_USER_KEY);
    return raw ? (JSON.parse(raw) as LocalUser) : null;
  } catch {
    return null;
  }
}

export function useLocalAuth() {
  // Eagerly read localStorage in the initial state — returning users never see a flash.
  const [state, setState] = useState<LocalAuthState>(() => {
    const saved = readSavedUser();
    return {
      user: saved,
      isAuthenticated: Boolean(saved),
      isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
    };
  });

  useEffect(() => {
    const handleOnline  = () => setState(prev => ({ ...prev, isOnline: true }));
    const handleOffline = () => setState(prev => ({ ...prev, isOnline: false }));
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // All returned functions are wrapped in useCallback with [] deps so they
  // have stable references across renders. This is critical — hooks like
  // useOfflineChat include these in useEffect dependency arrays, and an
  // unstable reference would create an infinite re-render loop.

  const createLocalUser = useCallback((name = 'Caos'): LocalUser => {
    const user: LocalUser = {
      id: `local_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name,
      createdAt: new Date().toISOString(),
      isLocal: true,
    };
    localStorage.setItem(LOCAL_USER_KEY, JSON.stringify(user));
    setState(prev => ({ ...prev, user, isAuthenticated: true }));
    return user;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(LOCAL_USER_KEY);
    setState(prev => ({ ...prev, user: null, isAuthenticated: false }));
  }, []);

  const clearLocalSession = useCallback(() => {
    localStorage.removeItem(LOCAL_USER_KEY);
    localStorage.removeItem(LOCAL_MESSAGES_KEY);
    setState(prev => ({ ...prev, user: null, isAuthenticated: false }));
  }, []);

  const getLocalMessages = useCallback((): LocalStoredMessage[] => {
    try {
      const raw = localStorage.getItem(LOCAL_MESSAGES_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }, []);

  const saveLocalMessages = useCallback((messages: LocalStoredMessage[]) => {
    localStorage.setItem(LOCAL_MESSAGES_KEY, JSON.stringify(messages));
  }, []);

  return {
    ...state,
    createLocalUser,
    logout,
    clearLocalSession,
    getLocalMessages,
    saveLocalMessages,
  };
}
