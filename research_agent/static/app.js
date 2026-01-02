/**
 * Investment Research Agent - Main Application JavaScript
 */

// Global state
let ws = null;
let sessionId = null;
let totalCost = 0;
let isProcessing = false;
let messageQueue = [];
let selectedCommandIndex = 0;
let currentModel = 'claude-sonnet-4-20250514';
let selectedFile = null;
let isResizing = false;
let isResizingFiles = false;

// Slash commands definition
const COMMANDS = [
    { name: '/clear', description: 'Clear the chat history' },
    { name: '/new', description: 'Start a new session (clears context)' },
    { name: '/stop', description: 'Stop the current generation' },
    { name: '/help', description: 'Show available commands' },
];

// ============================================
// WebSocket Connection
// ============================================

function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

    ws.onopen = () => {
        updateStatus('Connected', 'status-connected');
        document.getElementById('send-btn').disabled = false;
    };

    ws.onclose = () => {
        updateStatus('Disconnected - Reconnecting...', 'status-error');
        document.getElementById('send-btn').disabled = true;
        setTimeout(connect, 2000);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateStatus('Connection error', 'status-error');
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleMessage(data);
    };
}

// ============================================
// Status Updates
// ============================================

function updateStatus(text, className) {
    const status = document.getElementById('status');
    const statusBar = status.parentElement;
    status.textContent = text;
    statusBar.className = 'status-bar ' + (className || '');
}

function updateQueueStatus() {
    const queueStatus = document.getElementById('queue-status');
    if (messageQueue.length > 0) {
        queueStatus.textContent = `${messageQueue.length} message${messageQueue.length > 1 ? 's' : ''} queued`;
    } else {
        queueStatus.textContent = '';
    }
}

// ============================================
// Message Handling
// ============================================

