#!/usr/bin/env python3
"""Web UI for the Investment Research Agent.

A simple FastAPI-based web interface for interacting with the research agent.
Supports message queueing and interruption.

Usage:
    python -m research_agent.web

Then open http://localhost:8000 in your browser.
"""

import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
)

from research_agent.agent import get_agent_options

app = FastAPI(title="Investment Research Agent")

# Store active sessions
sessions: dict[str, ClaudeSDKClient] = {}


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Investment Research Agent</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #1a1a2e;
            color: #eee;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        header {
            background: #16213e;
            padding: 0.75rem 1.5rem;
            border-bottom: 1px solid #0f3460;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-shrink: 0;
        }

        header .title-section h1 {
            font-size: 1.25rem;
            color: #e94560;
        }

        header .title-section p {
            color: #888;
            font-size: 0.8rem;
            margin-top: 0.1rem;
        }

        header .hint {
            font-size: 0.75rem;
            color: #555;
        }

        header .hint code {
            background: #0f3460;
            padding: 0.15rem 0.4rem;
            border-radius: 3px;
            color: #888;
        }

        /* Split pane layout */
        .split-container {
            flex: 1;
            display: flex;
            overflow: hidden;
        }

        /* Left pane - Viewer */
        .viewer-pane {
            width: 50%;
            min-width: 300px;
            background: #12121f;
            display: flex;
            flex-direction: column;
            border-right: 1px solid #0f3460;
        }

        .viewer-header {
            padding: 0.75rem 1rem;
            background: #16213e;
            border-bottom: 1px solid #0f3460;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .viewer-header h2 {
            font-size: 0.9rem;
            color: #888;
            font-weight: 500;
        }

        .viewer-tabs {
            display: flex;
            gap: 0.25rem;
        }

        .viewer-tab {
            padding: 0.3rem 0.6rem;
            font-size: 0.75rem;
            background: transparent;
            color: #666;
            border: 1px solid #333;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .viewer-tab:hover {
            border-color: #555;
            color: #888;
        }

        .viewer-tab.active {
            background: #0f3460;
            border-color: #0f3460;
            color: #eee;
        }

        .viewer-content {
            flex: 1;
            overflow: auto;
            padding: 1rem;
        }

        .viewer-placeholder {
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #444;
            text-align: center;
        }

        .viewer-placeholder svg {
            width: 64px;
            height: 64px;
            margin-bottom: 1rem;
            opacity: 0.5;
        }

        .viewer-placeholder p {
            font-size: 0.9rem;
            max-width: 300px;
            line-height: 1.5;
        }

        /* Resizer */
        .resizer {
            width: 6px;
            background: #0f3460;
            cursor: col-resize;
            transition: background 0.2s;
            flex-shrink: 0;
        }

        .resizer:hover,
        .resizer.dragging {
            background: #e94560;
        }

        /* Right pane - Chat */
        .chat-pane {
            flex: 1;
            min-width: 350px;
            display: flex;
            flex-direction: column;
            background: #1a1a2e;
        }

        #chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
        }

        .message {
            margin-bottom: 1rem;
            padding: 0.875rem;
            border-radius: 8px;
            line-height: 1.6;
        }

        .message.user {
            background: #0f3460;
            margin-left: 1.5rem;
        }

        .message.assistant {
            background: #16213e;
            border: 1px solid #0f3460;
            margin-right: 1.5rem;
        }

        .message.system {
            background: #2d132c;
            border: 1px solid #e94560;
            text-align: center;
            font-size: 0.85rem;
            color: #e94560;
        }

        .message.tool {
            background: #1e3a5f;
            border: 1px solid #4a9eff;
            font-size: 0.85rem;
        }

        .message.queued {
            background: #2d2d44;
            border: 1px dashed #666;
            opacity: 0.7;
        }

        .message-label {
            font-size: 0.7rem;
            color: #888;
            margin-bottom: 0.4rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .message h2 {
            color: #e94560;
            font-size: 1rem;
            margin: 0.875rem 0 0.4rem 0;
        }

        .message h2:first-child {
            margin-top: 0;
        }

        .message p {
            margin-bottom: 0.6rem;
        }

        .message ul, .message ol {
            margin-left: 1.25rem;
            margin-bottom: 0.6rem;
        }

        .message li {
            margin-bottom: 0.2rem;
        }

        .message code {
            background: #0f3460;
            padding: 0.15rem 0.35rem;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.85em;
        }

        .message pre {
            background: #0f3460;
            padding: 0.875rem;
            border-radius: 4px;
            overflow-x: auto;
            margin-bottom: 0.6rem;
        }

        .message pre code {
            background: none;
            padding: 0;
        }

        /* Input area */
        .input-area {
            padding: 0.75rem;
            background: #16213e;
            border-top: 1px solid #0f3460;
        }

        #input-container {
            display: flex;
            gap: 0.5rem;
        }

        #query-input {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #0f3460;
            border-radius: 6px;
            background: #1a1a2e;
            color: #eee;
            font-size: 0.9rem;
            resize: none;
            min-height: 80px;
            max-height: 120px;
            font-family: inherit;
        }

        #query-input:focus {
            outline: none;
            border-color: #e94560;
        }

        #query-input::placeholder {
            color: #555;
        }

        .input-buttons {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }

        button {
            padding: 0.6rem 1rem;
            background: #e94560;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: background 0.2s;
        }

        button:hover {
            background: #ff6b6b;
        }

        button:disabled {
            background: #444;
            cursor: not-allowed;
        }

        #stop-btn {
            background: #ff9800;
            display: none;
        }

        #stop-btn:hover {
            background: #ffb74d;
        }

        #stop-btn.visible {
            display: block;
        }

        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.4rem 0.75rem;
            font-size: 0.75rem;
            color: #666;
            background: #12121f;
        }

        #status {
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        #status::before {
            content: '';
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #666;
        }

        .status-connected #status::before {
            background: #4ade80;
        }

        .status-error #status::before {
            background: #e94560;
        }

        .status-processing #status::before {
            background: #ff9800;
            animation: pulse 1s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .cost-info {
            font-size: 0.75rem;
            color: #666;
            margin-top: 0.4rem;
            text-align: right;
        }

        .typing-indicator {
            display: inline-block;
            padding: 0.5rem 1rem;
            background: #16213e;
            border-radius: 8px;
            color: #888;
        }

        .typing-indicator span {
            animation: blink 1.4s infinite both;
        }

        .typing-indicator span:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-indicator span:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes blink {
            0%, 80%, 100% { opacity: 0; }
            40% { opacity: 1; }
        }

        #queue-status {
            font-size: 0.75rem;
            color: #ff9800;
        }

        /* Slash command autocomplete */
        .command-menu {
            position: absolute;
            bottom: 100%;
            left: 0;
            right: 0;
            background: #16213e;
            border: 1px solid #0f3460;
            border-radius: 6px;
            margin-bottom: 0.5rem;
            display: none;
            overflow: hidden;
            box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.3);
        }

        .command-menu.visible {
            display: block;
        }

        .command-item {
            padding: 0.6rem 0.75rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            border-bottom: 1px solid #0f3460;
            transition: background 0.15s;
        }

        .command-item:last-child {
            border-bottom: none;
        }

        .command-item:hover,
        .command-item.selected {
            background: #0f3460;
        }

        .command-item .command-name {
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.85rem;
            color: #e94560;
            min-width: 100px;
        }

        .command-item .command-desc {
            font-size: 0.8rem;
            color: #888;
        }

        .input-wrapper {
            position: relative;
            flex: 1;
            display: flex;
            flex-direction: column;
        }
    </style>
