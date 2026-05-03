import { useState, useEffect, useCallback } from 'react';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface VisualTheme {
  id: string;
  name: string;
  description: string;

  // Cores principais
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  foreground: string;

  // Sidebar
  sidebarBg: string;
  sidebarFg: string;
  sidebarBorder: string;

  // Cards e componentes
  cardBg: string;
  cardFg: string;
  cardBorder: string;

  // Botões
  buttonPrimary: string;
  buttonSecondary: string;
  buttonAccent: string;

  // Estados
  success: string;
  warning: string;
  error: string;
  info: string;

  // Bordas e sombras
  borderRadius: 'none' | 'sm' | 'md' | 'lg' | 'xl' | 'full';
  shadowIntensity: 'none' | 'sm' | 'md' | 'lg' | 'xl';

  // Tipografia
  fontSize: 'sm' | 'base' | 'lg' | 'xl';
  fontWeight: 'normal' | 'medium' | 'semibold' | 'bold';

  // Animações
  animationSpeed: 'none' | 'slow' | 'normal' | 'fast';

  // Layout
  spacing: 'tight' | 'normal' | 'loose';
  density: 'compact' | 'normal' | 'comfortable';
}

export interface LayoutConfig {
  id: string;
  name: string;
  description: string;

  // Sidebar
  sidebarPosition: 'left' | 'right' | 'top' | 'bottom';
  sidebarWidth: number;
  sidebarCollapsed: boolean;

  // Main content
  contentPadding: number;
  contentMaxWidth: number | 'none';

  // Sphere
  spherePosition: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  sphereSize: number;
  sphereVisible: boolean;

  // Grid system
  gridColumns: number;
  gridGap: number;

  // Responsividade
  breakpoints: {
    sm: number;
    md: number;
    lg: number;
    xl: number;
  };
}

export interface VisualCommand {
  command: string;
  description: string;
  examples: string[];
  handler: (params: string[]) => Promise<string>;
}

