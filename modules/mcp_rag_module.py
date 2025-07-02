# MCP RAG Module - SUPER_AGENT_MCP_DOCKER_N8N
"""
Módulo MCP (Model Context Protocol) com capacidades RAG (Retrieval-Augmented Generation)
para integração com IDEs e fornecimento de contexto inteligente.
"""

import asyncio
import json
import logging
import os
import sqlite3
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import numpy as np
import requests
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import websocket
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPMessage(BaseModel):
    """Modelo para mensagens MCP"""
    id: str
    method: str
    params: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class RAGQuery(BaseModel):
    """Modelo para consultas RAG"""
    query: str
    top_k: int = 5
    context_window: int = 2000
    
class DocumentChunk(BaseModel):
    """Modelo para chunks de documentos"""
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None

class MCPRAGModule:
    """Módulo principal MCP RAG"""
    
    def __init__(self, config_path: str = "config/mcp_config.json"):
        self.config = self.load_config(config_path)
        self.app = FastAPI(title="MCP RAG Module", version="1.0.0")
        self.setup_cors()
        self.setup_routes()
        
        # Inicialização de componentes
        self.embedding_model = None
        self.vector_db = None
        self.active_connections: List[WebSocket] = []
        self.is_running = False
        
        # Base de dados SQLite para metadados
        self.init_database()
        
        logger.info("MCPRAGModule inicializado")

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Carrega configurações do arquivo JSON"""
        default_config = {
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "vector_db_path": "./data/vectordb",
            "documents_path": "./documents",
            "mcp_host": "localhost",
            "mcp_port": 8000,
            "chunk_size": 500,
            "chunk_overlap": 50,
            "max_contexts": 10
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return {**default_config, **config}
        except Exception as e:
            logger.warning(f"Erro ao carregar configuração: {e}. Usando configuração padrão.")
        
        return default_config

    def init_database(self):
        """Inicializa banco de dados SQLite para metadados"""
        db_path = Path("data/mcp_rag.db")
        db_path.parent.mkdir(exist_ok=True)
        
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filepath TEXT UNIQUE,
                content_hash TEXT,
                processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                chunk_count INTEGER,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_text TEXT,
                response_text TEXT,
                contexts_used TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                execution_time REAL
            )
        ''')
        
        self.conn.commit()
        logger.info("Base de dados inicializada")

    def setup_cors(self):
        """Configura CORS para a API"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_routes(self):
        """Configura as rotas da API"""
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        @self.app.post("/initialize")
        async def initialize():
            """Inicializa o módulo MCP RAG"""
            try:
                await self.initialize_components()
                return {"status": "initialized", "message": "MCP RAG Module inicializado com sucesso"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Erro na inicialização: {str(e)}")
        
        @self.app.post("/process_documents")
        async def process_documents():
            """Processa documentos para indexação"""
            try:
                processed_count = await self.process_all_documents()
                return {"status": "processed", "documents_processed": processed_count}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")
        
        @self.app.post("/query")
        async def query_rag(query: RAGQuery):
            """Realiza consulta RAG"""
            try:
                start_time = time.time()
                result = await self.perform_rag_query(query.query, query.top_k, query.context_window)
                execution_time = time.time() - start_time
                
                # Salva consulta no banco
                self.save_query_log(query.query, result["response"], result["contexts"], execution_time)
                
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Erro na consulta: {str(e)}")
        
        @self.app.websocket("/mcp")
        async def mcp_websocket(websocket: WebSocket):
            """WebSocket para comunicação MCP"""
            await self.handle_mcp_connection(websocket)

    async def initialize_components(self):
        """Inicializa componentes do módulo"""
        if self.is_running:
            return
        
        logger.info("Inicializando componentes...")
        
        # Inicializa modelo de embedding
        self.embedding_model = SentenceTransformer(self.config["embedding_model"])
        logger.info(f"Modelo de embedding carregado: {self.config['embedding_model']}")
        
        # Inicializa banco vetorial
        self.vector_db = chromadb.PersistentClient(
            path=self.config["vector_db_path"],
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Cria ou obtém coleção
        self.collection = self.vector_db.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info("Banco vetorial inicializado")
        self.is_running = True

    async def process_all_documents(self) -> int:
        """Processa todos os documentos no diretório configurado"""
        docs_path = Path(self.config["documents_path"])
        if not docs_path.exists():
            docs_path.mkdir(parents=True)
            logger.info(f"Diretório de documentos criado: {docs_path}")
            return 0
        
        processed_count = 0
        supported_extensions = {'.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml', '.dockerfile'}
        
        for file_path in docs_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    await self.process_document(file_path)
                    processed_count += 1
                    logger.info(f"Documento processado: {file_path}")
                except Exception as e:
                    logger.error(f"Erro ao processar {file_path}: {e}")
        
        return processed_count

    async def process_document(self, file_path: Path):
        """Processa um documento individual"""
        try:
            # Lê conteúdo do arquivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Calcula hash do conteúdo
            import hashlib
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Verifica se já foi processado
            cursor = self.conn.cursor()
            cursor.execute('SELECT content_hash FROM documents WHERE filepath = ?', (str(file_path),))
            result = cursor.fetchone()
            
            if result and result[0] == content_hash:
                logger.debug(f"Documento já processado: {file_path}")
                return
            
            # Cria chunks do documento
            chunks = self.create_chunks(content, file_path)
            
            # Gera embeddings
            chunk_texts = [chunk.content for chunk in chunks]
            embeddings = self.embedding_model.encode(chunk_texts).tolist()
            
            # Prepara dados para inserção no banco vetorial
            ids = [f"{file_path.stem}_{i}" for i in range(len(chunks))]
            metadatas = [chunk.metadata for chunk in chunks]
            
            # Remove chunks antigos se existirem
            try:
                existing_ids = self.collection.get(where={"filepath": str(file_path)})["ids"]
                if existing_ids:
                    self.collection.delete(ids=existing_ids)
            except:
                pass
            
            # Adiciona novos chunks
            self.collection.add(
                embeddings=embeddings,
                documents=chunk_texts,
                metadatas=metadatas,
                ids=ids
            )
            
            # Atualiza registro no banco SQLite
            cursor.execute('''
                INSERT OR REPLACE INTO documents 
                (filepath, content_hash, chunk_count, metadata)
                VALUES (?, ?, ?, ?)
            ''', (str(file_path), content_hash, len(chunks), json.dumps({"file_size": len(content)})))
            
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Erro ao processar documento {file_path}: {e}")
            raise

    def create_chunks(self, content: str, file_path: Path) -> List[DocumentChunk]:
        """Cria chunks de um documento"""
        chunk_size = self.config["chunk_size"]
        chunk_overlap = self.config["chunk_overlap"]
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(content):
            end = start + chunk_size
            chunk_content = content[start:end]
            
            # Tenta encontrar uma quebra natural (linha ou palavra)
            if end < len(content):
                last_newline = chunk_content.rfind('\n')
                last_space = chunk_content.rfind(' ')
                break_point = max(last_newline, last_space)
                
                if break_point > start + chunk_size // 2:
                    chunk_content = content[start:start + break_point]
                    end = start + break_point
            
            metadata = {
                "filepath": str(file_path),
                "filename": file_path.name,
                "chunk_id": chunk_id,
                "start_pos": start,
                "end_pos": end,
                "file_extension": file_path.suffix
            }
            
            chunks.append(DocumentChunk(content=chunk_content.strip(), metadata=metadata))
            
            start = end - chunk_overlap
            chunk_id += 1
        
        return chunks

    async def perform_rag_query(self, query: str, top_k: int = 5, context_window: int = 2000) -> Dict[str, Any]:
        """Realiza consulta RAG"""
        if not self.is_running:
            raise Exception("Módulo não inicializado")
        
        # Gera embedding da consulta
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Busca documentos similares
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        
        # Processa resultados
        contexts = []
        for i, (doc, metadata, distance) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )):
            contexts.append({
                "content": doc,
                "metadata": metadata,
                "similarity": 1 - distance,  # Converte distância em similaridade
                "rank": i + 1
            })
        
        # Gera resposta baseada no contexto
        response = await self.generate_response(query, contexts, context_window)
        
        return {
            "query": query,
            "response": response,
            "contexts": contexts,
            "total_contexts": len(contexts)
        }

    async def generate_response(self, query: str, contexts: List[Dict], context_window: int) -> str:
        """Gera resposta baseada no contexto recuperado"""
        # Combina contextos relevantes
        combined_context = ""
        current_length = 0
        
        for context in contexts:
            content = context["content"]
            if current_length + len(content) <= context_window:
                combined_context += f"\n--- Documento: {context['metadata']['filename']} ---\n"
                combined_context += content + "\n"
                current_length += len(content)
            else:
                break
        
        # Para uma implementação básica, retorna o contexto formatado
        # Em uma implementação completa, aqui seria feita a chamada para um LLM
        response = f"""
Baseado nos documentos encontrados, aqui está o contexto relevante para sua consulta "{query}":

{combined_context}

Resumo: Foram encontrados {len(contexts)} documentos relevantes que podem ajudar a responder sua consulta.
"""
        
        return response.strip()

    async def handle_mcp_connection(self, websocket: WebSocket):
        """Gerencia conexão WebSocket MCP"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        try:
            while True:
                # Recebe mensagem
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Processa mensagem MCP
                response = await self.process_mcp_message(message)
                
                # Envia resposta
                await websocket.send_text(json.dumps(response))
                
        except WebSocketDisconnect:
            self.active_connections.remove(websocket)
            logger.info("Conexão MCP desconectada")
        except Exception as e:
            logger.error(f"Erro na conexão MCP: {e}")
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def process_mcp_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Processa mensagem MCP"""
        method = message.get("method")
        params = message.get("params", {})
        msg_id = message.get("id")
        
        try:
            if method == "initialize":
                await self.initialize_components()
                result = {"status": "initialized"}
                
            elif method == "query":
                query_text = params.get("query", "")
                top_k = params.get("top_k", 5)
                result = await self.perform_rag_query(query_text, top_k)
                
            elif method == "process_documents":
                processed_count = await self.process_all_documents()
                result = {"processed_documents": processed_count}
                
            elif method == "get_status":
                result = {
                    "is_running": self.is_running,
                    "active_connections": len(self.active_connections),
                    "documents_count": self.get_documents_count()
                }
                
            else:
                raise Exception(f"Método não suportado: {method}")
            
            return {
                "id": msg_id,
                "result": result
            }
            
        except Exception as e:
            return {
                "id": msg_id,
                "error": {
                    "code": -1,
                    "message": str(e)
                }
            }

    def get_documents_count(self) -> int:
        """Retorna número de documentos processados"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM documents')
            return cursor.fetchone()[0]
        except:
            return 0

    def save_query_log(self, query: str, response: str, contexts: List[Dict], execution_time: float):
        """Salva log da consulta"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO queries (query_text, response_text, contexts_used, execution_time)
                VALUES (?, ?, ?, ?)
            ''', (query, response, json.dumps(contexts), execution_time))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Erro ao salvar log da consulta: {e}")

    def shutdown(self):
        """Desliga o módulo"""
        self.is_running = False
        if hasattr(self, 'conn'):
            self.conn.close()
        logger.info("Módulo MCP RAG desligado")

# Instância global do módulo
mcp_rag_instance = None

def create_app():
    """Cria instância da aplicação FastAPI"""
    global mcp_rag_instance
    mcp_rag_instance = MCPRAGModule()
    return mcp_rag_instance.app

def run_server(host: str = "localhost", port: int = 8000):
    """Executa servidor"""
    app = create_app()
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    import sys
    
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    
    run_server(host, port) 