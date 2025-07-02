# Checklist de Tarefas - SUPER_AGENT_MCP_DOCKER_N8N

## [x] 1. Corrigir módulo de TTS e Audio to Speech
- [x] Diagnosticar e corrigir funcionamento do TTS/STT
- [x] Criar aba separada na GUI para configuração de voz
- [x] Dropdown para seleção de voz masculina/feminina
- [x] Campo de texto para testar vozes
- [x] Configuração de entrada/saída de áudio

## [x] 2. Criar aba de MCPs
- [x] Listar MCPs ativos
- [x] Visualizar MCPs das IDEs: Cursor, Cline, RooCline, Windsurf, Trae

## [x] 3. Adicionar URLs ao RAG
- [x] Adicionar as URLs:
  - https://cursor.directory/mcp
  - https://smithery.ai/
  - https://github.com/orgs/modelcontextprotocol/repositories?type=all

## [x] 4. Modificar módulo OpenRouter na GUI
- [x] Remover botão "Carregar Modelos"
- [x] Adicionar dropdown para filtrar por empresa (OpenAI, Meta, Anthropic, Deepseek...)
- [x] Substituir botão "Filtrar Gratuitos" por checkbox "Modelos Gratuitos"

## [x] 5. Criar aba RAG com documentações
- [x] Criar aba RAG separada
- [x] Adicionar documentações: N8N, Docker, Docker Compose, GitHub Commands, Digital Ocean, Cloudflare, Oracle Cloud
- [x] Interface para visualizar e buscar na base de conhecimento

## [x] 6. Implementar sistema de abas completo
- [x] Aba Principal (interface original)
- [x] Aba Voz (configuração TTS/STT)
- [x] Aba MCPs (listagem de MCPs)
- [x] Aba RAG (base de conhecimento)

## [x] 7. Atualizar main.bat e MEMORIES.json
- [x] Garantir que main.bat acesse todos os recursos da interface gráfica
- [x] Atualizar MEMORIES.json com as mudanças

## ✅ TODAS AS TAREFAS CONCLUÍDAS!

# Checklist de Testes Funcionais - SUPER_AGENT_MCP_DOCKER_N8N

## [x] Seleção de modelo OpenRouter
- [x] Dropdown sincroniza corretamente com self.selected_model
- [x] Modelo selecionado é realmente usado na requisição
- [ ] Teste manual: selecionar modelo, enviar mensagem e conferir logs

## [x] Microfone (Speech-to-Text)
- [x] Botão ativa/desativa corretamente a escuta
- [x] Texto reconhecido é enviado ao modelo
- [x] Resposta do modelo é falada pelo TTS
- [ ] Teste manual: clicar no microfone, falar, conferir resposta e áudio

## [x] Aba de Voz (TTS)
- [x] Dropdown de gênero e vozes preenchido corretamente
- [x] Teste de voz funciona para todas as vozes
- [ ] Teste manual: selecionar voz, digitar texto e ouvir TTS

## [ ] Teste final de integração
- [ ] Testar todos os fluxos juntos: voz, modelo, resposta, TTS

## [ ] Bugs/pendências
- [ ] Corrigir qualquer erro encontrado nos testes acima

## [ ] Atualizar MEMORIES.json após testes finais 