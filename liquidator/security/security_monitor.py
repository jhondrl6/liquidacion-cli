"""
Security Monitor - Tracks security events and monitors for threats.
Detects suspicious activity and implements security policies.
"""

import hashlib
import json
import logging
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class SecurityEvent:
    """Represents a security event."""

    def __init__(self, event_type: str, severity: str, source: str, details: dict[str, Any]):
        self.timestamp = datetime.now()
        self.event_type = event_type
        self.severity = severity  # LOW, MEDIUM, HIGH, CRITICAL
        self.source = source
        self.details = details
        self.event_id = self._generate_event_id()

    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        data = f"{self.timestamp}_{self.event_type}_{self.source}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'severity': self.severity,
            'source': self.source,
            'details': self.details
        }


class SecurityMonitor:
    """Monitors security events and detects threats."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.security_log_path = Path("logs/security.log")
        self.events = deque(maxlen=1000)  # Keep last 1000 events in memory
        self.rate_limits = defaultdict(deque)  # Rate limiting per source
        self.blocked_sources = set()
        self.failed_attempts = defaultdict(int)
        self.security_events_file = Path("audit/security/events.json")

        # Security thresholds
        self.max_login_attempts = self.config.get('max_login_attempts', 5)
        self.rate_limit_per_minute = self.config.get('rate_limit_per_minute', 60)
        self.failed_attempt_window = self.config.get('failed_attempt_window', 300)  # 5 minutes
        self.auto_block_duration = self.config.get('auto_block_duration', 3600)  # 1 hour

    def log_security_event(self, event_type: str, severity: str, source: str, details: dict[str, Any] = None) -> SecurityEvent:
        """Log a security event."""
        event = SecurityEvent(event_type, severity, source, details or {})
        self.events.append(event)

        # Log to security file
        json.dumps(event.to_dict(), indent=2)

        try:
            self.security_events_file.parent.mkdir(parents=True, exist_ok=True)
            if not self.security_events_file.exists():
                self.security_events_file.write_text('{"security_events": []}\n')

            # Append to existing file
            with open(self.security_events_file, 'r+') as f:
                data = json.load(f)
                data['security_events'].append(event.to_dict())
                f.seek(0)
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to write security event: {e}")

        logger.warning(f"SECURITY: {severity.upper()} {event_type} from {source} - {details}")

        return event

    def check_rate_limit(self, source: str) -> tuple[bool, str | None]:
        """Check if source has exceeded rate limit."""
        now = time.time()
        one_minute_ago = now - 60

        # Clean old requests
        while (self.rate_limits[source] and self.rate_limits[source][0] < one_minute_ago):
            self.rate_limits[source].popleft()

        request_count = len(self.rate_limits[source])

        if request_count >= self.rate_limit_per_minute:
            return False, f"Rate limit exceeded for {source}: {request_count}/{self.rate_limit_per_minute} per minute"

        # Add current request
        self.rate_limits[source].append(now)
        return True, None

    def check_failed_attempts(self, source: str, event_type: str = 'login') -> tuple[bool, str | None]:
        """Check failed attempts and implement progressive blocking."""
        time.time()

        # Increment failed attempts counter
        self.failed_attempts[(source, event_type)] += 1

        fail_count = self.failed_attempts[(source, event_type)]

        # Check thresholds
        if fail_count >= self.max_login_attempts * 3:  # Critical threshold
            return False, f"Critical: Too many failed {event_type} attempts from {source}: {fail_count}"
        elif fail_count >= self.max_login_attempts * 2:  # High threshold
            return False, f"High: Multiple failed {event_type} attempts from {source}: {fail_count}"
        elif fail_count >= self.max_login_attempts:  # Warning threshold
            return False, f"Warning: {fail_count} failed {event_type} attempts from {source}"

        return True, None

    def detect_suspicious_input(self, input_data: dict[str, Any], source: str) -> list[str]:
        """Detect suspicious patterns in input data."""
        alerts = []

        # Check for suspicious field patterns
        suspicious_patterns = [
            (r"(?i)script.*?javascript", "Potential JavaScript injection"),
            (r"(?i)<iframe", "Potential iframe injection"),
            (r"(?i)(DROP|DELETE|INSERT|UPDATE)\s+", "Potential SQL injection"),
            (r"(?i)system\(|eval\(|exec\(", "Potential command injection"),
            (r"(?i)\.\./\.\./", "Path traversal attempt"),
            (r"(?i)<\?php", "PHP injection attempt"),
            (r"(?i)<%.*%>", "ASP injection attempt")
        ]

        def check_value(value, path):
            if isinstance(value, dict):
                for key, val in value.items():
                    alerts.extend(check_value(val, f"{path}.{key}"))
            elif isinstance(value, list):
                for i, val in enumerate(value):
                    alerts.extend(check_value(val, f"{path}[{i}]"))
            elif isinstance(value, str):
                for pattern, message in suspicious_patterns:
                    if pattern.search(value):
                        alerts.append(f"Suspicious input at {path}: {message}")

        check_value(input_data, "input")

        if alerts:
            self.log_security_event(
                "SUSPICIOUS_INPUT",
                "HIGH" if len(alerts) > 2 else "MEDIUM",
                source,
                {"detected_patterns": alerts, "input_hash": hashlib.sha256(json.dumps(input_data).encode()).hexdigest()[:16]}
            )

        return alerts

    def detect_anomalous_usage(self, usage_metrics: dict[str, Any], source: str) -> list[str]:
        """Detect anomalous usage patterns."""
        alerts = []

        # Calculate metrics per session
        calculations_per_session = usage_metrics.get('calculations_count', 0)
        errors_per_session = usage_metrics.get('errors_count', 0)

        # Anomaly thresholds
        if calculations_per_session > 1000:
            alerts.append(f"Unusually high calculation volume: {calculations_per_session}")

        error_rate = 0
        if calculations_per_session > 0:
            error_rate = errors_per_session / calculations_per_session

        if error_rate > 0.5:  # > 50% error rate
            alerts.append(f"High error rate: {error_rate:.1%}")

        # Check for rapid succession
        if usage_metrics.get('avg_duration_ms', 0) < 10:  # Very fast calculations (bot-like)
            alerts.append("Possibly automated requests (too fast)")

        if alerts:
            self.log_security_event(
                "ANOMALOUS_USAGE",
                "HIGH" if len(alerts) > 2 else "MEDIUM",
                source,
                {"anomalies": alerts, "metrics": usage_metrics}
            )

        return alerts

    def detect_compliance_threats(self, compliance_data: dict[str, Any], source: str) -> list[str]:
        """Detect potential threats related to compliance violations."""
        alerts = []

        failures = compliance_data.get('summary', {}).get('failures', 0)
        compliance_data.get('summary', {}).get('warnings', 0)

        # Critical compliance failures
        if failures > 5:
            alerts.append(f"Excessive compliance failures: {failures}")

        # Frequent overrides
        overrides_used = compliance_data.get('overrides_used', 0)
        if overrides_used > 3:
            alerts.append(f"Frequent compliance overrides: {overrides_used}")

        # Critical rule failures
        blocking_failures = compliance_data.get('blocking_failures', [])
        if len(blocking_failures) > 2:
            alerts.append(f"Multiple blocking compliance failures: {len(blocking_failures)}")

        if alerts:
            self.log_security_event(
                "COMPLIANCE_THREAT",
                "HIGH" if failures > 10 else "MEDIUM",
                source,
                {"threats": alerts, "compliance_data": compliance_data}
            )

        return alerts

    def auto_block_source(self, source: str, reason: str, duration_seconds: int | None = None) -> None:
        """Automatically block source for security reasons."""
        if duration_seconds is None:
            duration_seconds = self.auto_block_duration

        block_until = time.time() + duration_seconds
        self.blocked_sources.add((source, block_until))

        self.log_security_event(
            "AUTO_BLOCK",
            "HIGH",
            source,
            {"block_until": datetime.fromtimestamp(block_until).isoformat(), "reason": reason}
        )

        logger.warning(f"Auto-blocked source {source} for {duration_seconds} seconds: {reason}")

    def is_source_blocked(self, source: str) -> bool:
        """Check if source is currently blocked."""
        now = time.time()

        # Check and clean expired blocks
        source_blocks = [(s, t) for s, t in self.blocked_sources if s == source and t > now]

        # Update blocked_sources (remove expired blocks)
        remaining_blocks = [(s, t) for s, t in self.blocked_sources if t > now]
        self.blocked_sources = set(remaining_blocks)

        return len(source_blocks) > 0

    def get_security_summary(self) -> dict[str, Any]:
        """Get comprehensive security summary."""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        recent_events = [e for e in self.events if e.timestamp > last_24h]
        last_week_events = [e for e in self.events if e.timestamp > last_7d]

        # Count events by severity
        severity_counts = defaultdict(int)
        for event in recent_events:
            severity_counts[event.severity] += 1

        # Count events by type
        type_counts = defaultdict(int)
        for event in recent_events:
            type_counts[event.event_type] += 1

        # Find blocked sources
        currently_blocked = [
            (s, datetime.fromtimestamp(t).isoformat())
            for s, t in self.blocked_sources
            if t > time.time()
        ]

        return {
            'timestamp': now.isoformat(),
            'last_24_hours': {
                'total_events': len(recent_events),
                'by_severity': dict(severity_counts),
                'by_type': dict(type_counts)
            },
            'last_7_days': {
                'total_events': len(last_week_events)
            },
            'currently_blocked': currently_blocked,
            'failed_attempts': dict(self.failed_attempts),
            'total_events_in_memory': len(self.events),
            'rate_limits_active': len(self.rate_limits),
            'auto_block_duration': self.auto_block_duration
        }

    def cleanup_old_data(self) -> None:
        """Clean up old security data to prevent memory issues."""
        # This is called periodically to clean up old data

        # Clean old failed attempts
        time.time() - self.failed_attempt_window
        old_attempts = [
            (source, event_type)
            for (source, event_type), count in self.failed_attempts.items()
            if count > 0 and (source, event_type) not in [(s, t) for s, t in self.blocked_sources]
        ]

        for source_event in old_attempts:
            del self.failed_attempts[source_event]

        # Security events file rotation happens via log rotation in production_logging_config.yaml

        logger.info("Security monitor cleanup completed")
