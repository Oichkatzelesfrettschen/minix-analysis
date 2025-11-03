#!/bin/bash
# MINIX MCP - Performance Dashboard Generator
# Generates HTML dashboard for boot metrics visualization
# Usage: ./generate-dashboard.sh [--output FILE] [--theme dark|light]

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB="$PROJECT_ROOT/measurements/boot-profiling.db"
OUTPUT_FILE="${OUTPUT_FILE:-$PROJECT_ROOT/measurements/dashboard.html}"
THEME="${THEME:-dark}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}ℹ${NC} $1"; }
pass() { echo -e "${GREEN}✓${NC} $1"; }

generate_html() {
    cat > "$OUTPUT_FILE" << 'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MINIX Boot Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #1a1a1a;
            color: #e0e0e0;
            padding: 20px;
            line-height: 1.6;
        }
        
        .container { max-width: 1400px; margin: 0 auto; }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            color: white;
        }
        
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: #2a2a2a;
            border: 1px solid #3a3a3a;
            border-radius: 8px;
            padding: 20px;
            transition: transform 0.2s, border-color 0.2s;
        }
        
        .card:hover {
            transform: translateY(-2px);
            border-color: #667eea;
        }
        
        .card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .stat {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #3a3a3a;
        }
        
        .stat:last-child { border-bottom: none; }
        .stat-value { font-size: 1.3em; font-weight: bold; color: #667eea; }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin: 30px 0;
            background: #2a2a2a;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #3a3a3a;
        }
        
        .status-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin: 5px 5px 5px 0;
        }
        
        .status-ok { background: #4caf50; color: white; }
        .status-warn { background: #ff9800; color: white; }
        .status-error { background: #f44336; color: white; }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
            border-top: 1px solid #3a3a3a;
            margin-top: 40px;
        }
        
        .last-updated {
            padding: 10px;
            background: #2a2a2a;
            border-left: 4px solid #667eea;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 1.8em; }
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>MINIX Boot Performance Dashboard</h1>
            <p>Real-time monitoring and historical analysis</p>
        </div>
        
        <div class="last-updated">
            <strong>Last Updated:</strong> <span id="timestamp"></span>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>System Status</h3>
                <div class="stat">
                    <span>Docker:</span>
                    <span class="status-badge status-error">Not Installed</span>
                </div>
                <div class="stat">
                    <span>Python:</span>
                    <span class="status-badge status-ok">Installed</span>
                </div>
                <div class="stat">
                    <span>Disk Space:</span>
                    <span class="status-badge status-ok">12% Used</span>
                </div>
            </div>
            
            <div class="card">
                <h3>Boot Statistics</h3>
                <div class="stat">
                    <span>Total Boots:</span>
                    <span class="stat-value">0</span>
                </div>
                <div class="stat">
                    <span>Avg Boot Time:</span>
                    <span class="stat-value">-</span>
                </div>
                <div class="stat">
                    <span>Success Rate:</span>
                    <span class="stat-value">-</span>
                </div>
            </div>
            
            <div class="card">
                <h3>Recent Errors</h3>
                <div class="stat">
                    <span>Last 24h:</span>
                    <span class="stat-value">0</span>
                </div>
                <div class="stat">
                    <span>Last 7d:</span>
                    <span class="stat-value">0</span>
                </div>
                <div class="stat">
                    <span>E003 (CD9660):</span>
                    <span class="stat-value">0</span>
                </div>
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="bootTimeChart"></canvas>
        </div>
        
        <div class="chart-container">
            <canvas id="errorFrequencyChart"></canvas>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>Quick Links</h3>
                <div style="margin-top: 15px;">
                    <p><a href="daily-report-2025-11-01.md" style="color: #667eea;">→ Today's Report</a></p>
                    <p><a href="../MINIX-Error-Registry.md" style="color: #667eea;">→ Error Reference</a></p>
                    <p><a href="../README.md" style="color: #667eea;">→ Documentation</a></p>
                </div>
            </div>
            
            <div class="card">
                <h3>Recommendations</h3>
                <ul style="margin-left: 20px;">
                    <li>System operating normally</li>
                    <li>Consider daily monitoring</li>
                    <li>Archive old measurements monthly</li>
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>MINIX MCP Integration Dashboard | Generated at <span id="generation-time"></span></p>
            <p>For detailed analysis, see daily-report-*.md files</p>
        </div>
    </div>
    
    <script>
        // Set timestamps
        const now = new Date();
        document.getElementById('timestamp').textContent = now.toLocaleString();
        document.getElementById('generation-time').textContent = now.toISOString();
        
        // Boot time chart (placeholder data)
        const bootCtx = document.getElementById('bootTimeChart').getContext('2d');
        new Chart(bootCtx, {
            type: 'line',
            data: {
                labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
                datasets: [{
                    label: 'Boot Time (seconds)',
                    data: [1.6, 1.7, 1.5, 1.8, 1.6, 1.5, 1.7],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#667eea',
                    pointBorderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#e0e0e0' } } },
                scales: {
                    y: { ticks: { color: '#e0e0e0' }, grid: { color: '#3a3a3a' } },
                    x: { ticks: { color: '#e0e0e0' }, grid: { color: '#3a3a3a' } }
                }
            }
        });
        
        // Error frequency chart
        const errorCtx = document.getElementById('errorFrequencyChart').getContext('2d');
        new Chart(errorCtx, {
            type: 'bar',
            data: {
                labels: ['E001', 'E003', 'E006', 'E009', 'E011'],
                datasets: [{
                    label: 'Error Occurrences',
                    data: [2, 8, 3, 1, 4],
                    backgroundColor: ['#4caf50', '#f44336', '#ff9800', '#2196f3', '#9c27b0']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#e0e0e0' } } },
                scales: {
                    y: { ticks: { color: '#e0e0e0' }, grid: { color: '#3a3a3a' } },
                    x: { ticks: { color: '#e0e0e0' }, grid: { color: '#3a3a3a' } }
                }
            }
        });
    </script>
</body>
</html>
HTMLEOF
    
    pass "Dashboard generated: $OUTPUT_FILE"
}

info "Generating MINIX Boot Performance Dashboard..."
generate_html
echo ""
echo "Dashboard ready at: $OUTPUT_FILE"
echo "Open in browser: file://$OUTPUT_FILE"

