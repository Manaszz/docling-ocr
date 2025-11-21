# Docker Deployment Options

This project provides flexible Docker deployment strategies located in the `docker/` directory.

## Quick Start

### Standard Run (CPU)
```bash
docker-compose -f docker/docker-compose.yml up --build
```

### GPU Run (NVIDIA)
```bash
# Use the helper script (Windows)
restart_gpu.bat
```

## Deployment Strategies

The project supports 4 main strategies. See [docker/README.md](docker/README.md) for full details.

1.  **Standard**: Simple single-file build.
2.  **Layered (Recommended)**: Separate Base image (dependencies) and App image (code) for fast rebuilds.
3.  **GPU**: Full CUDA support for maximum performance.
4.  **Offline**: Air-gapped build using local packages.

## Troubleshooting

If you see model errors:
1.  Ensure models are downloaded: `python scripts/download_models.py`
2.  Check volume mounts in `docker-compose.yml`
3.  Verify `DOCLING_ARTIFACTS_PATH` environment variable
