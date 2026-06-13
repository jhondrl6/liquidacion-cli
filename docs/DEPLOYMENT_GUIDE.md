# Deployment Guide
## Colombia Payroll Settlement System 2025

This guide covers the complete setup and deployment of the settlement system in production environments.

---

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Security Setup](#security-setup)
5. [Monitoring and Logging](#monitoring-and-logging)
6. [Backup and Recovery](#backup-and-recovery)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance](#maintenance)

---

## System Requirements

### Minimum Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS 10.15+, or Windows 10+
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Disk Space**: 10GB free space minimum
- **Network**: Internet connection for package installation

### Recommended Production Setup
- **Server**: Dedicated server or VM with 8GB+ RAM
- **Operating System**: Ubuntu 22.04 LTS or CentOS 8
- **Python**: 3.11 (long-term support)
- **Storage**: 50GB+ with SSD for better performance
- **CPU**: 4+ cores for concurrent processing

### Software Dependencies
```bash
# System packages (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-dev python3-pip
sudo apt-get install -y build-essential libffi-dev libssl-dev
sudo apt-get install -y git curl wget

# System packages (CentOS/RHEL)
sudo yum update
sudo yum install -y python3 python3-devel python3-pip
sudo yum install -y gcc gcc-c++ libffi-devel openssl-devel
sudo yum install -y git curl wget
```

---

## Installation

### Method 1: From PyPI (Recommended for Production)
```bash
# Create virtual environment
python3.11 -m venv liquidacion-env
source liquidacion-env/bin/activate  # On Windows: liquidacion-env\Scripts\activate

# Install from PyPI
pip install colombia-payroll-settlement==1.0.0

# Verify installation
settle --version
settle --help
```

### Method 2: From Source (Development/Custom)
```bash
# Clone repository
git clone https://github.com/user/colombia_payroll_settlement.git
cd colombia_payroll_settlement

# Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Verify installation
python -m liquidator.cli --version
```

### Method 3: Docker Container
```bash
# Build image
docker build -t colombia-payroll:1.0.0 .

# Run container
docker run -d --name liquidacion-cli \
  -v /path/to/data:/app/data \
  -v /path/to/params:/app/params \
  colombia-payroll:1.0.0

# Check logs
docker logs liquidacion-cli
```

### Post-Installation Setup
```bash
# Create required directories
mkdir -p params audit/logs audit/trails audit/reports output logs metrics

# Set appropriate permissions
chmod 755 params audit output logs metrics
chmod 700 audit/security

# Initialize configuration
python -c "from liquidator.utils.config_manager import initialize_config; initialize_config('production')"

# Test installation
python -m liquidator.tests.runner --quick
```

---

## Configuration

### Production Configuration Files

After installation, configure the system for production:

```bash
# Copy production configuration templates
cp config/production_config.yaml config/default_config.yaml
cp config/production_logging_config.yaml config/logging_config.yaml
```

### Essential Configuration Settings

Edit `config/default_config.yaml`:

```yaml
system:
  environment: "production"
  log_level: "WARNING"
  performance_mode: true

# Critical settings for production
compliance:
  enforce_by_default: true
  default_policy: "standard"
  allow_overrides: true  
  override_require_justification: true
  override_require_operator_id: true

security:
  encrypt_sensitive: true
  hash_algorithm: "sha256"
  rate_limiting:
    enabled: true
    max_requests_per_minute: 60

monitoring:
  metrics_enabled: true
  performance_monitoring: true
  error_tracking: true
```

### Environment Variables

Set these environment variables for production:

```bash
# Security Configuration
export LIQUIDACION_ENV=production
export LIQUIDACION_ENCRYPTION_KEY="your-encryption-key-here"
export LIQUIDACION_DB_PASSWORD="your-secure-password"

# Paths Configuration
export LIQUIDACION_CONFIG_PATH="/opt/liquidacion/config"
export LIQUIDACION_DATA_PATH="/opt/liquidacion/data"

# Optional: Email for alerts
export LIQUIDACION_ALERT_EMAIL="admin@yourcompany.com"

# Add to system profile for permanence
echo 'export LIQUIDACION_ENV=production' >> ~/.bashrc
echo 'export LIQUIDACION_ENCRYPTION_KEY="your-encryption-key-here"' >> ~/.bashrc
```

### File Permissions (Linux/Unix)

Set secure permissions for sensitive files:

```bash
# Set ownership
sudo chown -R liquidador:liquidador /opt/liquidacion
sudo usermod -a -G liquidador $USER

# Secure sensitive directories
chmod 700 audit/security
chmod 600 config/production_config.yaml
chmod 600 config/logging_config.yaml

# Secure parameter files
chmod 600 params/*.json

# Allow access to logs and outputs
chmod 755 logs output
chmod 644 logs/*.log
chmod 644 output/*.json
```

---

## Security Setup

### User Account Setup

Create a dedicated system user for running the application:

```bash
# Create system user
sudo useradd -r -s /bin/false liquidador

# Create data directories with proper permissions
sudo mkdir -p /opt/liquidacion/{config,audit,params,output,logs}
sudo chown -R liquidador:liquidador /opt/liquidacion
sudo chmod 750 /opt/liquidacion
sudo chmod 700 /opt/liquidacion/{audit,params}
```

### Encryption Key Generation

Generate and store encryption keys securely:

```bash
# Generate secure key
python -c "
import secrets
print('ENCRYPTION_KEY=' + secrets.token_hex(32))
" > /tmp/encryption_key.txt

# Move to secure location (only readable by liquidador user)
sudo mkdir -p /opt/liquidacion/.secrets
sudo cp /tmp/encryption_key.txt /opt/liquidacion/.secrets/
sudo chown liquidador:liquidador /opt/liquidacion/.secrets/encryption_key.txt
sudo chmod 400 /opt/liquidacion/.secrets/encryption_key.txt
rm /tmp/encryption_key.txt

# Set in environment
export LIQUIDACION_ENCRYPTION_KEY=$(cat /opt/liquidacion/.secrets/encryption_key.txt | cut -d= -f2)
```

### Security Hardening

Implement these security measures:

```bash
# Disable unused services
sudo systemctl disable apache2
sudo systemctl disable mysql

# Configure firewall
sudo ufw allow 22/tcp  # SSH only
sudo ufw enable

# Install fail2ban for intrusion protection
sudo apt-get install fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Configure fail2ban for local protection
sudo tee /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 5
EOF

sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Input Validation Security

The system includes built-in security features:

- **Input Validation**: All inputs validated against injection attacks
- **Rate Limiting**: 60 requests per minute per source
- **Failed Attempt Tracking**: Auto-block after repeated failures
- **Data Sanitization**: Automatic removal of dangerous characters
- **Audit Logging**: All security events logged and tracked

---

## Monitoring and Logging

### Log Configuration Production

Production logging is configured in `config/production_logging_config.yaml`:

```bash
# Test logging configuration
python -c "
import logging.config
import yaml
with open('config/production_logging_config.yaml') as f:
    logging.config.dictConfig(yaml.safe_load(f))
logger = logging.getLogger('liquidator')
logger.info('Production logging test')
"
```

### Monitoring Setup

Set up system monitoring:

```bash
# Create monitoring directories
mkdir -p metrics health

# Enable built-in monitoring
python -c "
from liquidator.monitor.health_checker import HealthChecker
hc = HealthChecker()
hc.save_health_status()
print('Health check completed')
"

# Schedule regular health checks (cron job)
cat << EOF | sudo tee /etc/cron.d/liquidacion-monitor
# Monitor settlement system health every 5 minutes
*/5 * * * * liquidador /opt/liquidacion/venv/bin/python -c "
from liquidator.monitor.health_checker import HealthChecker;
hc = HealthChecker();
hc.save_health_status()
"

# Rotate logs daily
0 0 * * * liquidador /opt/liquidacion/venv/bin/python -c "
from liquidator.monitor.metrics_collector import MetricsCollector;
mc = MetricsCollector();
mc.save_metrics()
"
EOF

# Reload cron
sudo systemctl reload cron
```

### Health Check Endpoints

The system provides health information:

```bash
# Check system health
python -c "
from liquidator.monitor.health_checker import HealthChecker
hc = HealthChecker()
health = hc.get_health_summary()
print('Status:', health['overall_status'])
print('Issues:', health.get('issues', []))
"

# Get security status
python -c "
from liquidator.security.security_monitor import SecurityMonitor
sm = SecurityMonitor()
print('Security events in last 24h:', len(sm.get_security_summary()['last_24_hours']['total_events']))
"
```

### Alert Setup

Configure monitoring alerts:

```bash
# Create alert script
cat << 'EOF' > /opt/liquidacion/scripts/monitoring_alerts.sh
#!/bin/bash

HEALTH_FILE="/opt/liquidacion/health/system_health.json"
ALERT_EMAIL="admin@yourcompany.com"

if [ -f "$HEALTH_FILE" ]; then
    STATUS=$(python3 -c "
import json
with open('$HEALTH_FILE') as f:
    data = json.load(f)
    print(data['overall_status'])
")

    if [ "$STATUS" != "HEALTHY" ]; then
        python3 -c "
import json
import smtplib
from email.mime.text import MIMEText

with open('$HEALTH_FILE') as f:
    data = json.load(f)

msg = MIMEText(f'Liquidación System Status: {data[\"overall_status\"]}\n\nIssues: {data.get(\"issues\", [])}')
msg['Subject'] = 'ALERT: Settlement System Status'
msg['From'] = 'monitor@yourcompany.com'
msg['To'] = '$ALERT_EMAIL'

# Use your SMTP server here
# server = smtplib.SMTP('smtp.yourcompany.com')
# server.send_message(msg)
# server.quit()
"
        echo "Health check status: $STATUS - Issues detected, alert sent"
    fi
fi
EOF

chmod +x /opt/liquidacion/scripts/monitoring_alerts.sh

# Add to cron every 15 minutes
echo "*/15 * * * * /opt/liquidacion/scripts/monitoring_alerts.sh" | sudo tee -a /etc/cron.d/liquidacion-alerts
```

---

## Backup and Recovery

### Automated Backup Setup

Create a comprehensive backup strategy:

```bash
# Create backup directory
sudo mkdir -p /opt/backups/liquidacion
sudo chown liquidador:liquidador /opt/backups/liquidacion

# Create backup script
cat << 'EOF' > /opt/liquidacion/scripts/backup.sh
#!/bin/bash

backup_dir="/opt/backups/yacht"
current_date=$(date +%Y%m%d_%H%M%S)
backup_file="liquidacion_backup_${current_date}.tar.gz"

# Backup critical directories
tar -czf "${backup_dir}/system_${backup_file}" \
    /opt/liquidacion/config/ \
    /opt/liquidacion/params/ \
    /opt/liquidacion/audit/ \
    /opt/liquidacion/.secrets/ \
    --exclude='*.log'

# Backup database schema (if using database)
# mysqldump -u root -p liquidacion_db > "${backup_dir}/db_schema_${current_date}.sql"

# Compress old backups (older than 30 days)
find "$backup_dir" -name "*.tar.gz" -mtime +30 -exec gzip {} \;

# Remove very old backups (older than 90 days)
find "$backup_dir" -name "*.tar.gz.gz" -mtime +90 -delete

echo "Backup completed: ${backup_file}"
EOF

chmod +x /opt/liquidacion/scripts/backup.sh

# Add to cron - daily backup at 2 AM
echo "0 2 * * * liquidador /opt/liquidacion/scripts/backup.sh" | sudo tee -a /etc/cron.d/liquidacion-backup
```

### Recovery Procedures

Document recovery procedures:

```bash
# Create recovery script
cat << 'EOF' > /opt/liquidacion/scripts/recovery.sh
#!/bin/bash

backup_dir="/opt/backups/liquidacion"

echo "Available backups:"
ls -la "$backup_dir"/system_*.tar.gz | tail -5

read -p "Enter backup file to restore: " backup_file

if [ -f "$backup_dir/$backup_file" ]; then
    echo "Stopping services..."
    # systemctl stop liquidacion-service

    echo "Creating emergency backup of current data..."
    mkdir -p "/tmp/liquidacion_emergency_$(date +%Y%m%d_%H%M%S)"
    cp -r /opt/liquidacion/config /tmp/liquidacion_emergency_$(date +%Y%m%d_%H%M%S)/

    echo "Restoring from backup..."
    tar -xzf "$backup_dir/$backup_file" -C /opt/liquidacion/

    echo "Setting permissions..."
    chown -R liquidador:liquidador /opt/liquidacion/
    chmod 700 /opt/liquidacion/audit
    chmod 700 /opt/liquidacion/.secrets

    echo "Starting services..."
    # systemctl start liquidacion-service

    echo "Recovery completed"
else
    echo "Backup file not found: $backup_file"
    exit 1
fi
EOF

chmod +x /opt/liquidacion/scripts/recovery.sh
```

### Disaster Recovery Plan

Document emergency procedures:

```bash
# Create disaster recovery documentation
cat << 'EOF' > /opt/liquidacion/docs/DISASTER_RECOVERY.md
# Disaster Recovery Plan

## Emergency Contacts
- System Administrator: [Phone] [Email]
- Security Team: [Phone] [Email]
- Management: [Phone] [Email]

## Emergency Procedures

### 1. System Unresponsive
```bash
# Check system status
sudo systemctl status liquidacion-service
sudo journalctl -u liquidacion-service -f

# Restart service if needed
sudo systemctl restart liquidacion-service
```

### 2. Data Corruption
```bash
# Identify last good backup
ls -la /opt/backups/liquidacion/system_*.tar.gz | tail -3

# Restore from backup
/opt/liquidacion/scripts/recovery.sh
```

### 3. Security Breach
```bash
# Check security logs
tail -100 /opt/liquidacion/logs/security.log

# Review failed attempts
grep -i "failed" /opt/liquidacion/logs/security.log | tail -50

# If breach confirmed:
/opt/liquidacion/scripts/security_lockdown.sh
```

### 4. Complete System Failure
1. Deploy to new server using installation procedure
2. Restore latest backup
3. Verify system health
4. Update DNS/load balancer if needed
5. Notify users of recovery

## Recovery Time Objectives
- RTO (Recovery Time Objective): 2 hours
- RPO (Recovery Point Objective): 24 hours
EOF
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: Installation Fails
```bash
# Clear pip cache
pip cache purge

# Install specific version
pip install --upgrade pip setuptools wheel
pip install colombia-payroll-settlement==1.0.0 --no-cache-dir
```

#### Issue: Permission Denied
```bash
# Check file permissions
ls -la /opt/liquidacion/

# Fix ownership
sudo chown -R liquidador:liquidador /opt/liquidacion/

# Fix permissions
sudo chmod 750 /opt/liquidacion
sudo chmod 700 /opt/liquidacion/{audit,params}
```

#### Issue: Configuration Not Loading
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config/default_config.yaml'))"

# Check config path
echo $LIQUIDACION_CONFIG_PATH

# Reset to default
python -c "from liquidator.utils.config_manager import initialize_config; initialize_config('production')"
```

#### Issue: High Memory Usage
```bash
# Check memory usage
ps aux | grep liquidador
top -p $(pgrep -f liquidador)

# Clear cache
python -c "from liquidator.utils.cache_manager import clear_cache; clear_cache()"

# Restart service
sudo systemctl restart liquidacion-service
```

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# Create debug configuration
cp config/default_config.yaml config/debug_config.yaml

# Edit debug_config.yaml:
# system.log_level: "DEBUG"
# logging.performance_monitoring: true

export LIQUIDACION_CONFIG_PATH="/path/to/debug_config.yaml"

# Run with debug
settle --debug --test-run
```

### Health Check Commands

```bash
# Basic health check
python -c "from liquidator.monitor.health_checker import HealthChecker; HealthChecker().get_health_summary()"

# Detailed system info
python -c "
import psutil
print('CPU:', psutil.cpu_percent())
print('Memory:', psutil.virtual_memory().percent)
print('Disk:', psutil.disk_usage('/').percent)
"

# Test core functionality
python -c "
from liquidator.core.engine import LiquidacionEngine
test_data = {
    'modo': 'PERIODICA',
    'fecha_ingreso': '2024-01-01',
    'fecha_corte': '2024-12-15',
    'salario_mensual': 2000000
}
result = LiquidacionEngine().process(test_data)
print('Test result:', 'SUCCESS' if result else 'FAILURE')
"
```

---

## Maintenance

### Regular Maintenance Tasks

Create maintenance scripts:

```bash
# Daily maintenance
cat << 'EOF' > /opt/liquidacion/scripts/daily_maintenance.sh
#!/bin/bash

# Rotate logs
/usr/sbin/logrotate /etc/logrotate.d/liquidacion

# Clean temp files
find /tmp -name "liquidacion_*" -mtime +1 -delete

# Check disk space
df -h /opt/liquidacion

# Monitor performance
python -c "
from liquidator.monitor.metrics_collector import MetricsCollector
from liquidator.monitor.health_checker import HealthChecker

mc = MetricsCollector()
hc = HealthChecker()

mc.save_metrics()
hc.save_health_status()
"
EOF

chmod +x /opt/liquidacion/scripts/daily_maintenance.sh

# Weekly maintenance
cat << 'EOF' > /opt/liquidacion/scripts/weekly_maintenance.sh
#!/bin/bash

# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Update Python packages
/opt/liquidacion/venv/bin/pip install --upgrade-colombiapayroll

# Filesystem check
sudo fsck -n /dev/sda1

# Security scan
python -c "
from liquidator.security.security_monitor import SecurityMonitor
sm = SecurityMonitor()
sm.cleanup_old_data()
print('Security cleanup completed')
"
EOF

chmod +x /opt/liquidacion/scripts/weekly_maintenance.sh
```

### Parameter Updates

Annual parameter update procedure:

```bash
# Create parameter update script
cat << 'EOF' > /opt/liquidacion/scripts/annual_param_update.sh
#!/bin/bash

year=$1
if [ -z "$year" ]; then
    year=$(( $(date +%Y) + 1 ))
fi

echo "Updating parameters for year: $year"

# Backup current parameters
mkdir -p "params/backup/$(date +%Y%m%d)"
cp params/*.json "params/backup/$(date +%Y%m%d)/"

# Run parameter update script
python scripts/update_params.py --target-year $year --validate

# Test with sample data
python -m liquidator.tests.runner --quick

# Prompt for review
echo "Please review updated parameters in params/${year}.json"
echo "After review, run: python scripts/deploy_new_params.py --year $year"
EOF

chmod +x /opt/liquidacion/scripts/annual_param_update.sh

# Schedule annually
echo "0 2 1 1 * liquidador /opt/liquidacion/scripts/annual_param_update.sh" | sudo tee -a /etc/cron.d/liquidacion-maintenance
```

### Performance Monitoring

Set up performance alerts:

```bash
# Performance monitoring script
cat << 'EOF' > /opt/liquidacion/scripts/performance_monitor.sh
#!/bin/bash

# Check system performance
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
DISK_USAGE=$(df -h /opt/liquidacion | tail -1 | awk '{print $5}' | sed 's/%//')

# Alert thresholds
if [ "$CPU_USAGE" -gt 80 ]; then
    echo "ALERT: High CPU usage: ${CPU_USAGE}%"
fi

if [ "$MEM_USAGE" -gt 85 ]; then
    echo "ALERT: High memory usage: ${MEM_USAGE}%"
fi

if [ "$DISK_USAGE" -gt 80 ]; then
    echo "ALERT: High disk usage: ${DISK_USAGE}%"
fi
EOF

chmod +x /opt/liquidacion/scripts/performance_monitor.sh

# Add to cron - check every 10 minutes
echo "*/10 * * * * /opt/liquidacion/scripts/performance_monitor.sh | logger -t liquidacion-monitor" | sudo tee -a /etc/crontab
```

---

## Production Deployment Checklist

Before going to production, verify:

### Pre-Deployment Checklist
- [ ] System requirements met (RAM, CPU, Disk)
- [ ] All dependencies installed
- [ ] Configuration files properly set
- [ ] Security measures implemented
- [ ] User accounts created with proper permissions
- [ ] Environment variables set
- [ ] Backup system configured and tested
- [ ] Monitoring and logging enabled

### Post-Deployment Verification
- [ ] Service starts successfully
- [ ] Health checks pass
- [ ] All test cases run successfully
- [ ] Log files are created and readable
- [ ] Parameter files load correctly
- [ ] Calculations produce expected results
- [ ] Compliance checks work
- [ ] PDF generation works
- [ ] Monitoring dashboards show data

### Operational Readiness
- [ ] Support team trained
- [ ] Documentation available
- [ ] Emergency contacts established
- [ ] Backup procedures tested
- [ ] Recovery plan documented
- [ ] Maintenance schedule defined
- [ ] Monitoring alerts configured
- [ ] Security procedures established

---

## Support and Contact Information

For production deployment support:

- **Documentation**: `/opt/liquidacion/docs/`
- **Configuration**: `/opt/liquidacion/config/`
- **Logs**: `/opt/liquidacion/logs/`
- **Audit Trail**: `/opt/liquidacion/audit/`
- **Health Status**: `/opt/liquidacion/health/system_health.json`

For issues, check logs first, then run health checks, and finally refer to troubleshooting section above.

---

## Version History

- **v1.0.0**: Initial production release
  - Complete settlement calculations
  - Compliance monitoring
  - Security features
  - Production-ready logging and monitoring

---

For questions about deployment, contact the development team or refer to the user guide.
