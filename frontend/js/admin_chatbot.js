document.addEventListener('DOMContentLoaded', async () => {
    // 1. Authenticate (bypassed in api.js currently)
    const currentUser = await requireAuth();
    if(!currentUser) return;
    
    // 2. Fetch and populate settings
    await loadSettings();
    
    // 3. Fetch related data for KPI cards
    await loadKPIData();
    
    // 4. UI Event Listeners
    setupEventListeners();
});

async function loadSettings() {
    try {
        const res = await apiFetch('/chatbot/settings');
        const data = await res.json();
        
        if (data.success && data.data) {
            populateUI(data.data);
        }
    } catch (e) {
        console.error("Failed to load settings:", e);
    }
}

function populateUI(settings) {
    // Model Configuration
    document.getElementById('set-provider').value = settings.provider;
    document.getElementById('set-model').value = settings.model_name;
    document.getElementById('set-temperature').value = parseFloat(settings.temperature) * 100;
    document.getElementById('temp-val').textContent = settings.temperature;
    document.getElementById('set-max-tokens').value = settings.max_tokens;
    
    // Language Support
    document.getElementById('set-default-lang').value = settings.default_language;
    document.getElementById('chk-eng').checked = settings.support_english;
    document.getElementById('chk-hin').checked = settings.support_hindi;
    document.getElementById('chk-hing').checked = settings.support_hinglish;
    
    // Content & Safety Filters
    document.getElementById('tgl-filter').checked = settings.filter_inappropriate;
    document.getElementById('tgl-edu').checked = settings.only_educational;
    document.getElementById('set-blocked').value = settings.blocked_keywords;
    
    // Response Behavior
    document.getElementById('set-style').value = settings.response_style;
    document.getElementById('set-tone').value = settings.tone;
    document.getElementById('tgl-source').checked = settings.include_source_links;
    document.getElementById('tgl-related').checked = settings.show_related_info;
    document.getElementById('tgl-tables').checked = settings.use_tables;
    
    // Knowledge & Retrieval Settings
    document.getElementById('tgl-pdf').checked = settings.search_pdfs;
    document.getElementById('tgl-keyword').checked = settings.keyword_matching;
    document.getElementById('tgl-rag').checked = settings.use_rag;
    document.getElementById('set-chunks').value = settings.max_chunks;
    document.getElementById('tgl-rerank').checked = settings.rerank_results;
    
    // Advanced Settings
    document.getElementById('tgl-memory').checked = settings.session_memory;
    document.getElementById('set-max-hist').value = settings.max_history;
    document.getElementById('set-fallback').value = settings.fallback_response;
    
    // Update KPI Model card
    document.getElementById('kpi-model').textContent = settings.model_name;
    
    // Update KPI Languages card
    let langs = 1; // English is default
    if(settings.support_hindi) langs++;
    if(settings.support_hinglish) langs++;
    document.getElementById('kpi-langs').textContent = langs + " Languages";
}

async function loadKPIData() {
    try {
        const res = await apiFetch('/documents');
        const data = await res.json();
        if (data.success) {
            document.getElementById('kpi-docs').textContent = data.data.length + " Documents";
        }
    } catch (e) {
        document.getElementById('kpi-docs').textContent = "0 Documents";
    }
}

function getSettingsFromUI() {
    return {
        provider: document.getElementById('set-provider').value,
        model_name: document.getElementById('set-model').value,
        temperature: (parseInt(document.getElementById('set-temperature').value) / 100).toFixed(1).toString(),
        max_tokens: parseInt(document.getElementById('set-max-tokens').value),
        
        default_language: document.getElementById('set-default-lang').value,
        support_english: document.getElementById('chk-eng').checked,
        support_hindi: document.getElementById('chk-hin').checked,
        support_hinglish: document.getElementById('chk-hing').checked,
        
        filter_inappropriate: document.getElementById('tgl-filter').checked,
        only_educational: document.getElementById('tgl-edu').checked,
        blocked_keywords: document.getElementById('set-blocked').value,
        
        response_style: document.getElementById('set-style').value,
        tone: document.getElementById('set-tone').value,
        include_source_links: document.getElementById('tgl-source').checked,
        show_related_info: document.getElementById('tgl-related').checked,
        use_tables: document.getElementById('tgl-tables').checked,
        
        search_pdfs: document.getElementById('tgl-pdf').checked,
        keyword_matching: document.getElementById('tgl-keyword').checked,
        use_rag: document.getElementById('tgl-rag').checked,
        max_chunks: parseInt(document.getElementById('set-chunks').value),
        rerank_results: document.getElementById('tgl-rerank').checked,
        
        session_memory: document.getElementById('tgl-memory').checked,
        max_history: parseInt(document.getElementById('set-max-hist').value),
        fallback_response: document.getElementById('set-fallback').value
    };
}

