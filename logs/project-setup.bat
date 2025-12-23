@echo off
echo ========================================
echo Mini SOC Log Parser - Project Creator
echo ========================================
echo.

REM Backend directories
echo Creating backend structure...
mkdir backend\config 2>nul
mkdir backend\parsers 2>nul
mkdir backend\models 2>nul
mkdir backend\services 2>nul
mkdir backend\api\routes 2>nul

REM Frontend directories
echo Creating frontend structure...
mkdir frontend\css 2>nul
mkdir frontend\js\components 2>nul
mkdir frontend\js\utils 2>nul

REM Logs directories
echo Creating logs structure...
mkdir logs\ssh 2>nul
mkdir logs\nginx 2>nul

REM Root level files
echo Creating root files...
type nul > docker-compose.yml
type nul > .env.example
type nul > README.md

REM Backend files
echo Creating backend files...
type nul > backend\Dockerfile
type nul > backend\requirements.txt
type nul > backend\main.py

REM Backend config
type nul > backend\config\__init__.py
type nul > backend\config\database.py

REM Backend parsers
type nul > backend\parsers\__init__.py
type nul > backend\parsers\base_parser.py
type nul > backend\parsers\ssh_parser.py
type nul > backend\parsers\nginx_parser.py

REM Backend models
type nul > backend\models\__init__.py
type nul > backend\models\ssh_log.py
type nul > backend\models\nginx_log.py

REM Backend services
type nul > backend\services\__init__.py
type nul > backend\services\log_watcher.py

REM Backend API
type nul > backend\api\__init__.py
type nul > backend\api\main.py
type nul > backend\api\routes\__init__.py
type nul > backend\api\routes\ssh.py
type nul > backend\api\routes\nginx.py

REM Frontend files
echo Creating frontend files...
type nul > frontend\Dockerfile
type nul > frontend\nginx.conf
type nul > frontend\index.html
type nul > frontend\css\style.css

REM Frontend JS
type nul > frontend\js\app.js
type nul > frontend\js\components\dashboard.js
type nul > frontend\js\components\ssh-monitor.js
type nul > frontend\js\components\nginx-monitor.js
type nul > frontend\js\utils\api.js

REM Log files
echo Creating log files...
type nul > logs\ssh\auth.log
type nul > logs\nginx\access.log
type nul > logs\nginx\error.log

echo.
echo ========================================
echo Project structure created successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Edit docker-compose.yml
echo 2. Configure .env.example
echo 3. Start coding!
echo.
pause