import React, { useEffect, useState } from 'react';
import { Palette, Undo, Save } from 'lucide-react';

interface Theme {
  name: string;
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  text: string;
  layout: 'compact' | 'comfortable' | 'spacious';
}

const DEFAULT_THEME: Theme = {
  name: 'Default',
  primary: '#3b82f6',
  secondary: '#1e293b',
  accent: '#8b5cf6',
  background: '#0f172a',
  text: '#f1f5f9',
  layout: 'comfortable'
};

const PRESET_THEMES: Theme[] = [
  {
    name: 'Dark',
    primary: '#3b82f6',
    secondary: '#1e293b',
    accent: '#8b5cf6',
    background: '#0f172a',
    text: '#f1f5f9',
    layout: 'comfortable'
  },
  {
    name: 'Ocean',
    primary: '#0369a1',
    secondary: '#0c4a6e',
    accent: '#06b6d4',
    background: '#001f3f',
    text: '#e0f2fe',
    layout: 'comfortable'
  },
  {
    name: 'Forest',
    primary: '#15803d',
    secondary: '#166534',
    accent: '#22c55e',
    background: '#0f172a',
    text: '#f0fdf4',
    layout: 'comfortable'
  },
  {
    name: 'Fire',
    primary: '#dc2626',
    secondary: '#991b1b',
    accent: '#f97316',
    background: '#1c1917',
    text: '#fed7aa',
    layout: 'comfortable'
  },
  {
    name: 'Sunset',
    primary: '#ea580c',
    secondary: '#9a3412',
    accent: '#f97316',
    background: '#1c1917',
    text: '#ffedd5',
    layout: 'comfortable'
  }
];

