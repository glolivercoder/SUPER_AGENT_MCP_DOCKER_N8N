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
from tkinter import simpledialog
from pathlib import Path
from typing import List, Dict, Optional
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
        # Carregar modelos OpenRouter automaticamente ao iniciar
        self._load_models()
        # Adicionar alerta visual se não houver modelos carregados após o carregamento
        self.root.after(3000, self._alerta_modelos_openrouter)
    
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
        """Cria a interface principal com sistema de abas"""
        # Criar sistema de abas
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(expand=1, fill="both", padx=10, pady=10)
        
        # Aba Principal
        self.main_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.main_tab, text="Principal")
        self._init_main_tab()
        
        # Aba Voz
        self.voice_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.voice_tab, text="Voz")
        self._init_voice_tab()
        
        # Aba MCPs
        self.mcps_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.mcps_tab, text="MCPs")
        self._init_mcps_tab()
        
        # Aba RAG
        self.rag_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.rag_tab, text="RAG")
        self._init_rag_tab()

    def _init_main_tab(self):
        """Inicializa a aba principal com a interface original"""
        # Frame principal
        main_frame = ttk.Frame(self.main_tab)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
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
        
        self.model_combo = ttk.Combobox(model_frame, state="readonly", textvariable=self.selected_model)
        self.model_combo.pack(side=tk.LEFT, padx=5)
        self.model_combo.bind("<<ComboboxSelected>>", self._on_model_selected)
        
        # Dropdown de empresa
        ttk.Label(model_frame, text="Empresa:").pack(side=tk.LEFT, padx=5)
        self.company_var = tk.StringVar()
        self.company_combo = ttk.Combobox(model_frame, textvariable=self.company_var, state="readonly")
        self.company_combo.pack(side=tk.LEFT, padx=5)
        self.company_combo.bind("<<ComboboxSelected>>", self._on_company_filter)
        
        # Checkbox de modelos gratuitos
        self.free_var = tk.BooleanVar()
        self.free_checkbox = ttk.Checkbutton(model_frame, text="Modelos Gratuitos", variable=self.free_var, command=self._on_free_filter)
        self.free_checkbox.pack(side=tk.LEFT, padx=5)
        
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
        
        # Switch para resposta por TTS
        self.tts_response_var = tk.BooleanVar(value=False)
        tts_switch = ttk.Checkbutton(button_frame, text="Responder por voz", variable=self.tts_response_var)
        tts_switch.pack(side=tk.RIGHT, padx=5)
        
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
            if not hasattr(self, '_voice_listen_thread') or not self._voice_listen_thread or not self._voice_listen_thread.is_alive():
                self._voice_listen_thread = threading.Thread(target=self._voice_listen_loop, daemon=True)
                self._voice_listen_thread.start()
                self.mic_button.config(bg="#27ae60", text="🔴")
                self.voice_status_label.config(text="Voz: Ativada - Diga algo...")
                self.log_text.insert(tk.END, "Escuta de voz ativada\n")
            else:
                self._stop_voice_listen = True
                self.mic_button.config(bg="#e74c3c", text="🎤")
                self.voice_status_label.config(text="Voz: Desativada")
                self.log_text.insert(tk.END, "Escuta de voz desativada\n")
            self.log_text.see(tk.END)
        except Exception as e:
            self.log_text.insert(tk.END, f"Erro ao alternar voz: {e}\n")
            self.log_text.see(tk.END)

    def _voice_listen_loop(self):
        self._stop_voice_listen = False
        while not self._stop_voice_listen:
            text = self.voice_module.listen_once(timeout=5)
            if text:
                # Ativar resposta por voz automaticamente quando usando microfone
                if hasattr(self, 'tts_response_var'):
                    self.tts_response_var.set(True)
                    
                self.prompt_text.delete(1.0, tk.END)
                self.prompt_text.insert(1.0, text)
                self._send_message()
                # Não precisamos falar a resposta aqui, pois o _handle_response já vai fazer isso
                # se o switch de TTS estiver ativado

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
            self.root.after(0, lambda: self.log_text.insert(tk.END, "Erro: OpenRouter Manager não inicializado\n"))
            return
        
        try:
            models = await self.openrouter_manager.get_models()
            model_names = [f"{m.name} ({m.company})" for m in models]
            
            # Atualizar combobox na thread principal
            self.root.after(0, lambda: self._update_model_combo(model_names, models))
            
        except Exception as e:
            self.root.after(0, lambda: self.log_text.insert(tk.END, f"Erro ao carregar modelos: {e}\n"))
            self.root.after(0, lambda: self.log_text.see(tk.END))
    
    def _load_models(self):
        """Carrega modelos OpenRouter"""
        if not self.openrouter_manager:
            self.log_text.insert(tk.END, "Erro: OpenRouter Manager não inicializado\n")
            self.log_text.see(tk.END)
            return
            
        self.log_text.insert(tk.END, "Carregando modelos OpenRouter...\n")
        self.log_text.see(tk.END)
        
        # Executar de forma assíncrona em thread separada
        def load_models_thread():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._load_models_async())
                loop.close()
            except Exception as e:
                # Usar after para atualizar GUI na thread principal
                if hasattr(self, 'root') and self.root:
                    self.root.after(0, lambda: self.log_text.insert(tk.END, f"Erro ao carregar modelos: {e}\n"))
                    self.root.after(0, lambda: self.log_text.see(tk.END))
        
        threading.Thread(target=load_models_thread, daemon=True).start()
    
    def _update_model_combo(self, model_names, models):
        """Atualiza combobox de modelos"""
        current = self.model_combo.get()
        self.model_combo['values'] = model_names
        if model_names:
            # Se o modelo atual ainda está na lista, manter selecionado
            if current in model_names:
                self.model_combo.set(current)
                self.selected_model.set(current)
            else:
                self.model_combo.set(model_names[0])
                self.selected_model.set(model_names[0])
        self.available_models = models
        # Atualizar empresas disponíveis
        companies = sorted(set(m.company for m in models))
        self.company_combo['values'] = companies
        if companies:
            self.company_combo.set(companies[0])
        self.log_text.insert(tk.END, f"Carregados {len(models)} modelos\n")
        self.log_text.see(tk.END)
    
    def _on_company_filter(self, event=None):
        # Filtrar modelos por empresa
        company = self.company_var.get()
        models = getattr(self, 'available_models', [])
        if company:
            filtered = [m for m in models if m.company == company]
        else:
            filtered = models
        self._update_model_combo([f"{m.name} ({m.company})" for m in filtered], filtered)

    def _on_free_filter(self):
        # Filtrar modelos gratuitos
        models = getattr(self, 'available_models', [])
        if self.free_var.get():
            filtered = [m for m in models if getattr(m, 'is_free', False)]
        else:
            filtered = models
        self._update_model_combo([f"{m.name} ({m.company})" for m in filtered], filtered)
    
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
    
    def _handle_response(self, result, message, agent_type, model_id):
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
            
            # Responder por TTS se o switch estiver ativado
            if hasattr(self, 'tts_response_var') and self.tts_response_var.get() and self.voice_module:
                try:
                    self.log_text.insert(tk.END, "Reproduzindo resposta por voz...\n")
                    self.voice_module.speak(response)
                except Exception as e:
                    self.log_text.insert(tk.END, f"Erro ao reproduzir resposta por voz: {e}\n")
            
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
        """Detecta MCPs instalados e mostra resultado"""
        if not self.mcp_manager:
            messagebox.showwarning("Aviso", "MCP Manager não inicializado")
            return
            
        try:
            mcps = self.mcp_manager.detect_installed_mcps()
            if not mcps:
                messagebox.showinfo("MCPs", "Nenhum MCP detectado nas IDEs instaladas")
                return
                
            # Mudar para a aba de MCPs
            self.tab_control.select(self.mcps_tab)
            
            # Atualizar lista
            self._update_mcps_list()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao detectar MCPs: {e}")
            self.log_text.insert(tk.END, f"Erro ao detectar MCPs: {e}\n")
            self.log_text.see(tk.END)
    
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
    
    def _alerta_modelos_openrouter(self):
        if not hasattr(self, 'available_models') or not self.available_models:
            messagebox.showwarning(
                "Atenção: Modelos OpenRouter",
                "Nenhum modelo OpenRouter foi carregado!\n\nVerifique sua conexão, a API key e tente novamente."
            )
        elif hasattr(self, 'available_models') and self.available_models and hasattr(self, 'model_combo'):
            # Se carregou, mas nenhum modelo gratuito
            gratuitos = [m for m in self.available_models if getattr(m, 'is_free', False)]
            if not gratuitos:
                messagebox.showinfo(
                    "Atenção: Modelos OpenRouter",
                    "Modelos carregados, mas nenhum modelo gratuito disponível no momento."
                )
    
    def _init_voice_tab(self):
        frame = ttk.Frame(self.voice_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Título
        ttk.Label(frame, text="Configurações de Voz (TTS/STT)", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))

        # Dropdown de idioma
        ttk.Label(frame, text="Idioma:").grid(row=1, column=0, sticky=tk.W)
        self.language_var = tk.StringVar(value="pt")
        self.language_combo = ttk.Combobox(frame, textvariable=self.language_var, state="readonly", width=15)
        self.language_combo.grid(row=1, column=1, padx=5, sticky=tk.W)
        self.language_combo.bind("<<ComboboxSelected>>", self._on_language_change)

        # Dropdown de gênero
        ttk.Label(frame, text="Gênero:").grid(row=1, column=2, sticky=tk.W, padx=(20, 0))
        self.gender_var = tk.StringVar(value="Masculino")
        self.gender_combo = ttk.Combobox(frame, textvariable=self.gender_var, state="readonly", width=15)
        self.gender_combo['values'] = ["Masculino", "Feminino"]
        self.gender_combo.grid(row=1, column=3, padx=5, sticky=tk.W)
        self.gender_combo.bind("<<ComboboxSelected>>", self._on_gender_change)

        # Dropdown de vozes/gênero (Silero)
        ttk.Label(frame, text="Voz específica:").grid(row=2, column=0, sticky=tk.W)
        self.speaker_var = tk.StringVar()
        self.speaker_combo = ttk.Combobox(frame, textvariable=self.speaker_var, state="readonly", width=40)
        self.speaker_combo.grid(row=2, column=1, columnspan=3, padx=5, sticky=tk.W+tk.E)
        self.speaker_combo.bind("<<ComboboxSelected>>", self._on_speaker_change)

        # Slider de tom
        ttk.Label(frame, text="Tom (Pitch):").grid(row=3, column=0, sticky=tk.W)
        self.pitch_var = tk.DoubleVar(value=1.0)
        self.pitch_slider = ttk.Scale(frame, from_=0.5, to=2.0, orient=tk.HORIZONTAL, variable=self.pitch_var, command=self._on_pitch_change)
        self.pitch_slider.grid(row=3, column=1, columnspan=2, padx=5, sticky=tk.W+tk.E)
        ttk.Label(frame, textvariable=self.pitch_var, width=5).grid(row=3, column=3)

        # Slider de velocidade
        ttk.Label(frame, text="Velocidade:").grid(row=4, column=0, sticky=tk.W)
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_slider = ttk.Scale(frame, from_=0.5, to=2.0, orient=tk.HORIZONTAL, variable=self.speed_var, command=self._on_speed_change)
        self.speed_slider.grid(row=4, column=1, columnspan=2, padx=5, sticky=tk.W+tk.E)
        ttk.Label(frame, textvariable=self.speed_var, width=5).grid(row=4, column=3)

        # Slider de volume
        ttk.Label(frame, text="Volume:").grid(row=5, column=0, sticky=tk.W)
        self.volume_var = tk.DoubleVar(value=1.0)
        self.volume_slider = ttk.Scale(frame, from_=0.1, to=2.0, orient=tk.HORIZONTAL, variable=self.volume_var, command=self._on_volume_change)
        self.volume_slider.grid(row=5, column=1, columnspan=2, padx=5, sticky=tk.W+tk.E)
        ttk.Label(frame, textvariable=self.volume_var, width=5).grid(row=5, column=3)

        # Campo de texto para testar TTS
        ttk.Label(frame, text="Texto de Teste:").grid(row=6, column=0, sticky=tk.W)
        self.voice_test_entry = ttk.Entry(frame, width=40)
        self.voice_test_entry.grid(row=6, column=1, columnspan=2, padx=5, sticky=tk.W+tk.E)
        ttk.Button(frame, text="Testar TTS", command=self._test_voice).grid(row=6, column=3, padx=5)

        # Botão para abrir configurações de áudio do sistema
        ttk.Button(frame, text="Abrir Config. de Áudio", command=self._open_system_audio).grid(row=11, column=0, columnspan=4, pady=(10,0))

        # Dispositivo de entrada
        ttk.Label(frame, text="Microfone:").grid(row=10, column=0, sticky=tk.W, pady=(10,0))
        self.mic_var = tk.StringVar()
        self.mic_combo = ttk.Combobox(frame, textvariable=self.mic_var, state="readonly", width=40)
        self.mic_combo.grid(row=10, column=1, columnspan=2, padx=5, sticky=tk.W+tk.E)
        ttk.Button(frame, text="Definir", command=self._on_mic_change).grid(row=10, column=3, padx=5, pady=(10,0))

        # Dropdown de engine STT
        ttk.Label(frame, text="Reconhecimento de Voz (STT):").grid(row=7, column=0, sticky=tk.W)
        
        # Proteger acesso ao voice_module
        stt_default = 'speech_recognition'
        if self.voice_module and hasattr(self.voice_module, 'voice_config'):
            stt_default = self.voice_module.voice_config.get('stt_engine', 'speech_recognition')
        
        self.stt_engine_var = tk.StringVar(value=stt_default)
        self.stt_engine_combo = ttk.Combobox(frame, textvariable=self.stt_engine_var, state="readonly", width=20)
        self.stt_engine_combo['values'] = ["speech_recognition", "vosk"]
        self.stt_engine_combo.grid(row=7, column=1, padx=5, sticky=tk.W)
        self.stt_engine_combo.bind("<<ComboboxSelected>>", self._on_stt_engine_change)
        
        # Status do STT
        self.stt_status_label = ttk.Label(frame, text="Status STT: Verificando...", foreground="orange")
        self.stt_status_label.grid(row=7, column=2, padx=5, sticky=tk.W)
        
        # Atualizar status do STT após um delay
        self.root.after(1000, self._update_stt_status)

        # Carregar dispositivos de áudio
        self._load_audio_devices()

    def _load_audio_devices(self):
        """Carrega lista de microfones disponíveis"""
        if self.voice_module:
            devices = self.voice_module.get_input_devices()
            self.mic_combo['values'] = devices
            if devices:
                # Selecionar previamente salvo se existir
                saved_idx = self.voice_module.voice_config.get("input_device_index")
                if saved_idx is not None and saved_idx < len(devices):
                    self.mic_combo.current(saved_idx)
                else:
                    self.mic_combo.current(0)

    def _update_speakers_by_language(self, language_code: str = "pt"):
        """Atualiza o combo de vozes de acordo com o idioma escolhido."""
        if not self.voice_module:
            return

        try:
            speakers_by_lang = self.voice_module.get_speakers_by_language()
            speakers = speakers_by_lang.get(language_code, []) or self.voice_module.get_speakers()

            # Montar lista exibindo gênero na UI
            display_speakers = []
            for spk in speakers:
                gender = self.voice_module.get_speaker_gender(spk)
                display_speakers.append(f"{spk} ({gender})")

            self.speaker_combo['values'] = display_speakers
            if display_speakers:
                self.speaker_combo.current(0)
                # Atualiza variável vinculada e VoiceModule
                self.speaker_var.set(display_speakers[0])
                self._on_speaker_change()
        except Exception as e:
            self.logger.error(f"Erro ao atualizar speakers: {e}")

    def _on_mic_change(self):
        idx = self.mic_combo.current()
        if self.voice_module:
            self.voice_module.set_input_device(idx)
            messagebox.showinfo("Microfone", f"Microfone definido para índice {idx}")

    def _on_language_change(self, event=None):
        """Quando o idioma é alterado"""
        language_display = self.language_var.get()
        language_map = {
            "Português": "pt",
            "Inglês": "en",
            "Espanhol": "es",
            "Francês": "fr",
            "Alemão": "de",
            "Italiano": "it",
            "Russo": "ru"
        }
        
        language_code = language_map.get(language_display, language_display)
        self._update_speakers_by_language(language_code)
    
    def _on_gender_change(self, event=None):
        """Quando o gênero é alterado"""
        gender = self.gender_var.get()
        
        # Filtrar vozes pelo gênero selecionado
        all_speakers = self.speaker_combo['values']
        if gender == "Masculino":
            filtered_speakers = [s for s in all_speakers if "Masculino" in s]
        elif gender == "Feminino":
            filtered_speakers = [s for s in all_speakers if "Feminino" in s]
        else:
            filtered_speakers = all_speakers
            
        if filtered_speakers:
            self.speaker_combo['values'] = filtered_speakers
            self.speaker_combo.current(0)
            self._on_speaker_change()
        else:
            # Se não houver vozes para o gênero selecionado, mostrar todas
            self.speaker_combo['values'] = all_speakers

    def _on_speaker_change(self, event=None):
        speaker_display = self.speaker_var.get()
        if speaker_display and self.voice_module:
            # Extrair nome do speaker sem o gênero
            speaker = speaker_display.split(" (")[0]
            self.voice_module.set_voice(speaker)

    def _on_pitch_change(self, event=None):
        pitch = self.pitch_var.get()
        if self.voice_module:
            self.voice_module.set_pitch(pitch)

    def _on_speed_change(self, event=None):
        speed = self.speed_var.get()
        if self.voice_module:
            self.voice_module.set_speed(speed)

    def _on_volume_change(self, event=None):
        volume = self.volume_var.get()
        if self.voice_module:
            self.voice_module.set_volume(volume)

    def _test_voice(self):
        text = self.voice_test_entry.get()
        if self.voice_module and text:
            self.voice_module.speak(text)

    def _open_system_audio(self):
        """Abre as configurações de áudio do sistema operacional"""
        try:
            import platform, os, subprocess
            if platform.system() == "Windows":
                os.startfile("ms-settings:sound")
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", "x-apple.systempreferences:com.apple.preference.sound"], check=False)
            else:  # Linux (tentativa)
                subprocess.run(["pavucontrol"], check=False)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir configurações de áudio: {e}")

    def _on_stt_engine_change(self, event=None):
        engine = self.stt_engine_var.get()
        if self.voice_module:
            self.voice_module.set_stt_engine(engine)
            messagebox.showinfo("STT", f"Engine de reconhecimento de voz definido para: {engine}")
            # Atualizar status após mudança
            self._update_stt_status()

    def _update_stt_status(self):
        """Atualiza o status do STT na interface"""
        if not self.voice_module:
            self.stt_status_label.config(text="Status STT: Módulo não inicializado", foreground="red")
            return
            
        try:
            status = self.voice_module.get_status()
            stt_ready = status.get('stt_ready', False)
            stt_type = status.get('stt_type', 'Nenhum')
            
            if stt_ready:
                self.stt_status_label.config(text=f"Status STT: {stt_type} (OK)", foreground="green")
            else:
                self.stt_status_label.config(text=f"Status STT: {stt_type} (Erro)", foreground="red")
        except Exception as e:
            self.stt_status_label.config(text="Status STT: Erro ao verificar", foreground="red")
            self.logger.error(f"Erro ao atualizar status STT: {e}")

    def _init_mcps_tab(self):
        frame = ttk.Frame(self.mcps_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        ttk.Label(frame, text="MCPs Ativos e Detectados nas IDEs:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=5)
        
        # TreeView com colunas atualizadas
        self.mcps_tree = ttk.Treeview(frame, columns=("IDE", "Status", "MCPs"), show="headings", height=12)
        self.mcps_tree.heading("IDE", text="IDE")
        self.mcps_tree.heading("Status", text="Status")
        self.mcps_tree.heading("MCPs", text="MCPs Detectados")
        
        # Configurar largura das colunas
        self.mcps_tree.column("IDE", width=100)
        self.mcps_tree.column("Status", width=120)
        self.mcps_tree.column("MCPs", width=400)
        
        # Scrollbar para TreeView
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.mcps_tree.yview)
        self.mcps_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack TreeView e Scrollbar
        self.mcps_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame para botões
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Atualizar Lista de MCPs", command=self._update_mcps_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Verificar Instalações", command=self._verify_ide_installations).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Mostrar Detalhes", command=self._show_mcp_details).pack(side=tk.LEFT, padx=5)
        
        # Carregar lista inicial
        self._update_mcps_list()

    def _update_mcps_list(self):
        if not self.mcp_manager:
            messagebox.showwarning("Aviso", "MCP Manager não inicializado")
            return
            
        # Limpar TreeView
        for row in self.mcps_tree.get_children():
            self.mcps_tree.delete(row)
        
        try:
            # Detectar MCPs
            mcps = self.mcp_manager.detect_installed_mcps()
            
            if not mcps:
                self.mcps_tree.insert("", tk.END, values=("Nenhuma IDE", "Não detectada", "Nenhum MCP encontrado"))
                return
                
            # Adicionar cada IDE na TreeView
            for ide, data in mcps.items():
                status = data.get("status", "Desconhecido")
                mcp_list = data.get("mcps", [])
                
                if mcp_list:
                    # Mostrar primeiros MCPs na linha principal
                    main_mcps = ", ".join(mcp_list[:3])
                    if len(mcp_list) > 3:
                        main_mcps += f" ... (+{len(mcp_list)-3} mais)"
                        
                    self.mcps_tree.insert("", tk.END, values=(ide, status, main_mcps))
                else:
                    self.mcps_tree.insert("", tk.END, values=(ide, status, "Nenhum MCP detectado"))
        except Exception as e:
            self.mcps_tree.insert("", tk.END, values=("Erro", "Falha na detecção", str(e)))
            self.log_text.insert(tk.END, f"Erro ao detectar MCPs: {e}\n")
            self.log_text.see(tk.END)
    
    def _verify_ide_installations(self):
        """Verifica quais IDEs estão instaladas no sistema"""
        try:
            import subprocess
            ide_status = {}
            
            # Verificar IDEs comuns
            ides_to_check = {
                "Cursor": "cursor --version",
                "VS Code": "code --version", 
                "Windsurf": "windsurf --version"
            }
            
            for ide, command in ides_to_check.items():
                try:
                    result = subprocess.run(command.split(), capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        ide_status[ide] = "✅ Instalado"
                    else:
                        ide_status[ide] = "❌ Não encontrado"
                except:
                    ide_status[ide] = "❌ Não encontrado"
            
            # Mostrar resultado
            status_text = "\n".join([f"{ide}: {status}" for ide, status in ide_status.items()])
            messagebox.showinfo("Status das IDEs", f"Verificação de instalação:\n\n{status_text}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao verificar IDEs: {e}")
            
    def _show_mcp_details(self):
        """Mostra detalhes do MCP selecionado"""
        selection = self.mcps_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma IDE para ver detalhes")
            return
            
        item = self.mcps_tree.item(selection[0])
        ide_name = item['values'][0]
        
        if not self.mcp_manager:
            return
            
        mcps = self.mcp_manager.detect_installed_mcps()
        ide_data = mcps.get(ide_name, {})
        
        # Criar janela de detalhes
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Detalhes - {ide_name}")
        detail_window.geometry("600x400")
        
        # Texto com detalhes
        text_widget = scrolledtext.ScrolledText(detail_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Montar texto de detalhes
        details = f"=== DETALHES DA IDE: {ide_name} ===\n\n"
        details += f"Status: {ide_data.get('status', 'Desconhecido')}\n\n"
        
        paths = ide_data.get('paths', [])
        if paths:
            details += "Caminhos encontrados:\n"
            for path in paths:
                details += f"  • {path}\n"
            details += "\n"
        
        mcps_list = ide_data.get('mcps', [])
        if mcps_list:
            details += f"MCPs detectados ({len(mcps_list)}):\n"
            for mcp in mcps_list:
                details += f"  • {mcp}\n"
        else:
            details += "Nenhum MCP específico detectado.\n"
            
        text_widget.insert(tk.END, details)

    def _init_rag_tab(self):
        """Inicializa a aba RAG com documentações"""
        frame = ttk.Frame(self.rag_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        ttk.Label(frame, text="Sistema RAG - Base de Conhecimento", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=5)
        
        # Frame para documentações
        docs_frame = ttk.LabelFrame(frame, text="Documentações Disponíveis")
        docs_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Lista de documentações
        self.rag_docs_list = tk.Listbox(docs_frame, selectmode=tk.SINGLE)
        self.rag_docs_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar para a lista
        docs_scrollbar = ttk.Scrollbar(docs_frame, orient=tk.VERTICAL, command=self.rag_docs_list.yview)
        docs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.rag_docs_list.config(yscrollcommand=docs_scrollbar.set)
        
        # Frame para botões
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(buttons_frame, text="Carregar Documentação", command=self._load_rag_doc).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Adicionar URL", command=self._add_rag_url).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Buscar na Base", command=self._search_rag_base).pack(side=tk.LEFT, padx=5)
        
        # Área de visualização do documento
        view_frame = ttk.LabelFrame(frame, text="Visualização do Documento")
        view_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.rag_view_text = scrolledtext.ScrolledText(view_frame, wrap=tk.WORD)
        self.rag_view_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Carregar documentações padrão
        self._load_default_rag_docs()

    def _load_default_rag_docs(self):
        """Carrega as documentações padrão na lista RAG"""
        default_docs = [
            "N8N Documentation",
            "Docker Documentation", 
            "Docker Compose Documentation",
            "GitHub Commands Documentation",
            "Digital Ocean Documentation",
            "Cloudflare Documentation",
            "Oracle Cloud Documentation"
        ]
        
        for doc in default_docs:
            self.rag_docs_list.insert(tk.END, doc)

    def _load_rag_doc(self):
        """Carrega documento selecionado na visualização"""
        selection = self.rag_docs_list.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma documentação")
            return
        
        doc_name = self.rag_docs_list.get(selection[0])
        # Aqui você implementaria a lógica para carregar o documento específico
        self.rag_view_text.delete(1.0, tk.END)
        self.rag_view_text.insert(1.0, f"Carregando documentação: {doc_name}\n\nEsta funcionalidade será implementada para carregar o conteúdo real da documentação.")

    def _add_rag_url(self):
        """Adiciona nova URL ao sistema RAG"""
        url = simpledialog.askstring("Adicionar URL", "Digite a URL da documentação:")
        if url:
            self.rag_docs_list.insert(tk.END, f"URL: {url}")
            if self.rag_system:
                try:
                    self.rag_system.add_url_content(url)
                    messagebox.showinfo("Sucesso", f"URL adicionada: {url}")
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao adicionar URL: {e}")

    def _search_rag_base(self):
        """Busca na base de conhecimento RAG"""
        query = simpledialog.askstring("Buscar na Base", "Digite sua consulta:")
        if query and self.rag_system:
            try:
                results = self.rag_system.search_knowledge(query)
                self.rag_view_text.delete(1.0, tk.END)
                self.rag_view_text.insert(1.0, f"Resultados para: {query}\n\n{results}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro na busca: {e}")

    def _on_model_selected(self, event=None):
        # Sincronizar o valor selecionado
        self.selected_model.set(self.model_combo.get())

    def run(self):
        """Executa a interface gráfica"""
        self.root.mainloop()
