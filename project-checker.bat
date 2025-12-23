@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Mini SOC Log Parser - Progress Checker
echo ========================================
echo.

set total=0
set filled=0
set empty=0

REM Function to check file
call :CheckFiles "Root Files" "docker-compose.yml" ".env.example" "README.md"

echo.
echo [BACKEND]
call :CheckFiles "Backend Core" "backend\Dockerfile" "backend\requirements.txt" "backend\main.py"
call :CheckFiles "Config" "backend\config\__init__.py" "backend\config\database.py"
call :CheckFiles "Parsers" "backend\parsers\__init__.py" "backend\parsers\base_parser.py" "backend\parsers\ssh_parser.py" "backend\parsers\nginx_parser.py"
call :CheckFiles "Models" "backend\models\__init__.py" "backend\models\ssh_log.py" "backend\models\nginx_log.py"
call :CheckFiles "Services" "backend\services\__init__.py" "backend\services\log_watcher.py"
call :CheckFiles "API Routes" "backend\api\__init__.py" "backend\api\main.py" "backend\api\routes\__init__.py" "backend\api\routes\ssh.py" "backend\api\routes\nginx.py"

echo.
echo [FRONTEND]
call :CheckFiles "Frontend Core" "frontend\Dockerfile" "frontend\nginx.conf" "frontend\index.html" "frontend\css\style.css"
call :CheckFiles "JavaScript" "frontend\js\app.js"
call :CheckFiles "Components" "frontend\js\components\dashboard.js" "frontend\js\components\ssh-monitor.js" "frontend\js\components\nginx-monitor.js"
call :CheckFiles "Utils" "frontend\js\utils\api.js"

echo.
echo [LOGS]
call :CheckFiles "Log Files" "logs\ssh\auth.log" "logs\nginx\access.log" "logs\nginx\error.log"

echo.
echo ========================================
echo SUMMARY
echo ========================================
echo Total Files    : !total!
echo Filled Files   : !filled! [92m✓[0m
echo Empty Files    : !empty! [91m✗[0m
echo.

set /a progress=filled*100/total
echo Progress       : !progress!%%

if !progress! LSS 30 (
    echo Status         : [91mJust Started[0m
) else if !progress! LSS 60 (
    echo Status         : [93mIn Progress[0m
) else if !progress! LSS 90 (
    echo Status         : [93mAlmost There[0m
) else if !progress! LSS 100 (
    echo Status         : [92mNearly Complete[0m
) else (
    echo Status         : [92mCompleted![0m
)

echo ========================================
echo.

REM Show empty files list
if !empty! GTR 0 (
    echo [91mEmpty files that need attention:[0m
    echo.
    for %%f in (
        "docker-compose.yml" ".env.example" "README.md"
        "backend\Dockerfile" "backend\requirements.txt" "backend\main.py"
        "backend\config\__init__.py" "backend\config\database.py"
        "backend\parsers\__init__.py" "backend\parsers\base_parser.py" "backend\parsers\ssh_parser.py" "backend\parsers\nginx_parser.py"
        "backend\models\__init__.py" "backend\models\ssh_log.py" "backend\models\nginx_log.py"
        "backend\services\__init__.py" "backend\services\log_watcher.py"
        "backend\api\__init__.py" "backend\api\main.py" "backend\api\routes\__init__.py" "backend\api\routes\ssh.py" "backend\api\routes\nginx.py"
        "frontend\Dockerfile" "frontend\nginx.conf" "frontend\index.html" "frontend\css\style.css"
        "frontend\js\app.js"
        "frontend\js\components\dashboard.js" "frontend\js\components\ssh-monitor.js" "frontend\js\components\nginx-monitor.js"
        "frontend\js\utils\api.js"
        "logs\ssh\auth.log" "logs\nginx\access.log" "logs\nginx\error.log"
    ) do (
        if exist %%f (
            for %%A in (%%f) do (
                if %%~zA EQU 0 (
                    echo   - %%~f
                )
            )
        )
    )
    echo.
)

pause
exit /b

:CheckFiles
set section=%~1
shift
echo.
echo [%section%]

:loop
if "%~1"=="" goto :endloop
set /a total+=1

if exist %~1 (
    for %%A in (%~1) do set size=%%~zA
    if !size! GTR 0 (
        echo [92m✓[0m %~1 ^(!size! bytes^)
        set /a filled+=1
    ) else (
        echo [91m✗[0m %~1 ^(empty^)
        set /a empty+=1
    )
) else (
    echo [91m✗[0m %~1 ^(not found^)
    set /a empty+=1
)
shift
goto :loop

:endloop
exit /b