export function ThemeBuilder() {
  const [currentTheme, setCurrentTheme] = useState<Theme>(DEFAULT_THEME);
  const [savedThemes, setSavedThemes] = useState<Theme[]>([]);
  const [showPreview, setShowPreview] = useState(true);

  useEffect(() => {
    // Carregar temas salvos do localStorage
    const saved = localStorage.getItem('aura_sphere_custom_themes');
    if (saved) {
      setSavedThemes(JSON.parse(saved));
    }
  }, []);

  useEffect(() => {
    // Aplicar tema atual ao documento
    const root = document.documentElement;
    root.style.setProperty('--theme-primary', currentTheme.primary);
    root.style.setProperty('--theme-secondary', currentTheme.secondary);
    root.style.setProperty('--theme-accent', currentTheme.accent);
    root.style.setProperty('--theme-background', currentTheme.background);
    root.style.setProperty('--theme-text', currentTheme.text);
  }, [currentTheme]);

  const updateThemeColor = (key: keyof Omit<Theme, 'name' | 'layout'>, value: string) => {
    setCurrentTheme(prev => ({ ...prev, [key]: value }));
  };

  const updateLayout = (layout: 'compact' | 'comfortable' | 'spacious') => {
    setCurrentTheme(prev => ({ ...prev, layout }));
  };

  const saveCurrentTheme = () => {
    const themeName = currentTheme.name === 'Default' 
      ? `Custom Theme ${Date.now()}` 
      : currentTheme.name;
    
    const theme = { ...currentTheme, name: themeName };
    const updated = [...savedThemes, theme];
    setSavedThemes(updated);
    localStorage.setItem('aura_sphere_custom_themes', JSON.stringify(updated));
  };

  const resetToDefault = () => {
    setCurrentTheme(DEFAULT_THEME);
  };

  const selectPresetTheme = (theme: Theme) => {
    setCurrentTheme({ ...theme });
  };

  const deleteCustomTheme = (themeName: string) => {
    const updated = savedThemes.filter(t => t.name !== themeName);
    setSavedThemes(updated);
    localStorage.setItem('aura_sphere_custom_themes', JSON.stringify(updated));
  };

  const getLayoutPadding = () => {
    switch (currentTheme.layout) {
      case 'compact': return 'p-2';
      case 'comfortable': return 'p-4';
      case 'spacious': return 'p-8';
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold text-white flex items-center gap-3">
          <Palette className="w-8 h-8 text-purple-500" />
          Theme Builder
        </h2>
        <div className="flex gap-2">
          <button
            onClick={resetToDefault}
            className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition"
          >
            <Undo className="w-4 h-4" />
            Reset
          </button>
          <button
            onClick={saveCurrentTheme}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
          >
            <Save className="w-4 h-4" />
            Salvar Tema
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Painel de Customização */}
        <div className="lg:col-span-1 space-y-6">
          {/* Color Picker */}
          <div className="bg-slate-700/50 border border-slate-600 rounded-lg p-6 space-y-4">
            <h3 className="text-lg font-semibold text-white">Cores</h3>
            
            {[
              { key: 'primary' as const, label: 'Primária' },
              { key: 'secondary' as const, label: 'Secundária' },
              { key: 'accent' as const, label: 'Destaque' },
              { key: 'background' as const, label: 'Fundo' },
              { key: 'text' as const, label: 'Texto' }
            ].map(({ key, label }) => (
              <div key={key} className="flex items-center gap-3">
                <label className="text-sm text-slate-300 flex-1">{label}</label>
                <div className="flex items-center gap-2">
                  <input
                    type="color"
                    value={currentTheme[key]}
                    onChange={(e) => updateThemeColor(key, e.target.value)}
                    className="w-10 h-10 rounded cursor-pointer border border-slate-600"
                  />
                  <input
                    type="text"
                    value={currentTheme[key]}
                    onChange={(e) => updateThemeColor(key, e.target.value)}
                    className="w-24 bg-slate-800 border border-slate-600 text-white text-xs px-2 py-1 rounded font-mono"
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Layout Settings */}
          <div className="bg-slate-700/50 border border-slate-600 rounded-lg p-6 space-y-4">
            <h3 className="text-lg font-semibold text-white">Layout</h3>
            <div className="space-y-2">
              {(['compact', 'comfortable', 'spacious'] as const).map((layoutType) => (
                <button
                  key={layoutType}
                  onClick={() => updateLayout(layoutType)}
                  className={`w-full px-4 py-2 rounded text-sm font-semibold transition ${
                    currentTheme.layout === layoutType
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  {layoutType === 'compact' ? '⬜ Compacto' : layoutType === 'comfortable' ? '📄 Confortável' : '📖 Espaçoso'}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Preview + Presets */}
        <div className="lg:col-span-2 space-y-6">
          {/* Live Preview */}
          <div className="bg-slate-700/50 border border-slate-600 rounded-lg p-6 space-y-4">
            <h3 className="text-lg font-semibold text-white mb-4">Pré-visualização</h3>
            
            <div
              className={`rounded-lg p-6 space-y-3 transition-all ${getLayoutPadding()}`}
              style={{
                backgroundColor: currentTheme.background,
                color: currentTheme.text
              }}
            >
              <div className="flex gap-2">
                {[currentTheme.primary, currentTheme.secondary, currentTheme.accent].map((color, idx) => (
                  <div
                    key={idx}
                    className="w-12 h-12 rounded"
                    style={{ backgroundColor: color }}
                  />
                ))}
              </div>

              <div className="space-y-2">
                <h4 className="text-lg font-bold">Título da Página</h4>
                <p>Este é um exemplo de texto em seu tema customizado. Você pode ver como as cores e layout funcionam juntos.</p>
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  className="px-4 py-2 rounded font-semibold"
                  style={{
                    backgroundColor: currentTheme.primary,
                    color: currentTheme.background
                  }}
                >
                  Botão Primário
                </button>
                <button
                  className="px-4 py-2 rounded font-semibold border"
                  style={{
                    borderColor: currentTheme.accent,
                    color: currentTheme.accent
                  }}
                >
                  Botão Secundário
                </button>
              </div>
            </div>
          </div>

          {/* Preset Themes */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Temas Presets</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {PRESET_THEMES.map((theme) => (
                <button
                  key={theme.name}
                  onClick={() => selectPresetTheme(theme)}
                  className={`p-4 rounded-lg border-2 transition ${
                    currentTheme.name === theme.name
                      ? 'border-blue-500 bg-blue-500/10'
                      : 'border-slate-600 hover:border-slate-500'
                  }`}
                >
                  <div className="flex gap-1 mb-2">
                    {[theme.primary, theme.secondary, theme.accent].map((color, idx) => (
                      <div
                        key={idx}
                        className="w-6 h-6 rounded"
                        style={{ backgroundColor: color }}
                      />
                    ))}
                  </div>
                  <p className="text-xs font-semibold text-white">{theme.name}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Temas Salvos */}
          {savedThemes.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white">Meus Temas</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {savedThemes.map((theme) => (
                  <div
                    key={theme.name}
                    className="bg-slate-700/50 border border-slate-600 rounded-lg p-3 hover:border-slate-500 transition"
                  >
                    <button
                      onClick={() => selectPresetTheme(theme)}
                      className="w-full text-left"
                    >
                      <div className="flex gap-1 mb-2">
                        {[theme.primary, theme.secondary, theme.accent].map((color, idx) => (
                          <div
                            key={idx}
                            className="w-6 h-6 rounded"
                            style={{ backgroundColor: color }}
                          />
                        ))}
                      </div>
                      <p className="text-xs font-semibold text-white truncate">{theme.name}</p>
                    </button>
                    <button
                      onClick={() => deleteCustomTheme(theme.name)}
                      className="text-xs text-red-400 hover:text-red-300 mt-2 w-full text-center"
                    >
                      Deletar
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
