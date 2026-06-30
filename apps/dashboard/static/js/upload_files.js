const fileUpload = document.getElementById('file-upload');
const fileNameLabel = document.getElementById('file-name-label');
const fileListContainer = document.getElementById('file-list-container'); // 📍 New Reference
const embedBtn = document.getElementById('embed-btn');
const clearBtn = document.getElementById('clear-btn');
const statusPanel = document.getElementById('status-panel');
const statusBox = document.getElementById('status-box');
const statusSpinner = document.getElementById('status-spinner');
const statusText = document.getElementById('status-text');

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

let selectedFiles = [];

fileUpload.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        // Append newly selected files natively into our tracking matrix
        const incomingFiles = Array.from(e.target.files);
        selectedFiles = [...selectedFiles, ...incomingFiles];

        renderFileList();
        updateButtonState();
    }
});

// 📍 New Function: Loops through and builds custom UI elements for every file
function renderFileList() {
    fileListContainer.innerHTML = '';

    if (selectedFiles.length === 0) {
        fileNameLabel.innerText = "Click to upload files";
        fileNameLabel.classList.remove('text-emerald-400');
        return;
    }

    // Change dropzone headline summary statement
    fileNameLabel.innerText = `${selectedFiles.length} file(s) ready for ingestion`;
    fileNameLabel.classList.add('text-emerald-400');

    selectedFiles.forEach((file, index) => {
        const fileRow = document.createElement('div');
        fileRow.className = "flex items-center justify-between bg-slate-950/60 border border-slate-800/80 p-3 rounded-xl text-sm transition-all hover:border-slate-700";

        // Detect correct file icons dynamically based on extension types
        let iconName = "description";
        let iconColor = "text-slate-400";
        if (file.name.endsWith('.pdf')) {
            iconName = "picture_as_pdf";
            iconColor = "text-red-400";
        } else if (file.name.endsWith('.md')) {
            iconName = "article";
            iconColor = "text-sky-400";
        }

        fileRow.innerHTML = `
            <div class="flex items-center gap-3 min-w-0">
                <span class="material-icons ${iconColor} shrink-0">${iconName}</span>
                <span class="text-slate-200 font-medium truncate max-w-[220px] sm:max-w-xs">${file.name}</span>
                <span class="text-xs text-slate-500 shrink-0">(${(file.size / 1024 / 1024).toFixed(2)} MB)</span>
            </div>
            <button type="button" onclick="removeFile(${index})" class="text-slate-500 hover:text-red-400 p-1 rounded-lg hover:bg-slate-900 transition-colors flex items-center justify-center">
                <span class="material-icons text-base">close</span>
            </button>
        `;
        fileListContainer.appendChild(fileRow);
    });
}

// 📍 New Function: Wipes item out of list array matrix safely
window.removeFile = function(indexToRemove) {
    selectedFiles = selectedFiles.filter((_, idx) => idx !== indexToRemove);
    renderFileList();
    updateButtonState();

    if (selectedFiles.length === 0) {
        fileUpload.value = '';
    }
};

// 📍 New Function: Keeps your layout states in sync cleanly
function updateButtonState() {
    if (selectedFiles.length > 0) {
        embedBtn.disabled = false;
        embedBtn.className = "px-5 py-2 text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl flex items-center gap-2 active:scale-95 transition-all shadow-lg shadow-emerald-950/20";
    } else {
        embedBtn.disabled = true;
        embedBtn.className = "px-5 py-2 text-sm font-semibold bg-slate-800 text-slate-500 rounded-xl flex items-center gap-2 cursor-not-allowed transition-all";
    }
}

clearBtn.addEventListener('click', resetForm);

function resetForm() {
    fileUpload.value = '';
    selectedFiles = [];
    fileListContainer.innerHTML = ''; // Clear individual documents out
    updateButtonState();
    statusPanel.classList.add('hidden');
}

embedBtn.addEventListener('click', async () => {
    if (selectedFiles.length === 0) return;

    statusPanel.classList.remove('hidden');
    statusSpinner.classList.remove('hidden');
    statusBox.className = "flex items-center gap-3 bg-slate-850 p-3 rounded-lg border border-slate-800 text-slate-300 text-sm";
    statusText.innerText = `Extracting raw data stream from ${selectedFiles.length} file(s)...`;

    const formData = new FormData();
    selectedFiles.forEach(file => {
        formData.append('documents', file);
    });

    try {
        const response = await fetch('api/embed/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        });

        const res = await response.json();

        if (res.success) {
            statusSpinner.classList.add('hidden');
            statusBox.className = "flex items-center gap-3 bg-emerald-950/30 border border-emerald-900/50 text-emerald-300 p-3 rounded-lg text-sm";
            statusBox.innerHTML = `<span class="material-icons text-sm text-emerald-400">check_circle</span> Successfully vectorized and compiled ${res.chunks_count} chunks into Qdrant index.`;
        } else {
            throw new Error(res.error || "Ingestion cycle failure");
        }

    } catch (err) {
        statusSpinner.classList.add('hidden');
        statusBox.className = "flex items-center gap-3 bg-red-950/30 border border-red-900/50 text-red-300 p-3 rounded-lg text-sm";
        statusBox.innerHTML = `<span class="material-icons text-sm text-red-400">error</span> Process Failed: ${err.message}`;
    }
});