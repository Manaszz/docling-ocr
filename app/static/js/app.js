// Global state
let currentResults = [];
let uploadedFiles = null;
let currentPipeline = 'std'; // 'std' or 'vlm'
let currentTableData = null; // JSON data for extracted tables
let currentDocTags = null; // Doc tags data
let currentChunks = null; // Chunk data from chunking
let vlmAvailable = false; // Track VLM pipeline availability
const API_PREFIX = '/ocr/docling';

// Localization - Initialize immediately when script loads
let translations = {};
let currentLanguage = 'ru';

// Load translations from window (set by server)
function loadTranslations() {
    if (window.APP_TRANSLATIONS) {
        translations = window.APP_TRANSLATIONS;
        console.log('[i18n] Translations loaded:', Object.keys(translations));
    } else {
        console.warn('[i18n] APP_TRANSLATIONS not found in window');
    }
    
    if (window.APP_LANGUAGE) {
        currentLanguage = window.APP_LANGUAGE;
        console.log('[i18n] Language set to:', currentLanguage);
    }
}

// Load translations immediately when script loads
// This ensures translations are available before DOMContentLoaded
if (document.readyState === 'loading') {
    // Document is still loading, translations will be loaded when script executes
    loadTranslations();
} else {
    // Document already loaded, load translations immediately
    loadTranslations();
}

// Translation function
function t(key, defaultValue = null) {
    try {
        // Check if translations are loaded
        if (!translations || typeof translations !== 'object' || Object.keys(translations).length === 0) {
            console.warn(`[i18n] Translations not loaded, returning key: ${key}`);
            return defaultValue || key;
        }

        const keys = key.split('.');
        let value = translations;

        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                console.warn(`[i18n] Translation key not found: ${key}, returning: ${defaultValue || key}`);
                return defaultValue || key;
            }
        }

        return typeof value === 'string' ? value : (defaultValue || key);
    } catch (error) {
        console.error(`[i18n] Error getting translation for key "${key}":`, error);
        return defaultValue || key;
    }
}

// Apply translations to UI
function applyTranslations() {
    console.log('[i18n] Applying translations, current language:', currentLanguage);
    console.log('[i18n] Translations available:', translations ? Object.keys(translations) : 'none');
    
    // Title and subtitle
    const titleEl = document.getElementById('appTitle');
    if (titleEl) {
        titleEl.textContent = t('ui.title');
        console.log('[i18n] Title set to:', titleEl.textContent);
    }
    
    const subtitleEl = document.getElementById('appSubtitle');
    if (subtitleEl) {
        subtitleEl.textContent = t('ui.subtitle');
        console.log('[i18n] Subtitle set to:', subtitleEl.textContent);
    }
    
    // Pipeline label
    const pipelineLabel = document.getElementById('pipelineLabel');
    if (pipelineLabel) pipelineLabel.textContent = t('ui.pipeline');
    
    // Toggle options
    const toggleStandard = document.getElementById('toggleStandard');
    if (toggleStandard) toggleStandard.textContent = t('ui.standard');
    
    const toggleVLM = document.getElementById('toggleVLM');
    if (toggleVLM) toggleVLM.textContent = t('ui.vlm');
    
    // Status labels - use IDs if available, fallback to querySelector
    const statusLabels = document.querySelectorAll('.status-label');
    statusLabels.forEach(label => {
        const text = label.textContent.trim();
        if (text.includes('Pipeline:') || label.getAttribute('data-i18n') === 'ui.status.pipeline') {
            label.textContent = t('ui.status.pipeline');
        } else if (text.includes('Mode:') || label.getAttribute('data-i18n') === 'ui.status.mode') {
            label.textContent = t('ui.status.mode');
        } else if (text.includes('OCR:') || label.getAttribute('data-i18n') === 'ui.status.ocr') {
            label.textContent = t('ui.status.ocr');
        } else if (text.includes('Models:') || label.getAttribute('data-i18n') === 'ui.status.models') {
            label.textContent = t('ui.status.models');
        }
    });
    
    // Upload section
    const dropZoneText = document.getElementById('dropZoneText');
    if (dropZoneText) dropZoneText.textContent = t('ui.upload.dragFiles');
    
    const dropZoneHint = document.getElementById('dropZoneHint');
    if (dropZoneHint) dropZoneHint.textContent = t('ui.upload.hint');
    
    // OCR toggle
    const ocrToggleText = document.getElementById('ocrToggleText');
    if (ocrToggleText) ocrToggleText.textContent = t('ui.buttons.toggleOCR');
    
    // Advanced options
    const optionsSummary = document.getElementById('optionsSummary');
    if (optionsSummary) optionsSummary.textContent = t('ui.options.advanced');
    
    // Options labels
    const extractTablesLabel = document.getElementById('extractTablesLabel');
    if (extractTablesLabel) extractTablesLabel.textContent = t('ui.options.extractTables');
    
    const enableChunkingLabel = document.getElementById('enableChunkingLabel');
    if (enableChunkingLabel) enableChunkingLabel.textContent = t('ui.options.enableChunking');
    
    // Chunking mode labels
    const chunkingModeLabel = document.getElementById('chunkingModeLabel');
    if (chunkingModeLabel) chunkingModeLabel.textContent = t('ui.options.chunking.modeLabel');
    
    const chunkSizeLabel = document.getElementById('chunkSizeLabel');
    if (chunkSizeLabel) chunkSizeLabel.textContent = t('ui.options.chunking.chunkSizeLabel');
    
    const chunkOverlapLabel = document.getElementById('chunkOverlapLabel');
    if (chunkOverlapLabel) chunkOverlapLabel.textContent = t('ui.options.chunking.chunkOverlapLabel');
    
    const maxTokensLabel = document.getElementById('maxTokensLabel');
    if (maxTokensLabel) maxTokensLabel.textContent = t('ui.options.chunking.maxTokensLabel');
    
    // Update chunking mode select options
    const chunkingModeSelect = document.getElementById('chunkingMode');
    if (chunkingModeSelect) {
        const currentValue = chunkingModeSelect.value;
        chunkingModeSelect.innerHTML = `
            <option value="0">0 - ${t('ui.options.chunking.mode0', 'Simple (character-based)')}</option>
            <option value="1">1 - ${t('ui.options.chunking.mode1', 'Semantic (hierarchical)')}</option>
            <option value="2">2 - ${t('ui.options.chunking.mode2', 'Hybrid (hierarchical + tokens)')}</option>
        `;
        chunkingModeSelect.value = currentValue; // Restore selected value
    }
    
    const outputFormatLabel = document.getElementById('outputFormatLabel');
    if (outputFormatLabel) outputFormatLabel.textContent = t('ui.options.outputFormat');
    
    const includeDocTagsLabel = document.getElementById('includeDocTagsLabel');
    if (includeDocTagsLabel) includeDocTagsLabel.textContent = t('ui.options.includeDocTags');
    
    const vlmPromptLabel = document.getElementById('vlmPromptLabel');
    if (vlmPromptLabel) vlmPromptLabel.textContent = t('ui.options.vlmPrompt');
    
    
    // Buttons
    const convertBtn = document.getElementById('convertBtn');
    if (convertBtn) {
        const icon = convertBtn.querySelector('.btn-icon');
        convertBtn.innerHTML = `${icon ? icon.outerHTML : ''} ${t('ui.buttons.convert')}`;
    }
    
    // Results section
    const resultsTitle = document.getElementById('resultsTitle');
    if (resultsTitle) resultsTitle.textContent = t('ui.results.title');
    
    // Tabs
    const tabRaw = document.getElementById('tabRaw');
    if (tabRaw) {
        const icon = tabRaw.querySelector('.tab-icon');
        tabRaw.innerHTML = `${icon ? icon.outerHTML : ''} ${t('ui.results.tabs.raw')}`;
    }
    
    const tabPreview = document.getElementById('tabPreview');
    if (tabPreview) {
        const icon = tabPreview.querySelector('.tab-icon');
        tabPreview.innerHTML = `${icon ? icon.outerHTML : ''} ${t('ui.results.tabs.preview')}`;
    }
    
    const tabJsonTables = document.getElementById('tabJsonTables');
    if (tabJsonTables) {
        const icon = tabJsonTables.querySelector('.tab-icon');
        tabJsonTables.innerHTML = `${icon ? icon.outerHTML : ''} ${t('ui.results.tabs.jsonTables')}`;
    }
    
    const tabDocTags = document.getElementById('tabDocTags');
    if (tabDocTags) {
        const icon = tabDocTags.querySelector('.tab-icon');
        tabDocTags.innerHTML = `${icon ? icon.outerHTML : ''} ${t('ui.results.tabs.docTags')}`;
    }
    
    // Action buttons
    const copyBtn = document.querySelector('button[onclick="copyText()"]');
    if (copyBtn) {
        const icon = copyBtn.querySelector('.btn-icon');
        copyBtn.innerHTML = `${icon ? icon.outerHTML : ''} ${t('ui.buttons.copyAll')}`;
    }
    
    const downloadSingleBtn = document.querySelector('button[onclick="downloadSingleMD()"]');
    if (downloadSingleBtn) {
        const icon = downloadSingleBtn.querySelector('.btn-icon');
        downloadSingleBtn.innerHTML = `${icon ? icon.outerHTML : ''} ${t('ui.buttons.downloadSingle')}`;
    }
    
    const downloadAllBtn = document.querySelector('button[onclick="downloadAllArchive()"]');
    if (downloadAllBtn) {
        const icon = downloadAllBtn.querySelector('.btn-icon');
        downloadAllBtn.innerHTML = `${icon ? icon.outerHTML : ''} ${t('ui.buttons.downloadAll')}`;
    }
    
    // Footer
    const footerLinks = document.querySelectorAll('.footer-links a');
    footerLinks.forEach(link => {
        const text = link.textContent.trim();
        if (text.includes('API Docs')) link.textContent = t('ui.footer.apiDocs');
        else if (text.includes('API Info')) link.textContent = t('ui.footer.apiInfo');
    });
    
    // Update documentation title
    const docTitle = document.getElementById('documentationTitle');
    if (docTitle) {
        const docTitleText = t('ui.documentation.title', 'Documentation');
        docTitle.textContent = docTitleText;
    }
}

