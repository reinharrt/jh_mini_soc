// Nginx Monitor Component
class NginxMonitor {
    constructor() {
        this.refreshInterval = 3000;
        this.intervalId = null;
        this.currentPage = 0;
        this.pageSize = 50;
        this.currentView = 'access'; // access or error
    }

    async init() {
        this.renderUI();
        await this.loadLogs();
        this.startAutoRefresh();
    }

    renderUI() {
        const container = document.getElementById('nginx-dashboard');
        container.innerHTML = `
            <div class="space-y-6">
                <!-- Stats Cards -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                        <p class="text-sm text-gray-400 mb-1">Total Requests</p>
                        <p id="nginx-stat-total" class="text-2xl font-bold">0</p>
                    </div>
                    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                        <p class="text-sm text-gray-400 mb-1">2xx Success</p>
                        <p id="nginx-stat-2xx" class="text-2xl font-bold text-green-500">0</p>
                    </div>
                    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                        <p class="text-sm text-gray-400 mb-1">4xx Errors</p>
                        <p id="nginx-stat-4xx" class="text-2xl font-bold text-yellow-500">0</p>
                    </div>
                    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                        <p class="text-sm text-gray-400 mb-1">5xx Errors</p>
                        <p id="nginx-stat-5xx" class="text-2xl font-bold text-red-500">0</p>
                    </div>
                </div>

                <!-- View Switcher -->
                <div class="flex space-x-2">
                    <button onclick="nginxMonitor.switchView('access')" 
                        id="btn-view-access"
                        class="px-4 py-2 bg-blue-600 text-white rounded">
                        Access Logs
                    </button>
                    <button onclick="nginxMonitor.switchView('error')"
                        id="btn-view-error"
                        class="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600">
                        Error Logs
                    </button>
                </div>

                <!-- Access Logs View -->
                <div id="nginx-access-view" class="space-y-4">
                    <!-- Filters -->
                    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                        <div class="flex flex-wrap gap-4">
                            <select id="nginx-filter-method" class="bg-gray-700 text-white px-4 py-2 rounded border border-gray-600">
                                <option value="">All Methods</option>
                                <option value="GET">GET</option>
                                <option value="POST">POST</option>
                                <option value="PUT">PUT</option>
                                <option value="DELETE">DELETE</option>
                            </select>
                            <select id="nginx-filter-status" class="bg-gray-700 text-white px-4 py-2 rounded border border-gray-600">
                                <option value="">All Status</option>
                                <option value="200">200 OK</option>
                                <option value="404">404 Not Found</option>
                                <option value="500">500 Error</option>
                            </select>
                            <button onclick="nginxMonitor.loadLogs()" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm">
                                Apply Filters
                            </button>
                        </div>
                    </div>

                    <!-- Access Logs Table -->
                    <div class="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
                        <div class="overflow-x-auto">
                            <table class="log-table">
                                <thead>
                                    <tr>
                                        <th>Time</th>
                                        <th>Method</th>
                                        <th>Path</th>
                                        <th>Status</th>
                                        <th>IP</th>
                                        <th>Size</th>
                                        <th>Time</th>
                                    </tr>
                                </thead>
                                <tbody id="nginx-access-tbody">
                                    <tr>
                                        <td colspan="7" class="text-center py-8">
                                            <div class="spinner mx-auto"></div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Error Logs View -->
                <div id="nginx-error-view" class="space-y-4 hidden">
                    <!-- Error Filters -->
                    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                        <div class="flex flex-wrap gap-4">
                            <select id="nginx-error-filter-level" class="bg-gray-700 text-white px-4 py-2 rounded border border-gray-600">
                                <option value="">All Levels</option>
                                <option value="error">Error</option>
                                <option value="warn">Warning</option>
                                <option value="crit">Critical</option>
                            </select>
                            <button onclick="nginxMonitor.loadLogs()" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm">
                                Apply Filters
                            </button>
                        </div>
                    </div>

                    <!-- Error Logs Table -->
                    <div class="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
                        <div class="overflow-x-auto">
                            <table class="log-table">
                                <thead>
                                    <tr>
                                        <th>Time</th>
                                        <th>Level</th>
                                        <th>Message</th>
                                        <th>Client IP</th>
                                    </tr>
                                </thead>
                                <tbody id="nginx-error-tbody">
                                    <tr>
                                        <td colspan="4" class="text-center py-8">
                                            <div class="spinner mx-auto"></div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    switchView(view) {
        this.currentView = view;
        
        // Update buttons
        document.getElementById('btn-view-access').className = 
            view === 'access' ? 'px-4 py-2 bg-blue-600 text-white rounded' : 'px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600';
        document.getElementById('btn-view-error').className = 
            view === 'error' ? 'px-4 py-2 bg-blue-600 text-white rounded' : 'px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600';
        
        // Toggle views
        document.getElementById('nginx-access-view').classList.toggle('hidden', view !== 'access');
        document.getElementById('nginx-error-view').classList.toggle('hidden', view !== 'error');
        
        this.loadLogs();
    }

    async loadLogs() {
        try {
            // Load stats
            const stats = await nginxApi.getStats(24);
            this.updateStats(stats);

            if (this.currentView === 'access') {
                await this.loadAccessLogs();
            } else {
                await this.loadErrorLogs();
            }

        } catch (error) {
            console.error('Error loading Nginx logs:', error);
        }
    }

    async loadAccessLogs() {
        const method = document.getElementById('nginx-filter-method')?.value || '';
        const statusCode = document.getElementById('nginx-filter-status')?.value || '';

        const params = {
            limit: this.pageSize,
            offset: this.currentPage * this.pageSize
        };

        if (method) params.method = method;
        if (statusCode) params.status_code = statusCode;

        const response = await nginxApi.getAccessLogs(params);
        this.renderAccessLogs(response.logs);
    }

    async loadErrorLogs() {
        const level = document.getElementById('nginx-error-filter-level')?.value || '';

        const params = {
            limit: this.pageSize,
            offset: this.currentPage * this.pageSize
        };

        if (level) params.level = level;

        const response = await nginxApi.getErrorLogs(params);
        this.renderErrorLogs(response.logs);
    }

    updateStats(stats) {
        document.getElementById('nginx-stat-total').textContent = 
            stats.access.total_requests.toLocaleString();

        const statusDist = stats.access.status_distribution;
        const count2xx = statusDist.filter(s => s.status >= 200 && s.status < 300)
            .reduce((sum, s) => sum + s.count, 0);
        const count4xx = statusDist.filter(s => s.status >= 400 && s.status < 500)
            .reduce((sum, s) => sum + s.count, 0);
        const count5xx = statusDist.filter(s => s.status >= 500)
            .reduce((sum, s) => sum + s.count, 0);

        document.getElementById('nginx-stat-2xx').textContent = count2xx.toLocaleString();
        document.getElementById('nginx-stat-4xx').textContent = count4xx.toLocaleString();
        document.getElementById('nginx-stat-5xx').textContent = count5xx.toLocaleString();
    }

    renderAccessLogs(logs) {
        const tbody = document.getElementById('nginx-access-tbody');
        
        if (logs.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center py-8 text-gray-500">No logs found</td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = logs.map(log => `
            <tr class="fade-in">
                <td class="text-xs whitespace-nowrap">${formatTimestamp(log.timestamp)}</td>
                <td><span class="badge badge-info">${log.method}</span></td>
                <td class="text-sm font-mono max-w-xs truncate">${log.path}</td>
                <td><span class="badge ${getHttpStatusBadge(log.status_code)}">${log.status_code}</span></td>
                <td class="text-sm font-mono">${log.ip_address}</td>
                <td class="text-xs text-gray-400">${log.response_size ? formatBytes(log.response_size) : '-'}</td>
                <td class="text-xs text-gray-400">${log.request_time ? (log.request_time * 1000).toFixed(0) + 'ms' : '-'}</td>
            </tr>
        `).join('');
    }

    renderErrorLogs(logs) {
        const tbody = document.getElementById('nginx-error-tbody');
        
        if (logs.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center py-8 text-gray-500">No errors found</td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = logs.map(log => `
            <tr class="fade-in">
                <td class="text-xs whitespace-nowrap">${formatTimestamp(log.timestamp)}</td>
                <td><span class="badge ${log.level === 'error' ? 'badge-danger' : log.level === 'warn' ? 'badge-warning' : 'badge-info'}">${log.level}</span></td>
                <td class="text-sm">${log.message}</td>
                <td class="text-sm font-mono">${log.client_ip || '-'}</td>
            </tr>
        `).join('');
    }

    startAutoRefresh() {
        this.intervalId = setInterval(() => {
            this.loadLogs();
        }, this.refreshInterval);
    }

    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }
}

// Global instance
let nginxMonitor = null;

function initNginxMonitor() {
    if (!nginxMonitor) {
        nginxMonitor = new NginxMonitor();
    }
    nginxMonitor.init();
}

function stopNginxMonitor() {
    if (nginxMonitor) {
        nginxMonitor.stop();
    }
}