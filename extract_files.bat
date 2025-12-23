@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Mini SOC - File Extractor
echo ========================================
echo.

REM Create extraction folder
set EXTRACT_FOLDER=extracted_files
if not exist %EXTRACT_FOLDER% mkdir %EXTRACT_FOLDER%

echo Extracting files to: %EXTRACT_FOLDER%\
echo.

set count=0

REM Extract Backend Config
call :ExtractFile "backend\config\database.py" "app_config_database.py"

REM Extract Backend Parsers
call :ExtractFile "backend\parsers\base_parser.py" "app_parsers_base_parser.py"
call :ExtractFile "backend\parsers\ssh_parser.py" "app_parsers_ssh_parser.py"
call :ExtractFile "backend\parsers\nginx_parser.py" "app_parsers_nginx_parser.py"

REM Extract Backend Models
call :ExtractFile "backend\models\ssh_log.py" "app_models_ssh_log.py"
call :ExtractFile "backend\models\nginx_log.py" "app_models_nginx_log.py"
call :ExtractFile "backend\models\attack_log.py" "app_models_attack_log.py"

REM Extract Backend Services
call :ExtractFile "backend\services\log_watcher.py" "app_services_log_watcher.py"
call :ExtractFile "backend\services\attack_detector.py" "app_services_attack_detector.py"

REM Extract Backend API
call :ExtractFile "backend\api\main.py" "app_api_main.py"
call :ExtractFile "backend\api\routes\ssh.py" "app_api_routes_ssh.py"
call :ExtractFile "backend\api\routes\nginx.py" "app_api_routes_nginx.py"

REM Extract Backend Main
call :ExtractFile "backend\main.py" "app_backend_main.py"

REM Extract Config Files
call :ExtractFile "backend\requirements.txt" "app_requirements.txt"
call :ExtractFile "backend\Dockerfile" "app_backend_Dockerfile"
call :ExtractFile "docker-compose.yml" "app_docker_compose.yml"

REM Extract Frontend Files
call :ExtractFile "frontend\Dockerfile" "app_frontend_Dockerfile"
call :ExtractFile "frontend\nginx.conf" "app_frontend_nginx.conf"
call :ExtractFile "frontend\index.html" "app_frontend_index.html"
call :ExtractFile "frontend\css\style.css" "app_frontend_style.css"
call :ExtractFile "frontend\js\app.js" "app_frontend_app.js"
call :ExtractFile "frontend\js\components\dashboard.js" "app_frontend_dashboard.js"
call :ExtractFile "frontend\js\components\ssh-monitor.js" "app_frontend_ssh_monitor.js"
call :ExtractFile "frontend\js\components\nginx-monitor.js" "app_frontend_nginx_monitor.js"
call :ExtractFile "frontend\js\components\attack-monitor.js" "app_frontend_attack_monitor.js"
call :ExtractFile "frontend\js\utils\api.js" "app_frontend_api.js"

echo.
echo ========================================
echo SUMMARY
echo ========================================
echo Total files extracted: !count!
echo Output folder: %EXTRACT_FOLDER%\
echo ========================================
echo.

REM Create index file
echo Creating index file...
(
    echo # Mini SOC Log Parser - Extracted Files
    echo.
    echo Extraction Date: %date% %time%
    echo.
    echo ## File Mapping:
    echo.
    echo ### Backend Core
    echo - app_backend_main.py          ^<-- backend\main.py
    echo - app_requirements.txt         ^<-- backend\requirements.txt
    echo - app_backend_Dockerfile       ^<-- backend\Dockerfile
    echo.
    echo ### Config
    echo - app_config_database.py       ^<-- backend\config\database.py
    echo.
    echo ### Parsers
    echo - app_parsers_base_parser.py   ^<-- backend\parsers\base_parser.py
    echo - app_parsers_ssh_parser.py    ^<-- backend\parsers\ssh_parser.py
    echo - app_parsers_nginx_parser.py  ^<-- backend\parsers\nginx_parser.py
    echo.
    echo ### Models
    echo - app_models_ssh_log.py        ^<-- backend\models\ssh_log.py
    echo - app_models_nginx_log.py      ^<-- backend\models\nginx_log.py
    echo - app_models_attack_log.py     ^<-- backend\models\attack_log.py
    echo.
    echo ### Services
    echo - app_services_log_watcher.py  ^<-- backend\services\log_watcher.py
    echo - app_services_attack_detector.py ^<-- backend\services\attack_detector.py
    echo.
    echo ### API
    echo - app_api_main.py              ^<-- backend\api\main.py
    echo - app_api_routes_ssh.py        ^<-- backend\api\routes\ssh.py
    echo - app_api_routes_nginx.py      ^<-- backend\api\routes\nginx.py
    echo.
    echo ### Docker
    echo - app_docker_compose.yml       ^<-- docker-compose.yml
    echo.
    echo ### Frontend
    echo - app_frontend_Dockerfile      ^<-- frontend\Dockerfile
    echo - app_frontend_nginx.conf      ^<-- frontend\nginx.conf
    echo - app_frontend_index.html      ^<-- frontend\index.html
    echo - app_frontend_style.css       ^<-- frontend\css\style.css
    echo - app_frontend_app.js          ^<-- frontend\js\app.js
    echo - app_frontend_dashboard.js    ^<-- frontend\js\components\dashboard.js
    echo - app_frontend_ssh_monitor.js  ^<-- frontend\js\components\ssh-monitor.js
    echo - app_frontend_nginx_monitor.js ^<-- frontend\js\components\nginx-monitor.js
    echo - app_frontend_attack_monitor.js ^<-- frontend\js\components\attack-monitor.js
    echo - app_frontend_api.js          ^<-- frontend\js\utils\api.js
    echo.
    echo ---
    echo.
    echo ## Notes:
    echo - .bat files are excluded from extraction
    echo - .env files are excluded for security
    echo - Only non-empty files are extracted
) > %EXTRACT_FOLDER%\README_MAPPING.md

echo Index file created: %EXTRACT_FOLDER%\README_MAPPING.md
echo.

pause
exit /b

:ExtractFile
set source=%~1
set target=%~2

if exist %source% (
    for %%A in (%source%) do set size=%%~zA
    if !size! GTR 0 (
        copy /Y %source% %EXTRACT_FOLDER%\%target% >nul 2>&1
        if !errorlevel! EQU 0 (
            echo [92m✓[0m Extracted: %source% -^> %target% ^(!size! bytes^)
            set /a count+=1
        ) else (
            echo [91m✗[0m Failed: %source%
        )
    ) else (
        echo [93m○[0m Skipped: %source% ^(empty file^)
    )
) else (
    echo [91m✗[0m Not found: %source%
)
exit /b