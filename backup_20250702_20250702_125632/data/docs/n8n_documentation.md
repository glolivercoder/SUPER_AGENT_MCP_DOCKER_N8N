# N8N Documentation para RAG

## Introdução ao N8N

### O que é N8N?
N8N é uma plataforma de automação de workflows open-source que permite conectar diferentes serviços e automatizar tarefas. Com interface visual de drag-and-drop, facilita a criação de integrações complexas sem necessidade de programação.

### Características Principais
- **Open Source**: Código aberto e gratuito
- **Visual Workflow Editor**: Interface drag-and-drop intuitiva
- **400+ Integrações**: Conectores para serviços populares
- **Self-hosted**: Controle total sobre dados e processos
- **Extensível**: Criação de nodes customizados
- **Multi-tenant**: Suporte a múltiplos usuários

## Instalação e Configuração

### Docker (Recomendado)
```bash
# Instalação básica
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  n8nio/n8n

# Com persistência de dados
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Docker Compose
version: '3.8'
services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=n8n
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    restart: always
    environment:
      POSTGRES_DB: n8n
      POSTGRES_USER: n8n
      POSTGRES_PASSWORD: n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  n8n_data:
  postgres_data:
```

### NPM Installation
```bash
# Instalação global
npm install n8n -g

# Executar
n8n start

# Com configurações específicas
N8N_PORT=5678 N8N_HOST=0.0.0.0 n8n start
```

### Variáveis de Ambiente
```bash
# Configurações básicas
export N8N_BASIC_AUTH_ACTIVE=true
export N8N_BASIC_AUTH_USER=admin
export N8N_BASIC_AUTH_PASSWORD=password
export N8N_HOST=0.0.0.0
export N8N_PORT=5678
export N8N_PROTOCOL=https
export N8N_ENCRYPTION_KEY=your-encryption-key

# Banco de dados
export DB_TYPE=postgresdb
export DB_POSTGRESDB_HOST=localhost
export DB_POSTGRESDB_PORT=5432
export DB_POSTGRESDB_DATABASE=n8n
export DB_POSTGRESDB_USER=n8n
export DB_POSTGRESDB_PASSWORD=password

# Email (SMTP)
export N8N_EMAIL_MODE=smtp
export N8N_SMTP_HOST=smtp.gmail.com
export N8N_SMTP_PORT=587
export N8N_SMTP_USER=your-email@gmail.com
export N8N_SMTP_PASS=your-app-password
```

## Conceitos Fundamentais

### Workflows
- **Definição**: Sequência de nodes conectados que processam dados
- **Execução**: Manual, scheduled, webhook-triggered
- **Estado**: Active/Inactive
- **Versionamento**: Histórico de alterações

### Nodes
- **Trigger Nodes**: Iniciam workflows (Webhook, Cron, Manual)
- **Regular Nodes**: Processam dados (HTTP Request, Database, APIs)
- **Output Nodes**: Finalizam workflows (Email, Slack, Database)

### Connections
- **Main Connection**: Fluxo principal de dados
- **Error Connection**: Tratamento de erros
- **Multiple Outputs**: Nodes com múltiplas saídas

### Executions
- **Manual**: Executado pelo usuário
- **Automatic**: Triggered por eventos
- **Scheduled**: Executado em horários específicos
- **Webhook**: Triggered por HTTP requests

## Nodes Essenciais

### Trigger Nodes

#### 1. Webhook
```javascript
// Configuração básica
{
  "httpMethod": "POST",
  "path": "webhook-path",
  "responseMode": "responseNode",
  "options": {}
}

// Exemplo de uso: Receber dados via POST
// URL: https://your-n8n.com/webhook/webhook-path
```

#### 2. Cron
```javascript
// Configuração de schedule
{
  "triggerTimes": {
    "mode": "cronExpression",
    "cronExpression": "0 9 * * 1-5"  // 9h, segunda a sexta
  }
}

// Exemplos de cron:
// 0 */6 * * *     - A cada 6 horas
// 0 0 * * 0       - Todo domingo à meia-noite
// 0 9-17 * * 1-5  - De hora em hora, 9h-17h, seg-sex
```