function handleMessage(data) {
    const container = document.getElementById('chat-container');

    // Remove typing indicator if present
    const typingEl = document.getElementById('typing-indicator');
    if (typingEl) typingEl.remove();

    if (data.type === 'session_id') {
        sessionId = data.session_id;
        return;
    }

    if (data.type === 'text') {
        // Find or create assistant message
        let msgEl = document.getElementById('current-response');
        if (!msgEl) {
            msgEl = document.createElement('div');
            msgEl.id = 'current-response';
            msgEl.className = 'message assistant';
            msgEl.innerHTML = '<div class="message-label">Assistant</div><div class="content"></div>';
            container.appendChild(msgEl);
        }

        const contentEl = msgEl.querySelector('.content');
        contentEl.innerHTML = formatMarkdown(data.content);
        container.scrollTop = container.scrollHeight;
    }

    if (data.type === 'tool_use') {
        // Clear current response ID so any subsequent text creates a new element
        const currentEl = document.getElementById('current-response');
        if (currentEl) currentEl.id = '';

        // Format tool display - extract simple name and create user-friendly messages
        const toolName = data.tool_name.toLowerCase();
        const simpleToolName = toolName.split('__').pop();

        // Create user-friendly display for specific tools
        let toolDisplay = '';
        let contentDisplay = '';

        if (simpleToolName === 'generate_report' || toolName.includes('generate_report')) {
            const company = data.input?.company_name || 'company';
            const ticker = data.input?.ticker || '';
            toolDisplay = 'Generating Report';
            contentDisplay = `Creating equity research report for ${company}${ticker ? ` (${ticker})` : ''}...`;
        } else if (simpleToolName === 'web_search' || toolName.includes('web_search')) {
            toolDisplay = 'Web Search';
            contentDisplay = `Searching for: ${data.input?.query || 'information'}`;
        } else if (simpleToolName === 'update_tasks' || toolName.includes('update_tasks')) {
            toolDisplay = data.input?.main_task || 'Task Progress';
            // Parse todos and render as checklist
            let todosData = [];
            try {
                const todosStr = data.input?.todos || '[]';
                todosData = JSON.parse(todosStr);
            } catch (e) {
                todosData = [];
            }
            if (todosData.length > 0) {
                contentDisplay = '<ul class="task-checklist">';
                for (const todo of todosData) {
                    const status = todo.status || 'pending';
                    let icon = '○';  // pending
                    let statusClass = 'pending';
                    if (status === 'completed' || status === 'complete') {
                        icon = '✓';
                        statusClass = 'completed';
                    } else if (status === 'in_progress') {
                        icon = '◐';
                        statusClass = 'in-progress';
                    }
                    const text = todo.content || todo.name || '';
                    contentDisplay += `<li class="task-item ${statusClass}"><span class="task-icon">${icon}</span> ${text}</li>`;
                }
                contentDisplay += '</ul>';
            } else {
                contentDisplay = 'Updating task progress...';
            }
        } else {
            // Default: show tool name and abbreviated input
            toolDisplay = simpleToolName.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
            contentDisplay = JSON.stringify(data.input, null, 2);
        }

        const msgEl = document.createElement('div');
        msgEl.className = 'message tool';
        msgEl.innerHTML = `
            <div class="message-label">${toolDisplay}</div>
            <div class="content">${contentDisplay}</div>
        `;
        container.appendChild(msgEl);
        container.scrollTop = container.scrollHeight;
    }

    if (data.type === 'tool_result') {
        // Clear current response ID so any subsequent text creates a new element
        const currentEl = document.getElementById('current-response');
        if (currentEl) currentEl.id = '';

        // Check if this is a report generation result
        const content = data.content || '';
        let displayContent = content;
        let label = 'Tool Result';

        if (content.includes('Reports generated successfully') || content.includes('HTML report generated')) {
            label = 'Report Generated';
            displayContent = '✅ Report generated successfully! Check the Files panel to view.';
        }

        const msgEl = document.createElement('div');
        msgEl.className = 'message tool';
        msgEl.innerHTML = `
            <div class="message-label">${label}</div>
            <div class="content">${formatMarkdown(displayContent)}</div>
        `;
        container.appendChild(msgEl);
        container.scrollTop = container.scrollHeight;

        // Refresh file list and tasks after tool execution
        refreshFiles();
        refreshTasks();
    }

    if (data.type === 'interrupted') {
        const msgEl = document.createElement('div');
        msgEl.className = 'message system';
        msgEl.textContent = 'Generation stopped';
        container.appendChild(msgEl);
        hideAgentToast();
        finishProcessing(true);
    }

    if (data.type === 'done') {
        // Clear current response ID so next response creates new element
        const currentEl = document.getElementById('current-response');
        if (currentEl) currentEl.id = '';

        if (data.cost) {
            totalCost += data.cost;
            const costEl = document.createElement('div');
            costEl.className = 'cost-info';
            costEl.textContent = `Turn: $${data.cost.toFixed(4)} | Session: $${totalCost.toFixed(4)}`;
            container.appendChild(costEl);
        }

        container.scrollTop = container.scrollHeight;
        finishProcessing();
    }

    if (data.type === 'error') {
        const msgEl = document.createElement('div');
        msgEl.className = 'message system';
        msgEl.textContent = 'Error: ' + data.message;
        container.appendChild(msgEl);
        finishProcessing();
    }
}

// ============================================
// Toast Notifications
// ============================================

function showAgentWorking() {
    const toast = document.getElementById('agent-toast');
    toast.querySelector('.toast-icon').textContent = '⚡';
    toast.querySelector('.toast-text').textContent = 'Agent is thinking...';
    toast.querySelector('.toast-stop').style.display = 'block';
    toast.classList.remove('complete');
    toast.classList.add('visible');
}

function showAgentComplete() {
    const toast = document.getElementById('agent-toast');
    toast.querySelector('.toast-icon').textContent = '✓';
    toast.querySelector('.toast-text').textContent = 'Response complete';
    toast.querySelector('.toast-stop').style.display = 'none';
    toast.classList.add('complete');

    setTimeout(() => {
        toast.classList.remove('visible', 'complete');
    }, 2000);
}

function hideAgentToast() {
    document.getElementById('agent-toast').classList.remove('visible', 'complete');
}

// ============================================
// Processing Control
// ============================================

