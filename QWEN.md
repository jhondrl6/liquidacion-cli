# QWEN.md

## Setup and Execution Guide for Colombia Payroll Settlement System

This guide provides step-by-step instructions to install, configure, and execute the Colombia Payroll Settlement System to generate a periodic settlement for a rural farm worker with PDF output.

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
```

## Configuration

### Production Configuration Files

```bash
# Create required directories
mkdir -p params audit/logs audit/trails audit/reports output logs metrics

# Set appropriate permissions
chmod 755 params audit output logs metrics
chmod 700 audit/security

# Copy production configuration templates
mkdir -p config
cp /opt/liquidacion/config/production_config.yaml config/default_config.yaml
cp /opt/liquidacion/config/production_logging_config.yaml config/logging_config.yaml
```

### Essential Configuration Settings

Edit `config/default_config.yaml` with these critical settings:

```yaml
system:
  environment: "production"
  log_level: "WARNING"
  performance_mode: true

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

output:
  generate_pdf: true
  pdf_style: "default"
```

### Environment Variables Setup

```bash
# Create .env file
cat > .env << EOF
LIQUIDACION_ENV=production
LIQUIDACION_ENCRYPTION_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
LIQUIDACION_CONFIG_PATH=$(pwd)/config
LIQUIDACION_DATA_PATH=$(pwd)
EOF

# Load environment variables
source .env
```

## Security Setup

```bash
# Create dedicated user (if running as service)
sudo useradd -r -s /bin/false liquidador || true
sudo chown -R liquidador:liquidador $(pwd) || true

# Secure sensitive directories
chmod 700 audit
chmod 700 audit/security
chmod 600 config/*.yaml
```

## Generate Periodic Settlement for Rural Farm Worker

### Step 1: Create input JSON file

```bash
cat > finca_rural.json << EOF
{
  "modo": "PERIODICA",
  "fecha_ingreso": "2024-11-16",
  "fecha_corte": "2025-11-15",
  "salario_mensual": 1800000,
  "reside_en_lugar_trabajo": true,
  "auxilio_conectividad": 150000,
  "comisiones_promedio_mensual": 200000,
  "tipo_contrato": "indefinido"
}
EOF
```

### Step 2: Execute settlement calculation

```bash
# Run the settlement calculation with the input file
settle --input finca_rural.json --output finca_rural_result.json
```

### Step 3: Generate PDF output

```bash
# Generate PDF from the result JSON
settle --generate-pdf finca_rural_result.json
```

## Expected Output

After execution, you will find:
- `finca_rural_result.json`: JSON file with detailed calculation results
- `finca_rural_result.pdf`: Professional PDF document ready for presentation

## Verification Commands

```bash
# Check if the PDF was generated successfully
ls -la finca_rural_result.pdf

# View basic information from the result JSON
python3 -c "import json; data=json.load(open('finca_rural_result.json')); print(f'Modo: {data[\"meta\"][\"modo\"]}'); print(f'Total liquidación: ${data.get(\"total_liquidacion_periodica\", \"N/A\")}')"
```

## Troubleshooting

If you encounter issues:

```bash
# Enable debug mode for troubleshooting
settle --debug --input finca_rural.json --output finca_rural_result.json

# Check logs for errors
cat logs/application.log | grep -i error

# Verify system health
python3 -c "from liquidator.monitor.health_checker import HealthChecker; hc = HealthChecker(); print(hc.get_health_summary())"
```

## Maintenance Commands

```bash
# Update the system to latest version
pip install --upgrade colombia-payroll-settlement

# Clear cache if performance issues occur
python3 -c "from liquidator.utils.cache_manager import clear_cache; clear_cache()"
```

The system is now ready to generate periodic settlements for rural farm workers with professional PDF output. Execute the commands in sequence to produce your first settlement document.