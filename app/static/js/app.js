// Global state
let currentResults = [];
let uploadedFiles = null;
let currentPipeline = 'std'; // 'std' or 'vlm'
let currentTableData = null; // JSON data for extracted tables
let currentDocTags = null; // Doc tags data
const API_PREFIX = '/ocr/docling';

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
pipelineToggle.addEventListener('change', (e) => {
    const newPipeline = e.target.checked ? 'vlm' : 'std';
    console.log(`[UI] Pipeline switched from '${currentPipeline}' to '${newPipeline}'`);
    currentPipeline = newPipeline;
    updatePipelineUI();
    updateStatusBarFromCurrentState();
});

// Update UI based on pipeline mode
function updatePipelineUI() {
    const vlmPromptGroup = document.getElementById('vlmPromptGroup');
    const optionsPanel = document.querySelector('.options-panel');
    
    if (!vlmPromptGroup) {
        console.warn('[UI] vlmPromptGroup element not found');
        return;
    }
    
    if (currentPipeline === 'vlm') {
        vlmPromptGroup.style.display = 'block';
        // Auto-open Advanced Options panel when VLM is selected
        if (optionsPanel && !optionsPanel.open) {
            optionsPanel.open = true;
            console.log('[UI] Advanced Options panel opened for VLM prompt');
        }
        console.log('[UI] VLM prompt editor shown');
    } else {
        vlmPromptGroup.style.display = 'none';
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
    const pipelineText = currentPipeline === 'std' ? 'Standard' : 'VLM';
    currentPipelineEl.textContent = pipelineText;
    currentPipelineEl.className = 'status-value success';

    // Update mode display
    const modeText = currentPipeline === 'std' ? 'Standard' : 'VLM';
    currentMode.textContent = modeText;
    currentMode.className = 'status-value success';

    // Update OCR status
    if (currentPipeline === 'std') {
        ocrStatus.textContent = 'Enabled'; // Default for standard pipeline
        ocrStatus.className = 'status-value success';
        if (ocrToggle) ocrToggle.checked = true;
    } else {
        ocrStatus.textContent = 'N/A';
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

            // Initialize pipeline toggle based on server status
            const serverPipeline = data.pipeline_mode === 'vlm' ? 'vlm' : 'std';
            if (currentPipeline !== serverPipeline) {
                console.log(`[UI] Pipeline initialized from server: '${serverPipeline}'`);
            }
            currentPipeline = serverPipeline;
            pipelineToggle.checked = (currentPipeline === 'vlm');
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
        pipelineToggle.checked = false;
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

    // Update pipeline display
    const pipelineText = status.pipeline_mode === 'standard' ? 'Standard' :
                        status.pipeline_mode === 'vlm' ? 'VLM' : 'Unknown';
    currentPipelineEl.textContent = pipelineText;
    currentPipelineEl.className = 'status-value ' + (status.pipeline_mode !== 'unknown' ? 'success' : 'error');

    // Update mode display
    const modeText = status.pipeline_mode === 'standard' ? 'Standard' :
                     status.pipeline_mode === 'vlm' ? 'VLM' : 'Unknown';
    currentMode.textContent = modeText;
    currentMode.className = 'status-value ' + (status.pipeline_mode !== 'unknown' ? 'success' : 'error');

    // Update OCR status
    if (status.pipeline_mode === 'standard') {
        ocrStatus.textContent = status.ocr_enabled ? 'Enabled' : 'Disabled';
        ocrStatus.className = 'status-value ' + (status.ocr_enabled ? 'success' : 'warning');
    } else {
        ocrStatus.textContent = 'N/A';
        ocrStatus.className = 'status-value';
    }

    // Update OCR toggle to match current state
    if (ocrToggle) {
        ocrToggle.checked = status.ocr_enabled || false;
    }

    // Update models status
    modelsStatus.textContent = status.models_loaded ? 'Loaded' : 'Not Found';
    modelsStatus.className = 'status-value ' + (status.models_loaded ? 'success' : 'warning');
}

// Toggle OCR on/off
async function toggleOCR() {
    const toggle = document.getElementById('ocrToggle');
    const enabled = toggle.checked;
    
    try {
        // Just update the toggle, no message while processing
        
        const response = await fetch(`${API_PREFIX}/pipeline/ocr/toggle`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ enabled })
        });
        
        if (!response.ok) {
            throw new Error('Failed to toggle OCR');
        }
        
        const result = await response.json();
        
        // Show message about restart requirement
        if (result.restart_required) {
            showSuccess(`OCR ${enabled ? 'enabled' : 'disabled'}. Please restart service for full effect.`);
        } else {
            showSuccess(`OCR ${enabled ? 'enabled' : 'disabled'} successfully!`);
        }
        
        // Update status bar
        await fetchSystemStatus();
        
    } catch (error) {
        console.error('Toggle OCR error:', error);
        showError(`Error toggling OCR: ${error.message}`);
        
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
        text.textContent = `${count} file${count > 1 ? 's' : ''} selected`;
        hint.textContent = 'Click "Convert" or select different files';
        convertBtn.classList.add('processing');
        setTimeout(() => convertBtn.classList.remove('processing'), 300);
    }
}