function finishProcessing(skipCompleteToast = false) {
    isProcessing = false;
    document.getElementById('stop-btn').classList.remove('visible');
    updateStatus('Connected', 'status-connected');
    if (!skipCompleteToast) {
        showAgentComplete();
    }

    // Process next queued message if any
    if (messageQueue.length > 0) {
        requestAnimationFrame(() => {
            const nextQuery = messageQueue.shift();
            updateQueueStatus();

            // Update the queued message to show it's now being processed
            const queuedMsgs = document.querySelectorAll('.message.queued');
            if (queuedMsgs.length > 0) {
                queuedMsgs[0].classList.remove('queued');
                queuedMsgs[0].classList.add('user');
            }

            processQuery(nextQuery);
        });
    }
}

function processQuery(query) {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    isProcessing = true;
    document.getElementById('stop-btn').classList.add('visible');
    updateStatus('Processing...', 'status-processing');
    showAgentWorking();

    // Add typing indicator
    const container = document.getElementById('chat-container');
    const typingEl = document.createElement('div');
    typingEl.id = 'typing-indicator';
    typingEl.className = 'typing-indicator';
    typingEl.innerHTML = '<span>.</span><span>.</span><span>.</span>';
    container.appendChild(typingEl);
    container.scrollTop = container.scrollHeight;

    // Send to server
    ws.send(JSON.stringify({
        type: 'query',
        query: query,
        session_id: sessionId
    }));
}

function sendMessage() {
    const input = document.getElementById('query-input');
    const query = input.value.trim();

    if (!query || !ws || ws.readyState !== WebSocket.OPEN) return;

    // Check for slash command
    if (query.startsWith('/')) {
        executeCommand(query);
        input.value = '';
        hideCommandMenu();
        return;
    }

    const container = document.getElementById('chat-container');

    if (isProcessing) {
        // Queue the message
        messageQueue.push(query);
        updateQueueStatus();

        // Show queued message in chat
        const msgEl = document.createElement('div');
        msgEl.className = 'message queued';
        msgEl.innerHTML = `<div class="message-label">Queued</div><div class="content">${formatMarkdown(query)}</div>`;
        container.appendChild(msgEl);
        container.scrollTop = container.scrollHeight;

        input.value = '';
        return;
    }

    // Add user message to chat
    const msgEl = document.createElement('div');
    msgEl.className = 'message user';
    msgEl.innerHTML = `<div class="message-label">You</div><div class="content">${formatMarkdown(query)}</div>`;
    container.appendChild(msgEl);

    input.value = '';
    processQuery(query);
}

function stopGeneration() {
    if (!isProcessing || !ws || ws.readyState !== WebSocket.OPEN) return;

    ws.send(JSON.stringify({ type: 'interrupt' }));
    updateStatus('Stopping...', 'status-error');
}

// ============================================
// Session Management
// ============================================

function newSession() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        messageQueue = [];
        updateQueueStatus();

        ws.send(JSON.stringify({ type: 'new_session' }));
        sessionId = null;
        totalCost = 0;
        isProcessing = false;
        document.getElementById('stop-btn').classList.remove('visible');
        clearChat();

        const container = document.getElementById('chat-container');
        const msgEl = document.createElement('div');
        msgEl.className = 'message system';
        msgEl.textContent = 'New session started';
        container.appendChild(msgEl);

        updateStatus('Connected', 'status-connected');
    }
}

function clearChat() {
    document.getElementById('chat-container').innerHTML = '';
}

function showHelp() {
    const container = document.getElementById('chat-container');
    const msgEl = document.createElement('div');
    msgEl.className = 'message system';
    msgEl.innerHTML = `
        <strong>Available Commands:</strong><br>
        <code>/clear</code> - Clear chat history<br>
        <code>/new</code> - Start new session<br>
        <code>/stop</code> - Stop generation<br>
        <code>/help</code> - Show this help
    `;
    container.appendChild(msgEl);
    container.scrollTop = container.scrollHeight;
}

// ============================================
// Commands
// ============================================

