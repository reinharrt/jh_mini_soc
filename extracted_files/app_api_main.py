from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import ssh, nginx, attacks

app = FastAPI(
    title="Mini SOC API",
    description="API for Mini SOC Log Analysis with Attack Detection",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ssh.router, prefix="/api/ssh", tags=["SSH Logs"])
app.include_router(nginx.router, prefix="/api/nginx", tags=["Nginx Logs"])
app.include_router(attacks.router, prefix="/api/attacks", tags=["Attack Detection"])

@app.get("/")
async def root():
    return {
        "message": "Mini SOC API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_root():
    """Health check endpoint at root"""
    return {"status": "healthy"}

@app.get("/api/health")
async def health_api():
    """Health check endpoint at /api/health for consistency"""
    return {"status": "healthy"}