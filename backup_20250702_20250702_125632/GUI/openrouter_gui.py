#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OpenRouter GUI Module
--------------------
Interface gráfica para integração com OpenRouter API, incluindo
seleção de modelos, filtros por empresa e modelos gratuitos.

Autor: [Seu Nome]
Data: 01/07/2025
Versão: 0.1.0
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
from typing import Dict, Any, List
import logging
import json
import threading
from datetime import datetime
import sys
import os

# Adicionar o diretório pai ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.advanced_rag_system import AdvancedRAGSystem

logger = logging.getLogger("OPENROUTER_GUI")

class OpenRouterGUI:
    """Interface gráfica para OpenRouter e RAG"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = None
        self.rag_system = AdvancedRAGSystem()
        
        # Cache de modelos
        self.all_models = []
        self.models_by_company = {}
        self.free_models = []
        self.current_models = []
        
        # Variáveis de interface
        self.selected_model = tk.StringVar()
        self.selected_company = tk.StringVar()
        self.show_free_only = tk.BooleanVar()
        self.api_key_var = tk.StringVar()
        
        self.logger = logger
        
    def create_window(self):
        """Cria janela principal da interface OpenRouter"""
        if self.parent:
            self.window = tk.Toplevel(self.parent)
        else:
            self.window = tk.Tk()
            
        self.window.title("SUPER AGENT - OpenRouter & RAG")
        self.window.geometry("1200x800")
        self.window.configure(bg='#2b2b2b')
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#2b2b2b')
        style.configure('TLabel', background='#2b2b2b', foreground='white')
        style.configure('TButton', background='#404040', foreground='white')
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Cria widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook para abas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba OpenRouter
        self._create_openrouter_tab(notebook)
        
        # Aba RAG
        self._create_rag_tab(notebook)
    
    def _create_openrouter_tab(self, notebook):
        """Cria aba do OpenRouter"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="OpenRouter Models")
        
        # Frame superior - Configuração de API
        api_frame = ttk.LabelFrame(frame, text="Configuração da API", padding=10)
        api_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(api_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, padx=5)
        api_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, show="*", width=50)
        api_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Button(api_frame, text="Carregar Modelos", 
                  command=self._load_models_async).grid(row=0, column=2, padx=5)
        
        # Frame de filtros
        filter_frame = ttk.LabelFrame(frame, text="Filtros", padding=10)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Dropdown de empresas
        ttk.Label(filter_frame, text="Empresa:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.company_combo = ttk.Combobox(filter_frame, textvariable=self.selected_company, 
                                         width=30, state="readonly")
        self.company_combo.grid(row=0, column=1, padx=5, pady=2)
        
        # Checkbox modelos gratuitos
        free_check = ttk.Checkbutton(filter_frame, text="Apenas Modelos Gratuitos", 
                                    variable=self.show_free_only)
        free_check.grid(row=0, column=2, padx=10)
        
        # Frame de modelos
        models_frame = ttk.LabelFrame(frame, text="Modelos Disponíveis", padding=10)
        models_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Lista de modelos
        columns = ('Nome', 'Empresa', 'Contexto')
        self.models_tree = ttk.Treeview(models_frame, columns=columns, show='headings', height=15)
        
        # Configurar colunas
        for col in columns:
            self.models_tree.heading(col, text=col)
            self.models_tree.column(col, width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(models_frame, orient=tk.VERTICAL, command=self.models_tree.yview)
        self.models_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid dos componentes
        self.models_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        models_frame.grid_rowconfigure(0, weight=1)
        models_frame.grid_columnconfigure(0, weight=1)
    
    def _create_rag_tab(self, notebook):
        """Cria aba do sistema RAG"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="RAG System")
        
        # Frame de upload
        upload_frame = ttk.LabelFrame(frame, text="Adicionar Documentos", padding=10)
        upload_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(upload_frame, text="Selecionar Arquivos", 
                  command=self._upload_files).grid(row=0, column=0, padx=5)
        
        ttk.Button(upload_frame, text="Adicionar URL", 
                  command=self._add_url).grid(row=0, column=1, padx=5)
        
        # Frame de busca
        search_frame = ttk.LabelFrame(frame, text="Busca na Base de Conhecimento", padding=10)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Buscar:").grid(row=0, column=0, sticky=tk.W)
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Button(search_frame, text="Buscar", 
                  command=self._search_knowledge).grid(row=0, column=2, padx=5)
        
        # Lista de resultados
        results_frame = ttk.LabelFrame(frame, text="Resultados", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tree para resultados de busca
        search_columns = ('Documento', 'Categoria', 'Snippet')
        self.search_tree = ttk.Treeview(results_frame, columns=search_columns, show='headings', height=10)
        
        for col in search_columns:
            self.search_tree.heading(col, text=col)
            self.search_tree.column(col, width=250)
        
        search_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=search_scrollbar.set)
        
        self.search_tree.grid(row=0, column=0, sticky='nsew')
        search_scrollbar.grid(row=0, column=1, sticky='ns')
        
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
    
    def _load_models_async(self):
        """Carrega modelos da OpenRouter em thread separada"""
        def load_models():
            try:
                self._log("Carregando modelos da OpenRouter...")
                
                # Atualizar API key se fornecida
                if self.api_key_var.get():
                    self.rag_system.openrouter_client.api_key = self.api_key_var.get()
                
                result = self.rag_system.get_openrouter_models()
                
                if result["success"]:
                    self.all_models = result["models"]
                    self.models_by_company = result["models_by_company"]
                    self.free_models = result["free_models"]
                    
                    # Atualizar interface na thread principal
                    self.window.after(0, self._update_models_ui)
                    self._log(f"Carregados {len(self.all_models)} modelos")
                else:
                    self._log(f"Erro ao carregar modelos: {result.get('error', 'Erro desconhecido')}")
                    
            except Exception as e:
                self._log(f"Erro na thread de carregamento: {e}")
        
        threading.Thread(target=load_models, daemon=True).start()
    
    def _update_models_ui(self):
        """Atualiza interface com modelos carregados"""
        # Atualizar dropdown de empresas
        companies = ['Todas'] + sorted(self.models_by_company.keys())
        self.company_combo['values'] = companies
        self.selected_company.set('Todas')
        
        # Atualizar lista de modelos
        self._update_models_list()
    
    def _update_models_list(self):
        """Atualiza lista de modelos baseado nos filtros"""
        # Limpar lista atual
        for item in self.models_tree.get_children():
            self.models_tree.delete(item)
        
        # Determinar modelos a mostrar
        models_to_show = self.all_models
        
        # Filtrar por empresa
        if self.selected_company.get() and self.selected_company.get() != 'Todas':
            models_to_show = self.models_by_company.get(self.selected_company.get(), [])
        
        # Filtrar por modelos gratuitos
        if self.show_free_only.get():
            models_to_show = [model for model in models_to_show if model in self.free_models]
        
        # Adicionar modelos à lista
        for model in models_to_show:
            name = model.get('id', 'N/A')
            company = model.get('owned_by', 'N/A')
            context = str(model.get('context_length', 'N/A'))
            
            self.models_tree.insert('', 'end', values=(name, company, context))
    
    def _upload_files(self):
        """Upload de arquivos para RAG"""
        files = filedialog.askopenfilenames(
            title="Selecionar Documentos",
            filetypes=[
                ("Todos os suportados", "*.pdf *.txt *.md *.docx *.html *.json"),
                ("PDF", "*.pdf"),
                ("Texto", "*.txt"),
                ("Markdown", "*.md")
            ]
        )
        
        if files:
            self._log(f"Selecionados {len(files)} arquivos")
    
    def _add_url(self):
        """Adiciona URL à base de conhecimento"""
        url = simpledialog.askstring("URL", "Digite a URL do documento:")
        if url:
            self._log(f"URL adicionada: {url}")
    
    def _search_knowledge(self):
        """Busca na base de conhecimento"""
        query = self.search_entry.get()
        if query:
            self._log(f"Buscando: {query}")
    
    def _log(self, message: str):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        self.logger.info(message)
    
    def run(self):
        """Executa a interface"""
        self.create_window()
        if not self.parent:
            self.window.mainloop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = OpenRouterGUI()
    app.run() 