function executeCommand(cmd) {
    const command = cmd.toLowerCase().trim();
    switch (command) {
        case '/clear':
            clearChat();
            break;
        case '/new':
            newSession();
            break;
        case '/stop':
            stopGeneration();
            break;
        case '/help':
            showHelp();
            break;
        default:
            const container = document.getElementById('chat-container');
            const msgEl = document.createElement('div');
            msgEl.className = 'message system';
            msgEl.textContent = `Unknown command: ${cmd}. Type /help for available commands.`;
            container.appendChild(msgEl);
    }
}

// ============================================
// Model Selection
// ============================================

function changeModel(model) {
    if (isProcessing) {
        document.getElementById('model-select').value = currentModel;
        const container = document.getElementById('chat-container');
        const msgEl = document.createElement('div');
        msgEl.className = 'message system';
        msgEl.textContent = 'Cannot change model while processing. Stop the current generation first.';
        container.appendChild(msgEl);
        return;
    }

    currentModel = model;

    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'set_model',
            model: model
        }));

        sessionId = null;
        totalCost = 0;
        messageQueue = [];
        updateQueueStatus();

        const container = document.getElementById('chat-container');
        const msgEl = document.createElement('div');
        msgEl.className = 'message system';
        msgEl.textContent = `Model changed to ${getModelDisplayName(model)}. Starting new session.`;
        container.appendChild(msgEl);
        container.scrollTop = container.scrollHeight;
    }
}

function getModelDisplayName(model) {
    const names = {
        'claude-sonnet-4-20250514': 'Claude Sonnet 4',
        'claude-opus-4-20250514': 'Claude Opus 4',
        'claude-3-5-sonnet-20241022': 'Claude 3.5 Sonnet',
        'claude-3-5-haiku-20241022': 'Claude 3.5 Haiku'
    };
    return names[model] || model;
}

// ============================================
// Command Menu
// ============================================

function showCommandMenu(filter = '') {
    const menu = document.getElementById('command-menu');
    const filtered = COMMANDS.filter(c => c.name.startsWith(filter));

    if (filtered.length === 0 || filter === '') {
        hideCommandMenu();
        return;
    }

    selectedCommandIndex = 0;
    menu.innerHTML = filtered.map((cmd, i) => `
        <div class="command-item ${i === 0 ? 'selected' : ''}" data-command="${cmd.name}">
            <span class="command-name">${cmd.name}</span>
            <span class="command-desc">${cmd.description}</span>
        </div>
    `).join('');

    menu.querySelectorAll('.command-item').forEach(item => {
        item.addEventListener('click', () => {
            selectCommand(item.dataset.command);
        });
    });

    menu.classList.add('visible');
}

function hideCommandMenu() {
    const menu = document.getElementById('command-menu');
    menu.classList.remove('visible');
    selectedCommandIndex = 0;
}

function selectCommand(command) {
    const input = document.getElementById('query-input');
    input.value = command;
    hideCommandMenu();
    input.focus();
}

function navigateCommandMenu(direction) {
    const menu = document.getElementById('command-menu');
    const items = menu.querySelectorAll('.command-item');
    if (items.length === 0) return;

    items[selectedCommandIndex].classList.remove('selected');
    selectedCommandIndex = (selectedCommandIndex + direction + items.length) % items.length;
    items[selectedCommandIndex].classList.add('selected');
}

function confirmCommandSelection() {
    const menu = document.getElementById('command-menu');
    const items = menu.querySelectorAll('.command-item');
    if (items.length > 0 && menu.classList.contains('visible')) {
        selectCommand(items[selectedCommandIndex].dataset.command);
        return true;
    }
    return false;
}

// ============================================
// Markdown Formatting
// ============================================

