# Mini SOC - Log Parser & Dashboard

Mini Security Operations Center (SOC) untuk parsing dan monitoring log SSH dan Nginx dengan real-time dashboard.

## 🚀 Features

- **Log Parser**: Otomatis parse SSH dan Nginx logs
- **Real-time Monitoring**: Live monitoring dengan auto-refresh
- **Dashboard Analytics**: Statistik lengkap dan visualisasi
- **Suspicious Activity Detection**: Deteksi aktivitas mencurigakan
- **REST API**: API lengkap untuk integrasi
- **Docker Ready**: Full containerized dengan Docker Compose

## 📋 Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy
- **Database**: PostgreSQL 15
- **Frontend**: Vanilla JavaScript + Tailwind CSS
- **Container**: Docker + Docker Compose
- **Log Monitoring**: Watchdog

## 🛠️ Installation

### Prerequisites

- Docker & Docker Compose
- Git

### Quick Start

1. **Clone Repository**
```bash
git clone <repo-url>
cd mini-soc
```

2. **Setup Environment**
```bash
cp .env.example .env
# Edit .env jika perlu custom config
```

3. **Siapkan Folder Logs**
```bash
mkdir -p logs/ssh logs/nginx
```

4. **Start Services**
```bash
docker-compose up -d
```

5. **Access Dashboard**
- Dashboard: http://localhost:8080
- API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
mini-soc/
├── backend/
│   ├── parsers/         # Log parsers (SSH, Nginx)
│   ├── models/          # Database models
│   ├── api/            # FastAPI routes
│   ├── services/       # Log watcher service
│   └── config/         # Database config
├── frontend/
│   ├── js/
│   │   ├── components/ # Dashboard components
│   │   └── utils/      # API client
│   └── css/            # Styles
├── logs/               # Log files directory
│   ├── ssh/
│   └── nginx/
└── docker-compose.yml
```

## 📝 Log Format Support

### SSH Logs
- Auth.log format (Ubuntu/Debian)
- Secure log format (CentOS/RHEL)
- Deteksi: login attempts, failed logins, disconnections

### Nginx Logs
- **Access logs**: Combined format
- **Error logs**: Standard error format

## 🔌 API Endpoints

### SSH Endpoints
- `GET /api/ssh/logs` - Get SSH logs dengan filtering
- `GET /api/ssh/stats` - Statistik SSH
- `GET /api/ssh/timeline` - Timeline data

### Nginx Endpoints
- `GET /api/nginx/access/logs` - Nginx access logs
- `GET /api/nginx/error/logs` - Nginx error logs
- `GET /api/nginx/stats` - Statistik Nginx

## 🔧 Configuration

### Environment Variables

```env
# Database
POSTGRES_DB=mini_soc
POSTGRES_USER=socadmin
POSTGRES_PASSWORD=socpass123

# Backend
LOG_PATH=/logs
API_PORT=8000
```

### Log Paths

Taruh log files di folder yang sesuai:
- SSH logs: `./logs/ssh/auth.log`
- Nginx access: `./logs/nginx/access.log`
- Nginx error: `./logs/nginx/error.log`

## 📊 Dashboard Features

### Overview Tab
- Total statistics (24h)
- Top failed SSH IPs
- Top accessed paths
- Auto-refresh setiap 5 detik

### SSH Monitor
- Real-time SSH log stream
- Filter by status, username, IP
- Suspicious activity highlight
- Statistics breakdown

### Nginx Monitor
- Access logs monitoring
- Error logs monitoring
- Status code distribution
- Response time analytics

## 🚨 Suspicious Activity Detection

Parser otomatis mendeteksi:
- Multiple failed login attempts
- Invalid user attempts
- Unusual IP patterns
- High error rates

## 📈 Performance

- Auto-refresh: 3-5 detik
- Database indexing untuk query cepat
- Efficient log parsing dengan regex
- Connection pooling

## 🔒 Security Notes

- Default credentials di `.env` harus diganti di production
- Gunakan reverse proxy (nginx) untuk HTTPS
- Set firewall rules untuk database port
- Regular backup database

## 🐛 Troubleshooting

### Parser tidak jalan
```bash
# Check logs
docker-compose logs backend

# Pastikan log files ada dan readable
ls -la logs/ssh/
ls -la logs/nginx/
```

### Database connection error
```bash
# Restart postgres
docker-compose restart postgres

# Check health
docker-compose ps
```

### Frontend tidak load data
```bash
# Check API
curl http://localhost:8000/health

# Check browser console untuk errors
```

## 🔄 Updates & Maintenance

### Backup Database
```bash
docker exec soc-postgres pg_dump -U socadmin mini_soc > backup.sql
```

### View Logs
```bash
# Backend logs
docker-compose logs -f backend

# Database logs
docker-compose logs -f postgres
```

### Stop Services
```bash
docker-compose down

# With data cleanup
docker-compose down -v
```

## 📝 Development

### Add New Parser

1. Create parser di `backend/parsers/`
2. Extend `BaseParser` class
3. Implement `parse()` dan `save_to_db()`
4. Register di `log_watcher.py`

### Add New Endpoint

1. Create route di `backend/api/routes/`
2. Include router di `main.py`
3. Update frontend API client

## 🤝 Contributing

Contributions welcome! Please:
1. Fork repository
2. Create feature branch
3. Submit pull request

## 📄 License

MIT License

## 👨‍💻 Author

Mini SOC Project

## 🙏 Acknowledgments

- FastAPI framework
- Tailwind CSS
- Watchdog library
- SQLAlchemy
