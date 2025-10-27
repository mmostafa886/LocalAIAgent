/**
 * Test Case Generator - Client-Side Application
 *
 * Handles all frontend logic including:
 * - Form submission and validation
 * - Input parsing (user story and acceptance criteria)
 * - Real-time log streaming via Server-Sent Events
 * - UI updates and user feedback
 */

// ============================================================================
// GLOBAL STATE
// ============================================================================

let sessionId = null;
let eventSource = null;

// ============================================================================
// PARSING FUNCTIONS
// ============================================================================

/**
 * Parse acceptance criteria from various text formats.
 * Supports bullets (-, *, •), numbers (1., 2.), labels (AC1:), etc.
 *
 * @param {string} text - Raw text containing criteria
 * @returns {Array<string>} - Cleaned array of acceptance criteria
 */
function parseCriteriaList(text) {
    if (!text || text.trim() === '') {
        return [];
    }

    const lines = text.split('\n');
    const criteria = [];

    for (let line of lines) {
        line = line.trim();

        // Skip empty lines
        if (line === '') continue;

        // Skip header lines
        if (line.match(/^(acceptance\s+)?criteria:/i)) continue;
        if (line.match(/^requirements:/i)) continue;

        // Remove common bullet/number prefixes
        line = line
            .replace(/^[-*•►▸→]\s*/, '')        // Remove bullets
            .replace(/^\d+[.)]\s*/, '')         // Remove numbers (1. or 1))
            .replace(/^[A-Z]\d+:\s*/i, '')      // Remove labels (AC1:, AC2:)
            .replace(/^\[\s*\]\s*/, '')         // Remove unchecked checkboxes
            .replace(/^\[x\]\s*/i, '')          // Remove checked checkboxes
            .trim();

        if (line !== '') {
            criteria.push(line);
        }
    }

    return criteria;
}

/**
 * Parse combined input to extract user story and acceptance criteria.
 * Auto-detects sections based on headers or content patterns.
 *
 * @param {string} text - Combined text with user story and criteria
 * @returns {Object} - Object with userStory and acceptanceCriteria properties
 */
function parseCombinedInput(text) {
    if (!text || text.trim() === '') {
        return { userStory: '', acceptanceCriteria: [] };
    }

    const lines = text.split('\n');
    let userStory = '';
    let criteriaLines = [];
    let inCriteriaSection = false;
    let inStorySection = false;

    for (let line of lines) {
        const trimmed = line.trim();

        // Skip empty lines
        if (trimmed === '') continue;

        // Check for explicit section headers
        if (trimmed.match(/^(user\s+)?story:/i)) {
            inStorySection = true;
            inCriteriaSection = false;
            continue;
        }

        if (trimmed.match(/^(acceptance\s+)?criteria:/i) ||
            trimmed.match(/^requirements:/i) ||
            trimmed.match(/^AC:/i)) {
            inCriteriaSection = true;
            inStorySection = false;
            continue;
        }

        // Auto-detect user story (starts with "As a/an")
        if (trimmed.match(/^as\s+(a|an)\s+/i) && !inCriteriaSection && userStory === '') {
            inStorySection = true;
            inCriteriaSection = false;
        }

        // Auto-detect criteria (starts with bullet/number)
        if (trimmed.match(/^[-*•\d+.►▸→]/)) {
            inCriteriaSection = true;
            inStorySection = false;
        }

        // Collect lines based on current section
        if (inStorySection && trimmed !== '') {
            userStory += (userStory ? ' ' : '') + trimmed;
        } else if (inCriteriaSection && trimmed !== '') {
            criteriaLines.push(trimmed);
        } else if (!inStorySection && !inCriteriaSection && trimmed !== '') {
            // If no section detected yet, first content is user story
            if (userStory === '') {
                userStory = trimmed;
            } else {
                criteriaLines.push(trimmed);
            }
        }
    }

    const acceptanceCriteria = parseCriteriaList(criteriaLines.join('\n'));

    return {
        userStory: userStory.trim(),
        acceptanceCriteria: acceptanceCriteria
    };
}

// ============================================================================
// LOG MANAGEMENT
// ============================================================================

/**
 * Add a log entry to the log panel.
 *
 * @param {string} message - Log message to display
 * @param {string} level - Log level (info, success, warning, error)
 */
function addLog(message, level = 'info') {
    const logContent = document.getElementById('logContent');
    const empty = logContent.querySelector('.log-empty');
    if (empty) {
        empty.remove();
    }

    const timestamp = new Date().toLocaleTimeString();
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerHTML = `
        <span class="log-timestamp">[${timestamp}]</span>
        <span class="log-level ${level}">${level.toUpperCase()}</span>
        <span class="log-message">${escapeHtml(message)}</span>
    `;

    logContent.appendChild(entry);
    logContent.scrollTop = logContent.scrollHeight;
}

/**
 * Clear all logs from the log panel.
 */
function clearLogs() {
    const logContent = document.getElementById('logContent');
    logContent.innerHTML = '<div class="log-empty">Logs cleared. Waiting for next generation...</div>';
}