#### 3. Manual Trigger
```javascript
// Execução manual simples
{
  "manualTriggerConfig": "empty"
}
```

### Regular Nodes

#### 1. HTTP Request
```javascript
// GET Request
{
  "method": "GET",
  "url": "https://api.example.com/users",
  "authentication": "none",
  "options": {
    "headers": {
      "User-Agent": "n8n-workflow"
    }
  }
}

// POST Request com autenticação
{
  "method": "POST",
  "url": "https://api.example.com/users",
  "authentication": "headerAuth",
  "credentials": "apiCredentials",
  "body": {
    "bodyType": "json",
    "jsonBody": "={{ JSON.stringify($json) }}"
  }
}
```

#### 2. Function / Function Item
```javascript
// Function: processa todos os items
for (const item of $input.all()) {
  item.json.newField = item.json.existingField.toUpperCase();
}

return $input.all();

// Function Item: processa item por item
$input.item.json.timestamp = new Date().toISOString();
$input.item.json.processed = true;

return $input.item;
```

#### 3. IF Node
```javascript
// Condições
{
  "conditions": {
    "string": [
      {
        "value1": "={{ $json.status }}",
        "operation": "equal",
        "value2": "success"
      }
    ],
    "number": [
      {
        "value1": "={{ $json.amount }}",
        "operation": "larger",
        "value2": 1000
      }
    ]
  }
}
```

#### 4. Set Node
```javascript
// Adicionar/modificar campos
{
  "options": {},
  "values": {
    "string": [
      {
        "name": "fullName",
        "value": "={{ $json.firstName }} {{ $json.lastName }}"
      }
    ],
    "number": [
      {
        "name": "total",
        "value": "={{ $json.price * $json.quantity }}"
      }
    ]
  }
}
```

### Database Nodes

#### PostgreSQL
```javascript
// Query
{
  "operation": "executeQuery",
  "query": "SELECT * FROM users WHERE created_at > $1",
  "additionalFields": {
    "queryParameters": "={{ [$json.date] }}"
  }
}

// Insert
{
  "operation": "insert",
  "schema": "public",
  "table": "users",
  "columns": "firstName,lastName,email",
  "additionalFields": {}
}
```

#### MySQL
```javascript
// Connection
{
  "host": "localhost",
  "port": 3306,
  "database": "myapp",
  "user": "root",
  "password": "password"
}

// Query com parâmetros
{
  "operation": "executeQuery",
  "query": "INSERT INTO logs (message, level, timestamp) VALUES (?, ?, ?)",
  "additionalFields": {
    "queryParameters": "={{ [$json.message, $json.level, $json.timestamp] }}"
  }
}
```

### API Integrations

#### Slack
```javascript
// Enviar mensagem
{
  "resource": "message",
  "operation": "post",
  "channel": "#general",
  "text": "={{ $json.message }}",
  "attachments": []
}

// Enviar arquivo
{
  "resource": "file",
  "operation": "upload",
  "channels": "#general",
  "fileName": "report.pdf",
  "binaryData": true
}
```

#### Gmail
```javascript
// Enviar email
{
  "resource": "message",
  "operation": "send",
  "to": "{{ $json.email }}",
  "subject": "{{ $json.subject }}",
  "message": "{{ $json.body }}",
  "options": {
    "attachments": "={{ $json.attachments }}"
  }
}
```

#### Google Sheets
```javascript
// Append data
{
  "resource": "spreadsheet",
  "operation": "appendOrUpdate",
  "sheetId": "1abc123...",
  "range": "Sheet1!A:E",
  "valueInputOption": "RAW",
  "values": {
    "values": [
      ["{{ $json.name }}", "{{ $json.email }}", "{{ $json.date }}"]
    ]
  }
}
```

## Expressões e Funções

