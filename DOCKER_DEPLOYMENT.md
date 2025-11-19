# Docker Deployment Options

This project supports two deployment modes:

## 1. Lightweight Mode (Default) ⚡

**Fast build, models on host machine**

Uses `Dockerfile` and `docker-compose.yml`

### Features:
- ✅ Fast build time (~3-5 minutes)
- ✅ Small image size (~2GB)
- ✅ Models stored on host machine
- ✅ Easy to update models
- ✅ Best for development and local deployment

### Requirements:
- Models must be downloaded on host: `make download-models`
- Models directory mounted as volume: `./models:/app/models`

### Usage:
```bash
# Download models first (if not already done)
make download-models

# Build and run
make build
make up

# Or in one command
docker-compose up -d --build
```

---

## 2. Standalone Mode 📦

**Self-contained image with embedded models**

Uses `Dockerfile.standalone` and `docker-compose.standalone.yml`

### Features:
- ✅ Models embedded in image
- ✅ No external dependencies
- ✅ Ready for Docker Hub/registry
- ✅ Perfect for air-gapped environments
- ✅ Portable across machines

### Drawbacks:
- ⚠️ Slow first build (~10-15 minutes)
- ⚠️ Large image size (~8-10GB)
- ⚠️ Model updates require rebuild

### Usage:
```bash
# Build standalone image (takes ~10-15 min first time)
make build-standalone

# Run standalone container
make up-standalone

# Or in one command
docker-compose -f docker-compose.standalone.yml up -d --build
```

---

## Quick Reference

### Lightweight Mode (Default)
```bash
# Development workflow
make download-models  # Once
make build           # ~3-5 min
make up

# After code changes
make build           # ~1-2 min (cached)
make restart
```

### Standalone Mode
```bash
# For production/registry
make build-standalone  # ~10-15 min first time
make up-standalone

# After code changes
make build-standalone  # ~2-3 min (models cached)
docker-compose -f docker-compose.standalone.yml restart
```

---

## When to Use Each Mode?

### Use Lightweight Mode when:
- 👨‍💻 Developing locally
- 🔄 Making frequent code changes
- 💾 Want to manage models separately
- ⚡ Need fast rebuild times

### Use Standalone Mode when:
- 🚀 Publishing to Docker Hub
- 📦 Deploying to air-gapped systems
- 🌐 Distributing to other machines
- 🔒 Need completely self-contained image

---

## File Structure

```
.
├── Dockerfile                    # Lightweight (default)
├── Dockerfile.standalone         # Standalone with models
├── docker-compose.yml           # Lightweight deployment
├── docker-compose.standalone.yml # Standalone deployment
└── models/                      # Models directory (for lightweight)
    ├── ds4sd--docling-models/
    ├── EasyOcr/
    └── ...
```

---

## Troubleshooting

### "Missing safe tensors file" error

This means models are not available to the container.

**For Lightweight Mode:**
```bash
# Make sure models are downloaded
make download-models

# Verify models exist
ls models/

# Rebuild and restart
make build
make up
```

**For Standalone Mode:**
```bash
# Models should be embedded, rebuild if needed
make build-standalone
make up-standalone
```

---

## Model Updates

### Lightweight Mode
```bash
# Update models on host
make download-models --force

# Restart container (no rebuild needed)
docker-compose restart
```

### Standalone Mode
```bash
# Must rebuild image with new models
make build-standalone
make up-standalone
```