</head>
<body>
    <header>
        <div class="title-section">
            <h1>Investment Research Agent</h1>
            <p>Conversational research assistant for institutional investors</p>
        </div>
        <div class="hint">
            Type <code>/</code> for commands
        </div>
    </header>

    <div class="split-container">
        <!-- Left: Viewer Pane -->
        <div class="viewer-pane" id="viewer-pane">
            <div class="viewer-header">
                <h2>Viewer</h2>
                <div class="viewer-tabs">
                    <button class="viewer-tab active" data-tab="preview">Preview</button>
                    <button class="viewer-tab" data-tab="data">Data</button>
                    <button class="viewer-tab" data-tab="charts">Charts</button>
                </div>
            </div>
            <div class="viewer-content" id="viewer-content">
                <div class="viewer-placeholder">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M9 17H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-4"/>
                        <path d="M12 15v6"/>
                        <path d="M8 21h8"/>
                        <path d="M7 9h2"/>
                        <path d="M7 13h6"/>
                    </svg>
                    <p>Research outputs, charts, and data visualizations will appear here as you interact with the agent.</p>
                </div>
            </div>
        </div>

        <!-- Resizer -->
        <div class="resizer" id="resizer"></div>

        <!-- Right: Chat Pane -->
        <div class="chat-pane">
            <div id="chat-container"></div>

            <div class="input-area">
                <div id="input-container">
                    <div class="input-wrapper">
                        <div class="command-menu" id="command-menu"></div>
                        <textarea
                            id="query-input"
                            placeholder="Ask a research question... (/ for commands)"
                            rows="2"
                        ></textarea>
                    </div>
                    <div class="input-buttons">
                        <button id="send-btn" onclick="sendMessage()">Send</button>
                        <button id="stop-btn" onclick="stopGeneration()">Stop</button>
                    </div>
                </div>
            </div>

            <div class="status-bar">
                <div id="status">Connecting...</div>
                <div id="queue-status"></div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let sessionId = null;
        let totalCost = 0;
        let isProcessing = false;
        let messageQueue = [];
        let selectedCommandIndex = 0;

        // Slash commands definition
        const COMMANDS = [
            { name: '/clear', description: 'Clear the chat history' },
            { name: '/new', description: 'Start a new session (clears context)' },
            { name: '/stop', description: 'Stop the current generation' },
            { name: '/help', description: 'Show available commands' },
        ];

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

        function updateStatus(text, className) {
            const status = document.getElementById('status');
            const statusBar = status.parentElement;
            status.textContent = text;
            // Apply class to parent status-bar for the ::before pseudo-element
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
                const msgEl = document.createElement('div');
                msgEl.className = 'message tool';
                msgEl.innerHTML = `
                    <div class="message-label">Tool: ${data.tool_name}</div>
                    <div class="content">${data.tool_name === 'generate_report' ? 'Generating research report...' : JSON.stringify(data.input, null, 2)}</div>
                `;
                container.appendChild(msgEl);
                container.scrollTop = container.scrollHeight;
            }

            if (data.type === 'tool_result') {
                const msgEl = document.createElement('div');
                msgEl.className = 'message tool';
                msgEl.innerHTML = `
                    <div class="message-label">Tool Result</div>
                    <div class="content">${formatMarkdown(data.content)}</div>
                `;
                container.appendChild(msgEl);
                container.scrollTop = container.scrollHeight;
            }

            if (data.type === 'interrupted') {
                const msgEl = document.createElement('div');
                msgEl.className = 'message system';
                msgEl.textContent = 'Generation stopped';
                container.appendChild(msgEl);
                finishProcessing();
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

        function finishProcessing() {
            isProcessing = false;
            document.getElementById('stop-btn').classList.remove('visible');
            updateStatus('Connected', 'status-connected');

            // Process next queued message if any
            if (messageQueue.length > 0) {
                const nextQuery = messageQueue.shift();
                updateQueueStatus();

                // Update the queued message to show it's now being processed
                const queuedMsgs = document.querySelectorAll('.message.queued');
                if (queuedMsgs.length > 0) {
                    queuedMsgs[0].classList.remove('queued');
                    queuedMsgs[0].classList.add('user');
                }

                processQuery(nextQuery);
            }
        }

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
            text = text.replace(/```(\w*)\\n([\\s\\S]*?)```/g, '<pre><code>$2</code></pre>');

            // Inline code
            text = text.replace(/`([^`]+)`/g, '<code>$1</code>');

            // Lists
            text = text.replace(/^- (.+)$/gm, '<li>$1</li>');
            text = text.replace(/(<li>.*<\\/li>\\n?)+/g, '<ul>$&</ul>');

            // Paragraphs
            text = text.replace(/\\n\\n/g, '</p><p>');
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

        function processQuery(query) {
            if (!ws || ws.readyState !== WebSocket.OPEN) return;

            isProcessing = true;
            document.getElementById('stop-btn').classList.add('visible');
            updateStatus('Processing...', 'status-processing');

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

        function newSession() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                // Clear queue
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
                    // Unknown command - show in chat
                    const container = document.getElementById('chat-container');
                    const msgEl = document.createElement('div');
                    msgEl.className = 'message system';
                    msgEl.textContent = `Unknown command: ${cmd}. Type /help for available commands.`;
                    container.appendChild(msgEl);
            }
        }

        // Command menu functions
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

            // Add click handlers
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

        // Resizer functionality
        const resizer = document.getElementById('resizer');
        const viewerPane = document.getElementById('viewer-pane');
        let isResizing = false;

        resizer.addEventListener('mousedown', (e) => {
            isResizing = true;
            resizer.classList.add('dragging');
            document.body.style.cursor = 'col-resize';
            document.body.style.userSelect = 'none';
        });

        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;

            const containerRect = document.querySelector('.split-container').getBoundingClientRect();
            const newWidth = e.clientX - containerRect.left;
            const minWidth = 300;
            const maxWidth = containerRect.width - 350 - 6; // 350 min chat, 6 resizer

            if (newWidth >= minWidth && newWidth <= maxWidth) {
                viewerPane.style.width = newWidth + 'px';
            }
        });

        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
                resizer.classList.remove('dragging');
                document.body.style.cursor = '';
                document.body.style.userSelect = '';
            }
        });

        // Viewer tab functionality
        document.querySelectorAll('.viewer-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.viewer-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                // Tab content switching will be implemented when viewer features are added
            });
        });

        // Connect on load
        connect();
    </script>
</body>
</html>
"""


@app.get("/favicon.ico")
async def get_favicon():
    """Return a simple favicon to prevent 404 errors."""
    # Simple SVG favicon - a chart/graph icon representing research
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
        <rect width="32" height="32" rx="6" fill="#1a1a2e"/>
        <path d="M6 24 L12 16 L18 20 L26 8" stroke="#e94560" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="12" cy="16" r="2" fill="#e94560"/>
        <circle cx="18" cy="20" r="2" fill="#e94560"/>
        <circle cx="26" cy="8" r="2" fill="#e94560"/>
    </svg>'''
    return Response(content=svg, media_type="image/svg+xml")


@app.get("/", response_class=HTMLResponse)
async def get_home():
    """Serve the main HTML page."""
    return HTML_TEMPLATE


@app.get("/outputs/{filename}")
async def get_output_file(filename: str):
    """Serve files from the outputs directory."""
    outputs_dir = Path(__file__).parent.parent / "outputs"
    file_path = outputs_dir / filename
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    return {"error": "File not found"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for real-time chat with interrupt support."""
    await websocket.accept()

    session_id = None
    client = None
    response_task = None

    async def process_response():
        """Process agent response in a separate task for interrupt support."""
        nonlocal client
        current_text = ""
        turn_cost = 0.0

        try:
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            current_text = block.text
                            await websocket.send_json({
                                "type": "text",
                                "content": current_text
                            })
                        elif isinstance(block, ToolUseBlock):
                            await websocket.send_json({
                                "type": "tool_use",
                                "tool_name": block.name,
                                "input": block.input
                            })
                        elif isinstance(block, ToolResultBlock):
                            content = ""
                            if block.content:
                                for item in block.content:
                                    if hasattr(item, "text"):
                                        content += item.text
                            await websocket.send_json({
                                "type": "tool_result",
                                "content": content
                            })

                elif isinstance(message, ResultMessage):
                    if message.total_cost_usd:
                        turn_cost = message.total_cost_usd

            await websocket.send_json({
                "type": "done",
                "cost": turn_cost
            })
        except asyncio.CancelledError:
            # Task was cancelled due to interrupt
            await websocket.send_json({"type": "interrupted"})
            raise

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "new_session":
                # Cancel any ongoing response
                if response_task and not response_task.done():
                    response_task.cancel()
                    try:
                        await response_task
                    except asyncio.CancelledError:
                        pass

                # Close existing client if any
                if client:
                    await client.__aexit__(None, None, None)
                session_id = None
                client = None
                continue

            if data.get("type") == "interrupt":
                # Interrupt the current response
                if client and response_task and not response_task.done():
                    try:
                        await client.interrupt()
                    except Exception:
                        pass
                    response_task.cancel()
                    try:
                        await response_task
                    except asyncio.CancelledError:
                        pass
                continue

            if data.get("type") == "query":
                query = data.get("query", "")

                if not query:
                    await websocket.send_json({"type": "error", "message": "Empty query"})
                    continue

                try:
                    # Create or reuse client
                    if client is None:
                        options = get_agent_options()
                        client = ClaudeSDKClient(options=options)
                        await client.__aenter__()
                        session_id = id(client)
                        await websocket.send_json({"type": "session_id", "session_id": str(session_id)})

                    # Send query
                    await client.query(query)

                    # Process response in a task so we can interrupt it
                    response_task = asyncio.create_task(process_response())
                    await response_task

                except asyncio.CancelledError:
                    # Response was interrupted
                    pass
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })

    except WebSocketDisconnect:
        pass
    finally:
        # Cancel any ongoing response
        if response_task and not response_task.done():
            response_task.cancel()
            try:
                await response_task
            except asyncio.CancelledError:
                pass

        if client:
            try:
                await client.__aexit__(None, None, None)
            except Exception:
                pass


def main():
    """Run the web server."""
    import uvicorn
    from research_agent.config import config

    print("\n" + "=" * 60)
    print("Investment Research Agent - Web UI")
    print("=" * 60)
    print(f"\nStarting server at http://localhost:{config.web.port}")
    print("Press Ctrl+C to stop\n")
    uvicorn.run(
        app,
        host=config.web.host,
        port=config.web.port,
        log_level=config.web.log_level,
    )


if __name__ == "__main__":
    main()
