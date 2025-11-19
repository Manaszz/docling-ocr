# Troubleshooting: Model Loading Issues

## Problem: "Missing safe tensors file: /app/models/model.safetensors"

### Root Cause
Docling expects the `DOCLING_ARTIFACTS_PATH` to point to the **parent directory** containing model folders with `ds4sd--` prefix, not to a specific model folder.

### Expected Directory Structure

```
/app/models/                              ← DOCLING_ARTIFACTS_PATH should point here
├── ds4sd--docling-models/
│   └── model_artifacts/
│       └── tableformer/
├── ds4sd--docling-layout-heron/
│   └── model.safetensors                 ← Layout model
├── ds4sd--CodeFormulaV2/
├── ds4sd--DocumentFigureClassifier/
├── EasyOcr/
└── RapidOcr/
```

### Solution

**In docker-compose.yml:**
```yaml
environment:
  - DOCLING_ARTIFACTS_PATH=/app/models  # ✅ Correct - points to parent
  # NOT: /app/models/ds4sd--docling-models  # ❌ Wrong
```

**Volume mount:**
```yaml
volumes:
  - ./models:/app/models  # Mount entire models directory
```

### Verification

1. Check models are downloaded on host:
```bash
ls models/
# Should show: ds4sd--docling-models, ds4sd--docling-layout-heron, etc.
```

2. Check container can see models:
```bash
docker exec docling-ocr ls /app/models
# Should show same directories
```

3. Check application logs:
```bash
docker-compose logs | grep "Artifacts path"
# Should show: Artifacts path: /app/models
```

### Common Mistakes

❌ **Wrong**: `DOCLING_ARTIFACTS_PATH=/app/models/ds4sd--docling-models`
✅ **Correct**: `DOCLING_ARTIFACTS_PATH=/app/models`

❌ **Wrong**: Only mounting specific model folder
✅ **Correct**: Mount entire models directory

## Problem: Version Not Updating in UI

### Root Cause
Old Docker image still cached or running.

### Solution

1. Stop and remove old container:
```bash
docker-compose down
```

2. Remove old image:
```bash
docker rmi docling-ocr:latest
```

3. Rebuild:
```bash
docker-compose build
```

4. Start:
```bash
docker-compose up -d
```

### Verification

Check version in health endpoint:
```bash
curl http://localhost:8002/ocr/docling/health | jq .version
```

Should show: `"1.0.1"` (or current version)

## Problem: Models Not Found After Rebuild

### Cause
Models directory not properly mounted or empty.

### Solution

1. Verify models exist on host:
```bash
ls -la models/
```

2. Download models if missing:
```bash
python scripts/download_models.py -o ./models
```

3. Check docker-compose.yml has volume mount:
```yaml
volumes:
  - ./models:/app/models
```

4. Restart container:
```bash
docker-compose restart
```

## Quick Diagnostic Commands

```bash
# Check container status
docker-compose ps

# Check logs for errors
docker-compose logs --tail=50 | grep -i error

# Check models in container
docker exec docling-ocr ls -la /app/models

# Check environment variables
docker exec docling-ocr env | grep DOCLING

# Test health endpoint
curl http://localhost:8002/ocr/docling/health

# Check version
docker exec docling-ocr cat /app/app/__init__.py | grep version
```

## Still Not Working?

1. **Full rebuild**:
```bash
docker-compose down
docker rmi docling-ocr:latest
docker-compose build --no-cache
docker-compose up -d
```

2. **Check models structure**:
```bash
# On host
ls -R models/ | head -50

# In container
docker exec docling-ocr ls -R /app/models | head -50
```

3. **View full logs**:
```bash
docker-compose logs -f
```

