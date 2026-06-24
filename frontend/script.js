// ── Remove browser-extension injected toolbars immediately ──────────────────
(function removeExtensionToolbars() {
    const SELECTORS = [
        '.toolbar-container',
        'div.toolbar-container',
        '[class*="__bs_"]',
        '[id*="__bs_"]',
        '#__ltc',
        '#__bs_notify__',
    ];

    function killToolbars() {
        SELECTORS.forEach(sel => {
            document.querySelectorAll(sel).forEach(el => el.remove());
        });
    }

    // Run immediately
    killToolbars();

    // Watch for extension injecting elements dynamically
    const observer = new MutationObserver(killToolbars);
    observer.observe(document.documentElement, { childList: true, subtree: true });
})();

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
                document.getElementById('download-flowchart-btn').classList.remove('hidden');
            } else {
                mermaidContainer.innerHTML = "<p>No architecture diagram was generated.</p>";
                document.getElementById('download-flowchart-btn').classList.add('hidden');
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

// ── Download Full PDF Report ──────────────────────────────────────────────
// Use window 'load' so all non-module scripts (jsPDF, marked) are available
window.addEventListener('load', () => {
    // ── SVG Flowchart Download ──────────────────────────────────────────────────
    const flowchartBtn = document.getElementById('download-flowchart-btn');
    if (flowchartBtn) {
        flowchartBtn.addEventListener('click', () => {
            if (!currentMermaidSVG) {
                alert('No flowchart available yet. Please analyze a repository first.');
                return;
            }
            const blob = new Blob([currentMermaidSVG], { type: 'image/svg+xml' });
            const url  = URL.createObjectURL(blob);
            const a    = document.createElement('a');
            a.href     = url;
            a.download = 'architecture_flowchart.svg';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    }

    // ── PDF Download ──────────────────────────────────────────────────────
    document.getElementById('download-report-btn').addEventListener('click', async () => {
        if (!currentSummaryMarkdown) {
            alert('No report to download yet. Please analyze a repository first.');
            return;
        }
        if (!window.jspdf || !window.jspdf.jsPDF) {
            alert('PDF library not loaded yet. Please wait a moment and try again.');
            return;
        }
        const { jsPDF } = window.jspdf;
        const btn = document.getElementById('download-report-btn');
        const btnText = document.getElementById('download-btn-text');
        const spinner = document.getElementById('download-spinner');
        btnText.textContent = '⏳ Generating PDF...';
        spinner.classList.remove('hidden');
        btn.disabled = true;

        try {
        const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });

        const pageW = doc.internal.pageSize.getWidth();
        const pageH = doc.internal.pageSize.getHeight();
        const margin = 15;
        const contentW = pageW - margin * 2;
        const footerH = 8; // reserved for footer
        let y = margin;

        // ── Helper: page break if needed ────────────────────────────────────
        function checkPageBreak(needed = 10) {
            if (y + needed > pageH - margin - footerH) {
                doc.addPage();
                y = margin;
            }
        }

        // ── Helper: blue section divider ─────────────────────────────────────
        function sectionHeader(title) {
            checkPageBreak(16);
            y += 4;
            doc.setFillColor(0, 98, 220);
            doc.roundedRect(margin, y, contentW, 10, 2, 2, 'F');
            doc.setFont('helvetica', 'bold');
            doc.setFontSize(11);
            doc.setTextColor(255, 255, 255);
            doc.text(title, margin + 4, y + 7);
            doc.setTextColor(30, 30, 30);
            y += 14;
        }

        // ── Helper: plain text renderer ──────────────────────────────────────
        function renderText(text, fontSize = 9, color = [30, 30, 30], isBold = false) {
            doc.setFont('helvetica', isBold ? 'bold' : 'normal');
            doc.setFontSize(fontSize);
            doc.setTextColor(...color);
            const wrapped = doc.splitTextToSize(text, contentW);
            wrapped.forEach(line => {
                checkPageBreak(fontSize * 0.45 + 1);
                doc.text(line, margin, y);
                y += fontSize * 0.45;
            });
        }

        // ── Helper: render a markdown section body ───────────────────────────
        function renderSection(text) {
            let inCodeBlock = false;
            for (const rawLine of text.split('\n')) {
                const line = rawLine.trim();
                if (!line) { y += 2; continue; }
                if (line.startsWith('```')) { inCodeBlock = !inCodeBlock; continue; }

                if (inCodeBlock) {
                    checkPageBreak(5);
                    doc.setFont('courier', 'normal');
                    doc.setFontSize(8);
                    doc.setTextColor(30, 90, 190);
                    doc.splitTextToSize(line, contentW - 4).forEach(cl => {
                        checkPageBreak(4.5);
                        doc.text(cl, margin + 3, y);
                        y += 4.5;
                    });
                    doc.setFont('helvetica', 'normal');
                } else if (/^#{1,2}\s/.test(line)) {
                    y += 2;
                    checkPageBreak(10);
                    renderText(line.replace(/^#{1,2}\s+/, '').replace(/\*\*(.*?)\*\*/g, '$1'), 11, [0, 72, 200], true);
                    y += 1;
                } else if (/^#{3,6}\s/.test(line)) {
                    checkPageBreak(8);
                    renderText(line.replace(/^#{3,6}\s+/, '').replace(/\*\*(.*?)\*\*/g, '$1'), 10, [0, 55, 160], true);
                } else if (/^[-*+]\s/.test(line)) {
                    const content = line.replace(/^[-*+]\s+/, '').replace(/\*\*(.*?)\*\*/g, '$1').replace(/`(.*?)`/g, '$1');
                    checkPageBreak(5);
                    doc.setFillColor(0, 114, 255);
                    doc.circle(margin + 1.5, y - 1.5, 1, 'F');
                    doc.setFont('helvetica', 'normal');
                    doc.setFontSize(9);
                    doc.setTextColor(30, 30, 30);
                    doc.splitTextToSize(content, contentW - 6).forEach(bl => {
                        checkPageBreak(4.5);
                        doc.text(bl, margin + 5, y);
                        y += 4.5;
                    });
                } else if (/^\d+\.\s/.test(line)) {
                    renderText(line.replace(/\*\*(.*?)\*\*/g, '$1').replace(/`(.*?)`/g, '$1'), 9, [30, 30, 30]);
                } else {
                    renderText(line.replace(/\*\*(.*?)\*\*/g, '$1').replace(/`(.*?)`/g, '$1'), 9, [40, 40, 40]);
                }
            }
        }

        // ── Parse AI markdown into named sections ────────────────────────────
        function parseSections(markdown) {
            const map = {};
            const parts = markdown.split(/^(#{1,3}\s+.+)$/m);
            let cur = '__preamble__';
            map[cur] = '';
            for (const part of parts) {
                if (/^#{1,3}\s+/.test(part)) {
                    cur = part.replace(/^#{1,3}\s+/, '').trim();
                    map[cur] = '';
                } else {
                    map[cur] = (map[cur] || '') + part;
                }
            }
            return map;
        }

        function findSection(keyword) {
            const key = Object.keys(sections).find(k => k.toLowerCase().includes(keyword.toLowerCase()));
            return key ? sections[key].trim() : null;
        }

        const sections = parseSections(currentSummaryMarkdown);

        // ════════════════════════════════════════════════════════════════════
        // REPORT TITLE (top of page 1, no separate cover page)
        // ════════════════════════════════════════════════════════════════════
        doc.setFillColor(10, 20, 40);
        doc.roundedRect(margin, y, contentW, 22, 3, 3, 'F');
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(18);
        doc.setTextColor(255, 255, 255);
        doc.text('CodeMind AI — Repository Analysis Report', margin + 5, y + 10);
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(8);
        doc.setTextColor(150, 175, 220);
        doc.text(`Generated: ${new Date().toLocaleString()}`, margin + 5, y + 18);
        y += 28;

        // ════════════════════════════════════════════════════════════════════
        // SECTION 1 — 🏗️ ARCHITECTURE
        // ════════════════════════════════════════════════════════════════════
        const archText = findSection('Architecture') || findSection('arch');
        if (archText) {
            sectionHeader('🏗️  Architecture');
            renderSection(archText);
            y += 4;
        }

        // ════════════════════════════════════════════════════════════════════
        // SECTION 2 — 📊 ARCHITECTURE FLOWCHART
        // ════════════════════════════════════════════════════════════════════
        if (currentMermaidSVG) {
            sectionHeader('📊  Architecture Flowchart');
            try {
                const svgBlob = new Blob([currentMermaidSVG], { type: 'image/svg+xml;charset=utf-8' });
                const svgUrl  = URL.createObjectURL(svgBlob);
                const img = new Image();
                await new Promise((resolve, reject) => { img.onload = resolve; img.onerror = reject; img.src = svgUrl; });

                const canvas = document.createElement('canvas');
                const scale  = 2;
                canvas.width  = (img.naturalWidth  || 1200) * scale;
                canvas.height = (img.naturalHeight || 800)  * scale;
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.scale(scale, scale);
                ctx.drawImage(img, 0, 0);
                URL.revokeObjectURL(svgUrl);

                const imgData = canvas.toDataURL('image/png');
                const aspect  = canvas.height / canvas.width;
                const imgW    = contentW;
                const imgH    = Math.min(imgW * aspect, pageH - y - margin - footerH - 5);

                checkPageBreak(imgH + 5);
                doc.addImage(imgData, 'PNG', margin, y, imgW, imgH);
                y += imgH + 6;
            } catch (svgErr) {
                renderText('(Flowchart could not be embedded in PDF. Use the "Download Flowchart (SVG)" button above.)', 9, [160, 50, 50]);
                y += 4;
            }
        }

        // ════════════════════════════════════════════════════════════════════
        // SECTION 3 — 🛠️ TOOLS & FRAMEWORKS
        // ════════════════════════════════════════════════════════════════════
        const toolsText = findSection('Tools') || findSection('Framework') || findSection('Librar');
        if (toolsText) {
            sectionHeader('🛠️  Tools & Frameworks');
            renderSection(toolsText);
            y += 4;
        }

        // ════════════════════════════════════════════════════════════════════
        // SECTION 4 — ⚙️ HOW IT WORKS
        // ════════════════════════════════════════════════════════════════════
        const howText = findSection('How it Works') || findSection('How It Works') || findSection('Workflow') || findSection('Functionality');
        if (howText) {
            sectionHeader('⚙️  How it Works');
            renderSection(howText);
            y += 4;
        }

        // ── Footer on every page ─────────────────────────────────────────────
        const totalPages = doc.internal.getNumberOfPages();
        for (let i = 1; i <= totalPages; i++) {
            doc.setPage(i);
            doc.setFillColor(0, 72, 200);
            doc.rect(0, pageH - footerH, pageW, footerH, 'F');
            doc.setFont('helvetica', 'normal');
            doc.setFontSize(7.5);
            doc.setTextColor(180, 200, 255);
            doc.text('CodeMind AI — Repository Analysis Report', margin, pageH - 2.8);
            doc.text(`Page ${i} of ${totalPages}`, pageW - margin, pageH - 2.8, { align: 'right' });
        }

        doc.save('CodeMind_AI_Report.pdf');


    } catch (err) {
        console.error('PDF generation failed:', err);
        alert('PDF generation failed. Please try again.');
    } finally {
        btnText.textContent = '📥 Download Full Report (PDF)';
        spinner.classList.add('hidden');
        btn.disabled = false;
        }
    });
}); // end window load


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