// Temas pré-definidos
export const DEFAULT_THEMES: Record<string, VisualTheme> = {
  default: {
    id: 'default',
    name: 'Padrão',
    description: 'Tema padrão do Aura Sphere',
    primary: 'hsl(262 83% 58%)',
    secondary: 'hsl(210 40% 96%)',
    accent: 'hsl(262 83% 58%)',
    background: 'hsl(224 71% 4%)',
    foreground: 'hsl(213 31% 91%)',
    sidebarBg: 'hsl(224 71% 4%)',
    sidebarFg: 'hsl(213 31% 91%)',
    sidebarBorder: 'hsl(216 34% 17%)',
    cardBg: 'hsl(224 71% 4%)',
    cardFg: 'hsl(213 31% 91%)',
    cardBorder: 'hsl(216 34% 17%)',
    buttonPrimary: 'hsl(262 83% 58%)',
    buttonSecondary: 'hsl(210 40% 96%)',
    buttonAccent: 'hsl(262 83% 58%)',
    success: 'hsl(142 76% 36%)',
    warning: 'hsl(38 92% 50%)',
    error: 'hsl(0 84% 60%)',
    info: 'hsl(199 89% 48%)',
    borderRadius: 'lg',
    shadowIntensity: 'md',
    fontSize: 'base',
    fontWeight: 'normal',
    animationSpeed: 'normal',
    spacing: 'normal',
    density: 'normal'
  },

  light: {
    id: 'light',
    name: 'Claro',
    description: 'Tema claro e limpo',
    primary: 'hsl(262 83% 58%)',
    secondary: 'hsl(210 40% 98%)',
    accent: 'hsl(262 83% 58%)',
    background: 'hsl(0 0% 100%)',
    foreground: 'hsl(224 71% 4%)',
    sidebarBg: 'hsl(0 0% 100%)',
    sidebarFg: 'hsl(224 71% 4%)',
    sidebarBorder: 'hsl(214 32% 91%)',
    cardBg: 'hsl(0 0% 100%)',
    cardFg: 'hsl(224 71% 4%)',
    cardBorder: 'hsl(214 32% 91%)',
    buttonPrimary: 'hsl(262 83% 58%)',
    buttonSecondary: 'hsl(210 40% 98%)',
    buttonAccent: 'hsl(262 83% 58%)',
    success: 'hsl(142 76% 36%)',
    warning: 'hsl(38 92% 50%)',
    error: 'hsl(0 84% 60%)',
    info: 'hsl(199 89% 48%)',
    borderRadius: 'lg',
    shadowIntensity: 'sm',
    fontSize: 'base',
    fontWeight: 'normal',
    animationSpeed: 'normal',
    spacing: 'normal',
    density: 'normal'
  },

  neon: {
    id: 'neon',
    name: 'Neon Cyberpunk',
    description: 'Tema cyberpunk com cores neon',
    primary: 'hsl(300 100% 70%)',
    secondary: 'hsl(180 100% 70%)',
    accent: 'hsl(60 100% 70%)',
    background: 'hsl(240 100% 5%)',
    foreground: 'hsl(300 100% 90%)',
    sidebarBg: 'hsl(240 100% 8%)',
    sidebarFg: 'hsl(300 100% 90%)',
    sidebarBorder: 'hsl(300 100% 30%)',
    cardBg: 'hsl(240 100% 8%)',
    cardFg: 'hsl(300 100% 90%)',
    cardBorder: 'hsl(300 100% 30%)',
    buttonPrimary: 'hsl(300 100% 70%)',
    buttonSecondary: 'hsl(180 100% 70%)',
    buttonAccent: 'hsl(60 100% 70%)',
    success: 'hsl(120 100% 70%)',
    warning: 'hsl(60 100% 70%)',
    error: 'hsl(0 100% 70%)',
    info: 'hsl(240 100% 70%)',
    borderRadius: 'full',
    shadowIntensity: 'xl',
    fontSize: 'lg',
    fontWeight: 'bold',
    animationSpeed: 'fast',
    spacing: 'loose',
    density: 'comfortable'
  },

  minimal: {
    id: 'minimal',
    name: 'Minimalista',
    description: 'Design minimalista e clean',
    primary: 'hsl(0 0% 20%)',
    secondary: 'hsl(0 0% 96%)',
    accent: 'hsl(0 0% 40%)',
    background: 'hsl(0 0% 100%)',
    foreground: 'hsl(0 0% 10%)',
    sidebarBg: 'hsl(0 0% 98%)',
    sidebarFg: 'hsl(0 0% 10%)',
    sidebarBorder: 'hsl(0 0% 90%)',
    cardBg: 'hsl(0 0% 100%)',
    cardFg: 'hsl(0 0% 10%)',
    cardBorder: 'hsl(0 0% 90%)',
    buttonPrimary: 'hsl(0 0% 20%)',
    buttonSecondary: 'hsl(0 0% 96%)',
    buttonAccent: 'hsl(0 0% 40%)',
    success: 'hsl(120 60% 40%)',
    warning: 'hsl(45 100% 50%)',
    error: 'hsl(0 80% 50%)',
    info: 'hsl(210 80% 50%)',
    borderRadius: 'none',
    shadowIntensity: 'none',
    fontSize: 'sm',
    fontWeight: 'normal',
    animationSpeed: 'none',
    spacing: 'tight',
    density: 'compact'
  }
};

// Layouts pré-definidos
export const DEFAULT_LAYOUTS: Record<string, LayoutConfig> = {
  default: {
    id: 'default',
    name: 'Padrão',
    description: 'Layout padrão do Aura Sphere',
    sidebarPosition: 'left',
    sidebarWidth: 288, // 18rem
    sidebarCollapsed: false,
    contentPadding: 24, // 1.5rem
    contentMaxWidth: 'none',
    spherePosition: 'bottom-right',
    sphereSize: 176, // 11rem (44 * 4px)
    sphereVisible: true,
    gridColumns: 12,
    gridGap: 16, // 1rem
    breakpoints: {
      sm: 640,
      md: 768,
      lg: 1024,
      xl: 1280
    }
  },

  compact: {
    id: 'compact',
    name: 'Compacto',
    description: 'Layout compacto para telas pequenas',
    sidebarPosition: 'left',
    sidebarWidth: 200,
    sidebarCollapsed: false,
    contentPadding: 16,
    contentMaxWidth: 'none',
    spherePosition: 'bottom-right',
    sphereSize: 120,
    sphereVisible: true,
    gridColumns: 12,
    gridGap: 12,
    breakpoints: {
      sm: 640,
      md: 768,
      lg: 1024,
      xl: 1280
    }
  },

  wide: {
    id: 'wide',
    name: 'Amplo',
    description: 'Layout amplo para telas grandes',
    sidebarPosition: 'left',
    sidebarWidth: 320,
    sidebarCollapsed: false,
    contentPadding: 32,
    contentMaxWidth: 1200,
    spherePosition: 'bottom-right',
    sphereSize: 224,
    sphereVisible: true,
    gridColumns: 16,
    gridGap: 24,
    breakpoints: {
      sm: 640,
      md: 768,
      lg: 1024,
      xl: 1400
    }
  }
};

