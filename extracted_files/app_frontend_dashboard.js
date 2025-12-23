// Dashboard Overview Component
class Dashboard {
    constructor() {
        this.refreshInterval = 5000; // 5 seconds
        this.intervalId = null;
    }

    async init() {
        await this.loadData();
        this.startAutoRefresh();
    }

    async loadData() {
        try {
            // Load SSH stats
            const sshStats = await sshApi.getStats(24);
            this.updateSSHStats(sshStats);

            // Load Nginx stats
            const nginxStats = await nginxApi.getStats(24);
            this.updateNginxStats(nginxStats);

            // Update last update time
            document.getElementById('lastUpdate').textContent = 
                `Last update: ${new Date().toLocaleTimeString('id-ID')}`;

        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    updateSSHStats(stats) {
        document.getElementById('stat-ssh-total').textContent = 
            stats.total_attempts.toLocaleString();
        
        document.getElementById('stat-ssh-failed').textContent = 
            stats.failed.toLocaleString();

        // Top failed IPs
        const topFailedIpsEl = document.getElementById('top-failed-ips');
        if (stats.top_failed_ips && stats.top_failed_ips.length > 0) {
            topFailedIpsEl.innerHTML = stats.top_failed_ips
                .slice(0, 5)
                .map(item => `
                    <div class="flex items-center justify-between p-3 bg-gray-700 rounded-lg hover:bg-gray-600 transition">
                        <div class="flex items-center space-x-3">
                            <span class="text-red-500">⚠️</span>
                            <div>
                                <p class="font-mono text-sm">${item.ip}</p>
                                <p class="text-xs text-gray-400">${item.count} failed attempts</p>
                            </div>
                        </div>
                        <span class="text-red-500 font-bold">${item.count}</span>
                    </div>
                `).join('');
        } else {
            topFailedIpsEl.innerHTML = '<p class="text-gray-500 text-center py-4">No failed attempts</p>';
        }
    }

    updateNginxStats(stats) {
        document.getElementById('stat-nginx-total').textContent = 
            stats.access.total_requests.toLocaleString();
        
        const avgTime = (stats.access.avg_response_time * 1000).toFixed(0);
        document.getElementById('stat-nginx-avgtime').textContent = `${avgTime}ms`;

        // Top paths
        const topPathsEl = document.getElementById('top-paths');
        if (stats.access.top_paths && stats.access.top_paths.length > 0) {
            topPathsEl.innerHTML = stats.access.top_paths
                .slice(0, 5)
                .map(item => `
                    <div class="flex items-center justify-between p-3 bg-gray-700 rounded-lg hover:bg-gray-600 transition">
                        <div class="flex-1 min-w-0">
                            <p class="font-mono text-sm truncate">${item.path}</p>
                            <p class="text-xs text-gray-400">${item.count} requests</p>
                        </div>
                        <span class="text-blue-500 font-bold ml-4">${item.count}</span>
                    </div>
                `).join('');
        } else {
            topPathsEl.innerHTML = '<p class="text-gray-500 text-center py-4">No data</p>';
        }
    }

    startAutoRefresh() {
        this.intervalId = setInterval(() => {
            this.loadData();
        }, this.refreshInterval);
    }

    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }
}

// Global dashboard instance
let dashboardInstance = null;

function initDashboard() {
    if (!dashboardInstance) {
        dashboardInstance = new Dashboard();
    }
    dashboardInstance.init();
}

function stopDashboard() {
    if (dashboardInstance) {
        dashboardInstance.stop();
    }
}