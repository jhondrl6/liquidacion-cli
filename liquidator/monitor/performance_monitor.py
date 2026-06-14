"""
Performance Monitor - Performance tracking and optimization monitoring.
Monitors calculation performance, resource usage, and bottlenecks.
"""

import logging
import threading
import time
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import psutil

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitors system performance and provides optimization insights."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.enabled = self.config.get('performance_monitoring', True)
        self.performance_data = []
        self.alerts = []
        self._lock = threading.Lock()

        # Performance thresholds
        self.slow_calculation_threshold = self.config.get('slow_calculation_ms', 2000)
        self.memory_warning_threshold = self.config.get('memory_warning_percent', 80)
        self.cpu_warning_threshold = self.config.get('cpu_warning_percent', 85)

    def start_monitoring(self, operation_name: str) -> None:
        """Start monitoring an operation."""
        if not self.enabled:
            return

        monitoring_data = {
            'operation': operation_name,
            'start_time': time.time(),
            'start_memory': psutil.Process().memory_info().rss / (1024 * 1024),  # MB
            'start_cpu': psutil.cpu_percent()
        }

        self._save_monitoring_state(monitoring_data)

    def end_monitoring(self, operation_name: str, status: str = 'SUCCESS', metadata: dict | None = None) -> None:
        """End monitoring an operation and record performance data."""
        if not self.enabled:
            return

        current_state = self._get_monitoring_state(operation_name)
        if not current_state:
            logger.warning(f"No monitoring state found for {operation_name}")
            return

        end_time = time.time()
        duration_ms = (end_time - current_state['start_time']) * 1000

        end_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
        memory_change_mb = end_memory - current_state['start_memory']

        end_cpu = psutil.cpu_percent()

        performance_record = {
            'operation': operation_name,
            'timestamp': datetime.now().isoformat(),
            'duration_ms': duration_ms,
            'status': status,
            'start_memory_mb': current_state['start_memory'],
            'end_memory_mb': end_memory,
            'memory_change_mb': memory_change_mb,
            'start_cpu_percent': current_state['start_cpu'],
            'end_cpu_percent': end_cpu,
            'metadata': metadata or {}
        }

        with self._lock:
            self.performance_data.append(performance_record)

            # Keep only last 1000 records to prevent memory issues
            if len(self.performance_data) > 1000:
                self.performance_data = self.performance_data[-1000:]

        self._check_performance_alerts(performance_record)

    def _save_monitoring_state(self, monitoring_data: dict) -> None:
        """Save monitoring state for operation."""
        # Simple implementation - in production, use thread-local storage
        if not hasattr(self, '_monitoring_states'):
            self._monitoring_states = {}
        self._monitoring_states[monitoring_data['operation']] = monitoring_data

    def _get_monitoring_state(self, operation_name: str) -> dict | None:
        """Get saved monitoring state for operation."""
        if not hasattr(self, '_monitoring_states'):
            return None
        return self._monitoring_states.get(operation_name)

    def _check_performance_alerts(self, performance_record: dict) -> None:
        """Check performance against thresholds and generate alerts."""
        alerts = []

        # Check duration
        if performance_record['duration_ms'] > self.slow_calculation_threshold:
            alerts.append({
                'type': 'SLOW_OPERATION',
                'operation': performance_record['operation'],
                'duration_ms': performance_record['duration_ms'],
                'threshold_ms': self.slow_calculation_threshold,
                'timestamp': performance_record['timestamp']
            })

        # Check memory increase
        if performance_record['memory_change_mb'] > 100:  # 100MB increase
            alerts.append({
                'type': 'MEMORY_INCREASE',
                'operation': performance_record['operation'],
                'memory_change_mb': performance_record['memory_change_mb'],
                'timestamp': performance_record['timestamp']
            })

        # Add to alerts list
        with self._lock:
            self.alerts.extend(alerts)
            # Keep only last 100 alerts
            if len(self.alerts) > 100:
                self.alerts = self.alerts[-100:]

    def get_performance_summary(self, hours_back: int = 24) -> dict[str, Any]:
        """Get performance summary for specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)

        recent_operations = [
            op for op in self.performance_data
            if datetime.fromisoformat(op['timestamp']) > cutoff_time
        ]

        if not recent_operations:
            return {
                'time_period_hours': hours_back,
                'total_operations': 0,
                'message': 'No performance data available'
            }

        # Calculate statistics
        durations = [op['duration_ms'] for op in recent_operations]
        memory_changes = [op['memory_change_mb'] for op in recent_operations]

        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        min_duration = min(durations) if durations else 0

        avg_memory_change = sum(memory_changes) / len(memory_changes) if memory_changes else 0

        # Operation counts by status
        status_counts = {}
        for op in recent_operations:
            status = op['status']
            status_counts[status] = status_counts.get(status, 0) + 1

        # Slow operations
        slow_ops = [
            op for op in recent_operations
            if op['duration_ms'] > self.slow_calculation_threshold
        ]

        # Recent alerts
        recent_alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']) > cutoff_time
        ]

        return {
            'time_period_hours': hours_back,
            'total_operations': len(recent_operations),
            'operation_stats': {
                'avg_duration_ms': round(avg_duration, 2),
                'min_duration_ms': min_duration,
                'max_duration_ms': max_duration,
                'avg_memory_change_mb': round(avg_memory_change, 2)
            },
            'operation_status_counts': status_counts,
            'slow_operations': {
                'count': len(slow_ops),
                'percentage': round((len(slow_ops) / len(recent_operations)) * 100, 2)
            },
            'performance_alerts': {
                'count': len(recent_alerts),
                'types': {alert['type']: recent_alerts.count(alert) for alert in recent_alerts}
            },
            'top_slow_operations': [
                {
                    'operation': op['operation'],
                    'duration_ms': op['duration_ms'],
                    'timestamp': op['timestamp']
                }
                for op in sorted(recent_operations, key=lambda x: x['duration_ms'], reverse=True)[:5]
            ]
        }

    def get_current_system_status(self) -> dict[str, Any]:
        """Get current system performance status."""
        current_process = psutil.Process()
        memory_info = current_process.memory_info()

        return {
            'timestamp': datetime.now().isoformat(),
            'process': {
                'pid': current_process.pid,
                'memory_rss_mb': memory_info.rss / (1024 * 1024),
                'memory_vms_mb': memory_info.vms / (1024 * 1024),
                'cpu_percent': current_process.cpu_percent(),
                'num_threads': current_process.num_threads(),
                'create_time': datetime.fromtimestamp(current_process.create_time()).isoformat()
            },
            'system': {
                'cpu_percent': psutil.cpu_percent(),
                'memory_total_gb': psutil.virtual_memory().total / (1024**3),
                'memory_available_gb': psutil.virtual_memory().available / (1024**3),
                'memory_percent_used': psutil.virtual_memory().percent,
                'disk_usage_gb': psutil.disk_usage('/').used / (1024**3),
                'disk_percent_used': (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
            }
        }

    def generate_performance_report(self, output_file: str | None = None) -> str:
        """Generate comprehensive performance report."""
        summary = self.get_performance_summary(24)
        current_status = self.get_current_system_status()

        report_lines = [
            "# Performance Report - Colombia Payroll Settlement System",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "## Current System Status",
            f"- Process PID: {current_status['process']['pid']}",
            f"- Memory Usage: {current_status['process']['memory_rss_mb']:.1f} MB",
            f"- CPU Usage: {current_status['process']['cpu_percent']:.1f}%",
            f"- System CPU: {current_status['system']['cpu_percent']:.1f}%",
            f"- System Memory: {current_status['system']['memory_percent_used']:.1f}% used",
            f"- System Disk: {current_status['system']['disk_percent_used']:.1f}% used",
            "",
            "## 24-Hour Performance Summary",
            f"- Total Operations: {summary['total_operations']}",
            f"- Average Duration: {summary['operation_stats']['avg_duration_ms']} ms",
            f"- Max Duration: {summary['operation_stats']['max_duration_ms']} ms",
            f"- Slow Operations: {summary['slow_operations']['count']} ({summary['slow_operations']['percentage']}%)",
            "",
            "## Operation Status Distribution",
        ]

        for status, count in summary['operation_status_counts'].items():
            report_lines.append(f"- {status}: {count}")

        report_lines.extend([
            "",
            "## Top 5 Slowest Operations",
        ])

        for i, op in enumerate(summary['top_slow_operations'], 1):
            report_lines.append(f"{i}. {op['operation']}: {op['duration_ms']} ms ({op['timestamp']})")

        recent_alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']) > datetime.now() - timedelta(hours=24)
        ]

        if recent_alerts:
            report_lines.extend([
                "",
                f"## Recent Performance Alerts ({len(recent_alerts)})",
            ])

            for alert in recent_alerts[-10:]:  # Last 10 alerts
                report_lines.append(f"- {alert['type']}: {alert['operation']} at {alert['timestamp']}")
        else:
            report_lines.append("\n## Recent Performance Alerts: None")

        report_content = "\n".join(report_lines)

        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)

        return report_content

    def monitor_function(self, operation_name: str) -> Callable:
        """Decorator to monitor function performance."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                self.start_monitoring(operation_name)
                result = None
                try:
                    result = func(*args, **kwargs)
                    status = 'SUCCESS'
                    metadata = {
                        'args_count': len(args),
                        'kwargs_count': len(kwargs)
                    }
                except Exception as e:
                    result = None
                    status = 'ERROR'
                    metadata = {
                        'error': str(e),
                        'error_type': type(e).__name__
                    }
                finally:
                    self.end_monitoring(operation_name, status, metadata)
                return result
            return wrapper
        return decorator

    def cleanup_old_data(self, days_to_keep: int = 30) -> None:
        """Clean up performance data older than specified days."""
        cutoff_time = datetime.now() - timedelta(days=days_to_keep)

        with self._lock:
            self.performance_data = [
                op for op in self.performance_data
                if datetime.fromisoformat(op['timestamp']) > cutoff_time
            ]

            self.alerts = [
                alert for alert in self.alerts
                if datetime.fromisoformat(alert['timestamp']) > cutoff_time
            ]

        logger.info(f"Cleaned up performance data older than {days_to_keep} days")
