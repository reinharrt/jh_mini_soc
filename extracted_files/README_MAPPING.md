# Mini SOC Log Parser - Extracted Files

Extraction Date: 23/12/2025 12:34:48,99

## File Mapping:

### Backend Core
- app_backend_main.py          <-- backend\main.py
- app_requirements.txt         <-- backend\requirements.txt
- app_backend_Dockerfile       <-- backend\Dockerfile

### Config
- app_config_database.py       <-- backend\config\database.py

### Parsers
- app_parsers_base_parser.py   <-- backend\parsers\base_parser.py
- app_parsers_ssh_parser.py    <-- backend\parsers\ssh_parser.py
- app_parsers_nginx_parser.py  <-- backend\parsers\nginx_parser.py

### Models
- app_models_ssh_log.py        <-- backend\models\ssh_log.py
- app_models_nginx_log.py      <-- backend\models\nginx_log.py
- app_models_attack_log.py     <-- backend\models\attack_log.py

### Services
- app_services_log_watcher.py  <-- backend\services\log_watcher.py
- app_services_attack_detector.py <-- backend\services\attack_detector.py

### API
- app_api_main.py              <-- backend\api\main.py
- app_api_routes_ssh.py        <-- backend\api\routes\ssh.py
- app_api_routes_nginx.py      <-- backend\api\routes\nginx.py

### Docker
- app_docker_compose.yml       <-- docker-compose.yml

### Frontend
- app_frontend_Dockerfile      <-- frontend\Dockerfile
- app_frontend_nginx.conf      <-- frontend\nginx.conf
- app_frontend_index.html      <-- frontend\index.html
- app_frontend_style.css       <-- frontend\css\style.css
- app_frontend_app.js          <-- frontend\js\app.js
- app_frontend_dashboard.js    <-- frontend\js\components\dashboard.js
- app_frontend_ssh_monitor.js  <-- frontend\js\components\ssh-monitor.js
- app_frontend_nginx_monitor.js <-- frontend\js\components\nginx-monitor.js
- app_frontend_attack_monitor.js <-- frontend\js\components\attack-monitor.js
- app_frontend_api.js          <-- frontend\js\utils\api.js

---

## Notes:
- .bat files are excluded from extraction
- .env files are excluded for security
- Only non-empty files are extracted