// Store Zustand para gerenciar estado visual
interface VisualState {
  currentTheme: VisualTheme;
  currentLayout: LayoutConfig;
  customThemes: Record<string, VisualTheme>;
  customLayouts: Record<string, LayoutConfig>;
  isCustomizing: boolean;

  // Actions
  setTheme: (theme: VisualTheme) => void;
  setLayout: (layout: LayoutConfig) => void;
  updateTheme: (updates: Partial<VisualTheme>) => void;
  updateLayout: (updates: Partial<LayoutConfig>) => void;
  saveCustomTheme: (theme: VisualTheme) => void;
  saveCustomLayout: (layout: LayoutConfig) => void;
  deleteCustomTheme: (themeId: string) => void;
  deleteCustomLayout: (layoutId: string) => void;
  setCustomizing: (customizing: boolean) => void;
  resetToDefaults: () => void;
}

export const useVisualStore = create<VisualState>()(
  persist(
    (set, get) => ({
      currentTheme: DEFAULT_THEMES.default,
      currentLayout: DEFAULT_LAYOUTS.default,
      customThemes: {},
      customLayouts: {},
      isCustomizing: false,

      setTheme: (theme) => set({ currentTheme: theme }),
      setLayout: (layout) => set({ currentLayout: layout }),

      updateTheme: (updates) => set((state) => ({
        currentTheme: { ...state.currentTheme, ...updates }
      })),

      updateLayout: (updates) => set((state) => ({
        currentLayout: { ...state.currentLayout, ...updates }
      })),

      saveCustomTheme: (theme) => set((state) => ({
        customThemes: { ...state.customThemes, [theme.id]: theme }
      })),

      saveCustomLayout: (layout) => set((state) => ({
        customLayouts: { ...state.customLayouts, [layout.id]: layout }
      })),

      deleteCustomTheme: (themeId) => set((state) => {
        const { [themeId]: deleted, ...rest } = state.customThemes;
        return { customThemes: rest };
      }),

      deleteCustomLayout: (layoutId) => set((state) => {
        const { [layoutId]: deleted, ...rest } = state.customLayouts;
        return { customLayouts: rest };
      }),

      setCustomizing: (customizing) => set({ isCustomizing: customizing }),

      resetToDefaults: () => set({
        currentTheme: DEFAULT_THEMES.default,
        currentLayout: DEFAULT_LAYOUTS.default,
        customThemes: {},
        customLayouts: {}
      })
    }),
    {
      name: 'aura-sphere-visual-state',
      partialize: (state) => ({
        currentTheme: state.currentTheme,
        currentLayout: state.currentLayout,
        customThemes: state.customThemes,
        customLayouts: state.customLayouts
      })
    }
  )
);

