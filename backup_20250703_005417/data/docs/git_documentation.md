# Git Documentation para RAG

## Comandos Básicos do Git

### Inicialização e Configuração
- `git init` - Inicializa repositório Git em diretório
- `git config --global user.name "Nome"` - Configura nome do usuário
- `git config --global user.email "email@exemplo.com"` - Configura email
- `git config --list` - Lista todas configurações

### Status e Informações
- `git status` - Mostra status dos arquivos (modified, staged, untracked)
- `git log` - Histórico de commits
- `git log --oneline` - Log resumido em uma linha
- `git log --graph` - Log com gráfico de branches
- `git show` - Mostra detalhes do último commit
- `git diff` - Diferenças entre working directory e staging area
- `git diff --staged` - Diferenças entre staging area e último commit

### Área de Stage (Staging Area)
- `git add arquivo.txt` - Adiciona arquivo específico ao stage
- `git add .` - Adiciona todos arquivos modificados ao stage
- `git add -A` - Adiciona todos arquivos (incluindo deletados)
- `git reset arquivo.txt` - Remove arquivo do stage
- `git reset` - Remove todos arquivos do stage
- `git reset --hard` - Desfaz mudanças no working directory

### Commits
- `git commit -m "mensagem"` - Cria commit com mensagem
- `git commit -am "mensagem"` - Add + commit em arquivos já trackeados
- `git commit --amend` - Modifica último commit
- `git revert <hash>` - Reverte commit específico

### Branches (Ramificações)
- `git branch` - Lista branches locais
- `git branch -a` - Lista todas branches (local + remote)
- `git branch nome-branch` - Cria nova branch
- `git checkout nome-branch` - Muda para branch
- `git checkout -b nome-branch` - Cria e muda para nova branch
- `git switch nome-branch` - Comando moderno para mudar branch
- `git switch -c nome-branch` - Cria e muda para nova branch
- `git merge nome-branch` - Faz merge da branch especificada
- `git branch -d nome-branch` - Deleta branch (safe)
- `git branch -D nome-branch` - Força deleção de branch

### Repositórios Remotos
- `git remote add origin <URL>` - Adiciona repositório remoto
- `git remote -v` - Lista repositórios remotos
- `git push origin main` - Envia commits para branch main do remote
- `git push -u origin main` - Push + configura upstream
- `git pull origin main` - Baixa e faz merge do remote
- `git fetch origin` - Baixa mudanças sem fazer merge
- `git clone <URL>` - Clona repositório remoto

### Stash (Armazenamento Temporário)
- `git stash` - Salva mudanças temporariamente
- `git stash pop` - Aplica último stash e o remove
- `git stash list` - Lista todos stashes
- `git stash apply` - Aplica stash sem removê-lo
- `git stash drop` - Remove stash
- `git stash clear` - Remove todos stashes

### Tags
- `git tag v1.0.0` - Cria tag lightweight
- `git tag -a v1.0.0 -m "versão 1.0"` - Cria tag anotada
- `git tag` - Lista tags
- `git push origin v1.0.0` - Envia tag para remote
- `git push origin --tags` - Envia todas tags

## Workflows Comuns

### Workflow Básico
1. `git status` - Verificar status
2. `git add .` - Adicionar mudanças
3. `git commit -m "mensagem"` - Commit
4. `git push origin main` - Enviar para remote

### Feature Branch Workflow
1. `git checkout -b feature/nova-funcionalidade`
2. Desenvolver funcionalidade
3. `git add .` e `git commit -m "adiciona nova funcionalidade"`
4. `git push origin feature/nova-funcionalidade`
5. Abrir Pull Request
6. `git checkout main` e `git pull origin main`
7. `git branch -d feature/nova-funcionalidade`

