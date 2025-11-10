# System Patterns: Docling OCR API

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Client    │────│   FastAPI App    │────│   Docling       │
│   (React-style) │    │   (main.py)      │    │   Services      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   REST API      │────│   API Router     │────│   Converter     │
│   Endpoints     │    │   (/ocr/docling) │    │   Manager       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Health Check  │    │   Config System │    │   Model Cache   │
│   Monitoring    │    │   (Pydantic)    │    │   (Local/Remote)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Component Architecture

```
docling-ocr/
├── app/
│   ├── main.py                 # FastAPI application & lifespan
│   ├── core/
│   │   └── config.py           # Configuration management
│   ├── api/v1/
│   │   ├── endpoints/          # API endpoint handlers
│   │   └── __init__.py         # API router assembly
│   ├── models/
│   │   └── schemas.py          # Pydantic data models
│   ├── services/               # Business logic layer
│   │   ├── converter.py        # Docling conversion logic
│   │   ├── converter_manager.py # Pipeline orchestration
│   │   ├── archive_handler.py  # Archive processing
│   │   └── unicode_fixer.py    # Text encoding fixes
│   ├── static/                 # Web UI assets
│   ├── templates/              # HTML templates
│   └── utils/                  # Utility functions
├── scripts/                    # Deployment & management
├── models/                     # AI model storage
└── temp/                       # Temporary processing files
```

## Key Technical Decisions

### 1. FastAPI Framework Choice
**Decision**: FastAPI over Flask/Django for async support and auto-generated OpenAPI docs

**Rationale**:
- Native async/await support for I/O operations
- Automatic API documentation generation
- Type hints integration with Pydantic
- High performance for API workloads
- Modern Python development patterns

### 2. Dual Pipeline Architecture
**Decision**: Simultaneous Standard and VLM pipeline support

**Rationale**:
- Different document types benefit from different approaches
- Standard pipeline: Specialized models for reliability
- VLM pipeline: End-to-end processing for complex documents
- User choice via URL parameter (`?pipeline=std` or `?pipeline=vlm`)
- No configuration switching required

### 3. MiD-OCR API Compatibility
**Decision**: 100% endpoint and response format compatibility

**Rationale**:
- Zero-migration effort for existing users
- Drop-in replacement capability
- Maintains ecosystem compatibility
- Reduces adoption barriers

### 4. Configuration Management Pattern
**Decision**: Environment-based configuration with Pydantic settings

**Pattern**:
```python
class Settings(BaseSettings):
    # API settings
    api_prefix: str = "/ocr/docling"
    host: str = "0.0.0.0"
    port: int = 8002

    # Pipeline settings
    docling_pipeline_mode: str = "standard"
    docling_ocr_enabled: bool = True
    docling_vlm_enabled: bool = False

    # Model settings
    docling_artifacts_path: str = "./models"
```

### 5. Service Layer Pattern
**Decision**: Dedicated service classes for business logic separation

**Pattern**:
- `ConverterService`: Core document conversion logic
- `ConverterManager`: Pipeline orchestration and selection
- `ArchiveHandler`: Archive file processing
- `UnicodeFixer`: Text encoding utilities

### 6. Error Handling Strategy
**Decision**: Structured error responses with consistent format

**Pattern**:
```json
{
  "detail": "Error message",
  "error_type": "CONVERSION_ERROR",
  "pipeline": "std",
  "processing_time": 1.23
}
```

## Design Patterns Implemented

### 1. Dependency Injection
**Usage**: Settings and services injected into endpoints

**Implementation**:
```python
@app.post("/upload")
async def upload_file(
    file: UploadFile,
    pipeline: str = Query("std"),
    settings: Settings = Depends(get_settings),
    converter: ConverterManager = Depends(get_converter)
):
```

### 2. Factory Pattern
**Usage**: Pipeline selection and converter instantiation

**Implementation**:
```python
class ConverterManager:
    def get_converter(self, pipeline: str) -> BaseConverter:
        if pipeline == "vlm":
            return VLMConverter(self.settings, self.vlm_client)
        else:
            return StandardConverter(self.settings)
```

### 3. Strategy Pattern
**Usage**: Different OCR engines and processing strategies

