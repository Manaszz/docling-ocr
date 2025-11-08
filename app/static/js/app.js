// Global state
let currentResults = [];
let uploadedFiles = null;
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

// Initialize App
async function initializeApp() {
    await fetchSystemStatus();
}

// Fetch system status
async function fetchSystemStatus() {
    try {
        const response = await fetch(`${API_PREFIX}/health`);
        if (response.ok) {
            const data = await response.json();
            updateStatusBar(data);
        }
    } catch (error) {
        console.error('Failed to fetch system status:', error);
        updateStatusBar({
            pipeline_mode: 'unknown',
            ocr_enabled: false,
            models_loaded: false,
        });
    }
}

// Update status bar
function updateStatusBar(status) {
    const currentMode = document.getElementById('currentMode');
    const ocrStatus = document.getElementById('ocrStatus');
    const modelsStatus = document.getElementById('modelsStatus');
    const ocrToggle = document.getElementById('ocrToggle');
    
    // Update pipeline mode
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

        // Get VLM prompt
        const vlmPromptElement = document.getElementById('vlmPrompt');
        const vlmPrompt = vlmPromptElement ? vlmPromptElement.value.trim() : '';

        const formData = new FormData();
        formData.append('file', files[0]);

        // Add VLM prompt if provided
        if (vlmPrompt) {
            formData.append('vlm_prompt', vlmPrompt);
        }

        // Use appropriate endpoint
        const endpoint = extractTables ? '/extract/tables' : '/upload';
        
        const response = await fetch(`${API_PREFIX}${endpoint}`, {
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

// Display Results
function displayResults(results) {
    const resultsSection = document.getElementById('resultsSection');
    const preview = document.getElementById('preview');
    const resultsCount = document.getElementById('resultsCount');
    
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
    
    preview.textContent = combinedText;
    resultsCount.textContent = `${results.length} file${results.length > 1 ? 's' : ''}`;
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Display table extraction results
function displayTableResults(result) {
    const resultsSection = document.getElementById('resultsSection');
    const resultsCount = document.getElementById('resultsCount');
    const preview = document.getElementById('preview');
    
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
    
    preview.textContent = tableText;
    resultsCount.textContent = `${tables.length} table${tables.length > 1 ? 's' : ''}`;
    resultsSection.style.display = 'block';
    
    showSuccess(`Extracted ${tables.length} table${tables.length > 1 ? 's' : ''} successfully!`);
    showSpinner(false);
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Copy text to clipboard
async function copyText() {
    const preview = document.getElementById('preview');
    const text = preview.textContent;
    
    try {
        await navigator.clipboard.writeText(text);
        showSuccess('Text copied to clipboard!');
    } catch (error) {
        console.error('Copy error:', error);
        showError('Failed to copy text');
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
document.addEventListener('DOMContentLoaded', initializeApp);

