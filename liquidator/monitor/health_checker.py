"""
Health Checker - System health and availability monitoring.
Provides health endpoints and diagnostic information.
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Plantillas del paquete (liquidator/templates/). Ver REGISTRY.md (S14 —
# Tarea 1.A-plan) y KB_LLM/06 R-OP-07.
_PACKAGE_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
_PACKAGE_TEMPLATE_FILES = [
    _PACKAGE_TEMPLATES_DIR / "comprobante_periodica.md",
    _PACKAGE_TEMPLATES_DIR / "comprobante_finiquito.md",
]


class HealthChecker:
    """Monitors system health and provides diagnostic information."""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.health_file = Path("health/system_health.json")
        self.last_check = None

    def check_component_health(self) -> Dict:
        """Check health of individual system components."""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'HEALTHY',
            'components': {}
        }

        # Check essential directories (operacionales, cwd-relative).
        # Antes del packaging v2.0, esta lista incluía 'templates' (raíz).
        # Ahora las plantillas viajan dentro del paquete; se chequean aparte
        # más abajo. Ver KB_LLM/06 R-OP-07.
        essential_dirs = ['params', 'audit', 'output']
        for dir_path in essential_dirs:
            dir_exists = Path(dir_path).exists()
            dir_writable = dir_exists and os.access(dir_path, os.W_OK)
            
            health_status['components'][f'directory_{dir_path}'] = {
                'status': 'HEALTHY' if dir_exists and dir_writable else 'UNHEALTHY',
                'exists': dir_exists,
                'writable': dir_writable
            }
            
        # Check parameter files
        param_files = ['params/2025.json', 'params/normas.json', 'params/plazos.json']
        for param_file in param_files:
            file_path = Path(param_file)
            file_exists = file_path.exists()
            file_readable = file_exists and os.access(file_path, os.R_OK)
            file_valid_json = False
            
            if file_exists and file_readable:
                try:
                    with open(file_path, 'r') as f:
                        json.load(f)
                    file_valid_json = True
                except (json.JSONDecodeError, IOError):
                    file_valid_json = False
                    
            health_status['components'][f'param_file_{param_file}'] = {
                'status': 'HEALTHY' if file_exists and file_readable and file_valid_json else 'UNHEALTHY',
                'exists': file_exists,
                'readable': file_readable,
                'valid_json': file_valid_json
            }
            
        # Check templates (ahora viven dentro del paquete, no en cwd).
        # Ver REGISTRY.md (S14 — Tarea 1.A-plan) y KB_LLM/06 R-OP-07.
        for template_file in _PACKAGE_TEMPLATE_FILES:
            file_path = template_file
            file_exists = file_path.exists()
            file_readable = file_exists and os.access(file_path, os.R_OK)

            health_status['components'][f'template_{template_file.name}'] = {
                'status': 'HEALTHY' if file_exists and file_readable else 'UNHEALTHY',
                'exists': file_exists,
                'readable': file_readable
            }
            
        # Check configuration files
        config_files = ['config/default_config.yaml', 'config/logging_config.yaml']
        for config_file in config_files:
            file_path = Path(config_file)
            file_exists = file_path.exists()
            file_readable = file_exists and os.access(file_path, os.R_OK)
            
            health_status['components'][f'config_{config_file}'] = {
                'status': 'HEALTHY' if file_exists and file_readable else 'UNHEALTHY',
                'exists': file_exists,
                'readable': file_readable
            }
            
        # Determine overall health
        unhealth_components = [
            name for name, component in health_status['components'].items()
            if component['status'] == 'UNHEALTHY'
        ]
        
        if unhealth_components:
            health_status['overall_status'] = 'UNHEALTHY'
            health_status['unhealthy_components'] = unhealth_components
            
        return health_status
        
    def check_dependencies(self) -> Dict:
        """Check Python dependencies and versions."""
        dependency_status = {
            'timestamp': datetime.now().isoformat(),
            'python_version': f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}.{__import__('sys').version_info.micro}",
            'dependencies': {}
        }
        
        # Critical dependencies to check
        critical_deps = {
            'jsonschema': '4.19.0',
            'yaml': '6.0',
            'markdown': '3.4.0',
            'dateutil': '2.8.0',
            'psutil': '5.9.0'  # for monitoring
        }
        
        for package, min_version in critical_deps.items():
            try:
                module = __import__(package)
                version = getattr(module, '__version__', 'UNKNOWN')
                dependency_status['dependencies'][package] = {
                    'installed': True,
                    'version': version,
                    'minimum_required': min_version,
                    'status': 'HEALTHY'  # For now, always healthy if installed
                }
            except ImportError:
                dependency_status['dependencies'][package] = {
                    'installed': False,
                    'version': None,
                    'minimum_required': min_version,
                    'status': 'MISSING'
                }
                
        return dependency_status
        
    def check_disk_space(self, threshold_gb: float = 1.0) -> Dict:
        """Check available disk space for critical directories."""
        try:
            import psutil
            disk_usage = psutil.disk_usage('/')
            
            free_space_gb = disk_usage.free / (1024**3)
            critical = free_space_gb < threshold_gb
            
            return {
                'timestamp': datetime.now().isoformat(),
                'free_space_gb': round(free_space_gb, 2),
                'total_space_gb': round(disk_usage.total / (1024**3), 2),
                'used_space_gb': round(disk_usage.used / (1024**3), 2),
                'percent_used': round((disk_usage.used / disk_usage.total) * 100, 2),
                'threshold_gb': threshold_gb,
                'status': 'CRITICAL' if critical else 'HEALTHY',
                'alert_message': f"Only {free_space_gb:.2f} GB free space remaining" if critical else None
            }
        except ImportError:
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'UNKNOWN',
                'message': 'psutil not available for disk space checking'
            }
            
    def check_recent_errors(self, hours_back: int = 24) -> Dict:
        """Check for recent errors in log files."""
        error_log = Path('logs/errors.log')
        if not error_log.exists():
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'HEALTHY',
                'recent_errors': 0,
                'message': 'No error log file found'
            }
            
        try:
            # Check errors in last N hours
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            recent_errors = 0
            recent_error_details = []
            
            with open(error_log, 'r') as f:
                for line in f:
                    # Parse timestamp from log (simplified)
                    try:
                        # Expect format: "2025-11-04 12:00:00"
                        if 'ERROR' in line:
                            timestamp_str = line.split(' - ')[0]
                            if timestamp_str:
                                log_timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                                if log_timestamp > cutoff_time:
                                    recent_errors += 1
                                    if len(recent_error_details) < 10:  # Limit details
                                        recent_error_details.append({
                                            'timestamp': timestamp_str,
                                            'message': line.split(' - ')[-1].strip()
                                        })
                    except (ValueError, IndexError):
                        continue
                        
            status = 'HEALTHY'
            if recent_errors > 100:
                status = 'CRITICAL'
            elif recent_errors > 50:
                status = 'WARNING'
                
            return {
                'timestamp': datetime.now().isoformat(),
                'status': status,
                'hours_checked': hours_back,
                'recent_errors': recent_errors,
                'sample_errors': recent_error_details
            }
            
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'ERROR',
                'message': f'Error reading log file: {e}'
            }
            
    def get_health_summary(self) -> Dict:
        """Get comprehensive health summary."""
        self.last_check = datetime.now()
        
        component_health = self.check_component_health()
        dependency_health = self.check_dependencies()
        disk_health = self.check_disk_space()
        error_health = self.check_recent_errors()
        
        # Determine overall status
        overall_status = 'HEALTHY'
        issues = []
        
        if component_health['overall_status'] != 'HEALTHY':
            overall_status = 'UNHEALTHY'
            issues.append(f"Component issues: {len(component_health.get('unhealthy_components', []))}")
            
        if any(dep['status'] == 'MISSING' for dep in dependency_health['dependencies'].values()):
            overall_status = 'UNHEALTHY'
            missing_deps = [name for name, dep in dependency_health['dependencies'].items() if dep['status'] == 'MISSING']
            issues.append(f"Missing dependencies: {', '.join(missing_deps)}")
            
        if disk_health['status'] == 'CRITICAL':
            overall_status = 'CRITICAL'
            issues.append("Critical disk space low")
            
        if error_health['status'] in ['WARNING', 'CRITICAL']:
            overall_status = error_health['status']
            issues.append(f"Recent errors: {error_health['recent_errors']}")
            
        return {
            'timestamp': datetime.now().isoformat(),
            'last_check': self.last_check.isoformat(),
            'overall_status': overall_status,
            'issues': issues,
            'components': component_health,
            'dependencies': dependency_health,
            'disk_space': disk_health,
            'recent_errors': error_health
        }
        
    def save_health_status(self) -> None:
        """Save current health status to file for monitoring systems."""
        try:
            health_status = self.get_health_summary()
            self.health_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.health_file, 'w') as f:
                json.dump(health_status, f, indent=2)
                
            logger.info(f"Health status saved to {self.health_file}")
            
        except Exception as e:
            logger.error(f"Error saving health status: {e}")
            
    def is_healthy(self) -> bool:
        """Simple boolean health check for load balancers and monitoring."""
        summary = self.get_health_summary()
        return summary['overall_status'] in ['HEALTHY', 'WARNING']  # Allow warnings to pass health checks