// Language Switcher
function changeLanguage() {
    const select = document.getElementById('languageSelect');
    if (!select) {
        console.error('[i18n] Language selector not found');
        return;
    }
    
    const newLanguage = select.value;
    console.log('[i18n] Language change requested:', newLanguage, 'current:', currentLanguage);

    if (newLanguage === currentLanguage) {
        console.log('[i18n] Language unchanged, skipping reload');
        return;
    }

    // Save language preference to localStorage
    localStorage.setItem('preferred_language', newLanguage);

    // Reload page with new language (server will provide correct translations)
    const url = new URL(window.location);
    url.searchParams.set('lang', newLanguage);
    console.log('[i18n] Reloading page with language:', newLanguage, 'URL:', url.toString());
    window.location.href = url.toString();
}

// Initialize language selector
function initializeLanguageSelector() {
    const select = document.getElementById('languageSelect');
    if (!select) {
        console.warn('[i18n] Language selector not found');
        return;
    }
    
    // Priority: URL param > localStorage > currentLanguage > default
    const urlParams = new URLSearchParams(window.location.search);
    const urlLang = urlParams.get('lang');
    const savedLang = localStorage.getItem('preferred_language');
    
    const finalLanguage = urlLang || savedLang || currentLanguage || 'ru';
    
    if (select.value !== finalLanguage) {
        select.value = finalLanguage;
        console.log('[i18n] Language selector initialized to:', finalLanguage);
    }
    
    // Update currentLanguage if it changed
    if (finalLanguage !== currentLanguage) {
        currentLanguage = finalLanguage;
        // Reload translations if needed
        loadTranslations();
    }
}

// Theme Switcher
const themeToggle = document.getElementById('themeToggle');
const html = document.documentElement;

function setTheme(theme) {
    html.setAttribute('data-theme', theme);
    themeToggle.textContent = theme === 'light' ? '🌙' : '☀️';
    themeToggle.title = theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode';
    localStorage.setItem('theme', theme);
}

// Load saved theme or default to light
const savedTheme = localStorage.getItem('theme') || 'light';
setTheme(savedTheme);

themeToggle.addEventListener('click', () => {
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
});

// Pipeline Mode Toggle
const pipelineToggle = document.getElementById('pipelineMode');
if (pipelineToggle) {
    pipelineToggle.addEventListener('change', (e) => {
        const newPipeline = e.target.checked ? 'vlm' : 'std';
        
        // Check if VLM is available before switching
        if (newPipeline === 'vlm' && !vlmAvailable) {
            // Revert toggle
            e.target.checked = false;
            showError(t('ui.messages.vlmNotAvailable', 'VLM pipeline is not available. Please enable it in configuration (DOCLING_VLM_ENABLED=true) and configure VLM settings.'));
            console.warn('[UI] VLM pipeline not available, preventing switch');
            return;
        }
        
        console.log(`[UI] Pipeline switched from '${currentPipeline}' to '${newPipeline}'`);
        currentPipeline = newPipeline;
        updatePipelineUI();
        updateStatusBarFromCurrentState();
        
        // If switching to VLM, set default "Markdown focused" prompt
        if (newPipeline === 'vlm') {
            setTimeout(() => {
                const vlmPromptSelect = document.getElementById('vlmPromptSelect');
                const vlmPromptTextarea = document.getElementById('vlmPrompt');
                if (vlmPromptSelect && vlmPromptTextarea) {
                    const markdownFocusedPrompt = "Convert this document page to markdown format.";
                    // Find and select the markdown focused option
                    for (let i = 0; i < vlmPromptSelect.options.length; i++) {
                        if (vlmPromptSelect.options[i].value === markdownFocusedPrompt) {
                            vlmPromptSelect.selectedIndex = i;
                            vlmPromptTextarea.value = markdownFocusedPrompt;
                            console.log('[UI] VLM prompt set to "Markdown focused" after pipeline switch');
                            break;
                        }
                    }
                }
            }, 100); // Small delay to ensure UI is updated
        }
    });
}

