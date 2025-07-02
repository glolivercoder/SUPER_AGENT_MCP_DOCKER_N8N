# Docker Documentation para RAG

## Conceitos Fundamentais

### O que é Docker?
Docker é uma plataforma de containerização que permite empacotar aplicações e suas dependências em containers leves e portáveis.

### Componentes Principais
- **Docker Engine**: Runtime que executa containers
- **Docker Images**: Templates para criar containers
- **Docker Containers**: Instâncias executáveis de images
- **Dockerfile**: Script para construir images
- **Docker Registry**: Repositório de images (Docker Hub)
- **Docker Compose**: Ferramenta para aplicações multi-container

## Comandos Básicos

### Gerenciamento de Images
```bash
# Listar images locais
docker images
docker image ls

# Baixar image do registry
docker pull ubuntu:latest
docker pull nginx:alpine

# Construir image a partir de Dockerfile
docker build -t minha-app:v1.0 .
docker build -f Dockerfile.prod -t app:prod .

# Remover images
docker rmi ubuntu:latest
docker image rm nginx:alpine

# Limpar images não utilizadas
docker image prune
docker image prune -a  # Remove todas não utilizadas
```

### Gerenciamento de Containers
```bash
# Executar container
docker run hello-world
docker run -it ubuntu bash  # Interativo
docker run -d nginx  # Background (detached)
docker run -p 8080:80 nginx  # Port mapping

# Listar containers
docker ps  # Apenas rodando
docker ps -a  # Todos (incluindo parados)

# Parar containers
docker stop container_id
docker stop container_name

# Remover containers
docker rm container_id
docker rm -f container_id  # Força remoção

# Executar comandos em container rodando
docker exec -it container_id bash
docker exec container_id ls /app
```

### Logs e Monitoramento
```bash
# Ver logs do container
docker logs container_id
docker logs -f container_id  # Follow logs
docker logs --tail 100 container_id

# Estatísticas em tempo real
docker stats
docker stats container_id

# Inspecionar container/image
docker inspect container_id
docker inspect image_name
```

## Dockerfile

### Estrutura Básica
```dockerfile
# Definir image base
FROM node:18-alpine

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos
COPY package*.json ./
COPY . .

# Instalar dependências
RUN npm install

# Expor porta
EXPOSE 3000

# Definir comando padrão
CMD ["npm", "start"]
```

### Instruções Principais
- **FROM**: Define image base
- **WORKDIR**: Define diretório de trabalho
- **COPY/ADD**: Copia arquivos para image
- **RUN**: Executa comandos durante build
- **CMD**: Comando padrão ao executar container
- **ENTRYPOINT**: Ponto de entrada do container
- **EXPOSE**: Documenta portas expostas
- **ENV**: Define variáveis de ambiente
- **ARG**: Define argumentos de build

### Exemplo Completo
```dockerfile
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash app

# Definir diretório de trabalho
WORKDIR /home/app

# Copiar requirements primeiro (cache layer)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Mudar ownership para usuário app
RUN chown -R app:app /home/app

# Mudar para usuário não-root
USER app

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["python", "app.py"]
```

## Docker Compose

### docker-compose.yml Básico
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=1
    volumes:
      - .:/app
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Comandos do Compose
```bash
# Iniciar serviços
docker-compose up
docker-compose up -d  # Background

# Parar serviços
docker-compose down
docker-compose down -v  # Remove volumes

# Ver logs
docker-compose logs
docker-compose logs web

# Executar comandos
docker-compose exec web bash
docker-compose run web python manage.py migrate

# Construir images
docker-compose build
docker-compose build --no-cache
```

## Volumes e Persistência

### Tipos de Volumes
```bash
# Named volumes
docker volume create my_volume
docker run -v my_volume:/data alpine

# Bind mounts
docker run -v /host/path:/container/path alpine

# tmpfs mounts (memória)
docker run --tmpfs /app/temp alpine
```

### Gerenciamento de Volumes
```bash
# Listar volumes
docker volume ls

# Inspecionar volume
docker volume inspect my_volume

# Remover volumes
docker volume rm my_volume
docker volume prune  # Remove volumes não utilizados
```

## Redes Docker

### Tipos de Rede
- **bridge**: Rede padrão para containers
- **host**: Usa rede do host diretamente  
- **none**: Sem conectividade de rede
- **overlay**: Para Docker Swarm
- **macvlan**: Atribui MAC address ao container