### Syntax Básica
```javascript
// Acessar dados do item anterior
$json.fieldName
$json["field-with-spaces"]

// Acessar múltiplos items
$input.all()
$input.first()
$input.last()

// Acessar item específico
$("Node Name").item.json.fieldName
$("Node Name").all()[0].json.fieldName
```

### Funções Built-in
```javascript
// String functions
{{ $json.email.toLowerCase() }}
{{ $json.name.toUpperCase() }}
{{ $json.text.includes('keyword') }}
{{ $json.description.substring(0, 100) }}

// Date functions
{{ new Date().toISOString() }}
{{ DateTime.now().toFormat('yyyy-MM-dd') }}
{{ DateTime.fromISO($json.date).plus({days: 30}) }}

// Math functions
{{ Math.round($json.price * 1.2) }}
{{ Math.max($json.value1, $json.value2) }}

// Array functions
{{ $json.items.length }}
{{ $json.tags.join(', ') }}
{{ $json.numbers.filter(n => n > 10) }}
```

### Expressões Avançadas
```javascript
// Conditional
{{ $json.status === 'active' ? 'enabled' : 'disabled' }}

// Object manipulation
{{
  {
    id: $json.id,
    fullName: `${$json.firstName} ${$json.lastName}`,
    isAdult: $json.age >= 18,
    metadata: {
      processedAt: new Date().toISOString(),
      source: 'n8n-workflow'
    }
  }
}}

// Loop through array
{{
  $json.items.map(item => ({
    ...item,
    total: item.price * item.quantity
  }))
}}
```

## Workflows Avançados

### Error Handling
```javascript
// Try/Catch em Function Node
try {
  const result = JSON.parse($json.data);
  return { success: true, data: result };
} catch (error) {
  return { success: false, error: error.message };
}

// Error Workflow
// Usar "On Error" connection para capturar falhas
// Enviar para Slack/Email quando erro ocorre
```

### Batch Processing
```javascript
// Split Into Batches Node
{
  "batchSize": 10,
  "options": {}
}

// Process em lotes para APIs com rate limit
// Aguardar entre batches com Wait Node
```

### Subworkflows
```javascript
// Execute Workflow Node
{
  "workflowId": "123",
  "source": "database",
  "options": {
    "loadedWorkflows": {}
  }
}

// Passar dados para subworkflow
// Receber resultados do subworkflow
```

### Loops
```javascript
// SplitInBatches para loops
{
  "batchSize": 1,
  "options": {
    "reset": false
  }
}

// Loop até condição ser atendida
// Usar IF node para controlar saída do loop
```

## Credenciais e Autenticação

### Tipos de Autenticação
```javascript
// API Key
{
  "name": "API Key",
  "authType": "headerAuth",
  "headerAuth": {
    "name": "Authorization",
    "value": "Bearer {{ $credentials.apiKey }}"
  }
}

// OAuth2
{
  "name": "OAuth2",
  "authType": "oauth2",
  "oauth2": {
    "authUrl": "https://api.service.com/oauth/authorize",
    "accessTokenUrl": "https://api.service.com/oauth/token",
    "clientId": "your-client-id",
    "clientSecret": "your-client-secret",
    "scope": "read write"
  }
}

// Basic Auth
{
  "name": "Basic Auth",
  "authType": "httpBasicAuth",
  "httpBasicAuth": {
    "user": "username",
    "password": "password"
  }
}
```

### Environment Variables
```bash
# Usar variáveis de ambiente para credenciais
export N8N_ENCRYPTION_KEY=your-key
export API_TOKEN=your-token
export DB_PASSWORD=secure-password

# Acessar em workflows
{{ $env.API_TOKEN }}
{{ $env.DB_PASSWORD }}
```

## Deployment e Produção