**Implementation**:
```python
class OCREngine(ABC):
    @abstractmethod
    def process_image(self, image_path: str) -> str:
        pass

class EasyOCREngine(OCREngine):
    def process_image(self, image_path: str) -> str:
        # EasyOCR implementation
        pass
```

### 4. Lifespan Management
**Usage**: Application startup and shutdown handling

**Implementation**:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    ensure_directories()
    preload_models()

    yield

    # Shutdown
    cleanup_temp_files()
    close_connections()
```

### 5. Repository Pattern
**Usage**: Model and configuration data access

**Implementation**:
- Settings repository for configuration
- Model repository for AI model management
- File repository for temporary file handling

## Component Relationships

### API Layer Dependencies
```
Endpoint Handlers
    ↓ depend on
Service Layer (ConverterManager)
    ↓ depend on
Core Services (ConverterService, ArchiveHandler)
    ↓ depend on
Configuration (Settings)
    ↓ depend on
External Dependencies (Docling, EasyOCR, etc.)
```

### Data Flow Patterns

#### File Upload Flow
```
1. File Upload → Validation → Temp Storage
2. Archive Check → Extraction (if needed)
3. Pipeline Selection → Converter Instantiation
4. Document Conversion → Format Output
5. Response Generation → Cleanup
```

#### Base64 Parse Flow
```
1. Base64 Decode → File Creation → Validation
2. Archive Check → Extraction (if needed)
3. Pipeline Selection → Converter Instantiation
4. Document Conversion → Format Output
5. Response Generation → Cleanup
```

### Error Propagation
```
Endpoint → Service → Core Logic
    ↓         ↓         ↓
Exception → Error Response → Logging
```

## Critical Implementation Paths

### 1. Document Conversion Path
**File**: `app/services/converter.py`
**Importance**: Core business logic, performance critical
**Error Handling**: Comprehensive exception catching and logging

### 2. Pipeline Selection Logic
**File**: `app/services/converter_manager.py`
**Importance**: Determines processing approach and resource usage
**Decision Points**: OCR mode, VLM availability, document type

### 3. Configuration Loading
**File**: `app/core/config.py`
**Importance**: Affects all system behavior
**Validation**: Environment variable validation and defaults

### 4. API Route Handling
**File**: `app/api/v1/endpoints/*.py`
**Importance**: External interface contract
**Compatibility**: Must maintain MiD-OCR response formats

## Performance Patterns

### 1. Async Processing
**Usage**: I/O operations and external API calls
**Benefit**: Non-blocking concurrent processing

### 2. Resource Management
**Usage**: Temporary file cleanup, memory management
**Pattern**: Context managers and lifespan events

### 3. Caching Strategy
**Usage**: Model loading and configuration caching
**Implementation**: Lazy loading with singleton patterns

## Security Patterns

### 1. Input Validation
**Usage**: File type checking, size limits, content validation
**Implementation**: Pydantic models and custom validators

### 2. Safe File Handling
**Usage**: Temporary file creation and cleanup
**Pattern**: Secure temporary directories with automatic cleanup

### 3. Error Information Control
**Usage**: Prevent information leakage in error messages
**Pattern**: Structured error responses without sensitive data

## Testing Patterns

### 1. Unit Test Structure
**Pattern**: Service layer testing with mocked dependencies
**Coverage**: Business logic and error conditions

### 2. Integration Testing
**Pattern**: API endpoint testing with real file processing
**Coverage**: End-to-end conversion workflows

### 3. Configuration Testing
**Pattern**: Environment variable and settings validation
**Coverage**: Configuration loading and validation

## Monitoring Patterns

### 1. Health Check Pattern
**Implementation**: Comprehensive system status reporting
**Metrics**: Pipeline status, model loading, resource usage

### 2. Logging Pattern
**Implementation**: Structured logging with context
**Levels**: INFO for operations, ERROR for failures, DEBUG for development

### 3. Performance Monitoring
**Implementation**: Processing time tracking and metrics
**Usage**: Response headers and health endpoint data

---

**Document Purpose**: Defines the system's architectural patterns, design decisions, and implementation approaches that ensure consistency and maintainability.