### Gitflow Workflow
- **main**: Código de produção
- **develop**: Branch de desenvolvimento
- **feature/***: Novas funcionalidades
- **release/***: Preparação de releases
- **hotfix/***: Correções urgentes

## Resolução de Conflitos

### Quando ocorrem conflitos
- Durante merge de branches
- Durante pull/rebase
- Quando múltiplas pessoas editam mesmo arquivo

### Resolver conflitos
1. `git status` - Ver arquivos em conflito
2. Abrir arquivo e procurar marcadores:
   ```
   <<<<<<< HEAD
   código da branch atual
   =======
   código da branch sendo merged
   >>>>>>> nome-da-branch
   ```
3. Editar arquivo removendo marcadores e escolhendo código final
4. `git add arquivo-resolvido.txt`
5. `git commit` - Finalizar merge

## Comandos Avançados

### Rebase
- `git rebase main` - Reaplica commits da branch atual sobre main
- `git rebase -i HEAD~3` - Rebase interativo dos últimos 3 commits
- `git rebase --continue` - Continua rebase após resolver conflitos
- `git rebase --abort` - Cancela rebase

### Reset
- `git reset --soft HEAD~1` - Desfaz último commit mantendo mudanças staged
- `git reset --mixed HEAD~1` - Desfaz último commit, mudanças ficam unstaged
- `git reset --hard HEAD~1` - Desfaz último commit e mudanças completamente

### Cherry-pick
- `git cherry-pick <hash>` - Aplica commit específico na branch atual

### Bisect
- `git bisect start` - Inicia busca binária por bug
- `git bisect bad` - Marca commit atual como ruim
- `git bisect good <hash>` - Marca commit como bom
- `git bisect reset` - Finaliza bisect

## Arquivos Especiais

### .gitignore
Arquivo que especifica quais arquivos/diretórios o Git deve ignorar:
```
# Dependências
node_modules/
*.log

# Arquivos de build
dist/
build/

# Arquivos de sistema
.DS_Store
Thumbs.db

# IDEs
.vscode/
.idea/

# Variáveis de ambiente
.env
```

### .gitattributes
Configurações específicas de arquivos:
```
# Forçar line endings
*.sh text eol=lf
*.bat text eol=crlf

# Marcar arquivos como binários
*.png binary
*.jpg binary
```

## Hooks do Git

### Hooks Client-side
- `pre-commit` - Executa antes do commit
- `commit-msg` - Valida mensagem de commit
- `post-commit` - Executa após commit
- `pre-push` - Executa antes do push

### Hooks Server-side
- `pre-receive` - Executa antes de receber push
- `post-receive` - Executa após receber push
- `update` - Executa para cada branch sendo atualizada

## Boas Práticas

### Mensagens de Commit
- Use presente imperativo: "adiciona", "corrige", "remove"
- Primeira linha até 50 caracteres
- Linha em branco, depois descrição detalhada
- Exemplo:
  ```
  adiciona autenticação de usuários
  
  - Implementa login/logout
  - Adiciona middleware de autenticação
  - Inclui testes unitários
  ```

### Estrutura de Branches
- `main`/`master`: Código estável de produção
- `develop`: Integração de features
- `feature/nome`: Desenvolvimento de funcionalidades
- `hotfix/nome`: Correções urgentes
- `release/versao`: Preparação de releases

### Commits
- Commits pequenos e focados
- Um commit por funcionalidade/correção
- Testar antes de fazer commit
- Não fazer commit de arquivos gerados automaticamente

## Troubleshooting

### Problemas Comuns

#### "Permission denied (publickey)"
```bash
ssh-keygen -t ed25519 -C "email@exemplo.com"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
# Adicionar chave pública no GitHub/GitLab
```

#### "fatal: not a git repository"
```bash
git init
# ou
cd diretorio-correto
```

#### "Your branch is ahead of origin/main by X commits"
```bash
git push origin main
```

#### "Your branch is behind origin/main"
```bash
git pull origin main
```

#### Desfazer último commit mantendo mudanças
```bash
git reset --soft HEAD~1
```

#### Remover arquivo já commitado do tracking
```bash
git rm --cached arquivo.txt
echo "arquivo.txt" >> .gitignore
git add .gitignore
git commit -m "remove arquivo.txt do tracking"
```

### Recuperação de Dados

#### Recuperar arquivo deletado
```bash
git checkout HEAD -- arquivo.txt
```

#### Recuperar commit deletado
```bash
git reflog
git checkout <hash-do-commit>
git checkout -b branch-recuperada
```

#### Ver histórico de um arquivo
```bash
git log --follow -- arquivo.txt
```

## Integração com IDEs

### VS Code
- Extensão GitLens
- Git Graph
- Controle de versão integrado

### Configurações úteis
```bash
# Editor padrão
git config --global core.editor "code --wait"

# Merge tool
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd 'code --wait $MERGED'

# Diff tool
git config --global diff.tool vscode
git config --global difftool.vscode.cmd 'code --wait --diff $LOCAL $REMOTE'
``` 