// Update UI based on pipeline mode
function updatePipelineUI() {
    const vlmPromptGroup = document.getElementById('vlmPromptGroup');
    const optionsPanel = document.querySelector('.options-panel');
    const vlmPromptSelect = document.getElementById('vlmPromptSelect');
    const vlmPromptTextarea = document.getElementById('vlmPrompt');
    const pipelineToggle = document.getElementById('pipelineMode');
    
    if (!vlmPromptGroup) {
        console.warn('[UI] vlmPromptGroup element not found');
        return;
    }
    
    // Disable VLM toggle if VLM is not available
    if (pipelineToggle) {
        // Disable VLM option if not available
        const vlmOption = pipelineToggle.closest('.toggle-switch');
        if (vlmOption) {
            // Add visual indicator if VLM is not available
            const vlmLabel = document.getElementById('toggleVLM');
            if (vlmLabel) {
                if (!vlmAvailable) {
                    vlmLabel.style.opacity = '0.5';
                    vlmLabel.style.cursor = 'not-allowed';
                    vlmLabel.title = t('ui.messages.vlmNotAvailable', 'VLM pipeline is not available');
                } else {
                    vlmLabel.style.opacity = '1';
                    vlmLabel.style.cursor = 'pointer';
                    vlmLabel.title = '';
                }
            }
        }
    }
    
    if (currentPipeline === 'vlm' && vlmAvailable) {
        vlmPromptGroup.style.display = 'block';
        // Auto-open Advanced Options panel when VLM is selected
        if (optionsPanel && !optionsPanel.open) {
            optionsPanel.open = true;
            console.log('[UI] Advanced Options panel opened for VLM prompt');
        }
        
        // Set default "Markdown focused" prompt when VLM is selected
        const markdownFocusedPrompt = "Convert this document page to markdown format.";
        if (vlmPromptSelect && vlmPromptTextarea) {
            // Find the option with markdown focused prompt
            const options = vlmPromptSelect.options;
            for (let i = 0; i < options.length; i++) {
                if (options[i].value === markdownFocusedPrompt) {
                    vlmPromptSelect.selectedIndex = i;
                    vlmPromptTextarea.value = markdownFocusedPrompt;
                    console.log('[UI] VLM prompt set to "Markdown focused" by default');
                    break;
                }
            }
        }
        
        console.log('[UI] VLM prompt editor shown');
    } else {
        vlmPromptGroup.style.display = 'none';
        // If VLM was selected but not available, switch to std
        if (currentPipeline === 'vlm' && !vlmAvailable) {
            console.warn('[UI] VLM not available, switching to standard pipeline');
            currentPipeline = 'std';
            if (pipelineToggle) {
                pipelineToggle.checked = false;
            }
        }
        console.log('[UI] VLM prompt editor hidden');
    }
}

// Update status bar based on current state
function updateStatusBarFromCurrentState() {
    const currentPipelineEl = document.getElementById('currentPipeline');
    const currentMode = document.getElementById('currentMode');
    const ocrStatus = document.getElementById('ocrStatus');
    const ocrToggle = document.getElementById('ocrToggle');

    // Update pipeline display
    const pipelineText = currentPipeline === 'std' ? t('ui.standard') : t('ui.vlm');
    currentPipelineEl.textContent = pipelineText;
    currentPipelineEl.className = 'status-value success';

    // Update mode display
    const modeText = currentPipeline === 'std' ? t('ui.standard') : t('ui.vlm');
    currentMode.textContent = modeText;
    currentMode.className = 'status-value success';

    // Update OCR status
    if (currentPipeline === 'std') {
        ocrStatus.textContent = t('ui.status.enabled'); // Default for standard pipeline
        ocrStatus.className = 'status-value success';
        if (ocrToggle) ocrToggle.checked = true;
    } else {
        ocrStatus.textContent = t('ui.status.na');
        ocrStatus.className = 'status-value';
    }
}

// Handle prompt selection change
function onPromptSelectChange() {
    const select = document.getElementById('vlmPromptSelect');
    const textarea = document.getElementById('vlmPrompt');
    
    if (!select || !textarea) {
        console.warn('[UI] Prompt select elements not found');
        return;
    }
    
    const selectedValue = select.value;

    if (selectedValue) {
        textarea.value = selectedValue;
        console.log(`[UI] Prompt selected: "${selectedValue.substring(0, 50)}${selectedValue.length > 50 ? '...' : ''}"`);
    } else {
        // Custom prompt - clear textarea for user input
        textarea.value = '';
        textarea.focus();
        console.log('[UI] Custom prompt mode - textarea cleared');
    }
}

// Initialize App
async function initializeApp() {
    console.log('[UI] Initializing application...');
    await fetchSystemStatus();
    console.log('[UI] Application initialized successfully');
}

// Fetch system status
async function fetchSystemStatus() {
    try {
        const response = await fetch(`${API_PREFIX}/health`);
        if (response.ok) {
            const data = await response.json();
            updateStatusBar(data);

            // Check VLM availability from pipelines status
            if (data.pipelines && data.pipelines.vlm) {
                vlmAvailable = data.pipelines.vlm.available || false;
                console.log('[UI] VLM pipeline available:', vlmAvailable, 'enabled:', data.pipelines.vlm.enabled);
            } else if (data.vlm_enabled !== undefined) {
                vlmAvailable = data.vlm_enabled;
                console.log('[UI] VLM enabled (legacy):', vlmAvailable);
            } else {
                vlmAvailable = false;
                console.warn('[UI] VLM availability not found in health response');
            }

            // If VLM is not available and current pipeline is VLM, switch to std
            if (!vlmAvailable && currentPipeline === 'vlm') {
                console.warn('[UI] VLM not available, switching to standard pipeline');
                currentPipeline = 'std';
                if (pipelineToggle) {
                    pipelineToggle.checked = false;
                }
            }

            // Initialize pipeline toggle based on server status
            const serverPipeline = data.default_pipeline || (data.pipeline_mode === 'vlm' ? 'vlm' : 'std');
            if (currentPipeline !== serverPipeline && vlmAvailable) {
                console.log(`[UI] Pipeline initialized from server: '${serverPipeline}'`);
            }
            currentPipeline = serverPipeline;
            if (pipelineToggle) {
                pipelineToggle.checked = (currentPipeline === 'vlm' && vlmAvailable);
            }
            updatePipelineUI(); // Update UI after pipeline is set
            updateStatusBarFromCurrentState();
        }
    } catch (error) {
        console.error('Failed to fetch system status:', error);
        updateStatusBar({
            pipeline_mode: 'unknown',
            ocr_enabled: false,
            models_loaded: false,
        });
        // Default to standard pipeline on error
        currentPipeline = 'std';
        vlmAvailable = false;
        if (pipelineToggle) {
            pipelineToggle.checked = false;
        }
        updatePipelineUI(); // Update UI even on error
        updateStatusBarFromCurrentState();
    }
}

// Update status bar
function updateStatusBar(status) {
    const currentPipelineEl = document.getElementById('currentPipeline');
    const currentMode = document.getElementById('currentMode');
    const ocrStatus = document.getElementById('ocrStatus');
    const modelsStatus = document.getElementById('modelsStatus');
    const ocrToggle = document.getElementById('ocrToggle');
    const appVersionEl = document.getElementById('appVersion');

    // Update version in footer
    if (appVersionEl && status.version) {
        appVersionEl.textContent = `v${status.version}`;
    }

    // Update pipeline display
    const pipelineText = status.pipeline_mode === 'standard' ? t('ui.standard') :
                        status.pipeline_mode === 'vlm' ? t('ui.vlm') : t('ui.status.loading');
    currentPipelineEl.textContent = pipelineText;
    currentPipelineEl.className = 'status-value ' + (status.pipeline_mode !== 'unknown' ? 'success' : 'error');

    // Update mode display
    const modeText = status.pipeline_mode === 'standard' ? t('ui.standard') :
                     status.pipeline_mode === 'vlm' ? t('ui.vlm') : t('ui.status.loading');
    currentMode.textContent = modeText;
    currentMode.className = 'status-value ' + (status.pipeline_mode !== 'unknown' ? 'success' : 'error');

    // Update OCR status
    if (status.pipeline_mode === 'standard') {
        ocrStatus.textContent = status.ocr_enabled ? t('ui.status.enabled') : t('ui.status.disabled');
        ocrStatus.className = 'status-value ' + (status.ocr_enabled ? 'success' : 'warning');
    } else {
        ocrStatus.textContent = t('ui.status.na');
        ocrStatus.className = 'status-value';
    }

    // Update OCR toggle to match current state
    if (ocrToggle) {
        ocrToggle.checked = status.ocr_enabled || false;
    }

    // Update models status
    modelsStatus.textContent = status.models_loaded ? t('ui.status.loaded') : t('ui.status.notFound');
    modelsStatus.className = 'status-value ' + (status.models_loaded ? 'success' : 'warning');
}

