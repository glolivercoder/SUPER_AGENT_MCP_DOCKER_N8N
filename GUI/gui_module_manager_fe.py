# GUI Module Manager para Fê - SUPER_AGENT_MCP_DOCKER_N8N
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import subprocess
import threading
import webbrowser
from datetime import datetime
import os
import psutil
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = ImageTk = None
import base64
from io import BytesIO
import time
import sqlite3
import asyncio
from pathlib import Path

class ModuleManagerFe:
    def __init__(self, root):
        self.root = root
        self.root.title("SUPER_AGENT_MCP_DOCKER_N8N - Module Manager")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Configuração de banco de dados para logs
        self.init_database()
        
        # Variáveis de controle
        self.modules_status = {}
        self.monitoring_active = True
        
        self.setup_microphone_favicon()
        self.setup_ui()
        self.start_monitoring()

    def init_database(self):
        """Inicializa o banco de dados SQLite para logs"""
        db_path = Path("logs/project_logs.db")
        db_path.parent.mkdir(exist_ok=True)
        
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS module_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                module_name TEXT,
                status TEXT,
                message TEXT,
                level TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_usage REAL,
                memory_usage REAL,
                disk_usage REAL,
                active_modules INTEGER
            )
        ''')
        
        self.conn.commit()

    def setup_microphone_favicon(self):
        """Configura ícone do microfone para a aplicação"""
        try:
            if Image and ImageTk:
                # Criar um ícone simples de microfone em base64
                icon_data = """
                iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmSQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVFiFtZdNaBNBFMd/s5tsNk1TbY3WqmhBwYNKQfGgB0UPIh48eBBBD4IHwYMHL3rwg1LwgwcP4kGwB8VDPXjw4MWDB0uxYFsQrFYtVmutbWpiY5JNdjOzu+Mhm02ym6SJ/mGZmffe/N6782beG8gppZSioCiKwnVdBEEAQAhBCCGEEMI5556/XtdFVVUkScK2bVRVRdd1dF1H13UkScK2bYrNhYQQhBBCCCGEEAI=
                """
                image_data = base64.b64decode(icon_data)
                image = Image.open(BytesIO(image_data))
                self.icon = ImageTk.PhotoImage(image)
                self.root.iconphoto(True, self.icon)
            else:
                print("PIL não disponível, ícone não será configurado")
        except Exception as e:
            print(f"Erro ao carregar ícone: {e}")

    def setup_ui(self):
        """Configura a interface principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook para abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba Dashboard
        self.setup_dashboard_tab()
        
        # Aba Módulos
        self.setup_modules_tab()
        
        # Aba Logs
        self.setup_logs_tab()
        
        # Aba Configurações
        self.setup_config_tab()

    def setup_dashboard_tab(self):
        """Configura a aba do dashboard principal"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Frame de status do sistema
        status_frame = ttk.LabelFrame(dashboard_frame, text="Status do Sistema")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Métricas do sistema
        metrics_frame = ttk.Frame(status_frame)
        metrics_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.cpu_label = ttk.Label(metrics_frame, text="CPU: 0%")
        self.cpu_label.grid(row=0, column=0, padx=10)
        
        self.memory_label = ttk.Label(metrics_frame, text="Memória: 0%")
        self.memory_label.grid(row=0, column=1, padx=10)
        
        self.disk_label = ttk.Label(metrics_frame, text="Disco: 0%")
        self.disk_label.grid(row=0, column=2, padx=10)
        
        # Frame de módulos ativos
        modules_frame = ttk.LabelFrame(dashboard_frame, text="Módulos Ativos")
        modules_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # TreeView para módulos
        self.modules_tree = ttk.Treeview(modules_frame, columns=('Status', 'Última Atualização', 'CPU', 'Memória'), show='tree headings')
        self.modules_tree.heading('#0', text='Módulo')
        self.modules_tree.heading('Status', text='Status')
        self.modules_tree.heading('Última Atualização', text='Última Atualização')
        self.modules_tree.heading('CPU', text='CPU %')
        self.modules_tree.heading('Memória', text='Memória %')
        
        self.modules_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def setup_modules_tab(self):
        """Configura a aba de gerenciamento de módulos"""
        modules_frame = ttk.Frame(self.notebook)
        self.notebook.add(modules_frame, text="Módulos")
        
        # Frame de controle
        control_frame = ttk.Frame(modules_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Iniciar MCP RAG", command=self.start_mcp_rag).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Parar MCP RAG", command=self.stop_mcp_rag).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Iniciar OpenRouter Agent", command=self.start_openrouter_agent).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Parar OpenRouter Agent", command=self.stop_openrouter_agent).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Reiniciar Todos", command=self.restart_all_modules).pack(side=tk.LEFT, padx=5)
        
        # Frame de informações dos módulos
        info_frame = ttk.LabelFrame(modules_frame, text="Informações dos Módulos")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.module_info_text = scrolledtext.ScrolledText(info_frame, height=20)
        self.module_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def setup_logs_tab(self):
        """Configura a aba de logs"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Logs")
        
        # Frame de controle de logs
        logs_control_frame = ttk.Frame(logs_frame)
        logs_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(logs_control_frame, text="Atualizar Logs", command=self.refresh_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(logs_control_frame, text="Limpar Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(logs_control_frame, text="Exportar Logs", command=self.export_logs).pack(side=tk.LEFT, padx=5)
        
        # Text widget para logs
        self.logs_text = scrolledtext.ScrolledText(logs_frame, height=25)
        self.logs_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def setup_config_tab(self):
        """Configura a aba de configurações"""
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Configurações")
        
        # Configurações de MCP
        mcp_frame = ttk.LabelFrame(config_frame, text="Configurações MCP")
        mcp_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(mcp_frame, text="Host MCP:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.mcp_host_entry = ttk.Entry(mcp_frame, width=30)
        self.mcp_host_entry.insert(0, "localhost")
        self.mcp_host_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(mcp_frame, text="Porta MCP:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.mcp_port_entry = ttk.Entry(mcp_frame, width=30)
        self.mcp_port_entry.insert(0, "8000")
        self.mcp_port_entry.grid(row=1, column=1, padx=5, pady=2)
        
        # Configurações de RAG
        rag_frame = ttk.LabelFrame(config_frame, text="Configurações RAG")
        rag_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(rag_frame, text="Modelo Embedding:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.embedding_model_entry = ttk.Entry(rag_frame, width=30)
        self.embedding_model_entry.insert(0, "sentence-transformers/all-MiniLM-L6-v2")
        self.embedding_model_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(rag_frame, text="Diretório de Documentos:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.docs_dir_entry = ttk.Entry(rag_frame, width=30)
        self.docs_dir_entry.insert(0, "./documents")
        self.docs_dir_entry.grid(row=1, column=1, padx=5, pady=2)
        
        # Botão de salvar configurações
        ttk.Button(config_frame, text="Salvar Configurações", command=self.save_config).pack(pady=10)

    def start_monitoring(self):
        """Inicia o monitoramento do sistema"""
        def monitor():
            while self.monitoring_active:
                try:
                    # Coleta métricas do sistema
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory_percent = psutil.virtual_memory().percent
                    disk_percent = psutil.disk_usage('/').percent
                    
                    # Atualiza interface
                    self.root.after(0, self.update_system_metrics, cpu_percent, memory_percent, disk_percent)
                    
                    # Salva métricas no banco
                    self.save_metrics(cpu_percent, memory_percent, disk_percent)
                    
                    time.sleep(5)  # Atualiza a cada 5 segundos
                except Exception as e:
                    self.log_message("SYSTEM", "ERROR", f"Erro no monitoramento: {e}")
                    time.sleep(10)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()

    def update_system_metrics(self, cpu, memory, disk):
        """Atualiza as métricas na interface"""
        self.cpu_label.config(text=f"CPU: {cpu:.1f}%")
        self.memory_label.config(text=f"Memória: {memory:.1f}%")
        self.disk_label.config(text=f"Disco: {disk:.1f}%")

    def save_metrics(self, cpu, memory, disk):
        """Salva métricas no banco de dados"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO project_metrics (cpu_usage, memory_usage, disk_usage, active_modules)
                VALUES (?, ?, ?, ?)
            ''', (cpu, memory, disk, len(self.modules_status)))
            self.conn.commit()
        except Exception as e:
            print(f"Erro ao salvar métricas: {e}")

    def log_message(self, module, level, message):
        """Registra mensagem no sistema de logs"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO module_logs (module_name, level, message)
                VALUES (?, ?, ?)
            ''', (module, level, message))
            self.conn.commit()
            
            # Atualiza interface de logs
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{level}] {module}: {message}\n"
            self.root.after(0, self.append_to_logs, log_entry)
        except Exception as e:
            print(f"Erro ao salvar log: {e}")

    def append_to_logs(self, log_entry):
        """Adiciona entrada aos logs na interface"""
        self.logs_text.insert(tk.END, log_entry)
        self.logs_text.see(tk.END)

    def start_mcp_rag(self):
        """Inicia o módulo MCP RAG"""
        try:
            self.log_message("MCP_RAG", "INFO", "Iniciando módulo MCP RAG...")
            # Aqui será implementada a inicialização do módulo MCP RAG
            self.modules_status["MCP_RAG"] = "RUNNING"
            self.update_modules_display()
            messagebox.showinfo("Sucesso", "Módulo MCP RAG iniciado com sucesso!")
        except Exception as e:
            self.log_message("MCP_RAG", "ERROR", f"Erro ao iniciar MCP RAG: {e}")
            messagebox.showerror("Erro", f"Erro ao iniciar MCP RAG: {e}")

    def start_openrouter_agent(self):
        """Inicia o agente OpenRouter"""
        try:
            from modules.openrouter_manager import OpenRouterManager
            
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                messagebox.showwarning("Aviso", "Configure OPENROUTER_API_KEY para usar o agente")
                return
            
            self.openrouter_manager = OpenRouterManager(api_key)
            self.modules_status["OPENROUTER_AGENT"] = "RUNNING"
            self.update_modules_display()
            self.log_message("OPENROUTER_AGENT", "INFO", "Agente OpenRouter iniciado")
            messagebox.showinfo("Sucesso", "Agente OpenRouter iniciado!")
            
        except Exception as e:
            self.log_message("OPENROUTER_AGENT", "ERROR", f"Erro ao iniciar agente: {e}")
            messagebox.showerror("Erro", f"Erro ao iniciar agente OpenRouter: {e}")

    def stop_openrouter_agent(self):
        """Para o agente OpenRouter"""
        try:
            if hasattr(self, 'openrouter_manager'):
                asyncio.create_task(self.openrouter_manager.shutdown())
                self.modules_status["OPENROUTER_AGENT"] = "STOPPED"
                self.update_modules_display()
                self.log_message("OPENROUTER_AGENT", "INFO", "Agente OpenRouter parado")
            messagebox.showinfo("Sucesso", "Agente OpenRouter parado!")
        except Exception as e:
            self.log_message("OPENROUTER_AGENT", "ERROR", f"Erro ao parar agente: {e}")
            messagebox.showerror("Erro", f"Erro ao parar agente: {e}")

    def stop_mcp_rag(self):
        """Para o módulo MCP RAG"""
        try:
            self.log_message("MCP_RAG", "INFO", "Parando módulo MCP RAG...")
            self.modules_status["MCP_RAG"] = "STOPPED"
            self.update_modules_display()
            messagebox.showinfo("Sucesso", "Módulo MCP RAG parado com sucesso!")
        except Exception as e:
            self.log_message("MCP_RAG", "ERROR", f"Erro ao parar MCP RAG: {e}")
            messagebox.showerror("Erro", f"Erro ao parar MCP RAG: {e}")

    def restart_all_modules(self):
        """Reinicia todos os módulos"""
        self.log_message("SYSTEM", "INFO", "Reiniciando todos os módulos...")
        # Implementar reinicialização de módulos
        messagebox.showinfo("Info", "Reinicialização de módulos em andamento...")

    def update_modules_display(self):
        """Atualiza a exibição dos módulos"""
        # Limpa TreeView
        for item in self.modules_tree.get_children():
            self.modules_tree.delete(item)
        
        # Adiciona módulos atuais
        for module, status in self.modules_status.items():
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.modules_tree.insert('', 'end', text=module, values=(status, timestamp, "0.0%", "0.0%"))

    def refresh_logs(self):
        """Atualiza os logs na interface"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT timestamp, module_name, level, message 
                FROM module_logs 
                ORDER BY timestamp DESC 
                LIMIT 100
            ''')
            logs = cursor.fetchall()
            
            self.logs_text.delete(1.0, tk.END)
            for log in reversed(logs):
                timestamp, module, level, message = log
                log_entry = f"[{timestamp}] [{level}] {module}: {message}\n"
                self.logs_text.insert(tk.END, log_entry)
            
            self.logs_text.see(tk.END)
        except Exception as e:
            self.log_message("SYSTEM", "ERROR", f"Erro ao carregar logs: {e}")

    def clear_logs(self):
        """Limpa os logs"""
        if messagebox.askyesno("Confirmar", "Deseja realmente limpar todos os logs?"):
            try:
                cursor = self.conn.cursor()
                cursor.execute('DELETE FROM module_logs')
                self.conn.commit()
                self.logs_text.delete(1.0, tk.END)
                self.log_message("SYSTEM", "INFO", "Logs limpos com sucesso")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao limpar logs: {e}")

    def export_logs(self):
        """Exporta os logs para arquivo"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                cursor = self.conn.cursor()
                cursor.execute('SELECT timestamp, module_name, level, message FROM module_logs ORDER BY timestamp')
                logs = cursor.fetchall()
                
                with open(filename, 'w', encoding='utf-8') as f:
                    for log in logs:
                        f.write(f"[{log[0]}] [{log[2]}] {log[1]}: {log[3]}\n")
                
                messagebox.showinfo("Sucesso", f"Logs exportados para {filename}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar logs: {e}")

    def save_config(self):
        """Salva as configurações"""
        config = {
            'mcp_host': self.mcp_host_entry.get(),
            'mcp_port': self.mcp_port_entry.get(),
            'embedding_model': self.embedding_model_entry.get(),
            'docs_directory': self.docs_dir_entry.get()
        }
        
        try:
            os.makedirs('config', exist_ok=True)
            with open('config/app_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.log_message("CONFIG", "INFO", "Configurações salvas com sucesso")
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
        except Exception as e:
            self.log_message("CONFIG", "ERROR", f"Erro ao salvar configurações: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {e}")

    def __del__(self):
        """Cleanup ao destruir a instância"""
        self.monitoring_active = False
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    root = tk.Tk()
    app = ModuleManagerFe(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.monitoring_active = False
        root.quit()

if __name__ == "__main__":
    main()
