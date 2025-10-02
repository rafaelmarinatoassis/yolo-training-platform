@echo off
chcp 65001 > nul
title YOLO Training Platform - Desenvolvimento

echo YOLO Training Platform - Modo Desenvolvimento
echo.

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERRO] Ambiente virtual nao encontrado! Execute start.bat primeiro.
    pause
    exit /b 1
)

REM Executar aplicação
echo Iniciando servidor em http://localhost:5000
echo Para parar: Ctrl+C
echo.
python run.py

echo.
echo Servidor interrompido!
pause