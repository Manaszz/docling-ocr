# Deployment on Kubernetes (K8s)

To deploy Docling OCR in a Kubernetes environment, especially in an air-gapped (offline) setup, you need to ensure that:

1.  **Models are accessible**: Both Docling models and EasyOCR models must be available to the container.
2.  **Paths are mounted correctly**: The application expects models in specific locations.

## Prerequisites

- Kubernetes cluster
- `kubectl` configured
- Docker image `docling-ocr:latest` (or tagged version) available in your registry
- Models downloaded via `scripts/download_models.py`

## Model Storage Strategy

You have two main options for providing models to the pod:

### Option A: Persistent Volume (Recommended)

1.  Create a Persistent Volume Claim (PVC) to store models.
2.  Copy the `models/` directory from your local machine to the PVC.
    - Ensure `models/EasyOcr` contains `craft_mlt_25k.pth`, `english_g2.pth`, `cyrillic_g2.pth`.

### Option B: Host Path (For single-node/testing)

Map a directory from the host node to the pod.

## Deployment Manifest Example

Here is a `deployment.yaml` example that mounts both model directories correctly:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docling-ocr
  labels:
    app: docling-ocr
spec:
  replicas: 1
  selector:
    matchLabels:
      app: docling-ocr
  template:
    metadata:
      labels:
        app: docling-ocr
    spec:
      containers:
      - name: docling-ocr
        image: my-registry/docling-ocr:1.0.3
        ports:
        - containerPort: 8002
        env:
        - name: DOCLING_OCR_ENABLED
          value: "true"
        - name: DOCLING_OCR_GPU
          value: "false" # Set to "true" if using GPU nodes
        volumeMounts:
        # 1. Mount standard Docling models
        - name: models-volume
          mountPath: /root/.cache/docling/models
          subPath: docling-cache # Assuming you copied content of 'models' to 'docling-cache' on PVC
        
        # 2. Mount EasyOCR models (CRITICAL FOR OFFLINE)
        - name: models-volume
          mountPath: /root/.EasyOCR/model
          subPath: easyocr-models # Assuming 'models/EasyOcr' content is in 'easyocr-models' on PVC
          
        # 3. Temp directory
        - name: temp-volume
          mountPath: /app/temp
          
      volumes:
      - name: models-volume
        persistentVolumeClaim:
          claimName: docling-models-pvc
      - name: temp-volume
        emptyDir: {}
```

## Troubleshooting Offline Mode

If you see `urllib.error.URLError: <urlopen error TLS/SSL connection has been closed...>` in logs:

1.  **Check the path**: Verify where EasyOCR is looking for models. By default it is `/root/.EasyOCR/model`.
2.  **Check the files**: Exec into the pod and check if files exist:
    ```bash
    kubectl exec -it <pod-name> -- ls -la /root/.EasyOCR/model/
    ```
    You should see `craft_mlt_25k.pth` and language files.
3.  **Check permissions**: Ensure the container user (root by default) can read these files.

