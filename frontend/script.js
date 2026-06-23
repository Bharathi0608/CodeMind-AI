import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';

mermaid.initialize({
    startOnLoad: false,
    theme: 'base',
    themeVariables: {
        background: '#f8fafc',
        primaryColor: '#0f172a',
        primaryTextColor: '#f8fafc',
        primaryBorderColor: '#0072ff',
        lineColor: '#64748b',
        secondaryColor: '#1e293b',
        tertiaryColor: '#e2e8f0',
        mainBkg: '#0f172a',
        nodeBorder: '#00c6ff',
        clusterBkg: '#f8fafc',
        clusterBorder: '#cbd5e1',
        edgeColor: '#3b82f6',
        fontFamily: 'Inter, sans-serif'
    }
});

const API_BASE = "/api";

const analyzeForm = document.getElementById('analyze-form');
const analyzeBtn = document.getElementById('analyze-btn');
const analyzeSpinner = document.getElementById('analyze-spinner');
const btnText = analyzeBtn.querySelector('.btn-text');
const statusMsg = document.getElementById('status-message');
const resultsContainer = document.getElementById('results-container');
const mermaidContainer = document.getElementById('mermaid-container');
const summaryContent = document.getElementById('summary-content');

const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatHistory = document.getElementById('chat-history');
const chatSpinner = document.getElementById('chat-spinner');
const chatSubmitBtn = document.getElementById('chat-submit-btn');
const chatBtnText = chatSubmitBtn.querySelector('.btn-text');

let currentMermaidSVG = "";
let currentSummaryMarkdown = "";

analyzeForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const repoUrl = document.getElementById('repo-url').value;
    
    // UI Loading state
    analyzeBtn.disabled = true;
    btnText.textContent = "Analyzing...";
    analyzeSpinner.classList.remove('hidden');
    statusMsg.classList.remove('hidden');
    statusMsg.innerHTML = "<em>Cloning and parsing repository. This may take a minute...</em>";
    resultsContainer.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ repo_url: repoUrl })
        });
        
        const data = await response.json();
        
        if (data.success) {
            statusMsg.innerHTML = "<span style='color: #00c6ff'>✅ Analysis Complete!</span>";
            resultsContainer.classList.remove('hidden');
            
            // Store and Render Markdown
            currentSummaryMarkdown = data.summary;
            summaryContent.innerHTML = marked.parse(data.summary);
            
            // Render Mermaid
            if (data.mermaid_code) {
                renderMermaid(data.mermaid_code);
            } else {
                mermaidContainer.innerHTML = "<p>No architecture diagram was generated.</p>";
            }
            
            // Clear old chat
            chatHistory.innerHTML = "";
            
        } else {
            statusMsg.innerHTML = `<span style='color: #ef4444'>❌ Error: ${data.error}</span>`;
        }
    } catch (err) {
        statusMsg.innerHTML = `<span style='color: #ef4444'>❌ Connection Error: Ensure backend is running at ${API_BASE}</span>`;
    } finally {
        analyzeBtn.disabled = false;
        btnText.textContent = "Analyze Repository";
        analyzeSpinner.classList.add('hidden');
    }
});

async function renderMermaid(code) {
    try {
        const { svg } = await mermaid.render('flowchart-svg-render', code);
        currentMermaidSVG = svg;
        mermaidContainer.innerHTML = svg;
        
        const svgElement = mermaidContainer.querySelector('svg');
        if(svgElement) {
            // Apply colors to backend nodes
            const nodes = svgElement.querySelectorAll('.node');
            nodes.forEach(node => {
                const text = node.textContent.toLowerCase();
                if(text.includes('backend') || text.includes('service') || text.includes('api')) {
                    node.querySelector('rect, circle, polygon')?.setAttribute('fill', '#0f766e');
                } else {
                    node.querySelector('rect, circle, polygon')?.setAttribute('fill', '#0056cc');
                }
                node.querySelectorAll('.label, text').forEach(t => {
                    t.setAttribute('fill', '#ffffff');
                    t.style.color = '#ffffff';
                });
            });

            svgElement.setAttribute('id', 'interactive-flowchart');
            svgElement.style.width = "100%";
            svgElement.style.height = "100%";
            svgElement.style.maxWidth = "none";
            
            svgPanZoom('#interactive-flowchart', {
                zoomEnabled: true,
                controlIconsEnabled: true,
                fit: true,
                center: true,
                minZoom: 0.1,
                maxZoom: 20
            });
        }
    } catch (e) {
        mermaidContainer.innerHTML = `<p style="color:red">Error rendering flowchart: ${e.message}</p>`;
    }
}

document.getElementById('download-btn').addEventListener('click', () => {
    if (!currentMermaidSVG) return;
    const blob = new Blob([currentMermaidSVG], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'architecture_flowchart.svg';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
});

document.getElementById('download-report-btn').addEventListener('click', () => {
    if (!currentSummaryMarkdown) return;
    const blob = new Blob([currentSummaryMarkdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'CodeMind_AI_Report.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
});

// Chat Functions
window.fillChat = function(query) {
    chatInput.value = query;
    chatForm.dispatchEvent(new Event('submit'));
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;

    // Add user message
    appendMessage(query, 'user');
    chatInput.value = "";
    
    // UI Loading state
    chatSubmitBtn.disabled = true;
    chatBtnText.textContent = "Thinking...";
    chatSpinner.classList.remove('hidden');

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });
        
        const data = await response.json();
        
        if (data.success) {
            appendMessage(data.answer, 'bot');
        } else {
            appendMessage(`Error: ${data.error}`, 'bot');
        }
    } catch (err) {
        appendMessage("Connection Error: Could not reach backend.", 'bot');
    } finally {
        chatSubmitBtn.disabled = false;
        chatBtnText.textContent = "Send";
        chatSpinner.classList.add('hidden');
    }
});

function appendMessage(content, role) {
    const div = document.createElement('div');
    div.classList.add('message', role === 'user' ? 'msg-user' : 'msg-bot');
    div.innerHTML = role === 'bot' ? marked.parse(content) : content;
    chatHistory.appendChild(div);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}