### Docker Compose Production
```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - WEBHOOK_URL=https://${N8N_HOST}/
      - GENERIC_TIMEZONE=America/Sao_Paulo
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=${DB_PASSWORD}
      - N8N_EMAIL_MODE=smtp
      - N8N_SMTP_HOST=${SMTP_HOST}
      - N8N_SMTP_PORT=587
      - N8N_SMTP_USER=${SMTP_USER}
      - N8N_SMTP_PASS=${SMTP_PASS}
    volumes:
      - n8n_data:/home/node/.n8n
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      - postgres
    networks:
      - n8n-network

  postgres:
    image: postgres:15
    restart: unless-stopped
    environment:
      - POSTGRES_DB=n8n
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - n8n-network

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl/certs:ro
    depends_on:
      - n8n
    networks:
      - n8n-network

volumes:
  n8n_data:
  postgres_data:

networks:
  n8n-network:
    driver: bridge
```

### Nginx Configuration
```nginx
events {
    worker_connections 1024;
}

http {
    upstream n8n {
        server n8n:5678;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl;
        server_name your-domain.com;

        ssl_certificate /etc/ssl/certs/cert.pem;
        ssl_certificate_key /etc/ssl/certs/key.pem;

        location / {
            proxy_pass http://n8n;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: n8n
spec:
  replicas: 1
  selector:
    matchLabels:
      app: n8n
  template:
    metadata:
      labels:
        app: n8n
    spec:
      containers:
      - name: n8n
        image: n8nio/n8n
        ports:
        - containerPort: 5678
        env:
        - name: N8N_HOST
          value: "n8n.example.com"
        - name: N8N_PROTOCOL
          value: "https"
        - name: WEBHOOK_URL
          value: "https://n8n.example.com/"
        - name: DB_TYPE
          value: "postgresdb"
        - name: DB_POSTGRESDB_HOST
          value: "postgres-service"
        volumeMounts:
        - name: n8n-data
          mountPath: /home/node/.n8n
      volumes:
      - name: n8n-data
        persistentVolumeClaim:
          claimName: n8n-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: n8n-service
spec:
  selector:
    app: n8n
  ports:
  - port: 80
    targetPort: 5678
  type: ClusterIP
```

## Monitoring e Logging

### Health Check
```javascript
// Workflow de health check
// HTTP Request para /healthz
// Verificar status da aplicação
// Alertar se não responder

// Endpoint: GET /webhook/healthcheck
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00Z",
  "uptime": "2 days",
  "workflows": {
    "active": 15,
    "total": 23
  }
}
```

### Logging
```javascript
// Function Node para logs estruturados
const log = {
  timestamp: new Date().toISOString(),
  level: 'INFO',
  workflow: $workflow.name,
  execution: $execution.id,
  message: 'Processing completed',
  data: $json
};

// Enviar para Elasticsearch/Splunk
console.log(JSON.stringify(log));
```

### Alertas
```javascript
// Workflow de monitoramento
// Verificar falhas de execução
// Enviar alertas para Slack/Email
// Incluir detalhes do erro

const alert = {
  type: 'workflow_failure',
  workflow: $('Webhook').item.json.workflow,
  error: $('Error').item.json.error,
  timestamp: new Date().toISOString(),
  severity: 'high'
};
```

## Boas Práticas

### Performance
- Usar SplitInBatches para grandes volumes
- Limitar concurrent executions
- Implementar timeouts apropriados
- Usar cache quando possível
- Otimizar queries de database

### Segurança
- Não hardcode credenciais
- Usar HTTPS em produção
- Implementar rate limiting
- Validar inputs de webhooks
- Rotate encryption keys regularmente

### Manutenibilidade
- Usar nomes descritivos para nodes
- Adicionar notes explicativos
- Versionamento de workflows
- Documentar dependências externas
- Implementar error handling completo

### Testing
```javascript
// Test workflow
// Usar dados mock para testes
// Verificar outputs esperados
// Testar edge cases

// Example test data
const testData = {
  "user": {
    "id": 123,
    "email": "test@example.com",
    "status": "active"
  },
  "expected_output": {
    "processed": true,
    "notifications_sent": 1
  }
};
``` 