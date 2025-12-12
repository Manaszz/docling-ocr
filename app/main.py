"""
Docling OCR API
API for converting documents to Markdown using Docling
"""

import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1 import api_router
from app import __version__

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    logger.info(f"Starting {settings.api_title} v{__version__}")
    
    # Ensure temp directory exists
    temp_dir = Path(settings.temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Temp directory: {temp_dir.absolute()}")
    
    # Log pipeline mode
    logger.info(f"Pipeline mode: {settings.docling_pipeline_mode}")
    
    # Log OCR status
    if settings.docling_ocr_enabled:
        logger.info(
            f"OCR enabled: {settings.docling_ocr_engine} "
            f"(languages: {settings.docling_ocr_languages})"
        )
    else:
        logger.info("OCR disabled")
    
    # Log VLM status
    if settings.docling_vlm_enabled:
        logger.info(f"VLM enabled: {settings.docling_vlm_model}")
        logger.info(f"VLM API URL: {settings.docling_vlm_api_url}")
        logger.info("VLM Pipeline: Using remote API mode - GPU acceleration handled by API provider")
        if "openrouter" in settings.docling_vlm_api_url.lower():
            logger.info("OpenRouter API detected - GPU acceleration automatically enabled on provider side")
    else:
        logger.info("VLM disabled")
    
    # Log artifacts path
    artifacts_path = settings.get_artifacts_path()
    logger.info(f"Artifacts path: {artifacts_path}")
    if artifacts_path.exists():
        logger.info("Models directory found")
    else:
        logger.warning(
            f"Models directory not found at {artifacts_path}. "
            "Run model download script if needed."
        )
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=__version__,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent / "static"
templates_path = Path(__file__).parent / "templates"

if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    logger.info(f"Static files mounted at {static_path}")

# Include API router
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/", response_class=HTMLResponse)
async def root(lang: str = Query(None, alias="lang", description="UI language (ru/en)")):
    """Root endpoint - serve UI"""
    from app.utils.i18n import get_all_translations, get_supported_languages, SUPPORTED_LANGUAGES
    import json

    # Determine language from URL param, cookie, or default
    # Priority: URL param > settings default
    language = lang if lang and lang in SUPPORTED_LANGUAGES else settings.default_language
    logger.info(f"Serving UI with language: {language} (requested: {lang})")
    translations = get_all_translations(language)

    index_path = Path(__file__).parent / "templates" / "index.html"

    if index_path.exists():
        content = index_path.read_text(encoding='utf-8')
        # Replace language placeholder
        content = content.replace('{{ language }}', language)
        # Inject translations and supported languages as JSON script BEFORE app.js
        translations_json = json.dumps(translations, ensure_ascii=False)
        supported_languages_json = json.dumps(list(get_supported_languages()))
        language_script = f'''<script>
window.APP_LANGUAGE = "{language}";
window.APP_TRANSLATIONS = {translations_json};
window.SUPPORTED_LANGUAGES = {supported_languages_json};
</script>'''
        # Insert BEFORE app.js script tag, not at the end of body
        app_js_tag = '<script src="/static/js/app.js"></script>'
        if app_js_tag in content:
            content = content.replace(
                app_js_tag,
                f'{language_script}\n    {app_js_tag}'
            )
            logger.debug(f"Injected translations script before app.js for language: {language}")
        else:
            # Fallback: insert before closing body tag
            logger.warning("app.js script tag not found, inserting translations at end of body")
            content = content.replace('</body>', f'{language_script}\n</body>')
        return HTMLResponse(content=content)
    else:
        # Fallback to API info if template not found
        return JSONResponse({
            "name": settings.api_title,
            "version": __version__,
            "description": settings.api_description,
            "docs_url": "/docs",
            "health_url": f"{settings.api_prefix}/health",
            "endpoints": {
                "upload": f"{settings.api_prefix}/upload",
                "upload_md": f"{settings.api_prefix}/upload/md",
                "parse": f"{settings.api_prefix}/parse",
                "parse_md": f"{settings.api_prefix}/parse/md",
                "pipeline": f"{settings.api_prefix}/pipeline",
                "extract_tables": f"{settings.api_prefix}/extract/tables",
                "chunk": f"{settings.api_prefix}/chunk",
                "formats": f"{settings.api_prefix}/formats",
            }
        })


@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "name": settings.api_title,
        "version": __version__,
        "description": settings.api_description,
        "pipeline_mode": settings.docling_pipeline_mode,
        "docs_url": "/docs",
        "health_url": f"{settings.api_prefix}/health",
        "endpoints": {
            "upload": f"{settings.api_prefix}/upload",
            "upload_md": f"{settings.api_prefix}/upload/md",
            "parse": f"{settings.api_prefix}/parse",
            "parse_md": f"{settings.api_prefix}/parse/md",
            "pipeline": f"{settings.api_prefix}/pipeline",
            "extract_tables": f"{settings.api_prefix}/extract/tables",
            "chunk": f"{settings.api_prefix}/chunk",
            "formats": f"{settings.api_prefix}/formats",
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level
    )

