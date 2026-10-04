let docsData = [];
let currentUser = null;
let selectedFile = null;

document.addEventListener('DOMContentLoaded', async () => {
    currentUser = await requireAuth();
    if(!currentUser) return;

    const nameSplit = currentUser.name.split(' ');
    document.getElementById('nav-avatar').textContent = nameSplit[0][0] + (nameSplit[1] ? nameSplit[1][0] : '');
    document.getElementById('nav-name').textContent = currentUser.name;
    document.getElementById('nav-role').textContent = 'Super Admin';

    // Drag and Drop Logic
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    
    fileInput.addEventListener('change', handleFileSelect);
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#00D261';
        dropZone.style.background = 'rgba(0, 210, 97, 0.05)';
    });
    
    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'rgba(255,255,255,0.2)';
        dropZone.style.background = 'rgba(255,255,255,0.01)';
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'rgba(255,255,255,0.2)';
        dropZone.style.background = 'rgba(255,255,255,0.01)';
        
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            handleFileSelect();
        }
    });

    document.getElementById('select-all-cb').addEventListener('change', function(e) {
        const cbs = document.querySelectorAll('.row-cb');
        cbs.forEach(cb => cb.checked = e.target.checked);
    });

    await fetchDocuments();
    
    // Refresh interval for processing docs
    setInterval(() => {
        if (docsData.some(d => d.status !== 'READY' && d.status !== 'FAILED')) {
            fetchDocuments(false);
        }
    }, 5000);
});

function handleFileSelect() {
    const fileInput = document.getElementById('file-input');
    if (fileInput.files && fileInput.files[0]) {
        selectedFile = fileInput.files[0];
        if(!selectedFile.name.toLowerCase().endsWith('.pdf')) {
            alert("Only PDF files are allowed.");
            clearFile();
            return;
        }
        document.getElementById('sel-file-name').textContent = selectedFile.name;
        document.getElementById('drop-zone').style.display = 'none';
        document.getElementById('selected-file-info').style.display = 'block';
    }
}

function clearFile() {
    selectedFile = null;
    document.getElementById('file-input').value = '';
    document.getElementById('drop-zone').style.display = 'block';
    document.getElementById('selected-file-info').style.display = 'none';
}

async function uploadFile() {
    if(!selectedFile) return;
    
    const cat = document.getElementById('sel-file-cat').value;
    const sem = document.getElementById('sel-file-sem').value;
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('title', selectedFile.name.replace('.pdf', ''));
    if(cat) formData.append('category', cat);
    if(sem) formData.append('semester', sem);
    
    try {
        const res = await apiFetch('/documents', {
            method: 'POST',
            body: formData,
            headers: {} // let browser set content-type for multipart
        });
        const data = await res.json();
        if(data.success) {
            clearFile();
            await fetchDocuments();
        } else {
            alert(data.message || "Upload failed");
        }
    } catch (e) {
        console.error(e);
        alert("Upload error.");
    }
}

async function fetchDocuments(showLoading = true) {
    try {
        const res = await apiFetch('/documents');
        const data = await res.json();
        if(data.success) {
            docsData = data.data;
            renderKPIs();
            renderQueue();
            filterTable();
        }
    } catch (e) {
        console.error(e);
    }
}

function renderKPIs() {
    const total = docsData.length;
    const ready = docsData.filter(d => d.status === 'READY').length;
    const failed = docsData.filter(d => d.status === 'FAILED').length;
    const processing = total - ready - failed;
    
    let totalBytes = docsData.reduce((acc, d) => acc + (d.file_size || 0), 0);
    let sizeStr = "0 MB";
    if(totalBytes > 1024*1024*1024) {
        sizeStr = (totalBytes / (1024*1024*1024)).toFixed(1) + " GB";
    } else {
        sizeStr = (totalBytes / (1024*1024)).toFixed(1) + " MB";
    }
    
    document.getElementById('kb-active-count').textContent = ready;
    document.getElementById('kpi-total').textContent = total;
    document.getElementById('kpi-processed').textContent = ready;
    document.getElementById('kpi-processing').textContent = processing;
    document.getElementById('kpi-failed').textContent = failed;
    document.getElementById('kpi-size').textContent = sizeStr;
}

function renderQueue() {
    const qContainer = document.getElementById('processing-queue-container');
    const processingDocs = docsData.filter(d => d.status !== 'READY' && d.status !== 'FAILED').slice(0,3);
    
    if(processingDocs.length === 0) {
        qContainer.innerHTML = `<div style="color:#9ca3af; font-size:0.8rem; text-align:center; margin-top:30px;">No documents in queue</div>`;
        return;
    }
    
    qContainer.innerHTML = processingDocs.map(d => {
        // mock progress percent based on status or ID
        let pct = 30;
        if(d.status === 'EXTRACTING') pct = 45;
        if(d.status === 'CHUNKING') pct = 75;
        
        return `
        <div class="queue-item">
            <div class="queue-file-icon"><i data-lucide="file-text" style="width:16px; height:16px;"></i></div>
            <div class="queue-details">
                <div class="queue-name" title="${d.title}">${d.title}.pdf</div>
                <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-size:0.75rem;">
                    <div style="background:rgba(255,255,255,0.1); width:70%; height:4px; border-radius:2px; margin-top:6px;">
                        <div style="width:${pct}%; height:100%; background:#00D261; border-radius:2px;"></div>
                    </div>
                    <div style="color:#9ca3af;">${pct}%</div>
                </div>
            </div>
            <div class="queue-status">Processing</div>
        </div>
        `;
    }).join('');
    
    if(window.lucide) lucide.createIcons();
}

