// Main Application
let currentTab = 'overview';

function switchTab(tabName) {
    // Stop current tab
    if (currentTab === 'overview') {
        stopDashboard();
    } else if (currentTab === 'attacks') {
        stopAttackMonitor();
    } else if (currentTab === 'ssh') {
        stopSSHMonitor();
    } else if (currentTab === 'nginx') {
        stopNginxMonitor();
    }

    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('border-blue-500', 'text-blue-500');
        btn.classList.add('border-transparent', 'text-gray-400');
    });

    const activeBtn = document.getElementById(`tab-${tabName}`);
    activeBtn.classList.remove('border-transparent', 'text-gray-400');
    activeBtn.classList.add('border-blue-500', 'text-blue-500');

    // Show/hide tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });

    document.getElementById(`content-${tabName}`).classList.remove('hidden');

    // Initialize new tab
    currentTab = tabName;

    if (tabName === 'overview') {
        initDashboard();
    } else if (tabName === 'attacks') {
        initAttackMonitor();
    } else if (tabName === 'ssh') {
        initSSHMonitor();
    } else if (tabName === 'nginx') {
        initNginxMonitor();
    }
}

// Initialize app on load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Mini SOC Dashboard initialized');
    
    // Check API health - gunakan endpoint yang ada
    fetch('/api/ssh/stats?hours=1')
        .then(res => res.json())
        .then(data => {
            console.log('API Status: Connected');
            console.log('Initial data:', data);
            
            // Load attack summary for badge
            updateAttackBadge();
            
            // Start with overview tab
            switchTab('overview');
        })
        .catch(error => {
            console.error('API connection failed:', error);
            alert('Failed to connect to backend API. Please check if the backend is running.');
        });
});

// Global error handler
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
});

// Update attack badge periodically
async function updateAttackBadge() {
    try {
        const response = await fetch('/api/attacks/summary?hours=24');
        const data = await response.json();
        
        const badge = document.getElementById('attack-badge');
        if (data.total_attacks > 0) {
            badge.textContent = data.total_attacks;
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }
    } catch (error) {
        console.error('Error updating attack badge:', error);
    }
}

// Update badge every 30 seconds
setInterval(updateAttackBadge, 30000);

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Alt+1: Overview
    if (e.altKey && e.key === '1') {
        e.preventDefault();
        switchTab('overview');
    }
    // Alt+2: Attacks
    else if (e.altKey && e.key === '2') {
        e.preventDefault();
        switchTab('attacks');
    }
    // Alt+3: SSH
    else if (e.altKey && e.key === '3') {
        e.preventDefault();
        switchTab('ssh');
    }
    // Alt+4: Nginx
    else if (e.altKey && e.key === '4') {
        e.preventDefault();
        switchTab('nginx');
    }
});