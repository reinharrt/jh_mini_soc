// Attack Monitor Component
class AttackMonitor {
    constructor() {
        this.refreshInterval = 3000;
        this.intervalId = null;
        this.currentPage = 0;
        this.pageSize = 50;
    }

    async init() {
        this.renderUI();
        await this.loadData();
        this.startAutoRefresh();
    }

    renderUI() {
        const container = document.getElementById('attack-dashboard');
        container.innerHTML = `
            <div class="space-y-6">
                <!-- Alert Banner -->
                <div id="critical-alert" class="hidden bg-red-900 border-l-4 border-red-500 p-4 rounded">
                    <div class="flex items-center">
                        <i class="fas fa-siren text-2xl mr-3 text-red-500"></i>
                        <div>
                            <p class="font-bold text-red-100">Critical Security Alert!</p>
                            <p class="text-red-200 text-sm" id="critical-message"></p>
                        </div>
                    </div>
                </div>

                <!-- Stats Cards -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                        <div class="flex items-center justify-between mb-2">
                            <p class="text-sm text-gray-400">Total Attacks</p>
                            <i class="fas fa-shield-virus text-2xl text-red-500"></i>
                        </div>
                        <p id="attack-stat-total" class="text-2xl font-bold text-red-500">0</p>
                        <p class="text-sm text-gray-500 mt-1">Last 24 hours</p>
                    </div>

                    <div class="bg-gray-800 rounded-lg p-4 border border-red-900">
                        <div class="flex items-center justify-between mb-2">
                            <p class="text-sm text-gray-400">Critical</p>
                            <i class="fas fa-circle-exclamation text-2xl text-red-600"></i>
                        </div>
                        <p id="attack-stat-critical" class="text-2xl font-bold text-red-600">0</p>
                        <p class="text-sm text-gray-500 mt-1">Immediate action required</p>
                    </div>

                    <div class="bg-gray-800 rounded-lg p-4 border border-orange-900">
                        <div class="flex items-center justify-between mb-2">
                            <p class="text-sm text-gray-400">High Priority</p>
                            <i class="fas fa-triangle-exclamation text-2xl text-orange-500"></i>
                        </div>
                        <p id="attack-stat-high" class="text-2xl font-bold text-orange-500">0</p>
                        <p class="text-sm text-gray-500 mt-1">Requires attention</p>
                    </div>

                    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                        <div class="flex items-center justify-between mb-2">
                            <p class="text-sm text-gray-400">Unresolved</p>
                            <i class="fas fa-clipboard-list text-2xl text-yellow-500"></i>
                        </div>
                        <p id="attack-stat-unresolved" class="text-2xl font-bold text-yellow-500">0</p>
                        <p class="text-sm text-gray-500 mt-1">Pending review</p>
                    </div>
                </div>

                <!-- Attack Types Distribution -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                        <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
                            <i class="fas fa-crosshairs"></i> Attack Types
                        </h3>
                        <div id="attack-types-chart" class="space-y-2"></div>
                    </div>

                    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                        <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
                            <i class="fas fa-user-secret"></i> Top Attackers
                        </h3>
                        <div id="top-attackers-list" class="space-y-2"></div>
                    </div>
                </div>

                <!-- Filters -->
                <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <div class="flex flex-wrap gap-4">
                        <select id="attack-filter-type" class="bg-gray-700 text-white px-4 py-2 rounded border border-gray-600">
                            <option value="">All Attack Types</option>
                            <option value="SQL Injection">SQL Injection</option>
                            <option value="XSS">XSS</option>
                            <option value="Path Traversal">Path Traversal</option>
                            <option value="Command Injection">Command Injection</option>
                            <option value="Web Shell">Web Shell</option>
                            <option value="Suspicious Access">Suspicious Access</option>
                        </select>
                        <select id="attack-filter-severity" class="bg-gray-700 text-white px-4 py-2 rounded border border-gray-600">
                            <option value="">All Severity</option>
                            <option value="CRITICAL">Critical</option>
                            <option value="HIGH">High</option>
                            <option value="MEDIUM">Medium</option>
                            <option value="LOW">Low</option>
                        </select>
                        <label class="flex items-center space-x-2">
                            <input type="checkbox" id="attack-filter-unresolved" class="rounded">
                            <span class="text-sm">Unresolved Only</span>
                        </label>
                        <button onclick="attackMonitor.loadData()" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm">
                            <i class="fas fa-filter mr-1"></i> Apply Filters
                        </button>
                    </div>
                </div>

                <!-- Attack Logs Table -->
                <div class="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="log-table">
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Severity</th>
                                    <th>Attack Type</th>
                                    <th>Source IP</th>
                                    <th>Target</th>
                                    <th>Description</th>
                                    <th>Status</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody id="attack-logs-tbody">
                                <tr>
                                    <td colspan="8" class="text-center py-8">
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

    async loadData() {
        try {
            const stats = await this.loadStats();
            this.updateStats(stats);
            await this.loadAttackLogs();
            this.showCriticalAlert(stats);
        } catch (error) {
            console.error('Error loading attack data:', error);
        }
    }

    async loadStats() {
        const response = await fetch('/api/attacks/stats?hours=24');
        return await response.json();
    }

    async loadAttackLogs() {
        const attackType = document.getElementById('attack-filter-type')?.value || '';
        const severity = document.getElementById('attack-filter-severity')?.value || '';
        const unresolvedOnly = document.getElementById('attack-filter-unresolved')?.checked || false;

        const params = new URLSearchParams({
            limit: this.pageSize,
            offset: this.currentPage * this.pageSize
        });

        if (attackType) params.append('attack_type', attackType);
        if (severity) params.append('severity', severity);
        if (unresolvedOnly) params.append('resolved_only', 'true');

        const response = await fetch(`/api/attacks/logs?${params}`);
        const data = await response.json();
        
        this.renderAttackLogs(data.attacks);
    }

    updateStats(stats) {
        document.getElementById('attack-stat-total').textContent = 
            stats.total_attacks.toLocaleString();
        document.getElementById('attack-stat-critical').textContent = 
            stats.critical_attacks.toLocaleString();
        document.getElementById('attack-stat-high').textContent = 
            (stats.severity_distribution.find(s => s.severity === 'HIGH')?.count || 0).toLocaleString();
        document.getElementById('attack-stat-unresolved').textContent = 
            stats.unresolved_attacks.toLocaleString();

        this.renderAttackTypes(stats.attack_types);
        this.renderTopAttackers(stats.top_attackers);
    }

    renderAttackTypes(types) {
        const container = document.getElementById('attack-types-chart');
        
        if (!types || types.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">No attack data</p>';
            return;
        }

        const maxCount = Math.max(...types.map(t => t.count));
        
        container.innerHTML = types.map(type => {
            const percentage = (type.count / maxCount) * 100;
            return `
                <div class="mb-3">
                    <div class="flex justify-between text-sm mb-1">
                        <span>${type.type}</span>
                        <span class="font-bold">${type.count}</span>
                    </div>
                    <div class="w-full bg-gray-700 rounded-full h-2">
                        <div class="bg-red-500 h-2 rounded-full" style="width: ${percentage}%"></div>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderTopAttackers(attackers) {
        const container = document.getElementById('top-attackers-list');
        
        if (!attackers || attackers.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">No attacker data</p>';
            return;
        }

        container.innerHTML = attackers.slice(0, 5).map(attacker => `
            <div class="flex items-center justify-between p-3 bg-gray-700 rounded-lg hover:bg-gray-600 transition">
                <div class="flex items-center space-x-3">
                    <i class="fas fa-skull-crossbones text-red-500"></i>
                    <div>
                        <p class="font-mono text-sm">${attacker.ip}</p>
                        <p class="text-xs text-gray-400">${attacker.count} attack attempts</p>
                    </div>
                </div>
                <span class="text-red-500 font-bold">${attacker.count}</span>
            </div>
        `).join('');
    }

    renderAttackLogs(logs) {
        const tbody = document.getElementById('attack-logs-tbody');
        
        if (logs.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center py-8 text-gray-500">No attacks detected</td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = logs.map(log => `
            <tr class="fade-in ${this.getSeverityRowClass(log.severity)}">
                <td class="text-xs whitespace-nowrap">${formatTimestamp(log.timestamp)}</td>
                <td>
                    <span class="badge ${this.getSeverityBadge(log.severity)}">
                        ${this.getSeverityIcon(log.severity)} ${log.severity}
                    </span>
                </td>
                <td>
                    <span class="text-sm font-semibold">${log.attack_type}</span>
                </td>
                <td class="font-mono text-sm">${log.source_ip}</td>
                <td class="text-sm truncate max-w-xs" title="${log.target_path || '-'}">
                    ${log.target_path || '-'}
                </td>
                <td class="text-sm text-gray-300">${log.description}</td>
                <td>
                    ${log.resolved 
                        ? '<span class="badge badge-success"><i class="fas fa-check"></i> Resolved</span>'
                        : '<span class="badge badge-warning"><i class="fas fa-clock"></i> Pending</span>'
                    }
                </td>
                <td>
                    ${!log.resolved 
                        ? `<button onclick="attackMonitor.resolveAttack(${log.id})" 
                             class="text-xs bg-green-600 hover:bg-green-700 px-2 py-1 rounded">
                             <i class="fas fa-check-circle"></i> Mark Resolved
                           </button>`
                        : ''
                    }
                </td>
            </tr>
        `).join('');
    }

    getSeverityBadge(severity) {
        const badges = {
            'CRITICAL': 'badge-danger',
            'HIGH': 'badge-warning',
            'MEDIUM': 'badge-info',
            'LOW': 'badge-success'
        };
        return badges[severity] || 'badge-info';
    }

    getSeverityIcon(severity) {
        const icons = {
            'CRITICAL': '<i class="fas fa-circle-xmark"></i>',
            'HIGH': '<i class="fas fa-exclamation-circle"></i>',
            'MEDIUM': '<i class="fas fa-info-circle"></i>',
            'LOW': '<i class="fas fa-check-circle"></i>'
        };
        return icons[severity] || '<i class="fas fa-circle"></i>';
    }

    getSeverityRowClass(severity) {
        if (severity === 'CRITICAL') return 'bg-red-900 bg-opacity-20';
        if (severity === 'HIGH') return 'bg-orange-900 bg-opacity-10';
        return '';
    }

    showCriticalAlert(stats) {
        const alertDiv = document.getElementById('critical-alert');
        const messageDiv = document.getElementById('critical-message');
        
        if (stats.critical_attacks > 0) {
            alertDiv.classList.remove('hidden');
            messageDiv.textContent = `${stats.critical_attacks} critical attack(s) detected in the last 24 hours. Immediate action required!`;
        } else {
            alertDiv.classList.add('hidden');
        }
    }

    async resolveAttack(attackId) {
        try {
            const response = await fetch(`/api/attacks/${attackId}/resolve`, {
                method: 'POST'
            });
            
            if (response.ok) {
                console.log(`Attack ${attackId} marked as resolved`);
                await this.loadData();
            }
        } catch (error) {
            console.error('Error resolving attack:', error);
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

let attackMonitor = null;

function initAttackMonitor() {
    if (!attackMonitor) {
        attackMonitor = new AttackMonitor();
    }
    attackMonitor.init();
}

function stopAttackMonitor() {
    if (attackMonitor) {
        attackMonitor.stop();
    }
}