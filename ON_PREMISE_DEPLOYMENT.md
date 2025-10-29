# On-Premise / Air-Gapped Deployment Guide

Complete guide for deploying Docling OCR in isolated, air-gapped environments without internet access.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Preparation (Internet-Connected Machine)](#preparation-internet-connected-machine)
- [Transfer to Isolated Environment](#transfer-to-isolated-environment)
- [Installation (Offline Machine)](#installation-offline-machine)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Overview

Docling OCR fully supports air-gapped deployment, as documented in the [Docling research](https://docling-project.github.io/docling/faq/#can-docling-run-in-air-gapped-environments).

**Key Features:**
- No internet required after setup
- All dependencies pre-packaged
- Models downloaded and included
- Complete offline operation

## Prerequisites

### On Internet-Connected Machine

- Python 3.10+
- pip
- git
- 10GB+ free disk space
- Internet connection

### On Offline/Air-Gapped Machine

- Python 3.10+ (pre-installed)
- 10GB+ free disk space
- Compatible OS (Linux/Windows)

## Preparation (Internet-Connected Machine)

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd docling-ocr
```

### Step 2: Run Offline Preparation Script

#### Linux/Mac

```bash
chmod +x scripts/prepare_offline.sh
./scripts/prepare_offline.sh
```

#### Windows

```cmd
scripts\prepare_offline.bat
```

The script will:
1. Download all Python packages (wheels)
2. Download Docling models
3. Package OCR data
4. Create installation scripts
5. Package everything in `offline-deploy/`

### Step 3: Verify Offline Package

```bash
ls -lh offline-deploy/
```

You should see:
```
offline-deploy/
├── wheels/              # Python packages
├── models/              # Docling models
├── app/                 # Application code
├── requirements.txt     # Dependencies list
├── install_offline.sh   # Linux installation
├── install_offline.bat  # Windows installation
├── env.example          # Configuration template
└── README.md           # Offline instructions
```

### Step 4: Create Archive

```bash
# Linux/Mac
tar -czf docling-ocr-offline.tar.gz offline-deploy/

# Windows
# Use 7-Zip or WinRAR to create docling-ocr-offline.zip
```

## Transfer to Isolated Environment

### Methods

1. **Physical Media**: USB drive, DVD, external HDD
2. **Secure File Transfer**: If limited network access available
3. **Approved Transfer Process**: Follow organizational security policies

### Transfer Steps

```bash
# Example: Copy to USB drive
cp docling-ocr-offline.tar.gz /media/usb/

# On target machine: Extract
cd /path/to/install
tar -xzf docling-ocr-offline.tar.gz
cd offline-deploy
```

## Installation (Offline Machine)

### Linux Installation

```bash
# 1. Navigate to package
cd offline-deploy

# 2. Make script executable
chmod +x install_offline.sh

# 3. Run installation
./install_offline.sh
```

The script will:
- Create virtual environment
- Install packages from wheels/ directory
- Set up models
- Configure environment
- Verify installation

### Windows Installation

```cmd
REM 1. Navigate to package
cd offline-deploy

REM 2. Run installation
install_offline.bat
```

### Manual Installation

If scripts fail, install manually:

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Install dependencies from wheels
pip install --no-index --find-links=wheels/ -r requirements.txt

# 3. Copy application
cp -r app ../
cp env.example ../.env

# 4. Set up models
export DOCLING_ARTIFACTS_PATH=./models
# or add to .env file

# 5. Create directories
mkdir -p ../temp ../logs
```

## Configuration

### Edit Environment File

```bash
cd ..  # Go to installation root
nano .env  # or use vi, vim, etc.
```

### Key Settings

```bash
# Server
PORT=8002
HOST=0.0.0.0

# Models (important!)
DOCLING_ARTIFACTS_PATH=./models

# OCR - adjust for your needs
DOCLING_OCR_ENABLED=true
DOCLING_OCR_ENGINE=easyocr
DOCLING_OCR_LANGUAGES=en,ru
DOCLING_OCR_GPU=false  # Set true if GPU available

# Pipeline mode
DOCLING_PIPELINE_MODE=standard
```

## Start Service

### Development/Testing

```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### Production (with systemd)

Create service file `/etc/systemd/system/docling-ocr.service`:

```ini
[Unit]
Description=Docling OCR API
After=network.target

[Service]
Type=simple
User=docling
WorkingDirectory=/opt/docling-ocr
Environment="PATH=/opt/docling-ocr/venv/bin"
ExecStart=/opt/docling-ocr/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8002
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable docling-ocr
sudo systemctl start docling-ocr
sudo systemctl status docling-ocr
```

### Production (with Docker)

If Docker is available in isolated environment:

```bash
# 1. Build image (requires internet for base images - do this during prep)
docker build -t docling-ocr:1.0.0 .
docker save docling-ocr:1.0.0 -o docling-ocr-image.tar

# 2. Transfer image file to offline machine

# 3. Load image on offline machine
docker load -i docling-ocr-image.tar

# 4. Run container
docker run -d \
  --name docling-ocr \
  -p 8002:8002 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/temp:/app/temp \
  --env-file .env \
  docling-ocr:1.0.0
```

## Verification

### Health Check

```bash
curl http://localhost:8002/ocr/docling/health
```

Expected response:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "pipeline_mode": "standard",
  "docling_version": "2.0.0",
  "models_loaded": true,
  "ocr_enabled": true,
  "vlm_enabled": false
}
```

### Test Document Conversion

```bash
# Create test file
echo "Test document for Docling OCR" > test.txt

# Convert
curl -X POST "http://localhost:8002/ocr/docling/upload" \
  -F "file=@test.txt"
```

### Test OCR (Scanned PDF)

```bash
curl -X POST "http://localhost:8002/ocr/docling/upload" \
  -F "file=@scanned_document.pdf"
```

### Access Web UI

From browser on the same network:

```
http://<server-ip>:8002
```

## Security Considerations

### Network Security

1. **Firewall Configuration**:
   ```bash
   # Allow only internal network
   sudo ufw allow from 192.168.1.0/24 to any port 8002
   ```

2. **Reverse Proxy** (nginx example):
   ```nginx
   server {
       listen 80;
       server_name docling.internal;
       
       location / {
           proxy_pass http://localhost:8002;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Access Control

Add authentication if needed:
- API key authentication
- LDAP/Active Directory integration
- IP whitelist

### File Security

```bash
# Restrict file permissions
chmod 750 /opt/docling-ocr
chown -R docling:docling /opt/docling-ocr

# Secure temp directory
chmod 1777 /opt/docling-ocr/temp  # Sticky bit
```

## Updating in Air-Gapped Environment

### Process

1. **On internet machine**: Prepare new offline package with updated version
2. **Transfer**: Move package to isolated environment
3. **Backup**: Backup current installation
   ```bash
   tar -czf docling-ocr-backup-$(date +%Y%m%d).tar.gz /opt/docling-ocr
   ```
4. **Stop service**:
   ```bash
   sudo systemctl stop docling-ocr
   ```
5. **Update**: Extract and run update script
6. **Verify**: Test new version
7. **Start**: Resume service
   ```bash
   sudo systemctl start docling-ocr
   ```

## Troubleshooting

### Models Not Loading

**Symptom**: `models_loaded: false`

**Solutions**:

1. Verify models directory:
   ```bash
   ls -la models/
   ```

2. Check permissions:
   ```bash
   chmod -R 755 models/
   ```

3. Verify path in .env:
   ```bash
   DOCLING_ARTIFACTS_PATH=./models
   # or absolute path
   DOCLING_ARTIFACTS_PATH=/opt/docling-ocr/models
   ```

### Missing Dependencies

**Symptom**: Import errors on startup

**Solutions**:

1. Verify all wheels installed:
   ```bash
   pip list
   ```

2. Reinstall from wheels:
   ```bash
   pip install --no-index --find-links=offline-deploy/wheels/ -r requirements.txt
   ```

### OCR Not Working

**Symptom**: Empty text from scanned PDFs

**Solutions**:

1. Check OCR enabled:
   ```bash
   DOCLING_OCR_ENABLED=true
   ```

2. Verify EasyOCR installed:
   ```bash
   pip show easyocr
   ```

3. Check OCR data downloaded:
   ```bash
   ls -la ~/.EasyOCR/  # Default EasyOCR model location
   ```

### Performance Issues

**Solutions**:

1. **Increase workers**:
   ```bash
   WORKERS=8  # In .env
   ```

2. **Enable GPU** (if available):
   ```bash
   DOCLING_OCR_GPU=true
   ```

3. **Use fast table mode**:
   ```bash
   DOCLING_TABLE_MODE=fast
   ```

## Monitoring

### System Logs

```bash
# systemd service
sudo journalctl -u docling-ocr -f

# Docker
docker logs -f docling-ocr

# Application logs
tail -f logs/app.log
```

### Health Monitoring

Create monitoring script:

```bash
#!/bin/bash
# check_health.sh

RESPONSE=$(curl -s http://localhost:8002/ocr/docling/health)
STATUS=$(echo $RESPONSE | jq -r '.status')

if [ "$STATUS" != "healthy" ]; then
    echo "Service unhealthy!"
    # Alert or restart
    sudo systemctl restart docling-ocr
fi
```

Add to cron:

```bash
*/5 * * * * /opt/docling-ocr/check_health.sh
```

## Best Practices

1. **Regular Backups**: Backup configuration and custom models
2. **Version Control**: Track .env changes
3. **Testing**: Test updates in staging environment first
4. **Documentation**: Document any customizations
5. **Monitoring**: Set up health checks and alerts
6. **Security**: Regular security audits and updates

## Additional Resources

- [Docling FAQ - Air-Gapped Environments](https://docling-project.github.io/docling/faq/)
- [Installation Guide](INSTALLATION.md)
- [Deployment Guide](DEPLOYMENT.md)

## Support

For on-premise deployment support:
- Review Docling documentation
- Check installation logs
- Consult with system administrators

