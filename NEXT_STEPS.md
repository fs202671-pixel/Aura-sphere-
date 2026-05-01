# Próximas tarefas integradas e pendentes para Aura Sphere

Este documento lista melhorias, integrações e ajustes necessários para o próximo desenvolvedor que trabalhar neste código.

## 1. Memória e contexto inteligente

- [ ] Consolidar a lógica de memória entre frontend, backend e funções de IA.
  - Integrar o mecanismo de busca de memória do backend com o fluxo de chat de forma transparente.
  - Garantir que as entradas de memória relevantes sejam recarregadas e reusadas quando o usuário iniciar uma conversa relacionada.
- [ ] Criar um visualizador de memórias com filtros por tipo (`user`, `assistant`, `system`, `category`), data e relevância.
- [ ] Adicionar a capacidade de fixar ou destacar memórias importantes no modo `Memória`.
- [ ] Permitir que o usuário transforme um resultado de memória em parte da mensagem de prompt antes de enviar.
- [ ] Implantar um mecanismo de classificação semântica para resultados de memória para melhorar precisão de busca.
- [ ] Reforçar o armazenamento de contexto com metadados: tags, projeto, tópico e prioridade.

## 2. Chat e assistente

- [ ] Implementar um histórico de conversas persistente com múltiplas sessões/threads.
- [ ] Suportar múltiplos tipos de prompt: `assistente`, `resumido`, `criativo`, `formal`, `técnico`.
- [ ] Expor presets de prompt configuráveis pelo usuário na interface de chat.
- [ ] Melhorar o envio em fluxo / streaming de respostas no frontend, incluindo pré-visualização de texto incremental.
- [ ] Integrar um modo de revisão de respostas com edição assistida e comentários em linha.
- [ ] Adicionar lógica para evitar repetição excessiva de conteúdo em mensagens longas.
- [ ] Criar um sistema de `sistema` + `pré-prompt` dinâmico com base no contexto do projeto.

## 3. UX/UI e experiência do usuário

- [ ] Refinar o painel `AIOnShell` para suportar acessibilidade e teclas de atalho.
- [ ] Tornar a navegação entre modos mais fluida, com animações e feedback visual claro.
- [ ] Adicionar carregamento de dados em tempo real e transições suaves ao alternar entre modos.
- [ ] Melhorar o design do modo `Memória`, incluindo cards de resultado com ações rápidas.
- [ ] Adicionar suporte nativo para temas `light` e `dark` e persistir a preferência do usuário.
- [ ] Incluir um tutorial inicial ou tour guiado para novos usuários.
- [ ] Implementar mensagens de erro e estados vazios mais úteis para APIs offline ou sem resultados.

## 4. Backend, APIs e integração

- [ ] Validar e padronizar todos os endpoints de backend usados pelo frontend (`/api/v1/memory`, `/api/v1/search`, Supabase Functions). 
- [ ] Garantir que a autenticação e o cabeçalho `Authorization` funcionem de forma consistente entre ambientes.
- [ ] Adicionar contratos de API/Swagger para as rotas do backend e documentação de tipos.
- [ ] Criar testes de integração para a pesquisa de memória e criação de entradas de memória.
- [ ] Considerar a migração do mecanismo de memória para um serviço de vetores/embedding se for necessário escalar.
- [ ] Adicionar validações de tamanho e sanidade para entradas de memória antes da persistência.
- [ ] Monitorar e registrar as chamadas de API para detectar latência e falhas frequentes.

## 5. Dados, persistência e segurança

- [ ] Implementar controle de acesso adequado para salvar e recuperar memórias por `user_id`.
- [ ] Proteger as rotas de memória contra injeções ou acesso não autorizado.
- [ ] Criar armazenamento seguro para chaves e tokens no ambiente de produção.
- [ ] Garantir que os dados sensíveis não sejam enviados por engano para prompts externos.
- [ ] Adicionar políticas de limpeza de dados e expiração para memórias antigas, se necessário.

## 6. Testes e qualidade de código

- [ ] Adicionar testes unitários para componentes de chat, memória e modo `Memória`.
- [ ] Criar testes e2e para fluxo de conversa completo e pesquisa de memórias.
- [ ] Revisar e ajustar `eslint` e `vitest` para garantir cobertura mínima de código.
- [ ] Validar compatibilidade do frontend com navegadores modernos e versões móveis principais.
- [ ] Incluir análise de código estático para detectar imports não usados ou tipos inconsistentes.

## 7. Performance e escalabilidade

- [ ] Minimizar chamadas redundantes de API, incluindo cache local de resultados de memória.
- [ ] Otimizar a renderização do feed de mensagens para diminuir re-renderizações desnecessárias.
- [ ] Implementar paginação ou paginação infinita para históricos de chat extensos.
- [ ] Avaliar o uso de embeddings e busca de similaridade para melhorar buscas de memória.
- [ ] Monitorar consumo de rede no modo de consulta de memória e reduzir carga desnecessária.

## 8. Documentação e onboarding

- [ ] Documentar claramente o fluxo de desenvolvimento no `README.md` ou em novo arquivo `CONTRIBUTING.md`.
- [ ] Escrever guias para configuração local, deploy em contêiner e uso do Supabase.
- [ ] Registrar como configurar variáveis de ambiente e chaves de API.
- [ ] Criar notas de arquitetura para os modos do AI ON, o backend de memória e a integração com Supabase.
- [ ] Adicionar um checklist de revisão para quem for manter o projeto.

## 9. Melhorias de arquitetura e produtos futuros

- [ ] Suportar múltiplos usuários e perfis com memórias ligadas a cada perfil.
- [ ] Adicionar modo de `AutoGPT` / agente multi-etapa para tarefas complexas.
- [ ] Integrar módulos de `notas` e `tarefas` com o histórico de chat e memória.
- [ ] Permitir exportar histórico e memórias para formatos como JSON ou Markdown.
- [ ] Adicionar painéis de análise para indicadores de uso do assistente e memórias.

## 10. Limpeza do repositório e manutenção

- [ ] Remover quaisquer dependências não usadas ou clones de repositórios temporários.
- [ ] Padronizar a nomenclatura de arquivos e rotas entre pacotes.
- [ ] Atualizar o `package.json` com scripts úteis para build, lint e test.
- [ ] Verificar se o contêiner Docker e `docker-compose` estão alinhados com a aplicação real.
- [ ] Garantir que a branch `main` permaneça com commits claros e com histórico bem documentado.