async function saveSettings() {
    const btn = document.getElementById('save-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = `<i data-lucide="loader" class="animate-spin" style="width:16px; height:16px;"></i> Saving...`;
    if(window.lucide) lucide.createIcons();
    
    const settings = getSettingsFromUI();
    
    try {
        const res = await apiFetch('/chatbot/settings', {
            method: 'PUT',
            body: JSON.stringify(settings)
        });
        
        const data = await res.json();
        if (data.success) {
            btn.innerHTML = `<i data-lucide="check" style="width:16px; height:16px;"></i> Saved!`;
            if(window.lucide) lucide.createIcons();
            
            // Re-populate UI to update KPIs
            populateUI(data.data);
            
            setTimeout(() => {
                btn.innerHTML = originalText;
                if(window.lucide) lucide.createIcons();
            }, 2000);
            
            // Update time
            const now = new Date();
            const timeStr = now.toLocaleDateString('en-US', {day:'numeric', month:'short', year:'numeric'}) + ', ' + 
                            now.toLocaleTimeString('en-US', {hour:'2-digit', minute:'2-digit'});
            document.getElementById('last-updated-time').textContent = timeStr;
        }
    } catch (e) {
        console.error("Failed to save settings:", e);
        alert("Failed to save settings.");
        btn.innerHTML = originalText;
        if(window.lucide) lucide.createIcons();
    }
}

async function sendTestMessage() {
    const input = document.getElementById('test-chat-input');
    const msg = input.value.trim();
    if (!msg) return;
    
    input.value = '';
    const chatBox = document.getElementById('test-chat-box');
    
    // Remove placeholder if it exists
    if (chatBox.innerHTML.includes("Test the live RAG model here")) {
        chatBox.innerHTML = '';
    }
    
    // Append User Message
    const timeStr = new Date().toLocaleTimeString('en-US', {hour:'2-digit', minute:'2-digit'});
    chatBox.insertAdjacentHTML('beforeend', `
        <div style="display: flex; justify-content: flex-end; gap: 10px;">
            <div style="background: rgba(37, 99, 235, 0.2); padding: 10px 14px; border-radius: 12px 12px 0 12px; font-size: 0.75rem; color: #e5e7eb; max-width: 80%;">
                ${msg}
                <div style="text-align: right; font-size: 0.6rem; color: #9ca3af; margin-top: 4px;">${timeStr}</div>
            </div>
            <div style="width: 28px; height: 28px; border-radius: 50%; background: #2563eb; display: flex; align-items: center; justify-content: center;"><i data-lucide="user" style="width:14px; height:14px; color:#fff;"></i></div>
        </div>
    `);
    if(window.lucide) lucide.createIcons();
    chatBox.scrollTop = chatBox.scrollHeight;
    
    // Show Loading
    const loadingId = 'loading-' + Date.now();
    chatBox.insertAdjacentHTML('beforeend', `
        <div id="${loadingId}" style="display: flex; gap: 10px;">
            <div style="width: 28px; height: 28px; border-radius: 50%; background: #00D261; display: flex; align-items: center; justify-content: center; flex-shrink: 0;"><i data-lucide="bot" style="width:14px; height:14px; color:#000;"></i></div>
            <div style="background: rgba(255, 255, 255, 0.05); padding: 14px; border-radius: 0 12px 12px 12px; font-size: 0.75rem; color: #9ca3af;">
                <i data-lucide="loader" class="animate-spin" style="width:14px; height:14px;"></i> Thinking...
            </div>
        </div>
    `);
    if(window.lucide) lucide.createIcons();
    chatBox.scrollTop = chatBox.scrollHeight;
    
    try {
        const res = await apiFetch('/chat', {
            method: 'POST',
            body: JSON.stringify({ message: msg })
        });
        const data = await res.json();
        
        document.getElementById(loadingId).remove();
        
        let answerText = "Error getting response.";
        if (data.success && data.data) {
            answerText = data.data.answer.replace(/\n/g, '<br>');
        }
        
        chatBox.insertAdjacentHTML('beforeend', `
            <div style="display: flex; gap: 10px;">
                <div style="width: 28px; height: 28px; border-radius: 50%; background: #00D261; display: flex; align-items: center; justify-content: center; flex-shrink: 0;"><i data-lucide="bot" style="width:14px; height:14px; color:#000;"></i></div>
                <div style="background: rgba(255, 255, 255, 0.05); padding: 14px; border-radius: 0 12px 12px 12px; font-size: 0.75rem; color: #e5e7eb; max-width: 90%; line-height: 1.5;">
                    ${answerText}
                    <div style="text-align: right; font-size: 0.6rem; color: #9ca3af; margin-top: 8px;">${timeStr}</div>
                </div>
            </div>
        `);
        if(window.lucide) lucide.createIcons();
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (e) {
        console.error(e);
        document.getElementById(loadingId).innerHTML = `<div style="color: #ef4444; font-size: 0.75rem;">Failed to get response. Is the backend running?</div>`;
    }
}

function setupEventListeners() {
    // Temperature slider update
    const tempSlider = document.getElementById('set-temperature');
    if (tempSlider) {
        tempSlider.addEventListener('input', (e) => {
            const val = (parseInt(e.target.value) / 100).toFixed(1);
            document.getElementById('temp-val').textContent = val;
        });
    }
    
    // Save button
    const saveBtn = document.getElementById('save-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveSettings);
    }
    
    // Test Chatbot Enter key
    const chatInput = document.getElementById('test-chat-input');
    if(chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendTestMessage();
            }
        });
    }
    
    // Test Chatbot Send button
    const chatBtn = document.getElementById('test-chat-send');
    if(chatBtn) {
        chatBtn.addEventListener('click', sendTestMessage);
    }
}
