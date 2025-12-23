// API Client - Fixed version
const API_BASE = '/api';  // Let nginx proxy handle the routing

class APIClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    async get(endpoint) {
        return this.request(endpoint);
    }

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }
}

// SSH API
class SSHApi {
    constructor(client) {
        this.client = client;
    }

    async getLogs(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.client.get(`/ssh/logs?${query}`);
    }

    async getStats(hours = 24) {
        return this.client.get(`/ssh/stats?hours=${hours}`);
    }

    async getTimeline(hours = 24, interval = 'hour') {
        return this.client.get(`/ssh/timeline?hours=${hours}&interval=${interval}`);
    }
}

// Nginx API
class NginxApi {
    constructor(client) {
        this.client = client;
    }

    async getAccessLogs(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.client.get(`/nginx/access/logs?${query}`);
    }

    async getErrorLogs(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.client.get(`/nginx/error/logs?${query}`);
    }

    async getStats(hours = 24) {
        return this.client.get(`/nginx/stats?hours=${hours}`);
    }
}

// Initialize API clients
const apiClient = new APIClient(API_BASE);
const sshApi = new SSHApi(apiClient);
const nginxApi = new NginxApi(apiClient);

// Helper functions
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('id-ID', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function getStatusBadge(status) {
    const badges = {
        'success': 'badge-success',
        'failed': 'badge-danger',
        'session': 'badge-info',
        'closed': 'badge-warning'
    };
    return badges[status] || 'badge-info';
}

function getHttpStatusBadge(code) {
    if (code >= 200 && code < 300) return 'badge-success';
    if (code >= 300 && code < 400) return 'badge-info';
    if (code >= 400 && code < 500) return 'badge-warning';
    if (code >= 500) return 'badge-danger';
    return 'badge-info';
}