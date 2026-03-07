#!/usr/bin/env python3
"""
RustChain Star Growth Dashboard - HTML Generator
Generates an interactive HTML dashboard with charts
"""

import sqlite3
from datetime import datetime, timedelta
from star_tracker import StarTracker
import json

class DashboardGenerator:
    def __init__(self, db_path: str = "star_tracker.db"):
        self.db_path = db_path
        self.tracker = StarTracker(db_path)
    
    def generate_html(self, output_path: str = "dashboard.html"):
        """Generate interactive HTML dashboard"""
        
        # Get data
        stats_7d = self.tracker.get_growth_stats(days=7)
        stats_30d = self.tracker.get_growth_stats(days=30)
        historical = self.tracker.get_historical_data(days=30)
        
        # Get top repos by current stars
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT repo_name, stars FROM star_snapshots
            WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM star_snapshots)
            ORDER BY stars DESC
            LIMIT 20
        """)
        top_repos = cursor.fetchall()
        conn.close()
        
        # Prepare chart data
        chart_labels = [d['date'] for d in historical]
        chart_data = [d['stars'] for d in historical]
        
        # HTML template with embedded Chart.js
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RustChain GitHub Star Growth Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            padding: 40px 20px;
            margin-bottom: 30px;
        }}
        header h1 {{
            font-size: 2.5em;
            background: linear-gradient(90deg, #ff6b35, #f7931e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        header p {{
            color: #888;
            font-size: 1.1em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: transform 0.2s;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.08);
        }}
        .stat-label {{
            color: #888;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #fff;
        }}
        .stat-change {{
            font-size: 1em;
            margin-top: 5px;
        }}
        .positive {{
            color: #4ade80;
        }}
        .negative {{
            color: #f87171;
        }}
        .chart-container {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 30px;
        }}
        .chart-title {{
            font-size: 1.3em;
            margin-bottom: 20px;
            color: #fff;
        }}
        .two-column {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        th {{
            color: #888;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.8em;
            letter-spacing: 1px;
        }}
        tr:hover {{
            background: rgba(255, 255, 255, 0.05);
        }}
        .repo-name {{
            color: #60a5fa;
            font-weight: 500;
        }}
        .growth-badge {{
            background: rgba(74, 222, 128, 0.2);
            color: #4ade80;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            font-size: 0.9em;
        }}
        .rust-badge {{
            display: inline-block;
            background: #ff6b35;
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 10px;
        }}
        @media (max-width: 768px) {{
            .two-column {{
                grid-template-columns: 1fr;
            }}
            header h1 {{
                font-size: 1.8em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🦀 RustChain Star Growth Dashboard</h1>
            <p>Tracking GitHub stars across all Scottcjn repositories</p>
            <span class="rust-badge">Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Repositories</div>
                <div class="stat-value">{stats_7d['repo_count']}</div>
                <div class="stat-change">Active projects</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Stars</div>
                <div class="stat-value">{stats_7d['total_current']:,}</div>
                <div class="stat-change positive">+{stats_7d['total_growth']:,} (7d)</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">30-Day Growth</div>
                <div class="stat-value">+{stats_30d['total_growth']:,}</div>
                <div class="stat-change positive">🚀 Growing fast</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Daily Average</div>
                <div class="stat-value">+{stats_7d['total_growth'] // 7 if stats_7d['total_growth'] > 0 else 0}</div>
                <div class="stat-change">Stars per day</div>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">📈 Star Growth Over Time (30 Days)</div>
            <canvas id="growthChart" height="100"></canvas>
        </div>
        
        <div class="two-column">
            <div class="chart-container">
                <div class="chart-title">🏆 Top Growing Repos (7 Days)</div>
                <table>
                    <thead>
                        <tr>
                            <th>Repository</th>
                            <th>Stars</th>
                            <th>Growth</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f"<tr><td class='repo-name'>{repo['name'][:30]}</td><td>{repo['current']:,}</td><td><span class='growth-badge'>+{repo['growth']}</span></td></tr>" for repo in stats_7d['top_growers'][:10])}
                    </tbody>
                </table>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">⭐ Top Repositories by Stars</div>
                <table>
                    <thead>
                        <tr>
                            <th>Repository</th>
                            <th>Stars</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f"<tr><td class='repo-name'>{repo[0][:35]}</td><td>{repo[1]:,}</td></tr>" for repo in top_repos[:15])}
                    </tbody>
                </table>
            </div>
        </div>
        
        <footer>
            <p>🦀 RustChain Star Tracker • Built with Python + SQLite + Chart.js</p>
            <p>Data source: GitHub API • Auto-updates daily</p>
        </footer>
    </div>
    
    <script>
        const ctx = document.getElementById('growthChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(chart_labels)},
                datasets: [{{
                    label: 'Total Stars',
                    data: {json.dumps(chart_data)},
                    borderColor: '#ff6b35',
                    backgroundColor: 'rgba(255, 107, 53, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#ff6b35',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    x: {{
                        grid: {{
                            color: 'rgba(255, 255, 255, 0.1)'
                        }},
                        ticks: {{
                            color: '#888'
                        }}
                    }},
                    y: {{
                        grid: {{
                            color: 'rgba(255, 255, 255, 0.1)'
                        }},
                        ticks: {{
                            color: '#888'
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
        
        with open(output_path, 'w') as f:
            f.write(html)
        
        print(f"Dashboard generated: {output_path}")
        return output_path


if __name__ == "__main__":
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else "star_tracker.db"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "dashboard.html"
    
    generator = DashboardGenerator(db_path)
    generator.generate_html(output_path)
    print(f"\nOpen {output_path} in your browser to view the dashboard!")