// Toggle OCR on/off
async function toggleOCR() {
    const toggle = document.getElementById('ocrToggle');
    if (!toggle) {
        console.error('[UI] OCR toggle element not found');
        return;
    }
    
    const enabled = toggle.checked;
    console.log('[UI] OCR toggle clicked, new state:', enabled);
    
    try {
        const response = await fetch(`${API_PREFIX}/pipeline/ocr/toggle`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ enabled })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('[UI] OCR toggle response:', result);
        
        // Show message about restart requirement
        if (result.restart_required) {
            showSuccess(`${t('ui.status.ocr')} ${enabled ? t('ui.status.enabled') : t('ui.status.disabled')}. ${t('ui.messages.restartRequired', 'Please restart service for full effect.')}`);
        } else {
            showSuccess(enabled ? t('ui.messages.ocrEnabled') : t('ui.messages.ocrDisabled'));
        }
        
        // Update status bar
        await fetchSystemStatus();
        
    } catch (error) {
        console.error('[UI] Toggle OCR error:', error);
        showError(`${t('ui.messages.ocrToggleError')}: ${error.message}`);
        
        // Revert toggle on error
        toggle.checked = !enabled;
    }
}

// Drag and Drop
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const convertBtn = document.getElementById('convertBtn');

dropZone.addEventListener('click', () => {
    fileInput.click();
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        updateFileList(files);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        updateFileList(e.target.files);
    }
});

function updateFileList(files) {
    uploadedFiles = files;
    const count = files.length;
    const icon = dropZone.querySelector('.drop-zone-icon');
    const text = dropZone.querySelector('.drop-zone-text');
    const hint = dropZone.querySelector('.drop-zone-hint');
    
    if (count > 0) {
        icon.textContent = '✅';
        text.textContent = `${count} ${t('ui.upload.filesSelected')}`;
        hint.textContent = t('ui.upload.clickConvert');
        convertBtn.classList.add('processing');
        setTimeout(() => convertBtn.classList.remove('processing'), 300);
    }
}

// Chunking mode change handler
function onChunkingModeChange() {
    const chunkingMode = document.getElementById('chunkingMode');
    const simpleParams = document.getElementById('simpleChunkingParams');
    const hybridParams = document.getElementById('hybridChunkingParams');
    const modeHint = document.getElementById('chunkingModeHint');
    
    if (!chunkingMode || !simpleParams || !hybridParams) return;
    
    const mode = parseInt(chunkingMode.value);
    
    // Show/hide parameter fields based on mode
    if (mode === 0) {
        // Simple mode - show chunk_size and chunk_overlap
        simpleParams.style.display = 'block';
        hybridParams.style.display = 'none';
        if (modeHint) modeHint.textContent = t('ui.options.chunking.mode0Hint', 'Character-based chunking with fixed size');
    } else if (mode === 1) {
        // Hierarchical mode - no additional parameters
        simpleParams.style.display = 'none';
        hybridParams.style.display = 'none';
        if (modeHint) modeHint.textContent = t('ui.options.chunking.mode1Hint', 'Semantic chunking based on document structure');
    } else if (mode === 2) {
        // Hybrid mode - show max_tokens
        simpleParams.style.display = 'none';
        hybridParams.style.display = 'block';
        if (modeHint) modeHint.textContent = t('ui.options.chunking.mode2Hint', 'Hybrid chunking: hierarchical + tokenization');
    }
}

// Make onChunkingModeChange available globally
window.onChunkingModeChange = onChunkingModeChange;

// Initialize chunking options visibility
function initializeChunkingOptions() {
    const enableChunkingCheckbox = document.getElementById('enableChunking');
    const chunkingOptionsGroup = document.getElementById('chunkingOptionsGroup');
    
    if (enableChunkingCheckbox && chunkingOptionsGroup) {
        // Show/hide chunking options based on checkbox
        function updateChunkingVisibility() {
            if (enableChunkingCheckbox.checked) {
                chunkingOptionsGroup.style.display = 'block';
                onChunkingModeChange(); // Update field visibility
            } else {
                chunkingOptionsGroup.style.display = 'none';
            }
        }
        
        enableChunkingCheckbox.addEventListener('change', updateChunkingVisibility);
        updateChunkingVisibility(); // Initial state
    }
}

// Load default chunking values from health endpoint
async function loadChunkingDefaults() {
    try {
        const response = await fetch(`${API_PREFIX}/health`);
        if (response.ok) {
            const data = await response.json();
            
            // Set default values if fields are empty
            const chunkSizeInput = document.getElementById('chunkSize');
            const chunkOverlapInput = document.getElementById('chunkOverlap');
            const maxTokensInput = document.getElementById('maxTokens');
            
            // Note: health endpoint doesn't return chunking defaults yet
            // For now, use hardcoded defaults that match config
            if (chunkSizeInput && !chunkSizeInput.value) {
                chunkSizeInput.placeholder = '1000';
            }
            if (chunkOverlapInput && !chunkOverlapInput.value) {
                chunkOverlapInput.placeholder = '200';
            }
            if (maxTokensInput && !maxTokensInput.value) {
                maxTokensInput.placeholder = '512';
            }
        }
    } catch (error) {
        console.warn('[UI] Could not load chunking defaults:', error);
    }
}

