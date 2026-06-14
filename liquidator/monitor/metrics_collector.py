"""
Metrics Collector - Collects and tracks system usage metrics.
Optimized for production monitoring and alerting.
"""

import json
import logging
import threading
from datetime import datetime
from pathlib import Path

import psutil

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects system and application metrics for monitoring."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.enabled = self.config.get('metrics_enabled', True)
        self.metrics_file = Path("metrics/system_metrics.json")
        self.session_metrics = {
            'session_start': datetime.now().isoformat(),
            'calculations_count': 0,
            'errors_count': 0,
            'compliance_failures': 0,
            'overrides_used': 0,
            'performance_samples': [],
            'memory_peaks': [],
            'cpu_usage_samples': []
        }
        self._lock = threading.Lock()

    def start_session(self) -> None:
        """Initialize monitoring session."""
        if not self.enabled:
            return

        self.session_metrics = {
            'session_start': datetime.now().isoformat(),
            'calculations_count': 0,
            'errors_count': 0,
            'compliance_failures': 0,
            'overrides_used': 0,
            'performance_samples': [],
            'memory_peaks': [],
            'cpu_usage_samples': []
        }
        logger.info("Metrics collector session started")

    def record_calculation(self, calculation_data: dict) -> None:
        """Record metrics for a calculation execution."""
        if not self.enabled:
            return

        with self._lock:
            self.session_metrics['calculations_count'] += 1
            self.session_metrics['performance_samples'].append({
                'timestamp': datetime.now().isoformat(),
                'duration_ms': calculation_data.get('duration_ms', 0),
                'input_size': calculation_data.get('input_size_bytes', 0),
                'mode': calculation_data.get('mode', 'UNKNOWN'),
                'compliance_status': calculation_data.get('compliance_status', 'UNKNOWN')
            })

        logger.debug(f"Calculation metrics recorded: {calculation_data.get('mode')}")

    def record_error(self, error_data: dict) -> None:
        """Record error metrics."""
        if not self.enabled:
            return

        with self._lock:
            self.session_metrics['errors_count'] += 1
            self.session_metrics['performance_samples'].append({
                'timestamp': datetime.now().isoformat(),
                'event_type': 'ERROR',
                'error_code': error_data.get('error_code', 'UNKNOWN'),
                'error_type': error_data.get('error_type', 'UNKNOWN'),
                'module': error_data.get('module', 'UNKNOWN')
            })

        logger.warning(f"Error recorded: {error_data.get('error_type')}")

    def record_compliance_event(self, event_data: dict) -> None:
        """Record compliance-related metrics."""
        if not self.enabled:
            return

        with self._lock:
            event_type = event_data.get('event_type', 'UNKNOWN')

            if event_type == 'COMPLIANCE_FAILURE':
                self.session_metrics['compliance_failures'] += 1
            elif event_type == 'OVERRIDE_USED':
                self.session_metrics['overrides_used'] += 1

            self.session_metrics['performance_samples'].append({
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'compliance_status': event_data.get('compliance_status', 'UNKNOWN'),
                'rule_id': event_data.get('rule_id', ''),
                'severity': event_data.get('severity', 'MEDIUM')
            })

        logger.info(f"Compliance event recorded: {event_type}")

    def collect_system_metrics(self) -> dict:
        """Collect current system performance metrics."""
        if not self.enabled:
            return {}

        try:
            memory_info = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)

            disk_usage = psutil.disk_usage('/')

            metrics = {
                'timestamp': datetime.now().isoformat(),
                'memory': {
                    'total_gb': memory_info.total / (1024**3),
                    'available_gb': memory_info.available / (1024**3),
                    'used_gb': memory_info.used / (1024**3),
                    'percent_used': memory_info.percent
                },
                'cpu': {
                    'percent_used': cpu_percent,
                    'cores': psutil.cpu_count()
                },
                'disk': {
                    'total_gb': disk_usage.total / (1024**3),
                    'free_gb': disk_usage.free / (1024**3),
                    'used_gb': disk_usage.used / (1024**3),
                    'percent_used': (disk_usage.used / disk_usage.total) * 100
                },
                'process_info': {
                    'pid': psutil.Process().pid,
                    'memory_mb': psutil.Process().memory_info().rss / (1024**2),
                    'cpu_percent': psutil.Process().cpu_percent()
                }
            }

            # Track peaks
            with self._lock:
                self.session_metrics['memory_peaks'].append(metrics['memory']['percent_used'])
                self.session_metrics['cpu_usage_samples'].append(metrics['cpu']['percent_used'])

                # Keep only last 100 samples to avoid memory bloat
                if len(self.session_metrics['memory_peaks']) > 100:
                    self.session_metrics['memory_peaks'] = self.session_metrics['memory_peaks'][-100:]
                if len(self.session_metrics['cpu_usage_samples']) > 100:
                    self.session_metrics['cpu_usage_samples'] = self.session_metrics['cpu_usage_samples'][-100:]

            return metrics

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}

    def get_session_summary(self) -> dict:
        """Get comprehensive session metrics summary."""
        if not self.enabled:
            return {}

        with self._lock:
            session_duration = None
            if self.session_metrics['session_start']:
                start_time = datetime.fromisoformat(self.session_metrics['session_start'])
                session_duration = (datetime.now() - start_time).total_seconds()

            avg_memory = 0
            max_memory = 0
            if self.session_metrics['memory_peaks']:
                avg_memory = sum(self.session_metrics['memory_peaks']) / len(self.session_metrics['memory_peaks'])
                max_memory = max(self.session_metrics['memory_peaks'])

            avg_cpu = 0
            max_cpu = 0
            if self.session_metrics['cpu_usage_samples']:
                avg_cpu = sum(self.session_metrics['cpu_usage_samples']) / len(self.session_metrics['cpu_usage_samples'])
                max_cpu = max(self.session_metrics['cpu_usage_samples'])

            # Find performance stats
            durations = [s.get('duration_ms', 0) for s in self.session_metrics['performance_samples'] if 'duration_ms' in s]
            avg_duration = sum(durations) / len(durations) if durations else 0
            max_duration = max(durations) if durations else 0

            return {
                'session_summary': {
                    'start_time': self.session_metrics['session_start'],
                    'duration_seconds': session_duration,
                    'calculations_count': self.session_metrics['calculations_count'],
                    'errors_count': self.session_metrics['errors_count'],
                    'compliance_failures': self.session_metrics['compliance_failures'],
                    'overrides_used': self.session_metrics['overrides_used']
                },
                'performance_summary': {
                    'avg_duration_ms': round(avg_duration, 2),
                    'max_duration_ms': max_duration,
                    'total_samples': len(self.session_metrics['performance_samples'])
                },
                'resource_summary': {
                    'avg_memory_usage_percent': round(avg_memory, 2),
                    'max_memory_usage_percent': max_memory,
                    'avg_cpu_usage_percent': round(avg_cpu, 2),
                    'max_cpu_usage_percent': max_cpu
                }
            }

    def save_metrics(self) -> None:
        """Save session metrics to file for analysis."""
        if not self.enabled:
            return

        try:
            self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

            # Add current system metrics
            current_system = self.collect_system_metrics()
            session_summary = self.get_session_summary()

            final_metrics = {
                'session_end': datetime.now().isoformat(),
                'session_metrics': self.session_metrics,
                'current_system': current_system,
                'session_summary': session_summary
            }

            # Append to metrics file (or create new)
            if self.metrics_file.exists():
                with open(self.metrics_file) as f:
                    existing_data = json.load(f)
                existing_data['sessions'].append(final_metrics)
            else:
                existing_data = {
                    'created': datetime.now().isoformat(),
                    'sessions': [final_metrics]
                }

            with open(self.metrics_file, 'w') as f:
                json.dump(existing_data, f, indent=2)

            logger.info(f"Session metrics saved to {self.metrics_file}")

        except Exception as e:
            logger.error(f"Error saving metrics: {e}")

    def check_alert_thresholds(self) -> list[str]:
        """Check metrics against alert thresholds and return alerts."""
        alerts = []

        if not self.enabled:
            return alerts

        metrics_summary = self.get_session_summary()
        resource_summary = metrics_summary.get('resource_summary', {})
        session_summary = metrics_summary.get('session_summary', {})

        # Memory alerts
        if resource_summary.get('max_memory_usage_percent', 0) > 90:
            alerts.append("HIGH_MEMORY_USAGE: Memory usage exceeded 90%")

        # CPU alerts
        if resource_summary.get('max_cpu_usage_percent', 0) > 95:
            alerts.append("HIGH_CPU_USAGE: CPU usage exceeded 95%")

        # Error rate alerts
        if session_summary.get('calculations_count', 0) > 0:
            error_rate = session_summary.get('errors_count', 0) / session_summary.get('calculations_count', 1) * 100
            if error_rate > 10:
                alerts.append(f"HIGH_ERROR_RATE: Error rate {error_rate:.1f}% exceeded 10%")

        # Compliance failure alerts
        if session_summary.get('compliance_failures', 0) > 0:
            alerts.append(f"COMPLIANCE_FAILURES: {session_summary['compliance_failures']} compliance failures detected")

        return alerts
