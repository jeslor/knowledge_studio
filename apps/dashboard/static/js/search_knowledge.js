const queryInput = document.getElementById('query-input');
const sendBtn = document.getElementById('send-btn');
const chatContainer = document.getElementById('chat-container');
const emptyState = document.getElementById('empty-state');
const historyContainer = document.getElementById('history-container');

// Handle Send actions
sendBtn.addEventListener('click', executePipeline);
queryInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        executePipeline();
    }
});

// Helper to safely extract CSRF token from Django's runtime cookies
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

async function executePipeline() {
    if (queryInput && queryInput.value.trim() === '') return;
    const query = queryInput.value.trim();
    if (!query) return;
    queryInput.value = '';

    if (emptyState) emptyState.remove();

    // 1. Add Query to Sidebar History
    const histItem = document.createElement('div');
    histItem.className = "w-full flex items-center gap-2 p-2 hover:bg-slate-800 rounded-lg cursor-pointer transition-colors group";
    histItem.innerHTML = `<span class="material-icons text-sm text-slate-500 group-hover:text-slate-300">chat_bubble_outline</span>
                          <span class="text-sm text-slate-400 group-hover:text-slate-200 truncate">${query.length > 22 ? query.substring(0,22)+'...' : query}</span>`;
    historyContainer.appendChild(histItem);

    // 2. Insert User Query Card in Chat Window
    const userCard = document.createElement('div');
    userCard.className = "w-full bg-slate-800 border border-slate-700/50 p-4 rounded-xl shadow-md";
    userCard.innerHTML = `<div class="flex items-center gap-2 text-slate-400 text-xs font-semibold uppercase mb-1"><span class="material-icons text-xs">person</span>You</div>
                          <div class="text-base text-slate-100">${query}</div>`;
    chatContainer.appendChild(userCard);

    // 3. Insert Empty AI Status Block Card
    const aiCard = document.createElement('div');
    aiCard.className = "w-full bg-slate-900 border border-slate-800 p-5 rounded-xl shadow-lg";
    aiCard.innerHTML = `
        <div class="flex items-center gap-2 text-emerald-400 text-xs font-semibold uppercase mb-3"><span class="material-icons text-xs">smart_toy</span>Assistant</div>
        <div id="status-box" class="flex items-center gap-3 bg-slate-850 p-3 rounded-lg border border-slate-800 w-full text-slate-300 text-sm transition-all duration-300">
            <div id="status-spinner" class="animate-spin rounded-full h-4 w-4 border-2 border-emerald-500 border-t-transparent"></div>
            <span id="status-text">Analyzing and processing query...</span>
        </div>
        <div id="ai-response-content" class="text-slate-200 leading-relaxed w-full mt-4 border-t border-slate-800 pt-4 hidden"></div>`;
    chatContainer.appendChild(aiCard);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    const statusBox = aiCard.querySelector('#status-box');
    const statusText = aiCard.querySelector('#status-text');
    const statusSpinner = aiCard.querySelector('#status-spinner');
    const responseContent = aiCard.querySelector('#ai-response-content');

    try {
        // 📍 Dynamic Fix: Explicitly use window.fetch to ensure we use the native browser tool
        const response = await window.fetch("/api/rag/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ query: query })
        });

        if (!response.ok) {
            throw new Error(`Server returned status code ${response.status}`);
        }

        // Set up the stream reader safely
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n\n");
            buffer = lines.pop();

            for (const line of lines) {
                if (!line.startsWith("data: ")) continue;

                const eventData = JSON.parse(line.replace("data: ", ""));

                if (eventData.step === 'error') {
                    throw new Error(eventData.msg);
                }

                if (eventData.step === 'complete') {
                    statusSpinner.classList.add('hidden');
                    statusBox.className = "flex items-center gap-3 bg-emerald-950/30 border border-emerald-900/50 text-emerald-300 p-3 rounded-lg text-sm";
                    statusBox.innerHTML = `<span class="material-icons text-sm text-emerald-400">check_circle</span> Pipeline completed successfully`;

                    responseContent.classList.remove('hidden');
                    responseContent.innerText = eventData.answer;
                } else {
                    statusText.innerText = eventData.msg;
                }
            }
        }

    } catch (err) {
        if (statusSpinner) statusSpinner.classList.add('hidden');
        statusBox.className = "flex items-center gap-3 bg-red-950/30 border border-red-900/50 text-red-300 p-3 rounded-lg text-sm";
        statusBox.innerHTML = `<span class="material-icons text-sm text-red-400">error</span> Pipeline failure: ${err.message}`;
    }

    chatContainer.scrollTop = chatContainer.scrollHeight;
}