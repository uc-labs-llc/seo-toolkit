<?php
require_once 'config.php';

class AnalyticsDashboard {
    private $conn;

    public function __construct($db) {
        $this->conn = $db;
    }

    public function getSummaryStats() {
        $query = "
            SELECT 
                COUNT(*) as total_events,
                COUNT(DISTINCT session_id) as total_sessions,
                COUNT(DISTINCT location) as total_pages,
                COUNT(DISTINCT DATE(event_timestamp)) as total_days,
                AVG(load_time) as avg_load_time,
                AVG(first_contentful_paint) as avg_fcp
            FROM analytics_events 
            WHERE action = 'PAGE_LOAD'
        ";
        $stmt = $this->conn->prepare($query);
        $stmt->execute();
        return $stmt->fetch(PDO::FETCH_ASSOC);
    }

    public function getEventsByAction() {
        $query = "
            SELECT action, COUNT(*) as count 
            FROM analytics_events 
            GROUP BY action 
            ORDER BY count DESC
        ";
        $stmt = $this->conn->prepare($query);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function getSessionsByHour() {
        $query = "
            SELECT 
                EXTRACT(HOUR FROM event_timestamp) as hour,
                COUNT(DISTINCT session_id) as session_count
            FROM analytics_events 
            WHERE session_id IS NOT NULL
            GROUP BY EXTRACT(HOUR FROM event_timestamp)
            ORDER BY hour
        ";
        $stmt = $this->conn->prepare($query);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function getDeviceBreakdown() {
        $query = "
            SELECT 
                CASE 
                    WHEN user_agent LIKE '%Mobile%' THEN 'Mobile'
                    ELSE 'Desktop'
                END as device_type,
                COUNT(DISTINCT session_id) as session_count,
                COUNT(*) as event_count,
                AVG(load_time) as avg_load_time
            FROM analytics_events 
            WHERE session_id IS NOT NULL
            GROUP BY 
                CASE 
                    WHEN user_agent LIKE '%Mobile%' THEN 'Mobile'
                    ELSE 'Desktop'
                END
        ";
        $stmt = $this->conn->prepare($query);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function getPagePerformance() {
        $query = "
            SELECT 
                location,
                page_title,
                COUNT(*) as load_count,
                AVG(load_time) as avg_load_time,
                AVG(dom_ready_time) as avg_dom_time,
                AVG(first_contentful_paint) as avg_fcp
            FROM analytics_events 
            WHERE action = 'PAGE_LOAD' AND load_time > 0
            GROUP BY location, page_title
            ORDER BY load_count DESC
            LIMIT 10
        ";
        $stmt = $this->conn->prepare($query);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function getDailyActivity() {
        $query = "
            SELECT 
                DATE(event_timestamp) as date,
                COUNT(*) as total_events,
                COUNT(DISTINCT session_id) as unique_sessions
            FROM analytics_events 
            GROUP BY DATE(event_timestamp)
            ORDER BY date DESC
            LIMIT 14
        ";
        $stmt = $this->conn->prepare($query);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
}

$database = new Database();
$db = $database->getConnection();
$dashboard = new AnalyticsDashboard($db);

$summary = $dashboard->getSummaryStats();
$eventsByAction = $dashboard->getEventsByAction();
$sessionsByHour = $dashboard->getSessionsByHour();
$deviceBreakdown = $dashboard->getDeviceBreakdown();
$pagePerformance = $dashboard->getPagePerformance();
$dailyActivity = $dashboard->getDailyActivity();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f6fa;
            color: #333;
        }
        .dashboard {
            display: grid;
            grid-template-columns: 250px 1fr;
            min-height: 100vh;
        }
        .sidebar {
            background: #2c3e50;
            color: white;
            padding: 20px;
            position: fixed;
            width: 250px;
            height: 100vh;
            overflow-y: auto;
        }
        .sidebar h2 {
            margin-bottom: 30px;
            text-align: center;
            color: #3498db;
        }
        .sidebar nav ul {
            list-style: none;
        }
        .sidebar nav ul li {
            margin-bottom: 10px;
        }
        .sidebar nav ul li a {
            color: #bdc3c7;
            text-decoration: none;
            padding: 10px 15px;
            display: block;
            border-radius: 5px;
            transition: all 0.3s;
        }
        .sidebar nav ul li a:hover,
        .sidebar nav ul li a.active {
            background: #34495e;
            color: #3498db;
        }
        .main-content {
            grid-column: 2;
            padding: 20px;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-card h3 {
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 10px;
        }
        .stat-card .value {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }
        .chart-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .chart-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .chart-card h3 {
            margin-bottom: 15px;
            color: #2c3e50;
        }
        .chart-container {
            height: 300px;
            position: relative;
        }
        .table-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
        }
        tr:hover {
            background: #f8f9fa;
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <!-- Sidebar -->
        <div class="sidebar">
            <h2>📊 Analytics Dashboard</h2>
            <nav>
                <ul>
                    <li><a href="dashboard.php" class="active">Overview</a></li>
                    <li><a href="sessions.php">Sessions</a></li>
                    <li><a href="performance.php">Performance</a></li>
                    <li><a href="users.php">User Analysis</a></li>
                    <li><a href="import_analytics.php">Import Data</a></li>
                    <li><a href="view_data.php">Raw Data</a></li>
                </ul>
            </nav>
        </div>

        <!-- Main Content -->
        <div class="main-content">
            <div class="header">
                <h1>Analytics Overview</h1>
                <p>Comprehensive view of your website analytics data</p>
            </div>

            <!-- Summary Stats -->
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total Events</h3>
                    <div class="value"><?php echo number_format($summary['total_events']); ?></div>
                </div>
                <div class="stat-card">
                    <h3>Total Sessions</h3>
                    <div class="value"><?php echo number_format($summary['total_sessions']); ?></div>
                </div>
                <div class="stat-card">
                    <h3>Unique Pages</h3>
                    <div class="value"><?php echo number_format($summary['total_pages']); ?></div>
                </div>
                <div class="stat-card">
                    <h3>Avg Load Time</h3>
                    <div class="value"><?php echo round($summary['avg_load_time'] ?? 0, 2); ?>ms</div>
                </div>
            </div>

            <!-- Charts Grid -->
            <div class="chart-grid">
                <!-- Events by Action -->
                <div class="chart-card">
                    <h3>Events by Action Type</h3>
                    <div class="chart-container">
                        <canvas id="actionsChart"></canvas>
                    </div>
                </div>

                <!-- Sessions by Hour -->
                <div class="chart-card">
                    <h3>Sessions by Hour of Day</h3>
                    <div class="chart-container">
                        <canvas id="sessionsHourChart"></canvas>
                    </div>
                </div>

                <!-- Device Breakdown -->
                <div class="chart-card">
                    <h3>Device Breakdown</h3>
                    <div class="chart-container">
                        <canvas id="deviceChart"></canvas>
                    </div>
                </div>

                <!-- Daily Activity -->
                <div class="chart-card">
                    <h3>Daily Activity (Last 14 Days)</h3>
                    <div class="chart-container">
                        <canvas id="dailyActivityChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Page Performance Table -->
            <div class="table-card">
                <h3>Page Performance Metrics</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Page</th>
                            <th>Load Count</th>
                            <th>Avg Load Time</th>
                            <th>Avg DOM Ready</th>
                            <th>Avg First Paint</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($pagePerformance as $page): ?>
                        <tr>
                            <td><?php echo htmlspecialchars($page['page_title'] ?: $page['location']); ?></td>
                            <td><?php echo number_format($page['load_count']); ?></td>
                            <td><?php echo round($page['avg_load_time'], 2); ?>ms</td>
                            <td><?php echo round($page['avg_dom_time'] ?? 0, 2); ?>ms</td>
                            <td><?php echo round($page['avg_fcp'] ?? 0, 2); ?>ms</td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        // Events by Action Chart
        const actionsCtx = document.getElementById('actionsChart').getContext('2d');
        new Chart(actionsCtx, {
            type: 'doughnut',
            data: {
                labels: <?php echo json_encode(array_column($eventsByAction, 'action')); ?>,
                datasets: [{
                    data: <?php echo json_encode(array_column($eventsByAction, 'count')); ?>,
                    backgroundColor: [
                        '#3498db', '#2ecc71', '#e74c3c', '#f39c12', 
                        '#9b59b6', '#1abc9c', '#34495e', '#d35400'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });

        // Sessions by Hour Chart
        const sessionsHourCtx = document.getElementById('sessionsHourChart').getContext('2d');
        new Chart(sessionsHourCtx, {
            type: 'bar',
            data: {
                labels: <?php echo json_encode(array_column($sessionsByHour, 'hour')); ?>,
                datasets: [{
                    label: 'Sessions',
                    data: <?php echo json_encode(array_column($sessionsByHour, 'session_count')); ?>,
                    backgroundColor: '#3498db',
                    borderColor: '#2980b9',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // Device Breakdown Chart
        const deviceCtx = document.getElementById('deviceChart').getContext('2d');
        new Chart(deviceCtx, {
            type: 'pie',
            data: {
                labels: <?php echo json_encode(array_column($deviceBreakdown, 'device_type')); ?>,
                datasets: [{
                    data: <?php echo json_encode(array_column($deviceBreakdown, 'session_count')); ?>,
                    backgroundColor: ['#3498db', '#2ecc71']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });

        // Daily Activity Chart
        const dailyCtx = document.getElementById('dailyActivityChart').getContext('2d');
        new Chart(dailyCtx, {
            type: 'line',
            data: {
                labels: <?php echo json_encode(array_column($dailyActivity, 'date')); ?>,
                datasets: [
                    {
                        label: 'Total Events',
                        data: <?php echo json_encode(array_column($dailyActivity, 'total_events')); ?>,
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Unique Sessions',
                        data: <?php echo json_encode(array_column($dailyActivity, 'unique_sessions')); ?>,
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    </script>
</body>
</html>
