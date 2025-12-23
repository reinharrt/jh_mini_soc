// SSH Monitor Component
class SSHMonitor {
    constructor() {
        this.refreshInterval = 3000; // 3 seconds
        this.intervalId = null;
        this.currentPage = 0;
        this.pageSize = 50;
    }

    async init() {
        this.renderUI();
        await this.loadLogs();
        this.startAutoRefresh();
    }

    renderUI() {
        const container = document.getElementById('ssh-dashboard');
        container.innerHTML = `
            <div class="space-y-6">
                <!-- Stats Cards -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                        <p class="text-sm text-gray-400 mb-1">Total Attempts</p>
                        <p id="ssh-stat-total" class="text-2xl font-bold">0</p>
                    </div>
                    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                        <p class="text-sm text-gray-400 mb-1">Successful</p>
                        <p id="ssh-stat-success" class="text-2xl font-bold text-green-500">0</p>
                    </div>
                    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                        <p class="text-sm text-gray-400 mb-1">Failed</p>
                        <p id="ssh-stat-failed" class="text-2xl font-bold text-red-500">0</p>
                    </div>
                    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                        <p class="text-sm text-gray-400 mb-1">Suspicious</p>
                        <p id="ssh-stat-suspicious" class="text-2xl font-bold text-yellow-500">0</p>
                    </div>
                </div>

                <!-- Filters -->
                <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <div class="flex flex-wrap gap-4">
                        <select id="ssh-filter-status" class="bg-gray-700 text-white px-4 py-2 rounded border border-gray-600">
                            <option value="">All Status</option>
                            <option value="success">Success</option>
                            <option value="failed">Failed</option>
                        </select>
                        <label class="flex items-center space-x-2">
                            <input type="checkbox" id="ssh-filter-suspicious" class="rounded">
                            <span class="text-sm">Suspicious Only</span>
                        </label>
                        <button onclick="sshMonitor.loadLogs()" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm">
                            Apply Filters
                        </button>
                    </div>
                </div>

                <!-- Logs Table -->
                <div class="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="log-table">
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Event</th>
                                    <th>Username</th>
                                    <th>IP Address</th>
                                    <th>Port</th>
                                    <th>Status</th>
                                    <th>Method</th>
                                </tr>
                            </thead>
                            <tbody id="ssh-logs-tbody">
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
        `;
    }

    async loadLogs() {
        try {
            // Get filters
            const status = document.getElementById('ssh-filter-status')?.value || '';
            const suspiciousOnly = document.getElementById('ssh-filter-suspicious')?.checked || false;

            const params = {
                limit: this.pageSize,
                offset: this.currentPage * this.pageSize
            };

            if (status) params.status = status;
            if (suspiciousOnly) params.suspicious_only = true;

            // Load stats
            const stats = await sshApi.getStats(24);
            this.updateStats(stats);

            // Load logs
            const response = await sshApi.getLogs(params);
            this.renderLogs(response.logs);

        } catch (error) {
            console.error('Error loading SSH logs:', error);
            document.getElementById('ssh-logs-tbody').innerHTML = `
                <tr>
                    <td colspan="7" class="text-center py-8 text-red-500">
                        Error loading logs: ${error.message}
                    </td>
                </tr>
            `;
        }
    }

    updateStats(stats) {
        document.getElementById('ssh-stat-total').textContent = 
            stats.total_attempts.toLocaleString();
        document.getElementById('ssh-stat-success').textContent = 
            stats.successful.toLocaleString();
        document.getElementById('ssh-stat-failed').textContent = 
            stats.failed.toLocaleString();
        document.getElementById('ssh-stat-suspicious').textContent = 
            stats.suspicious.toLocaleString();
    }

    renderLogs(logs) {
        const tbody = document.getElementById('ssh-logs-tbody');
        
        if (logs.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center py-8 text-gray-500">
                        No logs found
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = logs.map(log => `
            <tr class="fade-in ${log.is_suspicious ? 'bg-red-900 bg-opacity-10' : ''}">
                <td class="text-xs whitespace-nowrap">
                    ${formatTimestamp(log.timestamp)}
                </td>
                <td>
                    <span class="text-xs">${log.event_type || 'unknown'}</span>
                </td>
                <td>
                    <span class="font-mono text-sm ${log.username ? '' : 'text-gray-500'}">
                        ${log.username || '-'}
                    </span>
                </td>
                <td>
                    <span class="font-mono text-sm">
                        ${log.ip_address || '-'}
                        ${log.is_suspicious ? '<span class="text-red-500 ml-1">⚠️</span>' : ''}
                    </span>
                </td>
                <td class="text-sm">${log.port || '-'}</td>
                <td>
                    <span class="badge ${getStatusBadge(log.status)}">
                        ${log.status}
                    </span>
                </td>
                <td class="text-xs text-gray-400">${log.auth_method || '-'}</td>
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
let sshMonitor = null;

function initSSHMonitor() {
    if (!sshMonitor) {
        sshMonitor = new SSHMonitor();
    }
    sshMonitor.init();
}

function stopSSHMonitor() {
    if (sshMonitor) {
        sshMonitor.stop();
    }
}