function filterTable() {
    const query = document.getElementById('search-input').value.toLowerCase();
    const cat = document.getElementById('filter-category').value;
    const stat = document.getElementById('filter-status').value;
    const sem = document.getElementById('filter-semester').value;
    
    let filtered = docsData.filter(d => {
        const mq = d.title.toLowerCase().includes(query);
        const mc = cat === 'all' || d.category === cat;
        let ms = true;
        if (stat === 'READY') ms = d.status === 'READY';
        else if (stat === 'FAILED') ms = d.status === 'FAILED';
        else if (stat === 'PROCESSING') ms = d.status !== 'READY' && d.status !== 'FAILED';
        const msem = sem === 'all' || d.semester === sem;
        return mq && mc && ms && msem;
    });
    
    renderTable(filtered);
}

const colorMap = {
    'Syllabus': 'background:rgba(59, 130, 246, 0.2); color:#60a5fa;',
    'Study Material': 'background:rgba(16, 185, 129, 0.2); color:#34d399;',
    'Notes': 'background:rgba(139, 92, 246, 0.2); color:#a78bfa;',
    'Question Paper': 'background:rgba(20, 184, 166, 0.2); color:#2dd4bf;',
    'Lab Manual': 'background:rgba(236, 72, 153, 0.2); color:#f472b6;',
    'Guidelines': 'background:rgba(59, 130, 246, 0.2); color:#60a5fa;',
    'Academic': 'background:rgba(245, 158, 11, 0.2); color:#fbbf24;',
    'Admission': 'background:rgba(139, 92, 246, 0.2); color:#a78bfa;',
    'Facilities': 'background:rgba(16, 185, 129, 0.2); color:#34d399;'
};

function renderTable(data) {
    const tbody = document.getElementById('documents-table-body');
    if(data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding:20px; color:#9ca3af;">No documents found</td></tr>`;
        document.getElementById('pag-end').textContent = 0;
        document.getElementById('pag-total').textContent = docsData.length;
        return;
    }
    
    document.getElementById('pag-end').textContent = data.length;
    document.getElementById('pag-total').textContent = docsData.length;
    
    tbody.innerHTML = data.map((d, i) => {
        const catBadge = d.category ? `<span style="${colorMap[d.category] || colorMap['Notes']} padding:2px 8px; border-radius:12px; font-size:0.7rem; font-weight:600;">${d.category}</span>` : '-';
        const sizeMb = (d.file_size / (1024*1024)).toFixed(1) + ' MB';
        
        let statColor = '';
        let statLabel = d.status;
        if(d.status === 'READY') { statColor = 'color:#10b981;'; statLabel = 'Processed'; }
        else if(d.status === 'FAILED') { statColor = 'color:#ef4444;'; }
        else { statColor = 'color:#f59e0b;'; statLabel = 'Processing'; }
        
        const statHtml = `<div style="display:flex; align-items:center; gap:6px; ${statColor} font-size:0.75rem;"><div style="width:6px; height:6px; border-radius:50%; background:currentColor;"></div> ${statLabel}</div>`;
        
        const pubDate = d.created_at ? new Date(d.created_at + 'Z').toLocaleString('en-US', {day:'numeric', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit'}) : '-';
        
        return `
            <tr>
                <td><input type="checkbox" class="row-cb" value="${d.id}" style="accent-color: #00D261;"></td>
                <td style="color: #9ca3af;">${i+1}</td>
                <td>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <i data-lucide="file-text" style="color:#ef4444; width:16px; height:16px;"></i>
                        <span style="color: #fff; font-weight: 500;">${d.title}.pdf</span>
                    </div>
                </td>
                <td>${catBadge}</td>
                <td style="color: #9ca3af; font-size: 0.8rem;">${d.semester || 'All'}</td>
                <td style="color: #9ca3af; font-size: 0.8rem;">${sizeMb}</td>
                <td>${statHtml}</td>
                <td style="color: #9ca3af; font-size: 0.8rem;">${pubDate}</td>
                <td style="text-align: right;">
                    <div style="display:flex; justify-content:flex-end; gap:4px;">
                        <button class="action-btn-icon" title="View"><i data-lucide="eye" style="width:14px; height:14px; color:#9ca3af;"></i></button>
                        <button class="action-btn-icon" title="Edit"><i data-lucide="edit-2" style="width:14px; height:14px; color:#9ca3af;"></i></button>
                        <button class="action-btn-icon" title="Download"><i data-lucide="download" style="width:14px; height:14px; color:#9ca3af;"></i></button>
                        <button class="action-btn-icon delete" title="Delete" onclick="deleteDoc('${d.id}')"><i data-lucide="trash-2" style="width:14px; height:14px; color:#ef4444;"></i></button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
    
    if(window.lucide) lucide.createIcons();
}

async function deleteDoc(id) {
    if(!confirm("Are you sure you want to delete this document? It will be removed from the knowledge base.")) return;
    try {
        const res = await apiFetch('/documents/' + id, { method: 'DELETE' });
        if(res.ok) await fetchDocuments();
    } catch(e) {
        console.error(e);
    }
}

async function deleteSelected() {
    const checked = document.querySelectorAll('.row-cb:checked');
    if(checked.length === 0) return;
    if(!confirm(`Are you sure you want to delete ${checked.length} selected document(s)?`)) return;
    
    for(let cb of checked) {
        try {
            await apiFetch('/documents/' + cb.value, { method: 'DELETE' });
        } catch(e) {
            console.error(e);
        }
    }
    document.getElementById('select-all-cb').checked = false;
    await fetchDocuments();
}