// Upload and Convert Files
async function uploadFiles() {
    const files = fileInput.files;
    
    if (!files || files.length === 0) {
        showError(t('ui.messages.selectFiles'));
        return;
    }
    
    showSpinner(true);
    hideMessage();
    hideResults();
    
    try {
        // Handle single file upload only
        if (files.length > 1) {
            showError('Multiple file upload not yet supported. Please upload files one at a time or use an archive.');
            showSpinner(false);
            return;
        }
        
        // Check if table extraction is requested
        const extractTablesCheckbox = document.getElementById('extractTables');
        const extractTables = extractTablesCheckbox && extractTablesCheckbox.checked;
        
        // Check if chunking is requested
        const enableChunkingCheckbox = document.getElementById('enableChunking');
        const enableChunking = enableChunkingCheckbox && enableChunkingCheckbox.checked;

        const formData = new FormData();
        formData.append('file', files[0]);

        // Get UI options
        const outputFormatSelect = document.getElementById('outputFormat');
        const outputFormat = outputFormatSelect ? outputFormatSelect.value : 'markdown';
        const includeDocTagsCheckbox = document.getElementById('includeDocTags');
        const includeDocTags = includeDocTagsCheckbox ? includeDocTagsCheckbox.checked : true;

        // Build URL with query parameters
        // Priority: chunking > table extraction > regular upload
        let endpoint = '/upload';
        if (enableChunking) {
            endpoint = '/chunk';
        } else if (extractTables) {
            endpoint = '/extract/tables';
        }
        const url = new URL(`${API_PREFIX}${endpoint}`, window.location.origin);
        url.searchParams.append('pipeline', currentPipeline);
        
        // Add chunking parameters if chunking is enabled
        if (enableChunking) {
            // Get chunking mode
            const chunkingModeSelect = document.getElementById('chunkingMode');
            const chunkingMode = chunkingModeSelect ? parseInt(chunkingModeSelect.value) : 0;
            url.searchParams.append('chunking_mode', chunkingMode.toString());
            
            if (chunkingMode === 0) {
                // Simple mode - add chunk_size and chunk_overlap
                const chunkSizeInput = document.getElementById('chunkSize');
                const chunkOverlapInput = document.getElementById('chunkOverlap');
                const chunkSize = chunkSizeInput && chunkSizeInput.value ? parseInt(chunkSizeInput.value) : 1000;
                const chunkOverlap = chunkOverlapInput && chunkOverlapInput.value ? parseInt(chunkOverlapInput.value) : 200;
                url.searchParams.append('chunk_size', chunkSize.toString());
                url.searchParams.append('chunk_overlap', chunkOverlap.toString());
            } else if (chunkingMode === 2) {
                // Hybrid mode - add max_tokens
                const maxTokensInput = document.getElementById('maxTokens');
                if (maxTokensInput && maxTokensInput.value) {
                    url.searchParams.append('max_tokens', maxTokensInput.value);
                }
            }
        } else {
            url.searchParams.append('output_format', outputFormat);
            url.searchParams.append('include_doc_tags', includeDocTags.toString());
        }

        // Add VLM prompt only if VLM pipeline is selected
        if (currentPipeline === 'vlm') {
            const vlmPromptElement = document.getElementById('vlmPrompt');
            const vlmPrompt = vlmPromptElement ? vlmPromptElement.value.trim() : '';
            if (vlmPrompt) {
                console.log(`[UI] Using custom VLM prompt: "${vlmPrompt.substring(0, 50)}${vlmPrompt.length > 50 ? '...' : ''}"`);
                url.searchParams.append('vlm_prompt', vlmPrompt);
            } else {
                console.log(`[UI] Using default VLM prompt`);
            }
        }
        
        console.log(`[UI] Converting file '${files[0].name}' using pipeline: '${currentPipeline}'`);
        console.log(`[UI] Request URL: ${url.pathname}${url.search}`);

        // Check VLM availability before sending request
        if (currentPipeline === 'vlm' && !vlmAvailable) {
            showError(t('ui.messages.vlmNotAvailable', 'VLM pipeline is not available. Please enable it in configuration (DOCLING_VLM_ENABLED=true) and configure VLM settings.'));
            showSpinner(false);
            // Switch back to standard pipeline
            currentPipeline = 'std';
            if (pipelineToggle) {
                pipelineToggle.checked = false;
            }
            updatePipelineUI();
            return;
        }

        const response = await fetch(url.toString(), {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = errorData.detail || errorData.message || `HTTP ${response.status}: ${response.statusText}`;
            
            // Check if error is about VLM not available
            if (errorMessage.includes('VLM pipeline not available') || 
                errorMessage.includes('VLM pipeline is disabled') ||
                errorMessage.includes('VLM configuration')) {
                showError(t('ui.messages.vlmNotAvailable', 'VLM pipeline is not available. Please enable it in configuration (DOCLING_VLM_ENABLED=true) and configure VLM settings.'));
                // Switch back to standard pipeline
                currentPipeline = 'std';
                if (pipelineToggle) {
                    pipelineToggle.checked = false;
                }
                updatePipelineUI();
            } else {
                throw new Error(errorMessage);
            }
        }
        
        const results = await response.json();
        
        // Handle different response types
        if (enableChunking) {
            // Handle chunking response (ChunkResult)
            displayChunkResults(results);
        } else if (extractTables) {
            // Handle table extraction response
            displayTableResults(results);
        } else {
            // Handle regular conversion response
            currentResults = Array.isArray(results) ? results : [results];
            
            // Check for errors in results
            const hasErrors = currentResults.some(r => r.error);
            if (hasErrors) {
                const errorFiles = currentResults.filter(r => r.error).map(r => r.file_name).join(', ');
                showError(`${t('ui.messages.error')}: ${errorFiles}`);
            } else {
                showSuccess(t('ui.messages.converted'));
            }
            
            displayResults(currentResults);
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        showError(error.message || t('ui.messages.error'));
    } finally {
        showSpinner(false);
    }
}

// Switch between tabs
function switchTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });

    // Show selected tab content
    if (tabName === 'raw') {
        document.getElementById('previewRaw').classList.add('active');
        document.getElementById('tabRaw').classList.add('active');
    } else if (tabName === 'preview') {
        document.getElementById('previewMarkdown').classList.add('active');
        document.getElementById('tabPreview').classList.add('active');
        // Render markdown if not already rendered
        renderMarkdownPreview();
    } else if (tabName === 'json-tables') {
        document.getElementById('previewJsonTables').classList.add('active');
        document.getElementById('tabJsonTables').classList.add('active');
        // Render JSON tables if not already rendered
        renderJsonTables();
    } else if (tabName === 'doc-tags') {
        document.getElementById('previewDocTags').classList.add('active');
        document.getElementById('tabDocTags').classList.add('active');
        // Render doc tags if not already rendered
        renderDocTags();
    } else if (tabName === 'chunks') {
        document.getElementById('previewChunks').classList.add('active');
        document.getElementById('tabChunks').classList.add('active');
        // Render chunks if not already rendered
        renderChunks();
    }
}

// Render markdown preview
function renderMarkdownPreview() {
    const markdownContent = document.getElementById('previewMarkdownContent');
    const rawContent = document.getElementById('previewRawContent');
    
    if (!markdownContent || !rawContent) return;
    
    // Get raw text
    const rawText = rawContent.textContent;
    
    // Check if already rendered
    if (markdownContent.dataset.rendered === 'true') {
        return;
    }
    
    try {
        // Configure marked options
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                breaks: true,
                gfm: true,
                headerIds: false,
                mangle: false
            });
            
            // Render markdown
            const html = marked.parse(rawText);
            
            // Sanitize HTML with DOMPurify
            if (typeof DOMPurify !== 'undefined') {
                const cleanHtml = DOMPurify.sanitize(html, {
                    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                                   'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'table', 'thead', 'tbody', 
                                   'tr', 'th', 'td', 'a', 'img', 'hr', 'del', 'ins'],
                    ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'class']
                });
                markdownContent.innerHTML = cleanHtml;
            } else {
                markdownContent.innerHTML = html;
            }
            
            // Highlight code blocks
            if (typeof hljs !== 'undefined') {
                markdownContent.querySelectorAll('pre code').forEach(block => {
                    hljs.highlightElement(block);
                });
            }
            
            markdownContent.dataset.rendered = 'true';
        } else {
            markdownContent.innerHTML = '<p style="color: var(--text-secondary);">Markdown preview library not loaded. Showing raw text.</p><pre>' + 
                                       rawText.replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</pre>';
        }
    } catch (error) {
        console.error('Error rendering markdown:', error);
        markdownContent.innerHTML = '<p style="color: var(--error-color);">Error rendering markdown preview.</p>';
    }
}

// Render JSON tables
function renderJsonTables() {
    const jsonContent = document.getElementById('previewJsonTablesContent');

    if (!jsonContent) return;

    if (!currentTableData) {
        jsonContent.textContent = 'No table data available';
        return;
    }

    try {
        // Pretty print JSON
        const formattedJson = JSON.stringify(currentTableData, null, 2);
        jsonContent.textContent = formattedJson;
    } catch (error) {
        console.error('Error rendering JSON tables:', error);
        jsonContent.textContent = 'Error rendering JSON tables: ' + error.message;
    }
}

