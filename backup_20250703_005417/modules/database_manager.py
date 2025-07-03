#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Database Manager - Gerenciador de Banco de Dados SQLite
------------------------------------------------------
Módulo responsável por:
- Gerenciamento de banco de dados SQLite local
- Tabelas para RAG, memórias, configurações, logs
- Backup e restauração de dados
- Integração com outros módulos

Autor: [Seu Nome]
Data: 01/07/2025
Versão: 0.1.0
"""

import os
import sqlite3
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import threading

class DatabaseManager:
    """Gerenciador de banco de dados SQLite"""
    
    def __init__(self, db_path: str = "data/super_agent.db"):
        self.logger = logging.getLogger("DatabaseManager")
        self.db_path = Path(db_path)
        self.lock = threading.Lock()
        
        # Criar diretório se não existir
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializar banco
        self._initialize_database()
        self.logger.info(f"Database Manager inicializado: {self.db_path}")
    
    def _initialize_database(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de documentos RAG
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS rag_documents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        source_path TEXT,
                        source_type TEXT,
                        file_size INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        tags TEXT,
                        metadata TEXT
                    )
                """)
                
                # Tabela de memórias do sistema
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        memory_type TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        tags TEXT,
                        importance INTEGER DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT
                    )
                """)
                
                # Tabela de prompts e respostas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS prompt_responses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prompt TEXT NOT NULL,
                        response TEXT NOT NULL,
                        agent_type TEXT NOT NULL,
                        model_id TEXT,
                        context_used TEXT,
                        tokens_used INTEGER,
                        processing_time REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        tags TEXT,
                        metadata TEXT
                    )
                """)
                
                # Tabela de configurações
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS configurations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        module_name TEXT NOT NULL,
                        config_key TEXT NOT NULL,
                        config_value TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(module_name, config_key)
                    )
                """)
                
                # Tabela de logs do sistema
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        level TEXT NOT NULL,
                        module TEXT NOT NULL,
                        message TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT
                    )
                """)
                
                # Tabela de projetos
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        status TEXT DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT
                    )
                """)
                
                # Tabela de tasks
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER,
                        title TEXT NOT NULL,
                        description TEXT,
                        status TEXT DEFAULT 'TODO',
                        priority INTEGER DEFAULT 1,
                        estimated_time REAL,
                        actual_time REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP,
                        assigned_to TEXT,
                        tags TEXT,
                        FOREIGN KEY (project_id) REFERENCES projects (id)
                    )
                """)
                
                # Tabela de vozes TTS
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tts_voices (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        voice_name TEXT NOT NULL,
                        language TEXT NOT NULL,
                        provider TEXT NOT NULL,
                        voice_id TEXT,
                        is_free BOOLEAN DEFAULT 1,
                        quality_rating REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT
                    )
                """)
                
                # Índices para melhor performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_rag_documents_tags ON rag_documents(tags)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_memories_type ON system_memories(memory_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompt_responses_agent ON prompt_responses(agent_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_tts_voices_language ON tts_voices(language)")
                
                conn.commit()
                self.logger.info("Banco de dados inicializado com sucesso")
                
        except Exception as e:
            self.logger.error(f"Erro ao inicializar banco de dados: {e}")
            raise
    
    def add_rag_document(self, title: str, content: str, source_path: str = None, 
                        source_type: str = None, tags: List[str] = None, metadata: Dict = None) -> int:
        """Adiciona documento ao RAG"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        INSERT INTO rag_documents (title, content, source_path, source_type, tags, metadata)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        title,
                        content,
                        source_path,
                        source_type,
                        json.dumps(tags) if tags else None,
                        json.dumps(metadata) if metadata else None
                    ))
                    
                    doc_id = cursor.lastrowid
                    conn.commit()
                    
                    self.logger.info(f"Documento RAG adicionado: {title} (ID: {doc_id})")
                    return doc_id
                    
            except Exception as e:
                self.logger.error(f"Erro ao adicionar documento RAG: {e}")
                raise
    
    def search_rag_documents(self, query: str, limit: int = 10) -> List[Dict]:
        """Busca documentos RAG"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        SELECT id, title, content, source_path, tags, created_at
                        FROM rag_documents
                        WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
                        ORDER BY created_at DESC
                        LIMIT ?
                    """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))
                    
                    results = []
                    for row in cursor.fetchall():
                        results.append({
                            "id": row[0],
                            "title": row[1],
                            "content": row[2],
                            "source_path": row[3],
                            "tags": json.loads(row[4]) if row[4] else [],
                            "created_at": row[5]
                        })
                    
                    return results
                    
            except Exception as e:
                self.logger.error(f"Erro ao buscar documentos RAG: {e}")
                return []
    
    def add_memory(self, memory_type: str, title: str, content: str, 
                  tags: List[str] = None, importance: int = 1, metadata: Dict = None) -> int:
        """Adiciona memória ao sistema"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        INSERT INTO system_memories (memory_type, title, content, tags, importance, metadata)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        memory_type,
                        title,
                        content,
                        json.dumps(tags) if tags else None,
                        importance,
                        json.dumps(metadata) if metadata else None
                    ))
                    
                    memory_id = cursor.lastrowid
                    conn.commit()
                    
                    self.logger.info(f"Memória adicionada: {title} (ID: {memory_id})")
                    return memory_id
                    
            except Exception as e:
                self.logger.error(f"Erro ao adicionar memória: {e}")
                raise
    
    def get_memories(self, memory_type: str = None, limit: int = 50) -> List[Dict]:
        """Obtém memórias do sistema"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    if memory_type:
                        cursor.execute("""
                            SELECT id, memory_type, title, content, tags, importance, created_at
                            FROM system_memories
                            WHERE memory_type = ?
                            ORDER BY importance DESC, created_at DESC
                            LIMIT ?
                        """, (memory_type, limit))
                    else:
                        cursor.execute("""
                            SELECT id, memory_type, title, content, tags, importance, created_at
                            FROM system_memories
                            ORDER BY importance DESC, created_at DESC
                            LIMIT ?
                        """, (limit,))
                    
                    results = []
                    for row in cursor.fetchall():
                        results.append({
                            "id": row[0],
                            "memory_type": row[1],
                            "title": row[2],
                            "content": row[3],
                            "tags": json.loads(row[4]) if row[4] else [],
                            "importance": row[5],
                            "created_at": row[6]
                        })
                    
                    return results
                    
            except Exception as e:
                self.logger.error(f"Erro ao obter memórias: {e}")
                return []
    
    def add_prompt_response(self, prompt: str, response: str, agent_type: str, 
                          model_id: str = None, context_used: List[str] = None,
                          tokens_used: int = None, processing_time: float = None,
                          tags: List[str] = None, metadata: Dict = None) -> int:
        """Adiciona prompt e resposta"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        INSERT INTO prompt_responses 
                        (prompt, response, agent_type, model_id, context_used, tokens_used, processing_time, tags, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        prompt,
                        response,
                        agent_type,
                        model_id,
                        json.dumps(context_used) if context_used else None,
                        tokens_used,
                        processing_time,
                        json.dumps(tags) if tags else None,
                        json.dumps(metadata) if metadata else None
                    ))
                    
                    pr_id = cursor.lastrowid
                    conn.commit()
                    
                    self.logger.info(f"Prompt/Resposta adicionado (ID: {pr_id})")
                    return pr_id
                    
            except Exception as e:
                self.logger.error(f"Erro ao adicionar prompt/resposta: {e}")
                raise
    
    def add_tts_voice(self, voice_name: str, language: str, provider: str, 
                     voice_id: str = None, is_free: bool = True, 
                     quality_rating: float = None, metadata: Dict = None) -> int:
        """Adiciona voz TTS ao catálogo"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        INSERT INTO tts_voices (voice_name, language, provider, voice_id, is_free, quality_rating, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        voice_name,
                        language,
                        provider,
                        voice_id,
                        is_free,
                        quality_rating,
                        json.dumps(metadata) if metadata else None
                    ))
                    
                    voice_id = cursor.lastrowid
                    conn.commit()
                    
                    self.logger.info(f"Voz TTS adicionada: {voice_name} (ID: {voice_id})")
                    return voice_id
                    
            except Exception as e:
                self.logger.error(f"Erro ao adicionar voz TTS: {e}")
                raise
    
    def get_tts_voices(self, language: str = None, is_free: bool = None) -> List[Dict]:
        """Obtém vozes TTS"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    if language and is_free is not None:
                        cursor.execute("""
                            SELECT id, voice_name, language, provider, voice_id, is_free, quality_rating
                            FROM tts_voices
                            WHERE language = ? AND is_free = ?
                            ORDER BY quality_rating DESC
                        """, (language, is_free))
                    elif language:
                        cursor.execute("""
                            SELECT id, voice_name, language, provider, voice_id, is_free, quality_rating
                            FROM tts_voices
                            WHERE language = ?
                            ORDER BY quality_rating DESC
                        """, (language,))
                    elif is_free is not None:
                        cursor.execute("""
                            SELECT id, voice_name, language, provider, voice_id, is_free, quality_rating
                            FROM tts_voices
                            WHERE is_free = ?
                            ORDER BY quality_rating DESC
                        """, (is_free,))
                    else:
                        cursor.execute("""
                            SELECT id, voice_name, language, provider, voice_id, is_free, quality_rating
                            FROM tts_voices
                            ORDER BY quality_rating DESC
                        """)
                    
                    results = []
                    for row in cursor.fetchall():
                        results.append({
                            "id": row[0],
                            "voice_name": row[1],
                            "language": row[2],
                            "provider": row[3],
                            "voice_id": row[4],
                            "is_free": bool(row[5]),
                            "quality_rating": row[6]
                        })
                    
                    return results
                    
            except Exception as e:
                self.logger.error(f"Erro ao obter vozes TTS: {e}")
                return []
    
    def backup_database(self, backup_path: str = None) -> str:
        """Faz backup do banco de dados"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"data/backup/super_agent_backup_{timestamp}.db"
        
        backup_path = Path(backup_path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.copy2(self.db_path, backup_path)
            self.logger.info(f"Backup criado: {backup_path}")
            return str(backup_path)
        except Exception as e:
            self.logger.error(f"Erro ao criar backup: {e}")
            raise
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do banco de dados"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    stats = {}
                    
                    # Contar registros em cada tabela
                    tables = ['rag_documents', 'system_memories', 'prompt_responses', 
                             'configurations', 'system_logs', 'projects', 'tasks', 'tts_voices']
                    
                    for table in tables:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        stats[f"{table}_count"] = count
                    
                    # Tamanho do banco
                    stats['database_size'] = self.db_path.stat().st_size
                    
                    # Última atualização
                    cursor.execute("SELECT MAX(created_at) FROM system_logs")
                    last_update = cursor.fetchone()[0]
                    stats['last_update'] = last_update
                    
                    return stats
                    
            except Exception as e:
                self.logger.error(f"Erro ao obter estatísticas: {e}")
                return {}
    
    def cleanup_old_logs(self, days: int = 30):
        """Remove logs antigos"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        DELETE FROM system_logs 
                        WHERE created_at < datetime('now', '-{} days')
                    """.format(days))
                    
                    deleted_count = cursor.rowcount
                    conn.commit()
                    
                    self.logger.info(f"Removidos {deleted_count} logs antigos")
                    return deleted_count
                    
            except Exception as e:
                self.logger.error(f"Erro ao limpar logs: {e}")
                return 0 