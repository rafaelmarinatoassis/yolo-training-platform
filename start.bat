@echo off
chcp 65001 > nul
title YOLO Training Platform - Setup Automatico

echo.
echo ================================================================
echo                  YOLO Training Platform                        
echo                     Setup Automatico                           
echo ================================================================
echo.

REM Verificar se Python está instalado
echo [1/6] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado! 
    echo Baixe e instale Python em: https://www.python.org/downloads/
    echo IMPORTANTE: Certifique-se de marcar "Add Python to PATH" durante a instalacao
    echo.
    pause
    exit /b 1
)
python --version
echo.

REM Verificar se pip está disponível
echo [2/6] Verificando pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] pip nao encontrado!
    echo Reinstale Python com pip incluido
    pause
    exit /b 1
)
pip --version
echo.

REM Criar ambiente virtual se não existir
echo [3/6] Configurando ambiente virtual...
if not exist ".venv" (
    echo Criando novo ambiente virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar ambiente virtual!
        pause
        exit /b 1
    )
    echo [OK] Ambiente virtual criado com sucesso!
) else (
    echo [OK] Ambiente virtual ja existe!
)
echo.

REM Ativar ambiente virtual
echo [4/6] Ativando ambiente virtual...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERRO] Falha ao ativar ambiente virtual!
    echo Tentando com PowerShell...
    powershell -ExecutionPolicy Bypass -Command ".\.venv\Scripts\Activate.ps1"
    if errorlevel 1 (
        echo [ERRO] Falha na ativacao. Execute manualmente:
        echo    .venv\Scripts\activate.bat
        pause
        exit /b 1
    )
)
echo [OK] Ambiente virtual ativado!
echo.

REM Atualizar pip
echo [5/6] Atualizando pip e instalando dependencias...
echo Atualizando pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [AVISO] Falha ao atualizar pip, continuando...
)

REM Instalar dependências
echo Instalando dependencias do requirements.txt...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias!
    echo Tentando instalacao detalhada...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERRO] Erro critico na instalacao de dependencias!
        echo Verifique se requirements.txt existe e esta valido
        pause
        exit /b 1
    )
)
echo [OK] Dependencias instaladas com sucesso!
echo.

REM Verificar instalação das dependências principais
echo Testando imports principais...
python -c "import flask, ultralytics, pandas, torch, cv2; print('[OK] Todas as dependencias principais importadas!')" 2>nul
if errorlevel 1 (
    echo [AVISO] Algumas dependencias podem nao estar funcionando
    echo Isso pode ser normal na primeira execucao
)
echo.

REM Iniciar servidor
echo [6/6] Iniciando YOLO Training Platform...
echo.
echo ================================================================
echo   Servidor iniciando...                                        
echo   Acesse: http://localhost:5000                                
echo   Para parar: Ctrl+C                                          
echo ================================================================
echo.

REM Aguardar um pouco para o usuário ler
timeout /t 3 /nobreak >nul

REM Executar aplicação
python run.py

REM Se chegou aqui, o servidor foi interrompido
echo.
echo ================================================================
echo   Servidor interrompido                                        
echo   Obrigado por usar YOLO Training Platform!                    
echo ================================================================
echo.
pause