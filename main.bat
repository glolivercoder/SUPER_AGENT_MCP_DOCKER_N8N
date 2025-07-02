@echo off
echo Iniciando SUPER_AGENT_MCP_DOCKER_N8N...
echo.

REM Verificar se Python está instalado
py --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python não encontrado. Por favor, instale Python 3.11 ou superior.
    pause
    exit /b 1
)

REM Ir para o diretório do projeto
cd /d %~dp0

echo Verificando dependências...
echo.

REM Verificar se as dependências principais estão instaladas
py -c "import silero_tts, torch, sounddevice, soundfile, vosk, numpy; print('✅ Dependências principais OK')" 2>nul
if errorlevel 1 (
    echo Instalando dependências do sistema de voz...
    pip install silero-tts torch torchaudio sounddevice soundfile vosk numpy
    echo.
)

REM Verificar se as outras dependências estão instaladas
py -c "import requests, openai, aiohttp; print('✅ Dependências de API OK')" 2>nul
if errorlevel 1 (
    echo Instalando dependências do sistema...
    pip install -r requirements.txt
    echo.
)

echo Iniciando o sistema...
echo.

REM Executar o sistema principal
py main.py

REM Aguardar tecla se houve erro
if errorlevel 1 (
    echo.
    echo ERRO: Falha na execução do sistema.
    pause
) 