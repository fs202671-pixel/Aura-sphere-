import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Copy, Palette, Layout, Settings, Save, Trash2, Eye, EyeOff } from "lucide-react";
import { useVisualCommands, useVisualStore, DEFAULT_THEMES, DEFAULT_LAYOUTS, type VisualTheme, type LayoutConfig } from "@/hooks/useVisualCustomization";
import { speak } from "@/lib/speech";

interface VisualModeProps {
  userId: string;
  aiName: string;
  voiceId: string;
}

export default function VisualMode({ userId, aiName, voiceId }: VisualModeProps) {
  const { executeCommand, getAvailableCommands, currentTheme, currentLayout } = useVisualCommands();
  const {
    customThemes,
    customLayouts,
    saveCustomTheme,
    saveCustomLayout,
    deleteCustomTheme,
    deleteCustomLayout,
    setCustomizing
  } = useVisualStore();

  const [commandInput, setCommandInput] = useState("");
  const [commandOutput, setCommandOutput] = useState("");
  const [isExecuting, setIsExecuting] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);

  // Estados para criação de tema personalizado
  const [customThemeName, setCustomThemeName] = useState("");
  const [editingTheme, setEditingTheme] = useState<VisualTheme | null>(null);

  // Estados para criação de layout personalizado
  const [customLayoutName, setCustomLayoutName] = useState("");
  const [editingLayout, setEditingLayout] = useState<LayoutConfig | null>(null);

  const availableCommands = getAvailableCommands();
  const allThemes = { ...DEFAULT_THEMES, ...customThemes };
  const allLayouts = { ...DEFAULT_LAYOUTS, ...customLayouts };

  const executeVisualCommand = async () => {
    if (!commandInput.trim()) return;

    setIsExecuting(true);
    try {
      const result = await executeCommand(commandInput);
      setCommandOutput(result);

      // Falar o resultado se for voz
      if (voiceId) {
        speak(result, voiceId);
      }
    } catch (error) {
      setCommandOutput(`Erro: ${error}`);
    } finally {
      setIsExecuting(false);
    }
  };

  const copyCommandOutput = async () => {
    try {
      await navigator.clipboard.writeText(commandOutput);
    } catch (error) {
      console.error("Copy failed", error);
    }
  };

  const createCustomTheme = () => {
    if (!customThemeName.trim()) return;

    const newTheme: VisualTheme = {
      ...currentTheme,
      id: customThemeName.toLowerCase().replace(/\s+/g, '_'),
      name: customThemeName,
      description: `Tema personalizado: ${customThemeName}`
    };

    saveCustomTheme(newTheme);
    setCustomThemeName("");
  };

  const createCustomLayout = () => {
    if (!customLayoutName.trim()) return;

    const newLayout: LayoutConfig = {
      ...currentLayout,
      id: customLayoutName.toLowerCase().replace(/\s+/g, '_'),
      name: customLayoutName,
      description: `Layout personalizado: ${customLayoutName}`
    };

    saveCustomLayout(newLayout);
    setCustomLayoutName("");
  };

  const startThemeEditor = (theme: VisualTheme) => {
    setEditingTheme(theme);
    setCustomizing(true);
  };

  const startLayoutEditor = (layout: LayoutConfig) => {
    setEditingLayout(layout);
    setCustomizing(true);
  };

  const saveEditedTheme = () => {
    if (editingTheme) {
      saveCustomTheme(editingTheme);
      setEditingTheme(null);
      setCustomizing(false);
    }
  };

  const saveEditedLayout = () => {
    if (editingLayout) {
      saveCustomLayout(editingLayout);
      setEditingLayout(null);
      setCustomizing(false);
    }
  };

  return (
    <section className="space-y-6 p-6">
      <div className="space-y-2">
        <p className="text-sm uppercase tracking-[0.25em] text-muted-foreground">Modo Visual</p>
        <h2 className="text-2xl font-semibold">Personalize a aparência da sua interface</h2>
        <p className="text-sm text-muted-foreground max-w-2xl">
          Altere cores, layouts, temas e muito mais através de comandos ou interface visual.
        </p>
      </div>

      <Tabs defaultValue="commands" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="commands">Comandos</TabsTrigger>
          <TabsTrigger value="themes">Temas</TabsTrigger>
          <TabsTrigger value="layouts">Layouts</TabsTrigger>
          <TabsTrigger value="advanced">Avançado</TabsTrigger>
        </TabsList>

        <TabsContent value="commands" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Comandos Visuais
              </CardTitle>
              <CardDescription>
                Use comandos de voz ou texto para alterar a interface instantaneamente
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 lg:grid-cols-[1fr_0.8fr]">
                <div className="space-y-3">
                  <Label htmlFor="command-input">Digite um comando visual</Label>
                  <div className="flex gap-2">
                    <Input
                      id="command-input"
                      value={commandInput}
                      onChange={(e) => setCommandInput(e.target.value)}
                      placeholder="Ex: change_theme neon"
                      onKeyPress={(e) => e.key === 'Enter' && executeVisualCommand()}
                    />
                    <Button
                      onClick={executeVisualCommand}
                      disabled={isExecuting || !commandInput.trim()}
                    >
                      {isExecuting ? "Executando..." : "Executar"}
                    </Button>
                  </div>
                </div>

                <div className="space-y-3">
                  <Label>Resultado</Label>
                  <div className="relative">
                    <Textarea
                      value={commandOutput}
                      readOnly
                      rows={4}
                      className="pr-10"
                      placeholder="Resultado dos comandos aparecerá aqui..."
                    />
                    {commandOutput && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="absolute top-2 right-2 h-8 w-8 p-0"
                        onClick={copyCommandOutput}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              </div>

              <Separator />

              <div className="space-y-3">
                <h3 className="text-lg font-semibold">Comandos Disponíveis</h3>
                <div className="grid gap-3 md:grid-cols-2">
                  {availableCommands.map((cmd) => (
                    <Card key={cmd.command} className="p-4">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <code className="text-sm font-mono bg-muted px-2 py-1 rounded">
                            {cmd.command}
                          </code>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setCommandInput(cmd.command)}
                          >
                            Usar
                          </Button>
                        </div>
                        <p className="text-sm text-muted-foreground">{cmd.description}</p>
                        <div className="space-y-1">
                          <p className="text-xs font-medium">Exemplos:</p>
                          {cmd.examples.map((example, idx) => (
                            <code
                              key={idx}
                              className="text-xs bg-muted px-1 py-0.5 rounded cursor-pointer hover:bg-muted/80"
                              onClick={() => setCommandInput(example)}
                            >
                              {example}
                            </code>
                          ))}
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="themes" className="space-y-4">
          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Palette className="h-5 w-5" />
                  Temas Disponíveis
                </CardTitle>
                <CardDescription>
                  Escolha um tema pré-definido ou crie o seu próprio
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-3">
                  {Object.values(allThemes).map((theme) => (
                    <div
                      key={theme.id}
                      className="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className="w-6 h-6 rounded-full border-2 border-white shadow-sm"
                          style={{ backgroundColor: theme.primary }}
                        />
                        <div>
                          <p className="font-medium">{theme.name}</p>
                          <p className="text-sm text-muted-foreground">{theme.description}</p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => executeCommand(`change_theme ${theme.id}`)}
                        >
                          Aplicar
                        </Button>
                        {!DEFAULT_THEMES[theme.id] && (
                          <>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => startThemeEditor(theme)}
                            >
                              Editar
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => deleteCustomTheme(theme.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                <Separator />

                <div className="space-y-3">
                  <Label htmlFor="custom-theme-name">Criar Tema Personalizado</Label>
                  <div className="flex gap-2">
                    <Input
                      id="custom-theme-name"
                      value={customThemeName}
                      onChange={(e) => setCustomThemeName(e.target.value)}
                      placeholder="Nome do tema personalizado"
                    />
                    <Button onClick={createCustomTheme} disabled={!customThemeName.trim()}>
                      <Save className="h-4 w-4 mr-2" />
                      Criar
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Tema Atual</CardTitle>
                <CardDescription>
                  Configurações do tema atualmente aplicado
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4">
                  <div>
                    <Label className="text-sm font-medium">Nome</Label>
                    <p className="text-sm text-muted-foreground">{currentTheme.name}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-sm font-medium">Cor Primária</Label>
                      <div className="flex items-center gap-2 mt-1">
                        <div
                          className="w-4 h-4 rounded border"
                          style={{ backgroundColor: currentTheme.primary }}
                        />
                        <code className="text-xs">{currentTheme.primary}</code>
                      </div>
                    </div>

                    <div>
                      <Label className="text-sm font-medium">Fundo</Label>
                      <div className="flex items-center gap-2 mt-1">
                        <div
                          className="w-4 h-4 rounded border"
                          style={{ backgroundColor: currentTheme.background }}
                        />
                        <code className="text-xs">{currentTheme.background}</code>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-sm font-medium">Arredondamento</Label>
                      <Badge variant="secondary">{currentTheme.borderRadius}</Badge>
                    </div>

                    <div>
                      <Label className="text-sm font-medium">Fonte</Label>
                      <Badge variant="secondary">{currentTheme.fontSize}</Badge>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="layouts" className="space-y-4">
          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Layout className="h-5 w-5" />
                  Layouts Disponíveis
                </CardTitle>
                <CardDescription>
                  Configure o posicionamento e tamanho dos elementos
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-3">
                  {Object.values(allLayouts).map((layout) => (
                    <div
                      key={layout.id}
                      className="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div>
                        <p className="font-medium">{layout.name}</p>
                        <p className="text-sm text-muted-foreground">{layout.description}</p>
                        <div className="flex gap-2 mt-2">
                          <Badge variant="outline">{layout.sidebarPosition}</Badge>
                          <Badge variant="outline">{layout.sidebarWidth}px</Badge>
                          <Badge variant="outline">Sphere: {layout.sphereVisible ? 'On' : 'Off'}</Badge>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => executeCommand(`change_layout ${layout.id}`)}
                        >
                          Aplicar
                        </Button>
                        {!DEFAULT_LAYOUTS[layout.id] && (
                          <>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => startLayoutEditor(layout)}
                            >
                              Editar
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => deleteCustomLayout(layout.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                <Separator />

                <div className="space-y-3">
                  <Label htmlFor="custom-layout-name">Criar Layout Personalizado</Label>
                  <div className="flex gap-2">
                    <Input
                      id="custom-layout-name"
                      value={customLayoutName}
                      onChange={(e) => setCustomLayoutName(e.target.value)}
                      placeholder="Nome do layout personalizado"
                    />
                    <Button onClick={createCustomLayout} disabled={!customLayoutName.trim()}>
                      <Save className="h-4 w-4 mr-2" />
                      Criar
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Controles Rápidos</CardTitle>
                <CardDescription>
                  Ajustes rápidos da interface
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="sphere-toggle">Esfera de Partículas</Label>
                    <Switch
                      id="sphere-toggle"
                      checked={currentLayout.sphereVisible}
                      onCheckedChange={(checked) =>
                        executeCommand(`toggle_sphere ${checked ? 'on' : 'off'}`)
                      }
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Tamanho da Esfera: {currentLayout.sphereSize}px</Label>
                    <Slider
                      value={[currentLayout.sphereSize]}
                      onValueChange={([value]) => executeCommand(`set_sphere_size ${value}`)}
                      min={50}
                      max={500}
                      step={10}
                      className="w-full"
                    />
                  </div>
                </div>

                <Separator />

                <div className="space-y-3">
                  <Button
                    variant="outline"
                    onClick={() => executeCommand('list_themes')}
                    className="w-full"
                  >
                    Listar Temas Disponíveis
                  </Button>

                  <Button
                    variant="outline"
                    onClick={() => executeCommand('reset_visual')}
                    className="w-full"
                  >
                    Resetar para Padrão
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="advanced" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Configurações Avançadas</CardTitle>
              <CardDescription>
                Ajustes finos e recursos experimentais
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-3">
                  <Label>Modo de Visualização</Label>
                  <div className="flex items-center gap-2">
                    <Switch
                      checked={previewMode}
                      onCheckedChange={setPreviewMode}
                    />
                    <span className="text-sm text-muted-foreground">
                      {previewMode ? 'Visualização ativa' : 'Visualização desativada'}
                    </span>
                  </div>
                </div>

                <div className="space-y-3">
                  <Label>Exportar Configuração</Label>
                  <Button variant="outline" className="w-full">
                    Baixar Configurações
                  </Button>
                </div>
              </div>

              <Separator />

              <div className="space-y-3">
                <Label>Informações do Sistema Visual</Label>
                <div className="grid gap-2 text-sm">
                  <div className="flex justify-between">
                    <span>Tema atual:</span>
                    <code>{currentTheme.id}</code>
                  </div>
                  <div className="flex justify-between">
                    <span>Layout atual:</span>
                    <code>{currentLayout.id}</code>
                  </div>
                  <div className="flex justify-between">
                    <span>Temas personalizados:</span>
                    <span>{Object.keys(customThemes).length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Layouts personalizados:</span>
                    <span>{Object.keys(customLayouts).length}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Editor de Tema Modal/Overlay */}
      {editingTheme && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl max-h-[80vh] overflow-auto">
            <CardHeader>
              <CardTitle>Editar Tema: {editingTheme.name}</CardTitle>
              <CardDescription>
                Modifique as configurações do tema personalizado
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Aqui seria implementado o editor completo de tema */}
              <p className="text-sm text-muted-foreground">
                Editor de tema avançado seria implementado aqui...
              </p>
            </CardContent>
            <div className="flex justify-end gap-2 p-4 border-t">
              <Button variant="outline" onClick={() => setEditingTheme(null)}>
                Cancelar
              </Button>
              <Button onClick={saveEditedTheme}>
                <Save className="h-4 w-4 mr-2" />
                Salvar
              </Button>
            </div>
          </Card>
        </div>
      )}

      {/* Editor de Layout Modal/Overlay */}
      {editingLayout && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl max-h-[80vh] overflow-auto">
            <CardHeader>
              <CardTitle>Editar Layout: {editingLayout.name}</CardTitle>
              <CardDescription>
                Modifique as configurações do layout personalizado
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Aqui seria implementado o editor completo de layout */}
              <p className="text-sm text-muted-foreground">
                Editor de layout avançado seria implementado aqui...
              </p>
            </CardContent>
            <div className="flex justify-end gap-2 p-4 border-t">
              <Button variant="outline" onClick={() => setEditingLayout(null)}>
                Cancelar
              </Button>
              <Button onClick={saveEditedLayout}>
                <Save className="h-4 w-4 mr-2" />
                Salvar
              </Button>
            </div>
          </Card>
        </div>
      )}
    </section>
  );
}