function formatMarkdown(text) {
    if (!text) return '';

    // Escape HTML
    text = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

    // Headers
    text = text.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    text = text.replace(/^# (.+)$/gm, '<h2>$1</h2>');

    // Bold
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Italic
    text = text.replace(/\*(.+?)\*/g, '<em>$1</em>');

    // Code blocks
    text = text.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');

    // Inline code
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Lists
    text = text.replace(/^- (.+)$/gm, '<li>$1</li>');
    text = text.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');

    // Paragraphs
    text = text.replace(/\n\n/g, '</p><p>');
    text = '<p>' + text + '</p>';

    // Clean up empty paragraphs
    text = text.replace(/<p>\s*<\/p>/g, '');
    text = text.replace(/<p>\s*(<h2>)/g, '$1');
    text = text.replace(/(<\/h2>)\s*<\/p>/g, '$1');
    text = text.replace(/<p>\s*(<ul>)/g, '$1');
    text = text.replace(/(<\/ul>)\s*<\/p>/g, '$1');
    text = text.replace(/<p>\s*(<pre>)/g, '$1');
    text = text.replace(/(<\/pre>)\s*<\/p>/g, '$1');

    return text;
}

// ============================================
// Files Pane
// ============================================

function toggleFilesPane() {
    const pane = document.getElementById('files-pane');
    pane.classList.toggle('collapsed');
}

async function refreshFiles() {
    try {
        const response = await fetch('/api/files');
        const files = await response.json();
        renderFileList(files);
    } catch (err) {
        console.error('Failed to load files:', err);
        document.getElementById('files-content').innerHTML =
            '<div class="files-empty">Failed to load files</div>';
    }
}

function renderFileList(files) {
    const container = document.getElementById('files-content');

    if (!files || files.length === 0) {
        container.innerHTML = '<div class="files-empty">No files in outputs/</div>';
        return;
    }

    container.innerHTML = files.map(file => {
        const ext = file.name.split('.').pop() || '';
        const icon = getFileIcon(ext);
        const isSelected = selectedFile === file.name;
        return `
            <div class="file-item ${isSelected ? 'selected' : ''}"
                 onclick="selectFile('${file.name}')"
                 title="${file.name}">
                ${icon}
                <span class="file-name">${file.name}</span>
                <span class="file-ext">${ext}</span>
            </div>
        `;
    }).join('');
}

function getFileIcon(ext) {
    const icons = {
        docx: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <path d="M14 2v6h6"/>
            <path d="M16 13H8"/>
            <path d="M16 17H8"/>
            <path d="M10 9H8"/>
        </svg>`,
        pdf: `<svg viewBox="0 0 24 24" fill="none" stroke="#e94560" stroke-width="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <path d="M14 2v6h6"/>
        </svg>`,
        png: `<svg viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="1.5">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <path d="M21 15l-5-5L5 21"/>
        </svg>`,
        jpg: `<svg viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="1.5">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <path d="M21 15l-5-5L5 21"/>
        </svg>`,
        drawio: `<svg viewBox="0 0 24 24" fill="none" stroke="#f97316" stroke-width="1.5">
            <rect x="3" y="3" width="7" height="7"/>
            <rect x="14" y="3" width="7" height="7"/>
            <rect x="14" y="14" width="7" height="7"/>
            <rect x="3" y="14" width="7" height="7"/>
        </svg>`,
        json: `<svg viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <path d="M14 2v6h6"/>
        </svg>`,
        csv: `<svg viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <path d="M14 2v6h6"/>
            <path d="M8 13h2"/>
            <path d="M8 17h2"/>
            <path d="M14 13h2"/>
            <path d="M14 17h2"/>
        </svg>`,
        html: `<svg viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <path d="M14 2v6h6"/>
            <path d="M8 13l2 2-2 2"/>
            <path d="M16 13l-2 2 2 2"/>
        </svg>`,
        htm: `<svg viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <path d="M14 2v6h6"/>
            <path d="M8 13l2 2-2 2"/>
            <path d="M16 13l-2 2 2 2"/>
        </svg>`
    };
    return icons[ext.toLowerCase()] || `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <path d="M14 2v6h6"/>
    </svg>`;
}

function selectFile(filename) {
    selectedFile = filename;

    document.querySelectorAll('.file-item').forEach(el => {
        el.classList.remove('selected');
        if (el.getAttribute('title') === filename) {
            el.classList.add('selected');
        }
    });

    loadFileInViewer(filename);
}

function loadFileInViewer(filename) {
    const viewer = document.getElementById('viewer-content');
    const ext = filename.split('.').pop().toLowerCase();

    if (ext === 'png' || ext === 'jpg' || ext === 'jpeg' || ext === 'gif' || ext === 'svg') {
        viewer.innerHTML = `
            <div style="height: 100%; display: flex; align-items: center; justify-content: center; padding: 1rem;">
                <img src="/outputs/${filename}" style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 8px;" />
            </div>
        `;
    } else if (ext === 'pdf') {
        viewer.innerHTML = `
            <iframe src="/outputs/${filename}" style="width: 100%; height: 100%; border: none;"></iframe>
        `;
    } else if (ext === 'html' || ext === 'htm') {
        viewer.innerHTML = `
            <iframe src="/outputs/${filename}" style="width: 100%; height: 100%; border: none; background: white;"></iframe>
        `;
    } else if (ext === 'docx') {
        const htmlFilename = filename.replace(/\.docx$/i, '.html');
        fetch(`/outputs/${htmlFilename}`, { method: 'HEAD' })
            .then(res => {
                if (res.ok) {
                    viewer.innerHTML = `
                        <div style="height: 100%; display: flex; flex-direction: column;">
                            <div style="padding: 0.5rem 1rem; background: #2a2a2a; border-bottom: 1px solid #333; display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: #aaa; font-size: 0.85rem;">Viewing HTML version</span>
                                <a href="/outputs/${filename}" download style="color: #e94560; text-decoration: none; font-size: 0.85rem;">
                                    Download DOCX →
                                </a>
                            </div>
                            <iframe src="/outputs/${htmlFilename}" style="flex: 1; width: 100%; border: none; background: white;"></iframe>
                        </div>
                    `;
                } else {
                    showDocxDownloadPlaceholder(viewer, filename);
                }
            })
            .catch(() => {
                showDocxDownloadPlaceholder(viewer, filename);
            });
    } else if (ext === 'json' || ext === 'csv' || ext === 'txt' || ext === 'md') {
        fetch(`/outputs/${filename}`)
            .then(res => res.text())
            .then(content => {
                viewer.innerHTML = `
                    <pre style="padding: 1rem; margin: 0; overflow: auto; height: 100%; font-size: 0.85rem; line-height: 1.5; color: #ccc; background: transparent;">${escapeHtml(content)}</pre>
                `;
            })
            .catch(() => {
                viewer.innerHTML = `<div class="viewer-placeholder"><p>Failed to load file</p></div>`;
            });
    } else {
        viewer.innerHTML = `
            <div class="viewer-placeholder">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width: 48px; height: 48px;">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <path d="M14 2v6h6"/>
                </svg>
                <p style="margin-top: 1rem;"><strong>${filename}</strong></p>
                <p style="margin-top: 0.5rem; color: #666;">Preview not available for this file type.</p>
                <a href="/outputs/${filename}" download style="margin-top: 1rem; color: #e94560; text-decoration: none;">
                    Download file →
                </a>
            </div>
        `;
    }
}

function showDocxDownloadPlaceholder(viewer, filename) {
    viewer.innerHTML = `
        <div class="viewer-placeholder">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width: 48px; height: 48px;">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <path d="M14 2v6h6"/>
                <path d="M16 13H8"/>
                <path d="M16 17H8"/>
            </svg>
            <p style="margin-top: 1rem;"><strong>${filename}</strong></p>
            <p style="margin-top: 0.5rem; color: #666;">Word documents cannot be previewed in browser.</p>
            <a href="/outputs/${filename}" download style="margin-top: 1rem; color: #e94560; text-decoration: none;">
                Download file →
            </a>
        </div>
    `;
}

// ============================================
// Tasks
// ============================================

async function refreshTasks() {
    try {
        const response = await fetch('/api/tasks');
        const tasks = await response.json();
        renderTasks(tasks);
    } catch (err) {
        console.error('Failed to load tasks:', err);
    }
}

function renderTasks(tasks) {
    const container = document.getElementById('tasks-content');

    if (!tasks.main_task) {
        container.innerHTML = '<div class="tasks-empty">No active tasks</div>';
        return;
    }

    const subtasks = tasks.subtasks || [];
    const complete = subtasks.filter(t => t.status === 'complete').length;
    const total = subtasks.length;
    const progress = total > 0 ? Math.round((complete / total) * 100) : 0;

    const statusIcons = {
        'complete': '✓',
        'in_progress': '⚡',
        'pending': '○',
        'blocked': '⚠',
        'skipped': '–'
    };

    let html = `
        <div class="task-main">
            <div class="task-main-title">${escapeHtml(tasks.main_task.description)}</div>
            <div class="task-progress-bar">
                <div class="task-progress-fill" style="width: ${progress}%"></div>
            </div>
            <div class="task-progress-text">${complete}/${total} subtasks complete</div>
        </div>
    `;

    if (subtasks.length > 0) {
        html += subtasks.map(task => `
            <div class="subtask-item" title="${escapeHtml(task.description || task.name)}">
                <span class="subtask-status ${task.status}">${statusIcons[task.status] || '○'}</span>
                <span class="subtask-name">${escapeHtml(task.name)}</span>
            </div>
        `).join('');
    }

    container.innerHTML = html;
}

// ============================================
// Utilities
// ============================================

function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/&/g, '&amp;')
               .replace(/</g, '&lt;')
               .replace(/>/g, '&gt;')
               .replace(/"/g, '&quot;');
}

// ============================================
// Resizer Functionality
// ============================================

function initResizers() {
    const resizer = document.getElementById('resizer');
    const viewerPane = document.getElementById('viewer-pane');
    const resizerFiles = document.getElementById('resizer-files');
    const filesPane = document.getElementById('files-pane');

    resizer.addEventListener('mousedown', (e) => {
        isResizing = true;
        resizer.classList.add('dragging');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
    });

    resizerFiles.addEventListener('mousedown', (e) => {
        isResizingFiles = true;
        resizerFiles.classList.add('dragging');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
    });

    document.addEventListener('mousemove', (e) => {
        if (isResizingFiles) {
            const containerRect = document.querySelector('.split-container').getBoundingClientRect();
            const newWidth = e.clientX - containerRect.left;
            const minWidth = 180;
            const maxWidth = 350;

            if (newWidth >= minWidth && newWidth <= maxWidth) {
                filesPane.style.width = newWidth + 'px';
            }
        }

        if (isResizing) {
            const containerRect = document.querySelector('.split-container').getBoundingClientRect();
            const filesWidth = filesPane.classList.contains('collapsed') ? 40 : filesPane.offsetWidth;
            const newWidth = e.clientX - containerRect.left - filesWidth - 12;
            const minWidth = 300;
            const maxWidth = containerRect.width - filesWidth - 350 - 12;

            if (newWidth >= minWidth && newWidth <= maxWidth) {
                viewerPane.style.width = newWidth + 'px';
            }
        }
    });

    document.addEventListener('mouseup', () => {
        if (isResizingFiles) {
            isResizingFiles = false;
            resizerFiles.classList.remove('dragging');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        }
        if (isResizing) {
            isResizing = false;
            resizer.classList.remove('dragging');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        }
    });
}

// ============================================
// Event Listeners Setup
// ============================================

function initEventListeners() {
    // Input event handler for slash commands
    document.getElementById('query-input').addEventListener('input', (e) => {
        const value = e.target.value;
        if (value.startsWith('/')) {
            showCommandMenu(value);
        } else {
            hideCommandMenu();
        }
    });

    // Handle keyboard navigation
    document.getElementById('query-input').addEventListener('keydown', (e) => {
        const menu = document.getElementById('command-menu');
        const isMenuVisible = menu.classList.contains('visible');

        if (isMenuVisible) {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                navigateCommandMenu(1);
                return;
            }
            if (e.key === 'ArrowUp') {
                e.preventDefault();
                navigateCommandMenu(-1);
                return;
            }
            if (e.key === 'Tab' || (e.key === 'Enter' && !e.shiftKey)) {
                e.preventDefault();
                if (confirmCommandSelection()) return;
            }
            if (e.key === 'Escape') {
                e.preventDefault();
                hideCommandMenu();
                return;
            }
        }

        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Viewer tab functionality
    document.querySelectorAll('.viewer-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.viewer-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
        });
    });
}

// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    connect();
    refreshFiles();
    refreshTasks();
    initResizers();
    initEventListeners();

    // Poll for task updates every 5 seconds
    setInterval(refreshTasks, 5000);
});