/**
 * Escape HTML to prevent XSS attacks.
 *
 * @param {string} text - Text to escape
 * @returns {string} - Escaped text safe for HTML insertion
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================================
// LOG STREAMING
// ============================================================================

/**
 * Connect to the log stream via Server-Sent Events.
 *
 * @param {string} sid - Session ID for this generation
 */
function connectLogStream(sid) {
    // Close existing connection if any
    if (eventSource) {
        eventSource.close();
    }

    // Create new SSE connection
    eventSource = new EventSource(`/api/logs/${sid}`);

    eventSource.onmessage = function(event) {
        const log = JSON.parse(event.data);
        addLog(log.message, log.level);
    };

    eventSource.onerror = function() {
        // Connection closed or error occurred
        eventSource.close();
        eventSource = null;
    };
}

// ============================================================================
// RESULT DISPLAY
// ============================================================================

/**
 * Show result message to the user.
 *
 * @param {string} type - Result type (success or error)
 * @param {string} title - Result title
 * @param {string} message - Result message
 * @param {string} filePath - Optional file path to display
 */
function showResult(type, title, message, filePath = null) {
    const resultDiv = document.getElementById('result');
    resultDiv.className = `result ${type}`;

    let html = `
        <div class="result-title">${title}</div>
        <div class="result-message">${escapeHtml(message)}</div>
    `;

    if (filePath) {
        html += `<div class="file-path">📄 ${escapeHtml(filePath)}</div>`;
    }

    resultDiv.innerHTML = html;
    resultDiv.style.display = 'block';
}

// ============================================================================
// FORM SUBMISSION
// ============================================================================

/**
 * Handle form submission and test case generation.
 */
document.getElementById('testCaseForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    // Generate unique session ID
    sessionId = 'session_' + Date.now();

    // Clear previous logs and results
    clearLogs();

    // Parse user input
    const combinedInput = document.getElementById('combinedInput').value;
    const parsed = parseCombinedInput(combinedInput);
    const userStory = parsed.userStory;
    const acceptanceCriteria = parsed.acceptanceCriteria;

    const filename = document.getElementById('filename').value.trim();
    const appendDatetime = document.getElementById('appendDatetime').checked;

    // Validate inputs
    if (!userStory) {
        showResult('error', 'Validation Error', 'Please provide a user story');
        addLog('Validation failed: No user story provided', 'error');
        return;
    }

    if (acceptanceCriteria.length === 0) {
        showResult('error', 'Validation Error', 'Please add at least one acceptance criterion');
        addLog('Validation failed: No acceptance criteria provided', 'error');
        return;
    }

    // Start log stream
    connectLogStream(sessionId);

    // Add initial client-side logs
    addLog('Starting test case generation...', 'info');
    addLog(`User story parsed successfully`, 'success');
    addLog(`Found ${acceptanceCriteria.length} acceptance criteria`, 'success');

    // Disable generate button and show spinner
    const generateBtn = document.getElementById('generateBtn');
    generateBtn.disabled = true;
    document.getElementById('result').style.display = 'none';

    // Show spinner / hide button text
    const btnTextEl = document.getElementById('btnText');
    const btnSpinnerEl = document.getElementById('btnSpinner');
    if (btnTextEl) btnTextEl.style.display = 'none';
    if (btnSpinnerEl) btnSpinnerEl.style.display = 'inline-block';

    try {
        addLog('Sending request to server...', 'info');

        // Send request to backend API
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_story: userStory,
                acceptance_criteria: acceptanceCriteria,
                filename: filename,
                append_datetime: appendDatetime,
                session_id: sessionId
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Success
            addLog(`✓ Generated ${data.test_case_count} test cases successfully!`, 'success');
            addLog(`✓ Saved to: ${data.file_path}`, 'success');
            showResult('success', '✅ Success!',
                `Generated ${data.test_case_count} test cases successfully!`,
                data.file_path
            );
        } else {
            // Error from server
            addLog(`✗ Generation failed: ${data.error}`, 'error');
            showResult('error', '❌ Generation Failed', data.error || 'An unknown error occurred');
        }
    } catch (error) {
        // Network or connection error
        addLog(`✗ Connection error: ${error.message}`, 'error');
        showResult('error', '❌ Connection Error',
            'Could not connect to the server. Make sure the web server is running.');
    } finally {
        // Re-enable generate button
        generateBtn.disabled = false;
        // Reset spinner / show button text
        const btnTextReset = document.getElementById('btnText');
        const btnSpinnerReset = document.getElementById('btnSpinner');
        if (btnTextReset) btnTextReset.style.display = 'inline';
        if (btnSpinnerReset) btnSpinnerReset.style.display = 'none';

        // Close log stream after a brief delay
        if (eventSource) {
            setTimeout(() => {
                eventSource.close();
                eventSource = null;
            }, 1000);
        }
    }
});

// ============================================================================
// INITIALIZATION
// ============================================================================

/**
 * Initialize the application when DOM is ready.
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Test Case Generator initialized');
    console.log('Model:', window.APP_CONFIG.modelName);

    // Add initial log message
    addLog('Application ready. Paste your user story and criteria to begin.', 'info');
});
