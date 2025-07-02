#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de Interface Gráfica - SUPER_AGENT_MCP_DOCKER_N8N
--------------------------------------------------------
Interface gráfica completa com:
- Área de prompt funcional
- Integração OpenRouter
- Chat direto com agentes
- Geração de PRDs e tasks
- Integração N8N e Docker
- Sistema RAG integrado

Autor: [Seu Nome]
Data: 01/07/2025
Versão: 0.1.0
"""

import os
import sys
import json
import logging
import asyncio
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger("GUI_MODULE")

class SuperAgentGUI:
    """Interface gráfica completa para o SUPER_AGENT_MCP_DOCKER_N8N"""
    
    def __init__(self, root=None):
        self.logger = logger
        
        # Configuração da janela principal
        if root is None:
            self.root = tk.Tk()
        else:
            self.root = root
            
        self.root.title("SUPER_AGENT_MCP_DOCKER_N8N - Agente Inteligente")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Configuração de estilo
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Variáveis
        self.current_agent_type = tk.StringVar(value="chat")
        self.selected_model = tk.StringVar()
        self.chat_history = []
        self.rag_context = []
        
        # Referências aos módulos (serão definidas pelo main.py)
        self.agent = None
        self.openrouter_manager = None
        self.rag_system = None
        self.mcp_manager = None
        self.docker_manager = None
        self.fe_agent = None
        self.voice_module = None
        
        # Criar interface
        self._create_menu()
        self._create_main_interface()
        
        self.logger.info("Interface gráfica inicializada")
    
    def _create_menu(self):
        """Cria o menu principal"""
        menu_bar = tk.Menu(self.root)
        
        # Menu Arquivo
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Carregar Configuração", command=self._load_config)
        file_menu.add_command(label="Salvar Configuração", command=self._save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exportar Chat", command=self._export_chat)
        file_menu.add_command(label="Sair", command=self.root.quit)
        menu_bar.add_cascade(label="Arquivo", menu=file_menu)
        
        # Menu Agentes
        agents_menu = tk.Menu(menu_bar, tearoff=0)
        agents_menu.add_command(label="Chat Direto", command=lambda: self._on_agent_changed("chat"))
        agents_menu.add_command(label="PRD Generator", command=lambda: self._on_agent_changed("prompt"))
        agents_menu.add_command(label="N8N Workflow", command=lambda: self._on_agent_changed("n8n"))
        agents_menu.add_command(label="Deploy Manager", command=lambda: self._on_agent_changed("deploy"))
        menu_bar.add_cascade(label="Agentes", menu=agents_menu)
        
        # Menu Ferramentas
        tools_menu = tk.Menu(menu_bar, tearoff=0)
        tools_menu.add_command(label="Detectar MCPs", command=self._detect_mcps)
        tools_menu.add_command(label="Verificar Docker", command=self._check_docker)
        tools_menu.add_command(label="Iniciar N8N", command=self._start_n8n)
        tools_menu.add_command(label="Carregar RAG", command=self._load_rag_docs)
        menu_bar.add_cascade(label="Ferramentas", menu=tools_menu)
        
        # Menu Ajuda
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Sobre", command=self._show_about)
        help_menu.add_command(label="Documentação", command=self._show_docs)
        menu_bar.add_cascade(label="Ajuda", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def _create_main_interface(self):
        """Cria a interface principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame superior - Controles
        self._create_control_panel(main_frame)
        
        # Frame central - Chat e Prompt
        self._create_chat_panel(main_frame)
        
        # Frame inferior - Status e Logs
        self._create_status_panel(main_frame)
    
    def _create_control_panel(self, parent):
        """Cria painel de controles superior"""
        control_frame = ttk.LabelFrame(parent, text="Controles do Agente")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame superior - Microfone e status de voz
        voice_frame = ttk.Frame(control_frame)
        voice_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Botão de microfone (favicon)
        self.mic_button = tk.Button(
            voice_frame, 
            text="🎤", 
            font=("Arial", 16),
            width=3,
            command=self._toggle_voice_listening,
            relief=tk.RAISED,
            bg="#e74c3c",
            fg="white"
        )
        self.mic_button.pack(side=tk.LEFT, padx=5)
        
        # Status de voz
        self.voice_status_label = ttk.Label(voice_frame, text="Voz: Desativada")
        self.voice_status_label.pack(side=tk.LEFT, padx=10)
        
        # Wake word info
        wake_info = ttk.Label(voice_frame, text="Wake words: 'assistente', 'super agent', 'hey'")
        wake_info.pack(side=tk.LEFT, padx=10)
        
        # Separador
        separator = ttk.Separator(control_frame, orient='horizontal')
        separator.pack(fill=tk.X, padx=10, pady=5)
        
        # Frame para seleção de agente
        agent_frame = ttk.Frame(control_frame)
        agent_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(agent_frame, text="Tipo de Agente:").pack(side=tk.LEFT, padx=5)
        
        agent_types = [
            ("Chat Direto", "chat"),
            ("PRD Generator", "prompt"), 
            ("N8N Workflow", "n8n"),
            ("Deploy Manager", "deploy")
        ]
        
        for name, value in agent_types:
            ttk.Radiobutton(agent_frame, text=name, variable=self.current_agent_type, 
                           value=value, command=self._on_agent_changed).pack(side=tk.LEFT, padx=5)
        
        # Frame para seleção de modelo
        model_frame = ttk.Frame(control_frame)
        model_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(model_frame, text="Modelo OpenRouter:").pack(side=tk.LEFT, padx=5)
        
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.selected_model, width=40)
        self.model_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(model_frame, text="Carregar Modelos", command=self._load_models).pack(side=tk.LEFT, padx=5)
        ttk.Button(model_frame, text="Filtrar Gratuitos", command=self._filter_free_models).pack(side=tk.LEFT, padx=5)
        
        # Frame para ações rápidas
        actions_frame = ttk.Frame(control_frame)
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(actions_frame, text="Gerar PRD", command=self._generate_prd).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Gerar Tasks", command=self._generate_tasks).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Gerar N8N", command=self._generate_n8n).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Gerar Deploy", command=self._generate_deploy).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Limpar Chat", command=self._clear_chat).pack(side=tk.LEFT, padx=5)
    
    def _create_chat_panel(self, parent):
        """Cria painel de chat e prompt"""
        chat_frame = ttk.Frame(parent)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Frame esquerdo - Chat
        left_frame = ttk.Frame(chat_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Área de chat
        chat_label = ttk.Label(left_frame, text="Chat com Agente")
        chat_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.chat_text = scrolledtext.ScrolledText(left_frame, height=20, wrap=tk.WORD)
        self.chat_text.pack(fill=tk.BOTH, expand=True)
        
        # Frame direito - Prompt e Contexto
        right_frame = ttk.Frame(chat_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Área de prompt
        prompt_label = ttk.Label(right_frame, text="Prompt/Descrição do Projeto")
        prompt_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.prompt_text = scrolledtext.ScrolledText(right_frame, height=10, wrap=tk.WORD)
        self.prompt_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Botões de ação
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Enviar", command=self._send_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Buscar RAG", command=self._search_rag).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Salvar Memória", command=self._save_memory).pack(side=tk.LEFT, padx=5)
        
        # Área de contexto RAG
        context_label = ttk.Label(right_frame, text="Contexto RAG")
        context_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.context_text = scrolledtext.ScrolledText(right_frame, height=8, wrap=tk.WORD)
        self.context_text.pack(fill=tk.BOTH, expand=True)
    
    def _create_status_panel(self, parent):
        """Cria painel de status inferior"""
        status_frame = ttk.LabelFrame(parent, text="Status e Logs")
        status_frame.pack(fill=tk.X)
        
        # Frame para status
        status_info_frame = ttk.Frame(status_frame)
        status_info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = ttk.Label(status_info_frame, text="Status: Pronto")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.model_info_label = ttk.Label(status_info_frame, text="Modelo: Nenhum selecionado")
        self.model_info_label.pack(side=tk.LEFT, padx=20)
        
        self.rag_info_label = ttk.Label(status_info_frame, text="RAG: 0 documentos")
        self.rag_info_label.pack(side=tk.LEFT, padx=20)
        
        # Área de logs
        log_label = ttk.Label(status_frame, text="Logs")
        log_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(status_frame, height=6, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    def _on_agent_changed(self, agent_type=None):
        """Callback quando o tipo de agente muda"""
        if agent_type:
            self.current_agent_type.set(agent_type)
        
        agent_type = self.current_agent_type.get()
        agent_info = self._get_agent_info(agent_type)
        
        self.log_text.insert(tk.END, f"Agente alterado para: {agent_info['name']}\n")
        self.log_text.see(tk.END)
        
        # Atualizar prompt de exemplo
        self.prompt_text.delete(1.0, tk.END)
        self.prompt_text.insert(1.0, agent_info.get('example_prompt', ''))
    
    def _toggle_voice_listening(self):
        """Alterna entre ativar e desativar a escuta de voz"""
        if not self.voice_module:
            messagebox.showwarning("Aviso", "Módulo de voz não inicializado")
            return
        
        try:
            is_listening = self.voice_module.toggle_listening()
            
            if is_listening:
                self.mic_button.config(bg="#27ae60", text="🔴")  # Verde quando ativo
                self.voice_status_label.config(text="Voz: Ativada - Diga 'assistente'")
                self.log_text.insert(tk.END, "Escuta de voz ativada\n")
            else:
                self.mic_button.config(bg="#e74c3c", text="🎤")  # Vermelho quando inativo
                self.voice_status_label.config(text="Voz: Desativada")
                self.log_text.insert(tk.END, "Escuta de voz desativada\n")
            
            self.log_text.see(tk.END)
            
        except Exception as e:
            self.log_text.insert(tk.END, f"Erro ao alternar voz: {e}\n")
            self.log_text.see(tk.END)
    
    def _get_agent_info(self, agent_type: str) -> Dict[str, str]:
        """Obtém informações do agente"""
        agent_info = {
            "chat": {
                "name": "Chat Direto",
                "description": "Chat direto com acesso à web",
                "example_prompt": "Olá! Como posso ajudar você hoje com desenvolvimento de software?"
            },
            "prompt": {
                "name": "PRD Generator", 
                "description": "Cria PRDs com técnicas modernas",
                "example_prompt": "Crie um PRD para um sistema de e-commerce com autenticação, pagamentos e gestão de produtos."
            },
            "n8n": {
                "name": "N8N Workflow Generator",
                "description": "Cria workflows N8N",
                "example_prompt": "Crie um workflow N8N para sincronizar dados entre Google Sheets e uma API REST."
            },
            "deploy": {
                "name": "Deploy Manager",
                "description": "Scripts de deploy",
                "example_prompt": "Crie um script de deploy para DigitalOcean para uma aplicação Node.js com Docker."
            }
        }
        return agent_info.get(agent_type, agent_info["chat"])
    
    async def _load_models_async(self):
        """Carrega modelos OpenRouter de forma assíncrona"""
        if not self.openrouter_manager:
            self.log_text.insert(tk.END, "Erro: OpenRouter Manager não inicializado\n")
            return
        
        try:
            models = await self.openrouter_manager.get_models()
            model_names = [f"{m.name} ({m.company})" for m in models]
            
            # Atualizar combobox na thread principal
            self.root.after(0, lambda: self._update_model_combo(model_names, models))
            
        except Exception as e:
            self.log_text.insert(tk.END, f"Erro ao carregar modelos: {e}\n")
    
    def _load_models(self):
        """Carrega modelos OpenRouter"""
        self.log_text.insert(tk.END, "Carregando modelos OpenRouter...\n")
        self.log_text.see(tk.END)
        
        # Executar de forma assíncrona
        asyncio.run_coroutine_threadsafe(self._load_models_async(), asyncio.new_event_loop())
    
    def _update_model_combo(self, model_names: List[str], models: List):
        """Atualiza combobox de modelos"""
        self.model_combo['values'] = model_names
        if model_names:
            self.model_combo.set(model_names[0])
        
        # Armazenar referência aos modelos
        self.available_models = models
        
        self.log_text.insert(tk.END, f"Carregados {len(models)} modelos\n")
        self.log_text.see(tk.END)
    
    def _filter_free_models(self):
        """Filtra apenas modelos gratuitos"""
        if not hasattr(self, 'available_models'):
            messagebox.showwarning("Aviso", "Carregue os modelos primeiro")
            return
        
        free_models = [m for m in self.available_models if m.is_free]
        free_names = [f"{m.name} ({m.company})" for m in free_models]
        
        self.model_combo['values'] = free_names
        if free_names:
            self.model_combo.set(free_names[0])
        
        self.log_text.insert(tk.END, f"Filtrados {len(free_models)} modelos gratuitos\n")
        self.log_text.see(tk.END)
    
    async def _send_message_async(self, message: str, agent_type: str, model_id: str):
        """Envia mensagem de forma assíncrona"""
        if not self.openrouter_manager:
            return {"error": "OpenRouter Manager não inicializado"}
        
        try:
            # Buscar contexto RAG se disponível
            context_docs = []
            if self.rag_system and self.rag_context:
                context_docs = self.rag_context
            
            # Preparar mensagens
            messages = [{"role": "user", "content": message}]
            
            # Enviar para OpenRouter
            result = await self.openrouter_manager.chat_with_model(
                model_id, messages, agent_type, context_docs
            )
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def _send_message(self):
        """Envia mensagem para o agente"""
        message = self.prompt_text.get(1.0, tk.END).strip()
        if not message:
            messagebox.showwarning("Aviso", "Digite uma mensagem")
            return
        
        agent_type = self.current_agent_type.get()
        model_name = self.selected_model.get()
        
        if not model_name:
            messagebox.showwarning("Aviso", "Selecione um modelo")
            return
        
        # Encontrar modelo selecionado
        model_id = None
        for model in getattr(self, 'available_models', []):
            if f"{model.name} ({model.company})" == model_name:
                model_id = model.id
                break
        
        if not model_id:
            messagebox.showerror("Erro", "Modelo não encontrado")
            return
        
        # Adicionar mensagem ao chat
        self.chat_text.insert(tk.END, f"\nVocê: {message}\n")
        self.chat_text.see(tk.END)
        
        # Limpar prompt
        self.prompt_text.delete(1.0, tk.END)
        
        # Mostrar status
        self.status_label.config(text="Status: Processando...")
        self.log_text.insert(tk.END, f"Enviando mensagem para {model_name}...\n")
        self.log_text.see(tk.END)
        
        # Executar de forma assíncrona
        def send_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._send_message_async(message, agent_type, model_id))
            loop.close()
            
            # Atualizar interface na thread principal
            self.root.after(0, lambda: self._handle_response(result, message, agent_type, model_id))
        
        threading.Thread(target=send_async, daemon=True).start()
    
    def _handle_response(self, result: Dict, message: str, agent_type: str, model_id: str):
        """Processa resposta do agente"""
        self.status_label.config(text="Status: Pronto")
        
        if "error" in result:
            self.chat_text.insert(tk.END, f"\nErro: {result['error']}\n")
            self.log_text.insert(tk.END, f"Erro na resposta: {result['error']}\n")
        else:
            response = result.get("response", "")
            self.chat_text.insert(tk.END, f"\nAgente: {response}\n")
            
            # Salvar na memória
            if self.openrouter_manager:
                self.openrouter_manager.save_memory(message, response, agent_type, model_id, self.rag_context)
            
            self.log_text.insert(tk.END, f"Resposta recebida com sucesso\n")
        
        self.chat_text.see(tk.END)
        self.log_text.see(tk.END)
    
    def _generate_prd(self):
        """Gera PRD baseado no prompt"""
        message = self.prompt_text.get(1.0, tk.END).strip()
        if not message:
            messagebox.showwarning("Aviso", "Digite a descrição do projeto")
            return
        
        # Mudar para agente PRD
        self.current_agent_type.set("prompt")
        self._on_agent_changed()
        
        # Enviar mensagem
        self._send_message()
    
    def _generate_tasks(self):
        """Gera tasks baseado no PRD"""
        # Buscar último PRD no chat
        chat_content = self.chat_text.get(1.0, tk.END)
        if "PRD" not in chat_content:
            messagebox.showwarning("Aviso", "Gere um PRD primeiro")
            return
        
        # Extrair PRD do chat (implementação simplificada)
        self.prompt_text.delete(1.0, tk.END)
        self.prompt_text.insert(1.0, "Gere um arquivo de tasks detalhado baseado no PRD acima")
        
        self._send_message()
    
    def _generate_n8n(self):
        """Gera workflow N8N"""
        message = self.prompt_text.get(1.0, tk.END).strip()
        if not message:
            messagebox.showwarning("Aviso", "Digite a descrição do workflow")
            return
        
        # Mudar para agente N8N
        self.current_agent_type.set("n8n")
        self._on_agent_changed()
        
        # Enviar mensagem
        self._send_message()
    
    def _generate_deploy(self):
        """Gera script de deploy"""
        message = self.prompt_text.get(1.0, tk.END).strip()
        if not message:
            messagebox.showwarning("Aviso", "Digite informações do projeto e plataforma")
            return
        
        # Mudar para agente Deploy
        self.current_agent_type.set("deploy")
        self._on_agent_changed()
        
        # Enviar mensagem
        self._send_message()
    
    def _search_rag(self):
        """Busca no sistema RAG"""
        if not self.rag_system:
            messagebox.showwarning("Aviso", "Sistema RAG não inicializado")
            return
        
        query = self.prompt_text.get(1.0, tk.END).strip()
        if not query:
            messagebox.showwarning("Aviso", "Digite uma consulta para buscar")
            return
        
        try:
            results = self.rag_system.search_knowledge(query)
            
            # Mostrar resultados no contexto
            self.context_text.delete(1.0, tk.END)
            if results:
                context_content = "\n\n".join(results[:3])  # Primeiros 3 resultados
                self.context_text.insert(1.0, context_content)
                self.rag_context = results[:3]
                
                self.log_text.insert(tk.END, f"Encontrados {len(results)} resultados RAG\n")
            else:
                self.context_text.insert(1.0, "Nenhum resultado encontrado")
                self.rag_context = []
                
        except Exception as e:
            self.log_text.insert(tk.END, f"Erro na busca RAG: {e}\n")
    
    def _save_memory(self):
        """Salva memória do prompt atual"""
        prompt = self.prompt_text.get(1.0, tk.END).strip()
        if not prompt:
            messagebox.showwarning("Aviso", "Nenhum prompt para salvar")
            return
        
        # Buscar última resposta no chat
        chat_content = self.chat_text.get(1.0, tk.END)
        lines = chat_content.split('\n')
        response = ""
        
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].startswith("Agente:"):
                response = lines[i].replace("Agente:", "").strip()
                break
        
        if response and self.openrouter_manager:
            agent_type = self.current_agent_type.get()
            model_name = self.selected_model.get()
            
            self.openrouter_manager.save_memory(prompt, response, agent_type, model_name, self.rag_context)
            self.log_text.insert(tk.END, "Memória salva com sucesso\n")
        else:
            messagebox.showwarning("Aviso", "Nenhuma resposta encontrada para salvar")
    
    def _clear_chat(self):
        """Limpa o chat"""
        self.chat_text.delete(1.0, tk.END)
        self.chat_history = []
        self.log_text.insert(tk.END, "Chat limpo\n")
    
    def _load_rag_docs(self):
        """Carrega documentos RAG"""
        if not self.rag_system:
            messagebox.showwarning("Aviso", "Sistema RAG não inicializado")
            return
        
        directory = filedialog.askdirectory(title="Selecionar diretório com documentos")
        if directory:
            try:
                # Implementar carregamento de documentos
                self.log_text.insert(tk.END, f"Carregando documentos de: {directory}\n")
                # self.rag_system.load_directory(directory)
                
            except Exception as e:
                self.log_text.insert(tk.END, f"Erro ao carregar documentos: {e}\n")
    
    def _detect_mcps(self):
        """Detecta MCPs instalados"""
        if not self.mcp_manager:
            messagebox.showwarning("Aviso", "MCP Manager não inicializado")
            return
        
        try:
            mcps = self.mcp_manager.detect_installed_mcps()
            self.log_text.insert(tk.END, f"Detectados {len(mcps)} MCPs\n")
        except Exception as e:
            self.log_text.insert(tk.END, f"Erro ao detectar MCPs: {e}\n")
    
    def _check_docker(self):
        """Verifica status do Docker"""
        if not self.docker_manager:
            messagebox.showwarning("Aviso", "Docker Manager não inicializado")
            return
        
        try:
            is_installed = self.docker_manager.check_docker_installed()
            status = "instalado" if is_installed else "não encontrado"
            self.log_text.insert(tk.END, f"Docker: {status}\n")
        except Exception as e:
            self.log_text.insert(tk.END, f"Erro ao verificar Docker: {e}\n")
    
    def _start_n8n(self):
        """Inicia N8N"""
        if not self.docker_manager:
            messagebox.showwarning("Aviso", "Docker Manager não inicializado")
            return
        
        try:
            result = self.docker_manager.start_n8n()
            if result:
                self.log_text.insert(tk.END, "N8N iniciado com sucesso\n")
            else:
                self.log_text.insert(tk.END, "Erro ao iniciar N8N\n")
        except Exception as e:
            self.log_text.insert(tk.END, f"Erro ao iniciar N8N: {e}\n")
    
    def _load_config(self):
        """Carrega configuração"""
        filename = filedialog.askopenfilename(
            title="Carregar Configuração",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.log_text.insert(tk.END, f"Configuração carregada: {filename}\n")
            except Exception as e:
                self.log_text.insert(tk.END, f"Erro ao carregar configuração: {e}\n")
    
    def _save_config(self):
        """Salva configuração"""
        filename = filedialog.asksaveasfilename(
            title="Salvar Configuração",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                config = {
                    "agent_type": self.current_agent_type.get(),
                    "selected_model": self.selected_model.get(),
                    "timestamp": str(datetime.now())
                }
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                self.log_text.insert(tk.END, f"Configuração salva: {filename}\n")
            except Exception as e:
                self.log_text.insert(tk.END, f"Erro ao salvar configuração: {e}\n")
    
    def _export_chat(self):
        """Exporta chat para arquivo"""
        filename = filedialog.asksaveasfilename(
            title="Exportar Chat",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                chat_content = self.chat_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(chat_content)
                self.log_text.insert(tk.END, f"Chat exportado: {filename}\n")
            except Exception as e:
                self.log_text.insert(tk.END, f"Erro ao exportar chat: {e}\n")
    
    def _show_about(self):
        """Mostra informações sobre o sistema"""
        about_text = """
SUPER_AGENT_MCP_DOCKER_N8N
Versão: 0.1.0

Sistema inteligente para desenvolvimento de software com:
- Integração OpenRouter para modelos LLM
- Sistema RAG avançado
- Geração de PRDs e tasks
- Integração N8N e Docker
- Chat direto com agentes especializados

Desenvolvido com fé e dedicação.
        """
        messagebox.showinfo("Sobre", about_text)
    
    def _show_docs(self):
        """Mostra documentação"""
        docs_text = """
Documentação do Sistema:

1. CHAT DIRETO: Chat direto com acesso à web
2. PRD GENERATOR: Cria PRDs com técnicas modernas
3. N8N WORKFLOW: Cria workflows N8N
4. DEPLOY MANAGER: Scripts de deploy

Para usar:
1. Selecione o tipo de agente
2. Carregue os modelos OpenRouter
3. Digite seu prompt
4. Clique em Enviar

Use "Buscar RAG" para incluir contexto da base de conhecimento.
        """
        messagebox.showinfo("Documentação", docs_text)
    
    def run(self):
        """Executa a interface gráfica"""
        self.root.mainloop()