// Hook para gerenciar comandos visuais
export const useVisualCommands = () => {
  const {
    currentTheme,
    currentLayout,
    setTheme,
    setLayout,
    updateTheme,
    updateLayout,
    saveCustomTheme,
    customThemes
  } = useVisualStore();

  const commands: VisualCommand[] = [
    {
      command: 'change_theme',
      description: 'Alterar tema visual da interface',
      examples: [
        'change_theme neon',
        'change_theme light',
        'change_theme default'
      ],
      handler: async (params: string[]) => {
        const themeName = params[0]?.toLowerCase();
        if (!themeName) {
          return 'Erro: Especifique o nome do tema. Exemplos: neon, light, default';
        }

        const availableThemes = { ...DEFAULT_THEMES, ...customThemes };
        const theme = availableThemes[themeName];

        if (!theme) {
          const availableNames = Object.keys(availableThemes).join(', ');
          return `Erro: Tema "${themeName}" não encontrado. Temas disponíveis: ${availableNames}`;
        }

        setTheme(theme);
        return `Tema alterado para "${theme.name}"`;
      }
    },

    {
      command: 'change_layout',
      description: 'Alterar layout da interface',
      examples: [
        'change_layout compact',
        'change_layout wide',
        'change_layout default'
      ],
      handler: async (params: string[]) => {
        const layoutName = params[0]?.toLowerCase();
        if (!layoutName) {
          return 'Erro: Especifique o nome do layout. Exemplos: compact, wide, default';
        }

        const availableLayouts = { ...DEFAULT_LAYOUTS, ...useVisualStore.getState().customLayouts };
        const layout = availableLayouts[layoutName];

        if (!layout) {
          const availableNames = Object.keys(availableLayouts).join(', ');
          return `Erro: Layout "${layoutName}" não encontrado. Layouts disponíveis: ${availableNames}`;
        }

        setLayout(layout);
        return `Layout alterado para "${layout.name}"`;
      }
    },

    {
      command: 'toggle_sphere',
      description: 'Mostrar/ocultar esfera de partículas',
      examples: [
        'toggle_sphere on',
        'toggle_sphere off',
        'toggle_sphere'
      ],
      handler: async (params: string[]) => {
        const action = params[0]?.toLowerCase();
        let newVisible: boolean;

        if (action === 'on') {
          newVisible = true;
        } else if (action === 'off') {
          newVisible = false;
        } else {
          // Toggle atual
          newVisible = !currentLayout.sphereVisible;
        }

        updateLayout({ sphereVisible: newVisible });
        return `Esfera de partículas ${newVisible ? 'ativada' : 'desativada'}`;
      }
    },

    {
      command: 'set_sphere_size',
      description: 'Alterar tamanho da esfera de partículas',
      examples: [
        'set_sphere_size 200',
        'set_sphere_size 300',
        'set_sphere_size 150'
      ],
      handler: async (params: string[]) => {
        const sizeStr = params[0];
        if (!sizeStr) {
          return 'Erro: Especifique o tamanho em pixels. Exemplo: set_sphere_size 200';
        }

        const size = parseInt(sizeStr);
        if (isNaN(size) || size < 50 || size > 500) {
          return 'Erro: Tamanho deve ser um número entre 50 e 500 pixels';
        }

        updateLayout({ sphereSize: size });
        return `Tamanho da esfera alterado para ${size}px`;
      }
    },

    {
      command: 'set_primary_color',
      description: 'Alterar cor primária do tema',
      examples: [
        'set_primary_color #ff6b6b',
        'set_primary_color hsl(262 83% 58%)',
        'set_primary_color blue'
      ],
      handler: async (params: string[]) => {
        const color = params.join(' ');
        if (!color) {
          return 'Erro: Especifique uma cor. Exemplos: #ff6b6b, hsl(262 83% 58%), blue';
        }

        // Validação básica de cor
        const isValidColor = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$|^hsl\(\s*\d+\s*\d+%?\s*\d+%?\s*\)$|^[a-zA-Z]+$/.test(color);
        if (!isValidColor) {
          return 'Erro: Formato de cor inválido. Use #hex, hsl(), ou nome da cor';
        }

        updateTheme({ primary: color, accent: color });
        return `Cor primária alterada para ${color}`;
      }
    },

    {
      command: 'set_background',
      description: 'Alterar cor de fundo',
      examples: [
        'set_background #1a1a1a',
        'set_background hsl(224 71% 4%)',
        'set_background dark'
      ],
      handler: async (params: string[]) => {
        const color = params.join(' ');
        if (!color) {
          return 'Erro: Especifique uma cor de fundo';
        }

        updateTheme({ background: color });
        return `Cor de fundo alterada para ${color}`;
      }
    },

    {
      command: 'set_border_radius',
      description: 'Alterar arredondamento das bordas',
      examples: [
        'set_border_radius none',
        'set_border_radius lg',
        'set_border_radius full'
      ],
      handler: async (params: string[]) => {
        const radius = params[0]?.toLowerCase() as VisualTheme['borderRadius'];
        const validOptions: VisualTheme['borderRadius'][] = ['none', 'sm', 'md', 'lg', 'xl', 'full'];

        if (!radius || !validOptions.includes(radius)) {
          return `Erro: Opção inválida. Use: ${validOptions.join(', ')}`;
        }

        updateTheme({ borderRadius: radius });
        return `Arredondamento das bordas alterado para ${radius}`;
      }
    },

    {
      command: 'set_font_size',
      description: 'Alterar tamanho da fonte',
      examples: [
        'set_font_size sm',
        'set_font_size base',
        'set_font_size lg'
      ],
      handler: async (params: string[]) => {
        const size = params[0]?.toLowerCase() as VisualTheme['fontSize'];
        const validOptions: VisualTheme['fontSize'][] = ['sm', 'base', 'lg', 'xl'];

        if (!size || !validOptions.includes(size)) {
          return `Erro: Opção inválida. Use: ${validOptions.join(', ')}`;
        }

        updateTheme({ fontSize: size });
        return `Tamanho da fonte alterado para ${size}`;
      }
    },

    {
      command: 'list_themes',
      description: 'Listar todos os temas disponíveis',
      examples: ['list_themes'],
      handler: async (params: string[]) => {
        const availableThemes = { ...DEFAULT_THEMES, ...customThemes };
        const themeList = Object.values(availableThemes)
          .map(theme => `- ${theme.id}: ${theme.name} (${theme.description})`)
          .join('\n');

        return `Temas disponíveis:\n${themeList}`;
      }
    },

    {
      command: 'list_layouts',
      description: 'Listar todos os layouts disponíveis',
      examples: ['list_layouts'],
      handler: async (params: string[]) => {
        const availableLayouts = { ...DEFAULT_LAYOUTS, ...useVisualStore.getState().customLayouts };
        const layoutList = Object.values(availableLayouts)
          .map(layout => `- ${layout.id}: ${layout.name} (${layout.description})`)
          .join('\n');

        return `Layouts disponíveis:\n${layoutList}`;
      }
    },

    {
      command: 'reset_visual',
      description: 'Resetar configurações visuais para padrão',
      examples: ['reset_visual'],
      handler: async (params: string[]) => {
        useVisualStore.getState().resetToDefaults();
        return 'Configurações visuais resetadas para padrão';
      }
    },

    {
      command: 'current_theme',
      description: 'Mostrar informações do tema atual',
      examples: ['current_theme'],
      handler: async (params: string[]) => {
        return `Tema atual: ${currentTheme.name} (${currentTheme.id})\nDescrição: ${currentTheme.description}\nCor primária: ${currentTheme.primary}`;
      }
    },

    {
      command: 'current_layout',
      description: 'Mostrar informações do layout atual',
      examples: ['current_layout'],
      handler: async (params: string[]) => {
        return `Layout atual: ${currentLayout.name} (${currentLayout.id})\nDescrição: ${currentLayout.description}\nSidebar: ${currentLayout.sidebarWidth}px\nEsfera: ${currentLayout.sphereVisible ? 'visível' : 'oculta'} (${currentLayout.sphereSize}px)`;
      }
    }
  ];

  const executeCommand = useCallback(async (commandString: string): Promise<string> => {
    const parts = commandString.trim().split(/\s+/);
    const commandName = parts[0]?.toLowerCase();
    const params = parts.slice(1);

    const command = commands.find(cmd => cmd.command === commandName);
    if (!command) {
      const availableCommands = commands.map(cmd => cmd.command).join(', ');
      return `Comando visual não encontrado: ${commandName}. Comandos disponíveis: ${availableCommands}`;
    }

    try {
      return await command.handler(params);
    } catch (error) {
      return `Erro ao executar comando: ${error}`;
    }
  }, [commands, currentTheme, currentLayout, setTheme, setLayout, updateTheme, updateLayout, saveCustomTheme, customThemes]);

  const getAvailableCommands = useCallback(() => {
    return commands.map(cmd => ({
      command: cmd.command,
      description: cmd.description,
      examples: cmd.examples
    }));
  }, [commands]);

  return {
    executeCommand,
    getAvailableCommands,
    currentTheme,
    currentLayout
  };
};

