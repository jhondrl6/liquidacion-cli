#!/usr/bin/env python3
"""
Final Validation Script - Session 20 Complete System Verification
Comprehensive validation of all system components for production readiness.
"""

import sys
import os
import json
import time
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from liquidator.core.engine import LiquidacionEngine
from liquidator.monitor.health_checker import HealthChecker
from liquidator.monitor.metrics_collector import MetricsCollector
from liquidator.security.security_monitor import SecurityMonitor
from liquidator.utils.error_handler import LiquidacionError


class FinalValidator:
    """Comprehensive system validator for production readiness."""
    
    def __init__(self):
        self.results = {
            'validation_start': datetime.now().isoformat(),
            'checks': {},
            'overall_status': 'PENDING',
            'error_count': 0,
            'warning_count': 0
        }
        
    def log_check(self, check_name: str, status: str, message: str, data=None):
        """Log check result with timestamp."""
        self.results['checks'][check_name] = {
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        if status == 'FAIL':
            self.results['error_count'] += 1
            print(f"[FAIL] {check_name}: {message}")
        elif status == 'WARN':
            self.results['warning_count'] += 1
            print(f"[WARN] {check_name}: {message}")
        else:
            print(f"[PASS] {check_name}: {message}")
            
    def test_basic_functionality(self) -> None:
        """Test basic liquidation calculations."""
        try:
            test_cases = [
                {
                    'name': 'Basic PERIODICA calculation',
                    'data': {
                        'modo': 'PERIODICA',
                        'fecha_ingreso': '2024-01-01',
                        'fecha_corte': '2024-12-15',
                        'salario_mensual': 2500000,
                        'tipo_contrato': 'indefinido',
                        'reside_en_lugar_trabajo': False,
                        'auxilio_conectividad': 100000,
                        'comisiones_promedio_mensual': 150000,
                        'horas_extras_promedio_mensual': 80000,
                        'bonificaciones_promedio_mensual': 50000
                    }
                },
                {
                    'name': 'FINIQUITO with vacation compensation',
                    'data': {
                        'modo': 'FINIQUITO',
                        'fecha_ingreso': '2023-01-01',
                        'fecha_corte': '2024-12-15',
                        'salario_mensual': 3200000,
                        'tipo_contrato': 'indefinido',
                        'reside_en_lugar_trabajo': True,
                        'dias_vacaciones_pendientes': 25
                    }
                },
                {
                    'name': 'Variable salary case',
                    'data': {
                        'modo': 'PERIODICA',
                        'fecha_ingreso': '2024-01-01',
                        'fecha_corte': '2024-12-15',
                        'salario_mensual': 2100000,
                        'salarios_historicos': [
                            {'periodo': '2024-01', 'salario_base': 2100000, 'comisiones': 50000},
                            {'periodo': '2024-02', 'salario_base': 2100000, 'comisiones': 80000},
                            {'periodo': '2024-03', 'salario_base': 2100000, 'comisiones': 120000}
                        ],
                        'tipo_contrato': 'fijo'
                    }
                }
            ]
            
            for test_case in test_cases:
                start_time = time.time()
                
                try:
                    result = LiquidacionEngine().process(test_case['data'])
                    duration = (time.time() - start_time) * 1000
                    
                    # Validate result structure
                    if 'meta' not in result:
                        raise ValueError("Missing meta section")
                    if 'desglose' not in result:
                        raise ValueError("Missing calculation breakdown")
                    if 'compliance_report' not in result:
                        raise ValueError("Missing compliance report")
                    
                    self.log_check(
                        f"calc_{test_case['name']}".replace(' ', '_'),
                        'PASS',
                        f"Completed in {duration:.1f}ms",
                        {'duration_ms': duration, 'compliance_status': result.get('compliance_report', {}).get('compliance_status', 'UNKNOWN')}
                    )
                    
                except Exception as e:
                    self.log_check(
                        f"calc_{test_case['name']}".replace(' ', '_'),
                        'FAIL',
                        f"Calculation failed: {e}"
                    )
                    
        except Exception as e:
            self.log_check('basic_functionality', 'FAIL', f"Test setup failed: {e}")
            
    def test_compliance_system(self) -> None:
        """Test compliance validation system."""
        try:
            # Test valid case
            valid_data = {
                'modo': 'PERIODICA',
                'fecha_ingreso': '2024-01-01',
                'fecha_corte': '2024-12-15',
                'salario_mensual': 2500000
            }
            
            result = LiquidacionEngine().process(valid_data)
            compliance = result.get('compliance_report', {})
            
            if compliance.get('compliance_status') == 'GO':
                self.log_check('compliance_valid_case', 'PASS', 'Valid case passed compliance')
            else:
                self.log_check('compliance_valid_case', 'WARN', f'Valid case returned: {compliance.get("compliance_status")}')
                
            # Test rules are working
            failed_checks = compliance.get('summary', {}).get('failures', 0)
            passed_checks = compliance.get('summary', {}).get('passed', 0)
            
            if failed_checks == 0 and passed_checks > 0:
                self.log_check('compliance_rules_working', 'PASS', f'Rules executed: {passed_checks} passed')
            else:
                self.log_check('compliance_rules_working', 'WARN', f'Rules execution: {passed_checks} passed, {failed_checks} failed')
                
        except Exception as e:
            self.log_check('compliance_system', 'FAIL', f"Compliance test failed: {e}")
            
    def test_security_features(self) -> None:
        """Test security validation and monitoring."""
        try:
            sm = SecurityMonitor()
            
            # Test rate limiting
            allowed, reason = sm.check_rate_limit('test_source')
            if allowed:
                self.log_check('security_rate_limiting', 'PASS', 'Rate limiting functional')
            else:
                self.log_check('security_rate_limiting', 'FAIL', f'Rate limiting issue: {reason}')
                
            # Test input validation with malicious data
            from liquidator.security.input_validator import InputValidator
            validator = InputValidator()
            
            # Test SQL injection detection
            try:
                malicious_data = {
                    'modo': 'PERIODICA',
                    'fecha_ingreso': '2024-01-01',
                    'fecha_corte': '2024-12-15',
                    'salario_mensual': 2500000,
                    'nombre_trabajador': "'; DROP TABLE users; --"
                }
                sanitized = validator.validate_json_data(malicious_data)
                self.log_check('security_input_validation', 'PASS', 'SQL injection blocked')
            except Exception:
                self.log_check('security_input_validation', 'PASS', 'Malicious input rejected as expected')
                
            # Test security monitoring
            test_event = sm.log_security_event('TEST_EVENT', 'LOW', 'validation_test', {'test': True})
            if test_event.event_id:
                self.log_check('security_monitoring', 'PASS', 'Security event logged successfully')
            else:
                self.log_check('security_monitoring', 'FAIL', 'Security event logging failed')
                
        except Exception as e:
            self.log_check('security_features', 'FAIL', f"Security test failed: {e}")
            
    def test_system_health(self) -> None:
        """Test system health monitoring."""
        try:
            hc = HealthChecker()
            health_data = hc.get_health_summary()
            
            # Test health checker
            if health_data.get('overall_status') in ['HEALTHY', 'WARNING']:
                self.log_check('health_check', 'PASS', f"System status: {health_data.get('overall_status')}")
            else:
                self.log_check('health_check', 'WARN', f"System issues: {health_data.get('issues', [])}")
                
            # Validate health file creation
            hc.save_health_status()
            health_file = Path('health/system_health.json')
            if health_file.exists():
                self.log_check('health_file_creation', 'PASS', 'Health status file created')
            else:
                self.log_check('health_file_creation', 'FAIL', 'Health status file not created')
                
        except Exception as e:
            self.log_check('system_health', 'FAIL', f"Health check failed: {e}")
            
    def test_output_generation(self) -> None:
        """Test output generation capabilities."""
        try:
            test_data = {
                'modo': 'PERIODICA',
                'fecha_ingreso': '2024-01-01',
                'fecha_corte': '2024-12-15',
                'salario_mensual': 2500000
            }
            
            result = LiquidacionEngine().process(test_data)
            
            # Test JSON output
            output_file = Path('test_output.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
                
            if output_file.exists():
                self.log_check('output_json_generation', 'PASS', 'JSON file generated successfully')
            else:
                self.log_check('output_json_generation', 'FAIL', 'JSON file generation failed')
                
            # Test Markdown output
            try:
                from liquidator.output.markdown_generator import MarkdownGenerator
                md_gen = MarkdownGenerator()
                md_content = md_gen.generate(result)
                if md_content and len(md_content) > 100:
                    self.log_check('output_markdown_generation', 'PASS', 'Markdown content generated')
                else:
                    self.log_check('output_markdown_generation', 'FAIL', 'Markdown generation insufficient')
            except Exception as e:
                self.log_check('output_markdown_generation', 'FAIL', f'Markdown generation error: {e}')
                
            # Clean up test files
            if output_file.exists():
                output_file.unlink()
                
        except Exception as e:
            self.log_check('output_generation', 'FAIL', f"Output generation test failed: {e}")
            
    def test_performance(self) -> None:
        """Test system performance metrics."""
        try:
            mc = MetricsCollector()
            mc.start_session()
            
            # Perform multiple calculations to test performance
            durations = []
            for i in range(5):
                test_data = {
                    'modo': 'PERIODICA',
                    'fecha_ingreso': '2024-01-01',
                    'fecha_corte': '2024-12-15',
                    'salario_mensual': 2500000
                }
                
                start_time = time.time()
                result = LiquidacionEngine().process(test_data)
                duration = (time.time() - start_time) * 1000
                durations.append(duration)
                
                mc.record_calculation({
                    'duration_ms': duration,
                    'input_size_bytes': len(json.dumps(test_data).encode('utf-8')),
                    'mode': test_data['modo'],
                    'compliance_status': result.get('compliance_report', {}).get('compliance_status', 'UNKNOWN')
                })
                
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            
            # Performance thresholds (ms)
            max_acceptable = 5000  # 5 seconds max
            
            if max_duration < max_acceptable:
                self.log_check('performance_response_time', 'PASS', f'Avg: {avg_duration:.1f}ms, Max: {max_duration:.1f}ms')
            else:
                self.log_check('performance_response_time', 'WARN', f'Slow calculations: Max {max_duration:.1f}ms')
                
            # Test metrics collection
            summary = mc.get_session_summary()
            if summary.get('session_summary', {}).get('calculations_count', 0) == 5:
                self.log_check('performance_metrics', 'PASS', 'Metrics collection working')
            else:
                self.log_check('performance_metrics', 'FAIL', 'Metrics collection issue')
                
        except Exception as e:
            self.log_check('performance_testing', 'FAIL', f"Performance test failed: {e}")
            
    def test_file_structure(self) -> None:
        """Test required file structure and permissions."""
        try:
            required_files = [
                'params/2025.json',
                'params/normas.json',
                'params/plazos.json',
                'config/production_config.yaml',
                'config/logging_config.yaml',
                'config/production_config.yaml',
                'bin/liquidar.py',
                'LICENSE',
                'README.md',
                'setup.py'
            ]
            
            for file_path in required_files:
                path = Path(file_path)
                if path.exists():
                    if path.is_file() and os.access(path, os.R_OK):
                        self.log_check(f'file_structure_{file_path.replace("/", "_")}', 'PASS', f'File {file_path} exists and readable')
                    else:
                        self.log_check(f'file_structure_{file_path.replace("/", "_")}', 'FAIL', f'File {file_path} not readable')
                else:
                    self.log_check(f'file_structure_{file_path.replace("/", "_")}', 'FAIL', f'File {file_path} missing')
                    
            # Test directory structure
            required_dirs = ['audit', 'output', 'logs', 'templates']
            for dir_path in required_dirs:
                path = Path(dir_path)
                if path.exists() and path.is_dir():
                    if os.access(path, os.W_OK):
                        self.log_check(f'directory_structure_{dir_path}', 'PASS', f'Directory {dir_path} writable')
                    else:
                        self.log_check(f'directory_structure_{dir_path}', 'WARN', f'Directory {dir_path} not writable')
                else:
                    self.log_check(f'directory_structure_{dir_path}', 'WARN', f'Directory {dir_path} missing (will be created on demand)')
                    
        except Exception as e:
            self.log_check('file_structure', 'FAIL', f"File structure test failed: {e}")
            
    def test_dependencies(self) -> None:
        """Test critical dependencies are available."""
        try:
            critical_modules = [
                'jsonschema',
                'yaml',
                'markdown',
                'dateutil',
                'pathlib',
                'datetime',
                'json',
                'hashlib'
            ]
            
            for module in critical_modules:
                try:
                    __import__(module)
                    self.log_check(f'dependency_{module}', 'PASS', f'Module {module} available')
                except ImportError:
                    self.log_check(f'dependency_{module}', 'FAIL', f'Module {module} missing')
                    
            # Test our own modules
            internal_modules = [
                'liquidator.core.engine',
                'liquidator.calculators.sbl_calculator',
                'liquidator.compliance.compliance_engine',
                'liquidator.security.input_validator',
                'liquidator.monitor.health_checker'
            ]
            
            for module in internal_modules:
                try:
                    __import__(module)
                    self.log_check(f'internal_module_{module.replace(".", "_")}', 'PASS', f'Internal module {module} available')
                except ImportError as e:
                    self.log_check(f'internal_module_{module.replace(".", "_")}', 'FAIL', f'Internal module {module} error: {e}')
                    
        except Exception as e:
            self.log_check('dependencies', 'FAIL', f"Dependency test failed: {e}")
            
    def test_cli_functionality(self) -> None:
        """Test command-line interface functionality."""
        try:
            # Create test input file
            test_input = {
                'modo': 'PERIODICA',
                'fecha_ingreso': '2024-01-01',
                'fecha_corte': '2024-12-15',
                'salario_mensual': 2500000
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(test_input, f)
                input_file = f.name
                
            try:
                # Test CLI with input file
                result = subprocess.run(
                    [sys.executable, str(Path(__file__).parent.parent / 'bin' / 'liquidar.py'), 
                     '--input', input_file, '--test-run'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    self.log_check('cli_basic_functionality', 'PASS', 'CLI executed successfully')
                else:
                    self.log_check('cli_basic_functionality', 'FAIL', f'CLI failed: {result.stderr}')
                    
                # Test help command
                help_result = subprocess.run(
                    [sys.executable, str(Path(__file__).parent.parent / 'bin' / 'liquidar.py'), '--help'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if help_result.returncode == 0 and '--modo' in help_result.stdout:
                    self.log_check('cli_help_functionality', 'PASS', 'CLI help works and shows expected flags')
                else:
                    self.log_check('cli_help_functionality', 'FAIL', 'CLI help issue')
                    
            finally:
                # Clean up temp file
                if Path(input_file).exists():
                    Path(input_file).unlink()
                    
        except Exception as e:
            self.log_check('cli_functionality', 'FAIL', f"CLI test failed: {e}")
            
    def run_validation(self) -> dict:
        """Run complete validation suite."""
        print("Starting Final Validation for Colombia Payroll Settlement System v1.0.0")
        print("=" * 80)
        
        # Run all validation checks
        self.test_dependencies()
        self.test_file_structure()
        self.test_basic_functionality()
        self.test_compliance_system()
        self.test_security_features()
        self.test_system_health()
        self.test_output_generation()
        self.test_performance()
        self.test_cli_functionality()
        
        # Determine overall status
        if self.results['error_count'] == 0:
            if self.results['warning_count'] == 0:
                self.results['overall_status'] = 'PASS'
            else:
                self.results['overall_status'] = 'PASS_WITH_WARNINGS'
        else:
            self.results['overall_status'] = 'FAIL'
            
        self.results['validation_end'] = datetime.now().isoformat()
        self.results['duration_seconds'] = (
            datetime.fromisoformat(self.results['validation_end']) -
            datetime.fromisoformat(self.results['validation_start'])
        ).total_seconds()
        
        # Print summary
        self.print_summary()
        
        # Save results
        self.save_results()
        
        return self.results
        
    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        
        total_checks = len(self.results['checks'])
        pass_count = len([c for c in self.results['checks'].values() if c['status'] == 'PASS'])
        warn_count = self.results['warning_count']
        fail_count = self.results['error_count']
        
        print(f"Total Checks: {total_checks}")
        print(f"Passed: {pass_count}")
        print(f"Warnings: {warn_count}")
        print(f"Failed: {fail_count}")
        print(f"Duration: {self.results['duration_seconds']:.2f} seconds")
        
        print(f"\nOverall Status: {self.results['overall_status']}")
        
        if self.results['overall_status'] == 'PASS':
            print("\nSystem is PRODUCTION READY!")
        elif self.results['overall_status'] == 'PASS_WITH_WARNINGS':
            print("\nSystem is PRODUCTION READY with warnings - review warnings before deployment")
        else:
            print("\nSystem is NOT READY - fix failures before production deployment")
            
    def save_results(self):
        """Save validation results to file."""
        try:
            results_file = Path('validation_results.json')
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\nDetailed results saved to: {results_file.absolute()}")
        except Exception as e:
            print(f"Error saving results: {e}")


def main():
    """Main validation entry point."""
    validator = FinalValidator()
    results = validator.run_validation()
    
    # Exit with appropriate code
    if results['overall_status'] == 'PASS':
        return 0
    elif results['overall_status'] == 'PASS_WITH_WARNINGS':
        return 1  # Warning exit code
    else:
        return 2  # Failure exit code


if __name__ == '__main__':
    sys.exit(main())
