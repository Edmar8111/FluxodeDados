@echo off
setlocal

echo Baixando a última versão do instalador do Python...

:: Define o nome do instalador temporário
set "PYTHON_INSTALLER=python-latest.exe"

:: Baixa o instalador da última versão do Python (64 bits)
powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe -OutFile %PYTHON_INSTALLER%"

if exist %PYTHON_INSTALLER% (
    echo Instalador baixado com sucesso.

    echo Instalando Python de forma silenciosa...
    %PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

    echo Python instalado. Verificando versão instalada:
    python --version
    timeout /t 5 >nul
    py -m pip install requirements.txt
    timeout /t 5 >nul
    echo Instalação efetuada com sucesso!
) else (
    echo Erro ao baixar o instalador do Python.
)

:: Limpa instalador
del %PYTHON_INSTALLER% >nul 2>&1

endlocal
pause