// Render chunks in a formatted view
function renderChunks() {
    const chunksContent = document.getElementById('previewChunksContent');

    if (!chunksContent) return;

    if (!currentChunks || !currentChunks.chunks) {
        chunksContent.innerHTML = '<p>No chunk data available</p>';
        return;
    }

    try {
        const chunks = currentChunks.chunks;
        let html = '';
        
        html += `<div class="chunks-header">`;
        html += `<h3>Document Chunks</h3>`;
        html += `<p>Total: <strong>${chunks.length}</strong> chunk${chunks.length > 1 ? 's' : ''}</p>`;
        html += `</div>`;
        
        chunks.forEach((chunk, idx) => {
            html += `<div class="chunk-item">`;
            html += `<div class="chunk-header">`;
            html += `<h4>Chunk ${idx + 1}`;
            if (chunk.chunk_id !== undefined) {
                html += ` <span class="chunk-meta">(ID: ${chunk.chunk_id})</span>`;
            }
            html += `</h4>`;
            
            html += `<div class="chunk-metadata">`;
            if (chunk.chunk_id !== undefined) {
                html += `<span>ID: ${chunk.chunk_id}</span>`;
            }
            const chunkText = chunk.text || chunk.content || '';
            if (chunkText.length > 0) {
                html += `<span>Length: ${chunkText.length} chars</span>`;
            }
            if (chunk.start_char !== undefined && chunk.end_char !== undefined) {
                html += `<span>Range: ${chunk.start_char}-${chunk.end_char}</span>`;
            }
            if (chunk.metadata && chunk.metadata.page) {
                html += `<span>Page: ${chunk.metadata.page}</span>`;
            }
            html += `</div>`;
            html += `</div>`;
            
            html += `<div class="chunk-content">`;
            // Use already declared chunkText variable
            // Escape HTML and preserve line breaks
            const escapedText = chunkText
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/\n/g, '<br>');
            html += `<pre>${escapedText}</pre>`;
            html += `</div>`;
            
            html += `</div>`;
        });
        
        chunksContent.innerHTML = html;
    } catch (error) {
        console.error('Error rendering chunks:', error);
        chunksContent.innerHTML = '<p>Error rendering chunks: ' + error.message + '</p>';
    }
}

// Render doc tags
function renderDocTags() {
    const jsonContent = document.getElementById('previewDocTagsContent');

    if (!jsonContent) return;

    if (!currentDocTags) {
        jsonContent.textContent = 'No doc tags available';
        return;
    }

    try {
        // Pretty print JSON
        const formattedJson = JSON.stringify(currentDocTags, null, 2);
        jsonContent.textContent = formattedJson;
    } catch (error) {
        console.error('Error rendering doc tags:', error);
        jsonContent.textContent = 'Error rendering doc tags: ' + error.message;
    }
}

