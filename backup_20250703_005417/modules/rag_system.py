#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema RAG (Retrieval Augmented Generation)
-------------------------------------------
MÃ³dulo responsÃ¡vel pelo sistema RAG para carregar documentos e dados
de repositÃ³rios GitHub.

Autor: [Seu Nome]
Data: 01/07/2025
VersÃ£o: 0.1.0
"""

import os
import json
import logging
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger("RAG_SYSTEM")

class Document:
    """Classe para representar um documento no sistema RAG"""
    
    def __init__(self, content: str, metadata: Dict[str, Any] = None):
        self.content = content
        self.metadata = metadata or {}
        
    def __str__(self):
        return f"Document(metadata={self.metadata})"
    
    def to_dict(self):
        return {
            "content": self.content,
            "metadata": self.metadata
        }


class RAGSystem:
    """Sistema RAG para carregar e processar documentos"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.documents: List[Document] = []
        self.logger = logger
        self.index = None
        
        # Criar diretÃ³rio de dados se nÃ£o existir
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_document(self, file_path: str) -> Optional[Document]:
        """Carrega um documento a partir de um arquivo"""
        try:
            file_path = Path(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = {
                "source": str(file_path),
                "filename": file_path.name,
                "extension": file_path.suffix,
                "created_at": os.path.getctime(file_path),
                "modified_at": os.path.getmtime(file_path)
            }
            
            doc = Document(content, metadata)
            self.documents.append(doc)
            self.logger.info(f"Documento carregado: {file_path.name}")
            return doc
        except Exception as e:
            self.logger.error(f"Erro ao carregar documento {file_path}: {e}")
            return None
    
    def load_documents_from_directory(self, directory: str, extensions: List[str] = None) -> List[Document]:
        """Carrega documentos de um diretÃ³rio"""
        loaded_docs = []
        directory = Path(directory)
        
        if not directory.exists():
            self.logger.error(f"DiretÃ³rio nÃ£o encontrado: {directory}")
            return loaded_docs
        
        extensions = extensions or [".txt", ".md", ".py", ".js", ".html", ".css", ".json"]
        
        try:
            for file_path in directory.glob("**/*"):
                if file_path.is_file() and (not extensions or file_path.suffix in extensions):
                    doc = self.load_document(file_path)
                    if doc:
                        loaded_docs.append(doc)
            
            self.logger.info(f"Documentos carregados do diretÃ³rio {directory}: {len(loaded_docs)}")
            return loaded_docs
        except Exception as e:
            self.logger.error(f"Erro ao carregar documentos do diretÃ³rio {directory}: {e}")
            return loaded_docs
    
    def load_from_github(self, repo_url: str, branch: str = "main") -> List[Document]:
        """Carrega documentos de um repositÃ³rio GitHub"""
        loaded_docs = []
        
        # Extrair owner/repo do URL
        parts = repo_url.rstrip("/").split("/")
        if "github.com" not in repo_url or len(parts) < 5:
            self.logger.error(f"URL de repositÃ³rio GitHub invÃ¡lido: {repo_url}")
            return loaded_docs
        
        owner, repo = parts[-2], parts[-1]
        api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            
            data = response.json()
            files = [item for item in data.get("tree", []) if item["type"] == "blob"]
            
            for file_info in files:
                file_path = file_info["path"]
                if any(file_path.endswith(ext) for ext in [".md", ".txt", ".py", ".js"]):
                    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
                    file_response = requests.get(raw_url)
                    
                    if file_response.status_code == 200:
                        content = file_response.text
                        metadata = {
                            "source": raw_url,
                            "repo": f"{owner}/{repo}",
                            "branch": branch,
                            "path": file_path,
                            "sha": file_info["sha"]
                        }
                        
                        doc = Document(content, metadata)
                        self.documents.append(doc)
                        loaded_docs.append(doc)
                        self.logger.info(f"Documento carregado do GitHub: {file_path}")
            
            self.logger.info(f"Documentos carregados do repositÃ³rio {owner}/{repo}: {len(loaded_docs)}")
            return loaded_docs
        except Exception as e:
            self.logger.error(f"Erro ao carregar documentos do GitHub {repo_url}: {e}")
            return loaded_docs
    
    def save_documents(self, output_file: str = "documents.json"):
        """Salva os documentos carregados em um arquivo JSON"""
        try:
            output_path = self.data_dir / output_file
            docs_data = [doc.to_dict() for doc in self.documents]
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(docs_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Documentos salvos em {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar documentos: {e}")
            return False
    
    def load_saved_documents(self, input_file: str = "documents.json"):
        """Carrega documentos salvos anteriormente"""
        try:
            input_path = self.data_dir / input_file
            
            if not input_path.exists():
                self.logger.warning(f"Arquivo de documentos nÃ£o encontrado: {input_path}")
                return False
            
            with open(input_path, 'r', encoding='utf-8') as f:
                docs_data = json.load(f)
            
            self.documents = [Document(doc["content"], doc["metadata"]) for doc in docs_data]
            self.logger.info(f"Documentos carregados de {input_path}: {len(self.documents)}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao carregar documentos salvos: {e}")
            return False


if __name__ == "__main__":
    # Teste bÃ¡sico
    logging.basicConfig(level=logging.INFO)
    rag = RAGSystem()
    # Exemplo de uso
    # rag.load_from_github("https://github.com/username/repo")
    # rag.save_documents() 
