#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MÃ³dulo de Interface GrÃ¡fica
--------------------------
Interface grÃ¡fica para o SUPER_AGENT_MCP_DOCKER_N8N.

Autor: [Seu Nome]
Data: 01/07/2025
VersÃ£o: 0.1.0
"""

import os
import sys
import json
import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

logger = logging.getLogger("GUI_MODULE")

class SuperAgentGUI:
    """Interface grÃ¡fica para o SUPER_AGENT_MCP_DOCKER_N8N"""
    
    def __init__(self, root=None):
        self.logger = logger
        
        # ConfiguraÃ§Ã£o da janela principal
        if root is None:
            self.root = tk.Tk()
        else:
            self.root = root
            
        self.root.title("SUPER_AGENT_MCP_DOCKER_N8N")
        self.root.geometry("900x600")
        
        # ConfiguraÃ§Ã£o de estilo
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Tema mais moderno
        
        # VariÃ¡veis
        self.mcp_configs = {}
        self.current_ide = tk.StringVar(value="cursor")
        
        # Criar interface
        self._create_menu()
        self._create_notebook()
        
        self.logger.info("Interface grÃ¡fica inicializada")
    
    def _create_menu(self):
        """Cria o menu principal"""
        menu_bar = tk.Menu(self.root)
        
        # Menu Arquivo
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Carregar ConfiguraÃ§Ã£o", command=self._load_config)
        file_menu.add_command(label="Salvar ConfiguraÃ§Ã£o", command=self._save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        menu_bar.add_cascade(label="Arquivo", menu=file_menu)
        
        # Menu Ferramentas
        tools_menu = tk.Menu(menu_bar, tearoff=0)
        tools_menu.add_command(label="Detectar MCPs", command=self._detect_mcps)
        tools_menu.add_command(label="Verificar Docker", command=self._check_docker)
        tools_menu.add_command(label="Iniciar N8N", command=self._start_n8n)
        menu_bar.add_cascade(label="Ferramentas", menu=tools_menu)
        
        # Menu Ajuda
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Sobre", command=self._show_about)
        help_menu.add_command(label="DocumentaÃ§Ã£o", command=self._show_docs)
        menu_bar.add_cascade(label="Ajuda", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def _create_notebook(self):
        """Cria o notebook com abas"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Aba de MCPs
        self.mcp_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.mcp_frame, text="MCPs")
        self._create_mcp_tab()
        
        # Aba de Docker
        self.docker_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.docker_frame, text="Docker")
        self._create_docker_tab()
        
        # Aba de RAG
        self.rag_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.rag_frame, text="RAG")
        self._create_rag_tab()
        
        # Aba de ConfiguraÃ§Ãµes
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="ConfiguraÃ§Ãµes")
        self._create_settings_tab()
    
    def _create_mcp_tab(self):
        """Cria a aba de MCPs"""
        # Frame superior para seleÃ§Ã£o de IDE
        top_frame = ttk.Frame(self.mcp_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(top_frame, text="IDE:").pack(side=tk.LEFT, padx=5)
        ide_combo = ttk.Combobox(top_frame, textvariable=self.current_ide, 
                                 values=["cline", "roocline", "windsurf", "cursor"])
        ide_combo.pack(side=tk.LEFT, padx=5)
        ide_combo.bind("<<ComboboxSelected>>", self._on_ide_selected)
        
        ttk.Button(top_frame, text="Detectar MCPs", command=self._detect_mcps).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Compartilhar MCPs", command=self._share_mcps).pack(side=tk.LEFT, padx=5)
        
        # Frame para lista de MCPs
        list_frame = ttk.LabelFrame(self.mcp_frame, text="MCPs DisponÃ­veis")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview para mostrar MCPs
        columns = ("nome", "caminho", "status")
        self.mcp_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        self.mcp_tree.heading("nome", text="Nome")
        self.mcp_tree.heading("caminho", text="Caminho")
        self.mcp_tree.heading("status", text="Status")
        
        self.mcp_tree.column("nome", width=150)
        self.mcp_tree.column("caminho", width=400)
        self.mcp_tree.column("status", width=100)
        
        self.mcp_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.mcp_tree.yview)
        self.mcp_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_docker_tab(self):
        """Cria a aba de Docker"""
        # Frame superior para aÃ§Ãµes
        top_frame = ttk.Frame(self.docker_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(top_frame, text="Verificar Docker", command=self._check_docker).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Listar ContÃªineres", command=self._list_containers).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Iniciar N8N", command=self._start_n8n).pack(side=tk.LEFT, padx=5)
        
        # Frame para lista de contÃªineres
        list_frame = ttk.LabelFrame(self.docker_frame, text="ContÃªineres Docker")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview para mostrar contÃªineres
        columns = ("id", "nome", "status", "portas")
        self.docker_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        self.docker_tree.heading("id", text="ID")
        self.docker_tree.heading("nome", text="Nome")
        self.docker_tree.heading("status", text="Status")
        self.docker_tree.heading("portas", text="Portas")
        
        self.docker_tree.column("id", width=100)
        self.docker_tree.column("nome", width=150)
        self.docker_tree.column("status", width=200)
        self.docker_tree.column("portas", width=300)
        
        self.docker_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.docker_tree.yview)
        self.docker_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_rag_tab(self):
        """Cria a aba de RAG"""
        # Frame superior para aÃ§Ãµes
        top_frame = ttk.Frame(self.rag_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(top_frame, text="Carregar DiretÃ³rio", command=self._load_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Carregar GitHub", command=self._load_github).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Salvar Documentos", command=self._save_documents).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Carregar Documentos", command=self._load_documents).pack(side=tk.LEFT, padx=5)
        
        # Frame para entrada de GitHub
        github_frame = ttk.LabelFrame(self.rag_frame, text="RepositÃ³rio GitHub")
        github_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(github_frame, text="URL:").pack(side=tk.LEFT, padx=5)
        self.github_url = tk.StringVar()
        ttk.Entry(github_frame, textvariable=self.github_url, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Label(github_frame, text="Branch:").pack(side=tk.LEFT, padx=5)
        self.github_branch = tk.StringVar(value="main")
        ttk.Entry(github_frame, textvariable=self.github_branch, width=10).pack(side=tk.LEFT, padx=5)
        
        # Frame para lista de documentos
        list_frame = ttk.LabelFrame(self.rag_frame, text="Documentos Carregados")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview para mostrar documentos
        columns = ("nome", "tipo", "fonte", "tamanho")
        self.doc_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        self.doc_tree.heading("nome", text="Nome")
        self.doc_tree.heading("tipo", text="Tipo")
        self.doc_tree.heading("fonte", text="Fonte")
        self.doc_tree.heading("tamanho", text="Tamanho")
        
        self.doc_tree.column("nome", width=200)
        self.doc_tree.column("tipo", width=100)
        self.doc_tree.column("fonte", width=300)
        self.doc_tree.column("tamanho", width=100)
        
        self.doc_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.doc_tree.yview)
        self.doc_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_settings_tab(self):
        """Cria a aba de configuraÃ§Ãµes"""
        # Frame para configuraÃ§Ãµes gerais
        general_frame = ttk.LabelFrame(self.settings_frame, text="ConfiguraÃ§Ãµes Gerais")
        general_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # DiretÃ³rio de logs
        log_frame = ttk.Frame(general_frame)
        log_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(log_frame, text="DiretÃ³rio de Logs:").pack(side=tk.LEFT, padx=5)
        self.log_dir = tk.StringVar(value="logs")
        ttk.Entry(log_frame, textvariable=self.log_dir, width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(log_frame, text="...", width=3, command=self._select_log_dir).pack(side=tk.LEFT, padx=5)
        
        # NÃ­vel de log
        log_level_frame = ttk.Frame(general_frame)
        log_level_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(log_level_frame, text="NÃ­vel de Log:").pack(side=tk.LEFT, padx=5)
        self.log_level = tk.StringVar(value="INFO")
        ttk.Combobox(log_level_frame, textvariable=self.log_level, 
                     values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]).pack(side=tk.LEFT, padx=5)
        
        # Frame para configuraÃ§Ãµes de N8N
        n8n_frame = ttk.LabelFrame(self.settings_frame, text="ConfiguraÃ§Ãµes do N8N")
        n8n_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Porta do N8N
        port_frame = ttk.Frame(n8n_frame)
        port_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(port_frame, text="Porta:").pack(side=tk.LEFT, padx=5)
        self.n8n_port = tk.StringVar(value="5678")
        ttk.Entry(port_frame, textvariable=self.n8n_port, width=10).pack(side=tk.LEFT, padx=5)
        
        # DiretÃ³rio de dados do N8N
        data_frame = ttk.Frame(n8n_frame)
        data_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(data_frame, text="DiretÃ³rio de Dados:").pack(side=tk.LEFT, padx=5)
        self.n8n_data_dir = tk.StringVar(value="./n8n_data")
        ttk.Entry(data_frame, textvariable=self.n8n_data_dir, width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(data_frame, text="...", width=3, command=self._select_n8n_data_dir).pack(side=tk.LEFT, padx=5)
        
        # BotÃµes de aÃ§Ã£o
        button_frame = ttk.Frame(self.settings_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=20)
        ttk.Button(button_frame, text="Salvar ConfiguraÃ§Ãµes", command=self._save_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Carregar ConfiguraÃ§Ãµes", command=self._load_settings).pack(side=tk.RIGHT, padx=5)
    
    # MÃ©todos de callback
    def _load_config(self):
        """Carrega uma configuraÃ§Ã£o de arquivo"""
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo de configuraÃ§Ã£o",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.logger.info(f"ConfiguraÃ§Ã£o carregada de {file_path}")
                messagebox.showinfo("Sucesso", "ConfiguraÃ§Ã£o carregada com sucesso!")
            except Exception as e:
                self.logger.error(f"Erro ao carregar configuraÃ§Ã£o: {e}")
                messagebox.showerror("Erro", f"Erro ao carregar configuraÃ§Ã£o: {e}")
    
    def _save_config(self):
        """Salva a configuraÃ§Ã£o em um arquivo"""
        file_path = filedialog.asksaveasfilename(
            title="Salvar arquivo de configuraÃ§Ã£o",
            defaultextension=".json",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )
        if file_path:
            try:
                config = {
                    "log_dir": self.log_dir.get(),
                    "log_level": self.log_level.get(),
                    "n8n_port": self.n8n_port.get(),
                    "n8n_data_dir": self.n8n_data_dir.get()
                }
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                self.logger.info(f"ConfiguraÃ§Ã£o salva em {file_path}")
                messagebox.showinfo("Sucesso", "ConfiguraÃ§Ã£o salva com sucesso!")
            except Exception as e:
                self.logger.error(f"Erro ao salvar configuraÃ§Ã£o: {e}")
                messagebox.showerror("Erro", f"Erro ao salvar configuraÃ§Ã£o: {e}")
    
    def _detect_mcps(self):
        """Detecta MCPs instalados"""
        messagebox.showinfo("InformaÃ§Ã£o", "Detectando MCPs instalados...")
        # Implementar lÃ³gica para detectar MCPs
    
    def _check_docker(self):
        """Verifica se o Docker estÃ¡ instalado"""
        messagebox.showinfo("InformaÃ§Ã£o", "Verificando instalaÃ§Ã£o do Docker...")
        # Implementar lÃ³gica para verificar Docker
    
    def _start_n8n(self):
        """Inicia o contÃªiner N8N"""
        port = self.n8n_port.get()
        data_dir = self.n8n_data_dir.get()
        messagebox.showinfo("InformaÃ§Ã£o", f"Iniciando N8N na porta {port}...")
        # Implementar lÃ³gica para iniciar N8N
    
    def _on_ide_selected(self, event):
        """Callback quando uma IDE Ã© selecionada"""
        ide = self.current_ide.get()
        self.logger.info(f"IDE selecionada: {ide}")
        # Atualizar lista de MCPs para a IDE selecionada
    
    def _share_mcps(self):
        """Compartilha MCPs entre IDEs"""
        messagebox.showinfo("InformaÃ§Ã£o", "Compartilhando MCPs entre IDEs...")
        # Implementar lÃ³gica para compartilhar MCPs
    
    def _list_containers(self):
        """Lista os contÃªineres Docker em execuÃ§Ã£o"""
        messagebox.showinfo("InformaÃ§Ã£o", "Listando contÃªineres Docker...")
        # Implementar lÃ³gica para listar contÃªineres
    
    def _load_directory(self):
        """Carrega documentos de um diretÃ³rio"""
        directory = filedialog.askdirectory(title="Selecionar diretÃ³rio de documentos")
        if directory:
            messagebox.showinfo("InformaÃ§Ã£o", f"Carregando documentos de {directory}...")
            # Implementar lÃ³gica para carregar documentos
    
    def _load_github(self):
        """Carrega documentos de um repositÃ³rio GitHub"""
        url = self.github_url.get()
        branch = self.github_branch.get()
        if url:
            messagebox.showinfo("InformaÃ§Ã£o", f"Carregando documentos de {url} (branch: {branch})...")
            # Implementar lÃ³gica para carregar documentos do GitHub
        else:
            messagebox.showerror("Erro", "URL do repositÃ³rio GitHub nÃ£o especificada!")
    
    def _save_documents(self):
        """Salva os documentos carregados"""
        messagebox.showinfo("InformaÃ§Ã£o", "Salvando documentos...")
        # Implementar lÃ³gica para salvar documentos
    
    def _load_documents(self):
        """Carrega documentos salvos anteriormente"""
        messagebox.showinfo("InformaÃ§Ã£o", "Carregando documentos salvos...")
        # Implementar lÃ³gica para carregar documentos salvos
    
    def _select_log_dir(self):
        """Seleciona o diretÃ³rio de logs"""
        directory = filedialog.askdirectory(title="Selecionar diretÃ³rio de logs")
        if directory:
            self.log_dir.set(directory)
    
    def _select_n8n_data_dir(self):
        """Seleciona o diretÃ³rio de dados do N8N"""
        directory = filedialog.askdirectory(title="Selecionar diretÃ³rio de dados do N8N")
        if directory:
            self.n8n_data_dir.set(directory)
    
    def _save_settings(self):
        """Salva as configuraÃ§Ãµes"""
        messagebox.showinfo("InformaÃ§Ã£o", "Salvando configuraÃ§Ãµes...")
        # Implementar lÃ³gica para salvar configuraÃ§Ãµes
    
    def _load_settings(self):
        """Carrega as configuraÃ§Ãµes"""
        messagebox.showinfo("InformaÃ§Ã£o", "Carregando configuraÃ§Ãµes...")
        # Implementar lÃ³gica para carregar configuraÃ§Ãµes
    
    def _show_about(self):
        """Mostra informaÃ§Ãµes sobre o aplicativo"""
        messagebox.showinfo(
            "Sobre",
            "SUPER_AGENT_MCP_DOCKER_N8N\n"
            "VersÃ£o 0.1.0\n\n"
            "Agente especializado para integrar MCPs de diferentes IDEs, "
            "coordenar comandos, iniciar serviÃ§os e analisar prompts."
        )
    
    def _show_docs(self):
        """Mostra a documentaÃ§Ã£o"""
        messagebox.showinfo("DocumentaÃ§Ã£o", "Abrindo documentaÃ§Ã£o...")
        # Implementar lÃ³gica para abrir documentaÃ§Ã£o
    
    def run(self):
        """Executa o loop principal da interface grÃ¡fica"""
        self.root.mainloop()


if __name__ == "__main__":
    # ConfiguraÃ§Ã£o de logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Iniciar interface grÃ¡fica
    app = SuperAgentGUI()
    app.run() 