// Display Results
function displayResults(results) {
    const resultsSection = document.getElementById('resultsSection');
    const rawContent = document.getElementById('previewRawContent');
    const markdownContent = document.getElementById('previewMarkdownContent');
    const resultsCount = document.getElementById('resultsCount');

    if (!rawContent || !markdownContent) {
        console.error('Preview elements not found');
        return;
    }

    // Clear previous data
    currentTableData = null;
    currentDocTags = null;

    // Check if any result has doc_tags
    results.forEach(result => {
        if (result.doc_tags) {
            currentDocTags = result.doc_tags;
        }
    });

    // Show Doc Tags tab if doc tags are available
    if (currentDocTags) {
        document.getElementById('tabDocTags').style.display = 'inline-flex';
    } else {
        document.getElementById('tabDocTags').style.display = 'none';
    }

    // Hide JSON Tables tab for regular conversions
    document.getElementById('tabJsonTables').style.display = 'none';

    // Build combined text with separators
    let combinedText = '';

    results.forEach((result, index) => {
        const separator = '='.repeat(60);
        combinedText += `${separator}\n`;
        combinedText += `📄 ${result.file_name}\n`;

        // Add metadata if available
        if (result.metadata) {
            const meta = result.metadata;
            if (meta.num_pages) combinedText += `📑 Pages: ${meta.num_pages}\n`;
            if (meta.num_tables) combinedText += `📊 Tables: ${meta.num_tables}\n`;
            if (meta.num_pictures) combinedText += `🖼️ Pictures: ${meta.num_pictures}\n`;
        }

        combinedText += `${separator}\n\n`;

        if (result.error) {
            combinedText += `❌ Error: ${result.error}\n\n`;
        } else {
            combinedText += result.file_text + '\n\n';
        }

        if (index < results.length - 1) {
            combinedText += '\n\n';
        }
    });

    // Set raw content
    rawContent.textContent = combinedText;

    // Reset markdown content and mark as not rendered
    markdownContent.innerHTML = '';
    markdownContent.dataset.rendered = 'false';

    // Show results section
    resultsCount.textContent = `${results.length} ${t('ui.results.files')}`;
    resultsSection.style.display = 'block';

    // Switch to raw tab by default
    switchTab('raw');

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Display table extraction results
function displayTableResults(result) {
    const resultsSection = document.getElementById('resultsSection');
    const resultsCount = document.getElementById('resultsCount');
    const rawContent = document.getElementById('previewRawContent');
    const markdownContent = document.getElementById('previewMarkdownContent');

    if (result.error) {
        showError(`${t('ui.messages.tableExtractionError')}: ${result.error}`);
        showSpinner(false);
        return;
    }

    const tables = result.tables || [];

    if (tables.length === 0) {
        showError(t('ui.messages.noTables'));
        showSpinner(false);
        return;
    }

    // Store JSON data for the JSON Tables tab
    currentTableData = result;
    console.log('[UI] Stored table data:', currentTableData);

    // Store doc tags if available
    if (result.doc_tags) {
        currentDocTags = result.doc_tags;
        document.getElementById('tabDocTags').style.display = 'inline-flex';
        console.log('[UI] Doc tags tab enabled');
    }

    // Build table display
    let tableText = '';
    tableText += '='.repeat(60) + '\n';
    tableText += `📊 EXTRACTED TABLES from ${result.file_name}\n`;
    tableText += `Found ${tables.length} table${tables.length > 1 ? 's' : ''}\n`;
    tableText += '='.repeat(60) + '\n\n';

    tables.forEach((table, idx) => {
        tableText += `\n--- Table ${idx + 1} ---\n`;

        if (table.caption) {
            tableText += `Caption: ${table.caption}\n`;
        }

        if (table.bbox && table.bbox.page) {
            tableText += `Page: ${table.bbox.page}\n`;
        }

        tableText += '\n';

        // Display table data
        const data = table.data || [];
        if (data.length > 0) {
            // Get column headers from first row
            const headers = Object.keys(data[0]);

            // Create markdown table
            tableText += '| ' + headers.join(' | ') + ' |\n';
            tableText += '|' + headers.map(() => '---').join('|') + '|\n';

            // Add rows
            data.forEach(row => {
                const values = headers.map(h => (row[h] || '').toString().replace(/\n/g, ' '));
                tableText += '| ' + values.join(' | ') + ' |\n';
            });

            tableText += `\n(${data.length} rows)\n`;
        } else {
            tableText += '(No data)\n';
        }

        tableText += '\n';
    });

    if (!rawContent || !markdownContent) {
        console.error('Preview elements not found');
        return;
    }

    rawContent.textContent = tableText;
    markdownContent.innerHTML = '';
    markdownContent.dataset.rendered = 'false';
    resultsCount.textContent = `${tables.length} ${t('ui.results.tables')}`;
    resultsSection.style.display = 'block';

    // Show JSON Tables tab
    document.getElementById('tabJsonTables').style.display = 'inline-flex';
    console.log('[UI] JSON Tables tab enabled');

    // Default to JSON Tables tab for tables
    switchTab('json-tables');
    console.log('[UI] Switched to JSON Tables tab');

    showSuccess(`${tables.length} ${t('ui.messages.tablesExtracted')}`);
    showSpinner(false);

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Display chunking results
function displayChunkResults(result) {
    const resultsSection = document.getElementById('resultsSection');
    const resultsCount = document.getElementById('resultsCount');
    const rawContent = document.getElementById('previewRawContent');
    const markdownContent = document.getElementById('previewMarkdownContent');

    if (result.error) {
        showError(`Chunking error: ${result.error}`);
        showSpinner(false);
        return;
    }

    const chunks = result.chunks || [];

    if (chunks.length === 0) {
        showError('No chunks generated from document');
        showSpinner(false);
        return;
    }

    // Store chunk data
    currentChunks = result;
    console.log('[UI] Stored chunk data:', currentChunks);

    // Build chunk display
    let chunkText = '';
    chunkText += '='.repeat(60) + '\n';
    chunkText += `📦 DOCUMENT CHUNKS from ${result.file_name}\n`;
    chunkText += `Total chunks: ${chunks.length}\n`;
    chunkText += '='.repeat(60) + '\n\n';

    chunks.forEach((chunk, idx) => {
        chunkText += `\n--- Chunk ${idx + 1} ---\n`;
        
        // Display chunk metadata if available
        if (chunk.metadata) {
            if (chunk.metadata.page) {
                chunkText += `Page: ${chunk.metadata.page}\n`;
            }
            if (chunk.metadata.chunk_index !== undefined) {
                chunkText += `Index: ${chunk.metadata.chunk_index}\n`;
            }
            if (chunk.metadata.start_char !== undefined && chunk.metadata.end_char !== undefined) {
                chunkText += `Characters: ${chunk.metadata.start_char}-${chunk.metadata.end_char}\n`;
            }
        }
        
        chunkText += '\n';
        
        // Display chunk text
        const chunkTextContent = chunk.text || chunk.content || '';
        chunkText += chunkTextContent;
        chunkText += '\n';
        
        if (chunkTextContent.length > 0) {
            chunkText += `\n(Length: ${chunkTextContent.length} characters)\n`;
        }
        
        chunkText += '\n';
    });

    if (!rawContent || !markdownContent) {
        console.error('Preview elements not found');
        return;
    }

    rawContent.textContent = chunkText;
    markdownContent.innerHTML = '';
    markdownContent.dataset.rendered = 'false';
    resultsCount.textContent = `${chunks.length} chunk${chunks.length > 1 ? 's' : ''}`;
    resultsSection.style.display = 'block';

    // Show Chunks tab
    const tabChunks = document.getElementById('tabChunks');
    if (tabChunks) {
        tabChunks.style.display = 'inline-flex';
        console.log('[UI] Chunks tab enabled');
        // Default to Chunks tab
        switchTab('chunks');
    } else {
        // Fallback to raw text tab
        switchTab('raw');
    }

    showSuccess(`${chunks.length} chunk${chunks.length > 1 ? 's' : ''} generated successfully!`);
    showSpinner(false);

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Copy text to clipboard
async function copyText() {
    // Get the active tab content
    let text = '';

    if (document.getElementById('previewRaw').classList.contains('active')) {
        const rawContent = document.getElementById('previewRawContent');
        text = rawContent ? rawContent.textContent : '';
    } else if (document.getElementById('previewMarkdown').classList.contains('active')) {
        const markdownContent = document.getElementById('previewMarkdownContent');
        text = markdownContent ? markdownContent.textContent : '';
    } else if (document.getElementById('previewJsonTables').classList.contains('active')) {
        const jsonContent = document.getElementById('previewJsonTablesContent');
        text = jsonContent ? jsonContent.textContent : '';
    } else if (document.getElementById('previewDocTags').classList.contains('active')) {
        const jsonContent = document.getElementById('previewDocTagsContent');
        text = jsonContent ? jsonContent.textContent : '';
    }

    if (!text) {
        showError(t('ui.messages.noContent'));
        return;
    }

    try {
        await navigator.clipboard.writeText(text);
        showSuccess(t('ui.messages.copied'));
    } catch (error) {
        console.error('Copy error:', error);
        showError(t('ui.messages.error'));
    }
}

// Download single MD file
function downloadSingleMD() {
    if (!currentResults || currentResults.length === 0) {
        showError('No results to download');
        return;
    }
    
    // Combine all results into one markdown file
    let combinedText = '';
    
    currentResults.forEach((result, index) => {
        combinedText += `# ${result.file_name}\n\n`;
        
        if (result.error) {
            combinedText += `**Error:** ${result.error}\n\n`;
        } else {
            combinedText += result.file_text + '\n\n';
        }
        
        if (index < currentResults.length - 1) {
            combinedText += '\n---\n\n';
        }
    });
    
    const blob = new Blob([combinedText], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'converted_document.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showSuccess(t('ui.messages.downloadSuccess'));
}

// Download all as ZIP archive
async function downloadAllArchive() {
    if (!currentResults || currentResults.length === 0) {
        showError('No results to download');
        return;
    }
    
    showSpinner(true);
    
    try {
        // Use parse/md endpoint with base64 to get ZIP
        const docs = currentResults.map(r => ({
            filename: r.file_name,
            data: btoa(unescape(encodeURIComponent(r.file_text))),
            type: r.file_extension
        }));
        
        const response = await fetch(`${API_PREFIX}/parse/md`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                is_base64_or_document: true,
                docs: docs
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to create archive');
        }
        
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'converted_documents.zip';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showSuccess(t('ui.messages.downloadSuccess'));
        
    } catch (error) {
        console.error('Download error:', error);
        showError(t('ui.messages.error'));
    } finally {
        showSpinner(false);
    }
}

// UI Helper Functions
function showSpinner(show) {
    const spinner = document.getElementById('spinner');
    const spinnerText = document.getElementById('spinnerText');
    if (spinnerText) spinnerText.textContent = t('ui.messages.processing');
    spinner.style.display = show ? 'flex' : 'none';
}

function hideResults() {
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.style.display = 'none';

    // Hide additional tabs (but keep Doc Tags hidden until new results)
    document.getElementById('tabJsonTables').style.display = 'none';
    document.getElementById('tabDocTags').style.display = 'none';

    // Clear stored data
    currentTableData = null;
    currentDocTags = null;
}

function showMessage(message, type) {
    const messageEl = document.getElementById('errorMessage');
    messageEl.textContent = message;
    messageEl.className = `message ${type}`;
    messageEl.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        messageEl.style.display = 'none';
    }, 5000);
}

function showError(message) {
    showMessage(message, 'error');
}

function showSuccess(message) {
    showMessage(message, 'success');
}

function hideMessage() {
    const messageEl = document.getElementById('errorMessage');
    messageEl.style.display = 'none';
}

// Make toggleOCR globally available
window.toggleOCR = toggleOCR;
window.onPromptSelectChange = onPromptSelectChange;

// Render documentation from translations
function renderDocumentation() {
    const docContent = document.getElementById('documentationContent');
    const docTitle = document.getElementById('documentationTitle');
    
    if (!docContent || !docTitle) {
        console.warn('[docs] Documentation elements not found');
        return;
    }
    
    try {
        // Get documentation translations directly from window object
        let doc = null;
        if (window.APP_TRANSLATIONS && window.APP_TRANSLATIONS.ui && window.APP_TRANSLATIONS.ui.documentation) {
            doc = window.APP_TRANSLATIONS.ui.documentation;
        } else {
            // Fallback: try to get via t function
            const docKey = 'ui.documentation';
            const keys = docKey.split('.');
            let value = translations;
            for (const k of keys) {
                if (value && typeof value === 'object' && k in value) {
                    value = value[k];
                } else {
                    console.warn('[docs] Documentation translations not found');
                    return;
                }
            }
            doc = value;
        }
        
        if (!doc || typeof doc !== 'object') {
            console.warn('[docs] Documentation translations not found or invalid');
            return;
        }
        
        // Update title
        docTitle.textContent = doc.title || 'Documentation';
        
        // Build HTML content
        let html = '';
        const sections = doc.sections || {};
        
        // Overview
        if (sections.overview) {
            html += `<h3>${sections.overview.title}</h3>`;
            html += `<p>${sections.overview.content}</p>`;
        }
        
        // Pipelines
        if (sections.pipelines) {
            html += `<h3>${sections.pipelines.title}</h3>`;
            
            // Standard Pipeline
            if (sections.pipelines.standard) {
                const std = sections.pipelines.standard;
                html += `<h4>${std.title}</h4>`;
                html += `<p>${std.description}</p>`;
                if (std.features && Array.isArray(std.features)) {
                    html += `<ul class="feature-list">`;
                    std.features.forEach(feature => {
                        html += `<li>${feature}</li>`;
                    });
                    html += `</ul>`;
                }
                html += `<div class="info-box"><strong>${std.bestFor}</strong></div>`;
            }
            
            // VLM Pipeline
            if (sections.pipelines.vlm) {
                const vlm = sections.pipelines.vlm;
                html += `<h4>${vlm.title}</h4>`;
                html += `<p>${vlm.description}</p>`;
                if (vlm.features && Array.isArray(vlm.features)) {
                    html += `<ul class="feature-list">`;
                    vlm.features.forEach(feature => {
                        html += `<li>${feature}</li>`;
                    });
                    html += `</ul>`;
                }
                html += `<div class="info-box"><strong>${vlm.bestFor}</strong></div>`;
                if (vlm.note) {
                    html += `<div class="warning">${vlm.note}</div>`;
                }
            }
        }
        
        // Features
        if (sections.features) {
            html += `<h3>${sections.features.title}</h3>`;
            
            // OCR
            if (sections.features.ocr) {
                const ocr = sections.features.ocr;
                html += `<h4>${ocr.title}</h4>`;
                html += `<p>${ocr.description}</p>`;
                if (ocr.modes) {
                    html += `<ul>`;
                    Object.keys(ocr.modes).forEach(key => {
                        html += `<li><code>${key}</code> — ${ocr.modes[key]}</li>`;
                    });
                    html += `</ul>`;
                }
            }
            
            // Formats
            if (sections.features.formats) {
                const formats = sections.features.formats;
                html += `<h4>${formats.title}</h4>`;
                if (formats.input) {
                    html += `<p><strong>${formats.input.title}</strong> ${formats.input.list}</p>`;
                }
                if (formats.output) {
                    html += `<p><strong>${formats.output.title}</strong> ${formats.output.list}</p>`;
                }
                if (formats.archives) {
                    html += `<p><strong>${formats.archives.title}</strong> ${formats.archives.list}</p>`;
                }
            }
            
            // Advanced Features
            if (sections.features.advanced) {
                const adv = sections.features.advanced;
                html += `<h4>${adv.title}</h4>`;
                if (adv.tables) {
                    html += `<div class="scenario-item">`;
                    html += `<strong>${adv.tables.title}</strong>`;
                    html += `<p>${adv.tables.description}</p>`;
                    html += `</div>`;
                }
                if (adv.chunking) {
                    html += `<div class="scenario-item">`;
                    html += `<strong>${adv.chunking.title}</strong>`;
                    html += `<p>${adv.chunking.description}</p>`;
                    html += `</div>`;
                }
                if (adv.docTags) {
                    html += `<div class="scenario-item">`;
                    html += `<strong>${adv.docTags.title}</strong>`;
                    html += `<p>${adv.docTags.description}</p>`;
                    html += `</div>`;
                }
            }
        }
        
        // Usage
        if (sections.usage) {
            html += `<h3>${sections.usage.title}</h3>`;
            
            // UI Usage
            if (sections.usage.ui) {
                html += `<h4>${sections.usage.ui.title}</h4>`;
                if (sections.usage.ui.steps && Array.isArray(sections.usage.ui.steps)) {
                    html += `<ol>`;
                    sections.usage.ui.steps.forEach(step => {
                        html += `<li>${step}</li>`;
                    });
                    html += `</ol>`;
                }
            }
            
            // API Usage
            if (sections.usage.api) {
                html += `<h4>${sections.usage.api.title}</h4>`;
                if (sections.usage.api.endpoints) {
                    Object.keys(sections.usage.api.endpoints).forEach(key => {
                        const endpoint = sections.usage.api.endpoints[key];
                        html += `<div class="endpoint-item">`;
                        html += `<strong>${endpoint.title}</strong>`;
                        html += `<p>${endpoint.description}</p>`;
                        if (endpoint.params) {
                            html += `<p><em>Parameters:</em> <code>${endpoint.params}</code></p>`;
                        }
                        html += `</div>`;
                    });
                }
                if (sections.usage.api.example) {
                    html += `<h4>${sections.usage.api.example.title}</h4>`;
                    html += `<pre><code>${sections.usage.api.example.code}</code></pre>`;
                }
            }
            
            // Scenarios
            if (sections.usage.scenarios) {
                html += `<h4>${sections.usage.scenarios.title}</h4>`;
                Object.keys(sections.usage.scenarios).forEach(key => {
                    if (key === 'title') return;
                    const scenario = sections.usage.scenarios[key];
                    html += `<div class="scenario-item">`;
                    html += `<strong>${scenario.title}</strong>`;
                    html += `<p>${scenario.description}</p>`;
                    html += `</div>`;
                });
            }
        }
        
        // Tips
        if (sections.tips) {
            html += `<h3>${sections.tips.title}</h3>`;
            if (sections.tips.list && Array.isArray(sections.tips.list)) {
                html += `<ul>`;
                sections.tips.list.forEach(tip => {
                    html += `<li>${tip}</li>`;
                });
                html += `</ul>`;
            }
        }
        
        docContent.innerHTML = html;
        console.log('[docs] Documentation rendered successfully');
    } catch (error) {
        console.error('[docs] Error rendering documentation:', error);
        docContent.innerHTML = '<p>Error loading documentation. Please refresh the page.</p>';
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    console.log('[i18n] DOM loaded, initializing...');
    
    // Ensure translations are loaded
    loadTranslations();
    
    // Initialize language selector first (may trigger reload)
    initializeLanguageSelector();
    
    // Apply translations
    applyTranslations();
    
    // Render documentation
    renderDocumentation();
    
    // Initialize app
    initializeApp();
    
    // Initialize chunking options
    initializeChunkingOptions();
    loadChunkingDefaults();
    
    // Initialize UI state
    updatePipelineUI();
    updateStatusBarFromCurrentState();
    
    // Set default VLM prompt if VLM is selected
    if (currentPipeline === 'vlm') {
        const vlmPromptSelect = document.getElementById('vlmPromptSelect');
        const vlmPromptTextarea = document.getElementById('vlmPrompt');
        if (vlmPromptSelect && vlmPromptTextarea) {
            const markdownFocusedPrompt = "Convert this document page to markdown format.";
            // Find and select the markdown focused option
            for (let i = 0; i < vlmPromptSelect.options.length; i++) {
                if (vlmPromptSelect.options[i].value === markdownFocusedPrompt) {
                    vlmPromptSelect.selectedIndex = i;
                    vlmPromptTextarea.value = markdownFocusedPrompt;
                    break;
                }
            }
        }
    }
    
    console.log('[i18n] Initialization complete');
});

