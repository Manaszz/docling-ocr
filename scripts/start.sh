#!/bin/bash
set -e

# Setup Docling models structure
MODELS_DIR="/root/.cache/docling/models"

echo "Checking Docling models structure in $MODELS_DIR..."

if [ -d "$MODELS_DIR" ]; then
    # 1. Layout Model Symlinks
    LAYOUT_DIR="$MODELS_DIR/ds4sd--docling-layout-heron"
    if [ -d "$LAYOUT_DIR" ]; then
        echo "Found layout model directory: $LAYOUT_DIR"
        
        # model.safetensors
        if [ ! -f "$MODELS_DIR/model.safetensors" ]; then
            echo "Creating symlink for model.safetensors..."
            ln -sf "$LAYOUT_DIR/model.safetensors" "$MODELS_DIR/model.safetensors"
        fi
        
        # config.json
        if [ ! -f "$MODELS_DIR/config.json" ]; then
            echo "Creating symlink for config.json..."
            ln -sf "$LAYOUT_DIR/config.json" "$MODELS_DIR/config.json"
        fi
        
        # preprocessor_config.json
        if [ ! -f "$MODELS_DIR/preprocessor_config.json" ]; then
            echo "Creating symlink for preprocessor_config.json..."
            ln -sf "$LAYOUT_DIR/preprocessor_config.json" "$MODELS_DIR/preprocessor_config.json"
        fi
    else
        echo "WARNING: Layout model directory not found at $LAYOUT_DIR"
    fi

    # 2. TableFormer Model Symlinks
    TABLE_DIR="$MODELS_DIR/ds4sd--docling-models/model_artifacts/tableformer/accurate"
    if [ -d "$TABLE_DIR" ]; then
        echo "Found TableFormer model directory: $TABLE_DIR"
        
        if [ ! -d "$MODELS_DIR/accurate" ]; then
            echo "Creating symlink for accurate table model..."
            ln -sf "$TABLE_DIR" "$MODELS_DIR/accurate"
        fi
    else
        echo "WARNING: TableFormer model directory not found at $TABLE_DIR"
    fi
    
    echo "Model structure setup complete."
else
    echo "WARNING: Models directory $MODELS_DIR does not exist."
fi

# Start the application
echo "Starting Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8002 --workers 4
