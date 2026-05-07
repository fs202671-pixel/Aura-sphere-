import React, { useState } from 'react';
import { Instagram, AlertTriangle, Check, X, Loader } from 'lucide-react';

interface AccountData {
  id: string;
  username: string;
  email?: string;
  [key: string]: unknown;
}

interface LoginInstagramModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess: (accountData: AccountData) => void;
}

export function LoginInstagramModal({ isOpen, onClose, onLoginSuccess }: LoginInstagramModalProps) {
  const [step, setStep] = useState<'credentials' | '2fa' | 'success' | 'error'>('credentials');
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    verificationCode: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [accountData, setAccountData] = useState(null);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError('');
  };

  const handleLogin = async () => {
    if (!formData.username || !formData.password) {
      setError('Username e senha são obrigatórios');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/v1/social/instagram/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password,
          user_id: 'current_user' // TODO: Obter do contexto de autenticação
        })
      });

      const data = await response.json();

      if (data.success) {
        setAccountData(data.account);
        setStep('success');
        setTimeout(() => {
          onLoginSuccess(data);
          onClose();
          resetModal();
        }, 2000);
      } else if (data.requires_2fa) {
        setStep('2fa');
      } else {
        setError(data.error || 'Erro no login');
        setStep('error');
      }
    } catch (err) {
      setError('Erro de conexão. Tente novamente.');
      setStep('error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerify2FA = async () => {
    if (!formData.verificationCode) {
      setError('Código de verificação é obrigatório');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/v1/social/instagram/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password,
          verification_code: formData.verificationCode,
          user_id: 'current_user'
        })
      });

      const data = await response.json();

      if (data.success) {
        setAccountData(data.account);
        setStep('success');
        setTimeout(() => {
          onLoginSuccess(data);
          onClose();
          resetModal();
        }, 2000);
      } else {
        setError(data.error || 'Código inválido');
      }
    } catch (err) {
      setError('Erro de conexão. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
  };

  const resetModal = () => {
    setStep('credentials');
    setFormData({ username: '', password: '', verificationCode: '' });
    setError('');
    setAccountData(null);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-pink-600 rounded-lg flex items-center justify-center">
              <Instagram size={20} className="text-white" />
            </div>
            <h2 className="text-xl font-bold">Conectar Instagram</h2>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X size={24} />
          </button>
        </div>

        {step === 'credentials' && (
          <div className="space-y-4">
            <div className="text-sm text-gray-600 mb-4">
              Conecte sua conta do Instagram para sincronizar seus posts salvos e organizá-los automaticamente.
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Username
              </label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => handleInputChange('username', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-pink-500"
                placeholder="seu_username"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Senha
              </label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-pink-500"
                placeholder="••••••••"
              />
            </div>

            {error && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md">
                <AlertTriangle size={16} className="text-red-500" />
                <span className="text-sm text-red-700">{error}</span>
              </div>
            )}

            <button
              onClick={handleLogin}
              disabled={isLoading || !formData.username || !formData.password}
              className="w-full bg-pink-600 text-white py-2 px-4 rounded-md hover:bg-pink-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isLoading ? <Loader size={16} className="animate-spin" /> : <Instagram size={16} />}
              <span>{isLoading ? 'Conectando...' : 'Conectar'}</span>
            </button>
          </div>
        )}

        {step === '2fa' && (
          <div className="space-y-4">
            <div className="text-center">
              <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertTriangle size={24} className="text-yellow-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Verificação de 2 Fatores
              </h3>
              <p className="text-sm text-gray-600">
                Digite o código enviado para seu aplicativo de autenticação ou SMS.
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Código de Verificação
              </label>
              <input
                type="text"
                value={formData.verificationCode}
                onChange={(e) => handleInputChange('verificationCode', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-pink-500 text-center text-lg tracking-widest"
                placeholder="000000"
                maxLength={6}
              />
            </div>

            {error && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md">
                <AlertTriangle size={16} className="text-red-500" />
                <span className="text-sm text-red-700">{error}</span>
              </div>
            )}

            <div className="flex gap-2">
              <button
                onClick={() => setStep('credentials')}
                className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300"
              >
                Voltar
              </button>
              <button
                onClick={handleVerify2FA}
                disabled={isLoading || !formData.verificationCode}
                className="flex-1 bg-pink-600 text-white py-2 px-4 rounded-md hover:bg-pink-700 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {isLoading ? <Loader size={16} className="animate-spin" /> : <Check size={16} />}
                <span>{isLoading ? 'Verificando...' : 'Verificar'}</span>
              </button>
            </div>
          </div>
        )}

        {step === 'success' && accountData && (
          <div className="text-center space-y-4">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto">
              <Check size={24} className="text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">
              Conectado com sucesso!
            </h3>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="font-medium text-gray-900">{accountData.username}</p>
              <p className="text-sm text-gray-600">{accountData.follower_count?.toLocaleString()} seguidores</p>
            </div>
            <p className="text-sm text-gray-600">
              Sua conta está sendo configurada...
            </p>
          </div>
        )}

        {step === 'error' && (
          <div className="text-center space-y-4">
            <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto">
              <X size={24} className="text-red-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">
              Erro na conexão
            </h3>
            <p className="text-sm text-gray-600">{error}</p>
            <button
              onClick={() => setStep('credentials')}
              className="w-full bg-pink-600 text-white py-2 px-4 rounded-md hover:bg-pink-700"
            >
              Tentar Novamente
            </button>
          </div>
        )}
      </div>
    </div>
  );
}