// Hook para aplicar estilos CSS dinâmicos
export const useDynamicStyles = () => {
  const { currentTheme, currentLayout } = useVisualStore();

  useEffect(() => {
    // Aplicar variáveis CSS do tema
    const root = document.documentElement;

    // Cores principais
    root.style.setProperty('--color-primary', currentTheme.primary);
    root.style.setProperty('--color-secondary', currentTheme.secondary);
    root.style.setProperty('--color-accent', currentTheme.accent);
    root.style.setProperty('--color-background', currentTheme.background);
    root.style.setProperty('--color-foreground', currentTheme.foreground);

    // Sidebar
    root.style.setProperty('--sidebar-bg', currentTheme.sidebarBg);
    root.style.setProperty('--sidebar-fg', currentTheme.sidebarFg);
    root.style.setProperty('--sidebar-border', currentTheme.sidebarBorder);

    // Cards
    root.style.setProperty('--card-bg', currentTheme.cardBg);
    root.style.setProperty('--card-fg', currentTheme.cardFg);
    root.style.setProperty('--card-border', currentTheme.cardBorder);

    // Botões
    root.style.setProperty('--button-primary', currentTheme.buttonPrimary);
    root.style.setProperty('--button-secondary', currentTheme.buttonSecondary);
    root.style.setProperty('--button-accent', currentTheme.buttonAccent);

    // Estados
    root.style.setProperty('--color-success', currentTheme.success);
    root.style.setProperty('--color-warning', currentTheme.warning);
    root.style.setProperty('--color-error', currentTheme.error);
    root.style.setProperty('--color-info', currentTheme.info);

    // Layout
    root.style.setProperty('--sidebar-width', `${currentLayout.sidebarWidth}px`);
    root.style.setProperty('--content-padding', `${currentLayout.contentPadding}px`);
    root.style.setProperty('--sphere-size', `${currentLayout.sphereSize}px`);
    root.style.setProperty('--grid-gap', `${currentLayout.gridGap}px`);

    // Aplicar classes CSS dinâmicas
    const body = document.body;
    body.className = body.className.replace(/theme-\w+/g, '').trim();
    body.classList.add(`theme-${currentTheme.id}`);

    // Aplicar classes de layout
    body.className = body.className.replace(/layout-\w+/g, '').trim();
    body.classList.add(`layout-${currentLayout.id}`);

    // Aplicar classes de densidade e espaçamento
    body.className = body.className.replace(/density-\w+/g, '').trim();
    body.classList.add(`density-${currentTheme.density}`);

    body.className = body.className.replace(/spacing-\w+/g, '').trim();
    body.classList.add(`spacing-${currentTheme.spacing}`);

    // Aplicar classes de fonte
    body.className = body.className.replace(/font-size-\w+/g, '').trim();
    body.classList.add(`font-size-${currentTheme.fontSize}`);

    // Aplicar classes de borda
    body.className = body.className.replace(/border-radius-\w+/g, '').trim();
    body.classList.add(`border-radius-${currentTheme.borderRadius}`);

    // Aplicar classes de sombra
    body.className = body.className.replace(/shadow-\w+/g, '').trim();
    body.classList.add(`shadow-${currentTheme.shadowIntensity}`);

    // Aplicar classes de animação
    body.className = body.className.replace(/animation-\w+/g, '').trim();
    body.classList.add(`animation-${currentTheme.animationSpeed}`);

  }, [currentTheme, currentLayout]);

  return { currentTheme, currentLayout };
};

// Função utilitária para converter HSL para CSS
export const hslToCss = (hsl: string): string => {
  return hsl;
};

// Função utilitária para validar cores
export const isValidColor = (color: string): boolean => {
  // Simple validation - could be enhanced
  return color.startsWith('hsl(') || color.startsWith('rgb(') || color.startsWith('#');
};