// Upload and Convert Files
async function uploadFiles() {
    const files = fileInput.files;
    
    if (!files || files.length === 0) {
        showError('Please select files first');
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

        const formData = new FormData();
        formData.append('file', files[0]);

        // Get UI options
        const outputFormatSelect = document.getElementById('outputFormat');
        const outputFormat = outputFormatSelect ? outputFormatSelect.value : 'markdown';
        const includeDocTagsCheckbox = document.getElementById('includeDocTags');
        const includeDocTags = includeDocTagsCheckbox ? includeDocTagsCheckbox.checked : true;

        // Build URL with query parameters
        const endpoint = extractTables ? '/extract/tables' : '/upload';
        const url = new URL(`${API_PREFIX}${endpoint}`, window.location.origin);
        url.searchParams.append('pipeline', currentPipeline);
        url.searchParams.append('output_format', outputFormat);
        url.searchParams.append('include_doc_tags', includeDocTags.toString());

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

        const response = await fetch(url.toString(), {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        const results = await response.json();
        
        // Handle table extraction response differently
        if (extractTables) {
            displayTableResults(results);
        } else {
            currentResults = Array.isArray(results) ? results : [results];
            
            // Check for errors in results
            const hasErrors = currentResults.some(r => r.error);
            if (hasErrors) {
                const errorFiles = currentResults.filter(r => r.error).map(r => r.file_name).join(', ');
                showError(`Some files could not be converted: ${errorFiles}`);
            } else {
                showSuccess('All files converted successfully with Docling!');
            }
            
            displayResults(currentResults);
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        showError(error.message || 'Failed to upload files. Please try again.');
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
    resultsCount.textContent = `${results.length} file${results.length > 1 ? 's' : ''}`;
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
        showError(`Error extracting tables: ${result.error}`);
        showSpinner(false);
        return;
    }

    const tables = result.tables || [];

    if (tables.length === 0) {
        showError('No tables found in the document');
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
    resultsCount.textContent = `${tables.length} table${tables.length > 1 ? 's' : ''}`;
    resultsSection.style.display = 'block';

    // Show JSON Tables tab
    document.getElementById('tabJsonTables').style.display = 'inline-flex';
    console.log('[UI] JSON Tables tab enabled');

    // Default to JSON Tables tab for tables
    switchTab('json-tables');
    console.log('[UI] Switched to JSON Tables tab');

    showSuccess(`Extracted ${tables.length} table${tables.length > 1 ? 's' : ''} successfully!`);
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
        showError('No content to copy');
        return;
    }

    try {
        await navigator.clipboard.writeText(text);
        showSuccess('Content copied to clipboard!');
    } catch (error) {
        console.error('Copy error:', error);
        showError('Failed to copy content');
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
    
    showSuccess('Markdown file downloaded!');
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
        
        showSuccess('Archive downloaded!');
        
    } catch (error) {
        console.error('Download error:', error);
        showError('Failed to create archive');
    } finally {
        showSpinner(false);
    }
}

// UI Helper Functions
function showSpinner(show) {
    const spinner = document.getElementById('spinner');
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

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    // Initialize UI state
    updatePipelineUI();
    updateStatusBarFromCurrentState();
});