### Comandos de Rede
```bash
# Listar redes
docker network ls

# Criar rede
docker network create my_network
docker network create --driver bridge my_bridge

# Conectar container à rede
docker network connect my_network container_id

# Executar container em rede específica
docker run --network=my_network alpine
```

## Multi-stage Builds

### Exemplo de Build Multi-estágio
```dockerfile
# Estágio de build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Estágio final
FROM node:18-alpine AS runtime
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

## Otimização e Boas Práticas

### Otimização de Dockerfile
```dockerfile
# ✅ Bom: Usar image específica e leve
FROM node:18-alpine

# ✅ Bom: Copiar package.json primeiro
COPY package*.json ./
RUN npm ci --only=production

# ✅ Bom: Usar .dockerignore
COPY . .

# ✅ Bom: Usar usuário não-root
USER node

# ❌ Evitar: Image muito genérica
# FROM ubuntu:latest

# ❌ Evitar: Instalar tudo junto
# RUN apt-get update && apt-get install -y python3 nodejs npm
```

### .dockerignore
```
node_modules
npm-debug.log
.git
.gitignore
README.md
.env
.nyc_output
coverage
.vscode
```

### Layers e Cache
- Ordenar comandos por frequência de mudança
- Comandos que mudam pouco primeiro
- Usar cache do Docker Hub quando possível
- Minimizar número de layers

## Segurança

### Práticas de Segurança
```dockerfile
# Usar usuário não-root
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001
USER nextjs

# Não incluir segredos na image
# Usar secrets do Docker ou bind mounts

# Escanear vulnerabilidades
docker scan my-image:latest

# Usar images oficiais
FROM node:18-alpine  # ✅
# FROM random-user/node  # ❌
```

### Health Checks
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

## Docker Swarm

### Inicializar Swarm
```bash
# Inicializar cluster
docker swarm init

# Adicionar worker
docker swarm join --token TOKEN MANAGER_IP:2377

# Listar nodes
docker node ls
```

### Deploy de Serviços
```bash
# Deploy de stack
docker stack deploy -c docker-compose.yml myapp

# Listar stacks
docker stack ls

# Ver serviços
docker service ls

# Escalar serviço
docker service scale myapp_web=3
```

## Registry e Distribuição

### Docker Hub
```bash
# Login
docker login

# Tag e push
docker tag my-app:latest username/my-app:latest
docker push username/my-app:latest

# Pull
docker pull username/my-app:latest
```

### Registry Privado
```bash
# Executar registry local
docker run -d -p 5000:5000 --name registry registry:2

# Tag para registry local
docker tag my-app localhost:5000/my-app

# Push para registry local
docker push localhost:5000/my-app
```

## Debugging e Troubleshooting

### Problemas Comuns

#### Container não inicia
```bash
# Ver logs detalhados
docker logs container_id

# Executar com shell para debug
docker run -it image_name sh
```

#### Problemas de conectividade
```bash
# Inspecionar rede
docker network inspect bridge

# Testar conectividade
docker exec container_id ping other_container
```

#### Problemas de permissão
```bash
# Verificar usuário do container
docker exec container_id whoami

# Verificar permissões de arquivos
docker exec container_id ls -la /app
```

#### High disk usage
```bash
# Limpar sistema completo
docker system prune -a

# Ver uso de espaço
docker system df

# Limpar específicos
docker container prune
docker image prune
docker volume prune
docker network prune
```

## Ferramentas Úteis

### Docker Desktop
- Interface gráfica para Windows/Mac
- Kubernetes integrado
- Gerenciamento visual de containers

### Portainer
```bash
docker run -d -p 9000:9000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  portainer/portainer-ce
```

### Dive (Analisar layers)
```bash
# Instalar dive
curl -OL https://github.com/wagoodman/dive/releases/download/v0.10.0/dive_0.10.0_linux_amd64.deb
sudo apt install ./dive_0.10.0_linux_amd64.deb

# Analisar image
dive my-image:latest
```

## Exemplos Práticos

### Web App com Database
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/myapp
    depends_on:
      - db
    volumes:
      - .:/app
    
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - db_data:/var/lib/postgresql/data
    
  redis:
    image: redis:alpine
    
volumes:
  db_data:
```

### Aplicação de Monitoramento
```yaml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      
  node-exporter:
    image: prom/node-exporter
    ports:
      - "9100:9100"
``` 