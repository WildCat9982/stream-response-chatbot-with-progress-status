from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
import asyncio
import json
import random

app = FastAPI()

DEMO_HTML = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chat Stream Demo</title>
<style>
  :root {
    color-scheme: light;
    --bg-1: #cabdf4;
    --bg-2: #ddd5f9;
    --card: #ffffff;
    --border: #e6e6f0;
    --text: #1f2233;
    --muted: #6b7086;
    --accent-1: #6d5efc;
    --accent-2: #8b7bff;
    --header-1: #4739c4;
    --header-2: #5f4fca;
    --bubble-user: #6d5efc;
    --bubble-user-text: #ffffff;
    --bubble-assistant: #3f3f46;
    --shadow: 0 20px 45px -20px rgba(45, 40, 90, 0.35);
  }

  * { box-sizing: border-box; }

  body {
    font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
    margin: 0;
    min-height: 100vh;
    background: radial-gradient(circle at top left, var(--bg-1), var(--bg-2));
    color: var(--text);
  }

  .app {
    position: fixed;
    bottom: 4px;
    right: 4px;
    width: 360px;
    max-width: calc(100vw - 8px);
    height: 90vh;
    max-height: calc(100vh - 8px);
    display: flex;
    flex-direction: column;
    background: #e5e5ea;
    border-radius: 8px;
    box-shadow: var(--shadow);
    overflow: hidden;
    border: 1px solid var(--border);
    z-index: 1000;
    transition: width 0.2s ease, height 0.2s ease, border-radius 0.2s ease;
  }

  .resize-handle {
    flex: none;
    height: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: ns-resize;
    touch-action: none;
  }

  .resize-handle::before {
    content: "";
    width: 36px;
    height: 4px;
    border-radius: 999px;
    background: #9a9aa2;
    transition: background 0.15s ease;
  }

  .resize-handle:hover::before {
    background: var(--accent-2);
  }

  .app.minimized .resize-handle {
    display: none;
  }

  .app-header {
    flex: none;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    padding: 6px 16px;
    background: linear-gradient(120deg, var(--header-1), var(--header-2));
    color: #fff;
  }

  .minimize-btn {
    flex: none;
    align-self: center;
    margin: 0;
    width: 30px;
    height: 30px;
    border-radius: 6px;
    border: 1px solid transparent;
    background: transparent;
    color: #fff;
    font-size: 0.7rem;
    line-height: 1;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: border-color 0.15s ease, background 0.15s ease;
  }

  .minimize-btn:hover {
    border-color: rgba(255, 255, 255, 0.6);
  }

  .minimize-btn::before {
    content: "";
    width: 16px;
    height: 2px;
    border-radius: 999px;
    background: #fff;
  }

  .robot-icon {
    display: none;
    font-size: 2.6rem;
  }

  .app.minimized {
    position: fixed;
    bottom: 4px;
    right: 4px;
    width: 84px;
    height: 84px;
    border-radius: 50%;
    cursor: pointer;
    z-index: 1000;
    transition: width 0.2s ease, height 0.2s ease, border-radius 0.2s ease,
      transform 0.2s ease, box-shadow 0.2s ease;
  }

  .app.minimized:hover {
    transform: scale(1.08);
    box-shadow: 0 20px 45px -10px rgba(109, 94, 252, 0.6);
  }

  .app.minimized:hover .robot-icon {
    animation: bob 0.6s ease-in-out infinite;
  }

  .app.minimized .app-header-text,
  .app.minimized #chat,
  .app.minimized form,
  .app.minimized .minimize-btn {
    display: none;
  }

  .app.minimized .app-header {
    width: 100%;
    height: 100%;
    padding: 0;
    align-items: center;
    justify-content: center;
  }

  .app.minimized .robot-icon {
    display: block;
  }

  .app-header h1 {
    margin: 0;
    font-size: 0.92rem;
    font-weight: 400;
    letter-spacing: 0.3px;
  }

  .app-header p {
    margin: 0;
    font-size: 0.72rem;
    font-weight: 300;
    opacity: 0.8;
  }

  #chat {
    flex: 1;
    min-height: 0;
    padding: 20px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 14px;
    scroll-behavior: smooth;
    background-color: #efeafd;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='90' height='90'%3E%3Cg fill='none' stroke='%235b4ce4' stroke-width='1.5' opacity='0.12'%3E%3Cpath d='M14 16h24a5 5 0 0 1 5 5v11a5 5 0 0 1-5 5H24l-7 7v-7h-3a5 5 0 0 1-5-5V21a5 5 0 0 1 5-5z'/%3E%3Ccircle cx='66' cy='58' r='6'/%3E%3Cpath d='M55 72l5-5M65 72l-5-5' stroke-linecap='round'/%3E%3Ccircle cx='20' cy='72' r='2.5' fill='%235b4ce4' stroke='none'/%3E%3C/g%3E%3C/svg%3E");
    background-repeat: repeat;
    background-size: 90px 90px;
  }

  .row { display: flex; }
  .row.user { justify-content: flex-end; }
  .row.assistant { justify-content: flex-start; }

  .bubble {
    max-width: 82%;
    padding: 5px 8px;
    border-radius: 10px;
    font-size: 0.92rem;
    line-height: 1.5;
    animation: rise 0.25s ease;
  }

  .msg-time {
    display: inline-block;
    margin-left: 6px;
    font-size: 0.65rem;
    opacity: 0.7;
    vertical-align: bottom;
  }

  .row.user .bubble {
    background: var(--bubble-user);
    color: var(--bubble-user-text);
    border-bottom-right-radius: 2px;
  }

  .row.assistant .bubble {
    background: var(--bubble-assistant);
    color: var(--bubble-user-text);
    border-bottom-left-radius: 2px;
    width: 100%;
  }

  .row.assistant .group-header {
    background: rgba(255, 255, 255, 0.16);
    border-color: rgba(255, 255, 255, 0.35);
  }

  .row.assistant .group-header:hover {
    background: rgba(255, 255, 255, 0.26);
  }

  .row.assistant .group-latest {
    color: #ffd166;
  }

  .row.assistant .group.done .group-latest {
    color: rgba(255, 255, 255, 0.55);
  }

  .row.assistant .group-chevron {
    background: rgba(255, 255, 255, 0.9);
    color: var(--bubble-assistant);
  }

  .row.assistant .spinner {
    border-color: rgba(255, 255, 255, 0.35);
    border-top-color: #ffd166;
  }

  .row.assistant .group.done .spinner {
    border-top-color: rgba(255, 255, 255, 0.4);
  }

  .row.assistant .group-history {
    color: rgba(255, 255, 255, 0.55);
    border-left-color: rgba(255, 255, 255, 0.35);
  }

  .row.assistant .group-history li::before {
    background: rgba(255, 255, 255, 0.4);
  }

  .row.assistant .group-history li.executing {
    color: #ffd166;
  }

  .row.assistant .group-history li.executing::before {
    background: #ffd166;
  }

  .row.assistant .step-time {
    color: rgba(255, 255, 255, 0.85);
  }

  .row.assistant .cursor {
    background: #fff;
  }

  .group {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 8px;
  }

  .group-header {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    background: rgba(109, 94, 252, 0.08);
    border: 1px solid rgba(109, 94, 252, 0.3);
    border-radius: 999px;
    padding: 5px 8px 5px 10px;
    cursor: pointer;
    user-select: none;
    transition: background 0.15s ease;
  }

  .group-header:hover {
    background: rgba(109, 94, 252, 0.16);
  }

  .spinner {
    width: 13px;
    height: 13px;
    border-radius: 50%;
    border: 2px solid #d9d6ff;
    border-top-color: var(--accent-1);
    animation: spin 0.7s linear infinite;
    flex: none;
  }

  .group.done .spinner {
    border-top-color: #d9d6ff;
    animation: none;
  }

  .group-latest {
    flex: 1;
    min-width: 0;
    font-size: 0.68rem;
    color: var(--muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .group-chevron {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex: none;
    font-size: 0.6rem;
    color: #fff;
    background: var(--accent-1);
    transition: transform 0.2s ease;
  }

  .group.expanded .group-chevron { transform: rotate(180deg); }

  .group-history {
    display: none;
    list-style: none;
    margin: 2px 0 0 4px;
    padding-left: 14px;
    border-left: 2px solid var(--border);
    font-size: 0.68rem;
    color: var(--muted);
  }

  .group.expanded .group-history { display: block; }

  .group-history li {
    position: relative;
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 10px;
    padding: 2px 0 2px 14px;
  }

  .group-history li::before {
    content: "";
    position: absolute;
    left: 0;
    top: 10px;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--accent-2);
  }

  .step-text { flex: 1; }

  .step-time {
    flex: none;
    font-variant-numeric: tabular-nums;
    color: var(--accent-1);
    opacity: 0.75;
  }

  #response-text {
    white-space: pre-wrap;
  }

  .cursor {
    display: inline-block;
    width: 2px;
    height: 1em;
    background: var(--accent-1);
    margin-left: 2px;
    vertical-align: text-bottom;
    animation: blink 1s step-start infinite;
  }

  form {
    position: relative;
    flex: none;
    display: flex;
    gap: 8px;
    padding: 8px 10px;
    border-top: 1px solid var(--border);
    background: #fbfbfe;
  }

  input {
    flex: 1;
    padding: 6px 12px;
    border-radius: 999px;
    border: 1px solid var(--border);
    font-size: 0.78rem;
    outline: none;
    background: #fff;
    color: var(--text);
  }

  input:focus { border-color: var(--accent-2); }

  button.send {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    border: none;
    background: linear-gradient(120deg, var(--header-1), var(--header-2));
    color: #fff;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    flex: none;
    transition: transform 0.15s ease;
  }

  button.send:active { transform: scale(0.92); }
  button.send:disabled { opacity: 0.5; cursor: default; }

  .slash-menu {
    position: absolute;
    left: 16px;
    right: 16px;
    bottom: calc(100% + 8px);
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    box-shadow: var(--shadow);
    overflow: hidden;
    z-index: 10;
  }

  .slash-menu[hidden] { display: none; }

  .slash-item {
    display: block;
    width: 100%;
    padding: 9px 14px;
    border: none;
    background: none;
    text-align: left;
    font-size: 0.78rem;
    color: var(--text);
    cursor: pointer;
  }

  .slash-item + .slash-item {
    border-top: 1px solid var(--border);
  }

  .slash-item:hover,
  .slash-item.active {
    background: rgba(109, 94, 252, 0.1);
  }

  @keyframes bob { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
  @keyframes spin { to { transform: rotate(360deg); } }
  @keyframes rise { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
  @keyframes blink { 50% { opacity: 0; } }
</style>
</head>
<body>
  <div class="app" id="app">
    <div class="resize-handle" id="resizeHandle"></div>
    <div class="app-header">
      <div class="app-header-text">
        <h1>Chat Stream Demo</h1>
        <p>Server-sent events, grouped progress updates</p>
      </div>
      <span class="robot-icon">🤖</span>
      <button class="minimize-btn" id="minimizeBtn" type="button" aria-label="Minimize"></button>
    </div>
    <div id="chat"></div>
    <form id="form">
      <div class="slash-menu" id="slashMenu" hidden>
        <button type="button" class="slash-item" data-text="What is the status of my last order?">What is the status of my last order?</button>
        <button type="button" class="slash-item" data-text="How does the retrieval pipeline work?">How does the retrieval pipeline work?</button>
        <button type="button" class="slash-item" data-text="Summarize the latest incident report">Summarize the latest incident report</button>
      </div>
      <input id="query" placeholder="Ask something, or type / for suggestions..." value="hello" autocomplete="off" />
      <button class="send" type="submit" aria-label="Send">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
          <path d="M4 12L20 4L13 20L11 13L4 12Z" fill="currentColor"/>
        </svg>
      </button>
    </form>
  </div>

<script>
const form = document.getElementById('form');
const chat = document.getElementById('chat');
const input = document.getElementById('query');
const sendBtn = form.querySelector('button.send');
const appEl = document.getElementById('app');
const minimizeBtn = document.getElementById('minimizeBtn');

let customHeight = '';

minimizeBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  customHeight = appEl.style.height;
  appEl.style.height = '';
  appEl.classList.add('minimized');
});

appEl.addEventListener('click', () => {
  if (appEl.classList.contains('minimized')) {
    appEl.classList.remove('minimized');
    appEl.style.height = customHeight;
  }
});

const scrollObserver = new MutationObserver(() => {
  chat.scrollTop = chat.scrollHeight;
});
scrollObserver.observe(chat, { childList: true, subtree: true, characterData: true });

const resizeHandle = document.getElementById('resizeHandle');
let resizing = false;
let resizeStartY = 0;
let resizeStartHeight = 0;

resizeHandle.addEventListener('pointerdown', (e) => {
  resizing = true;
  resizeStartY = e.clientY;
  resizeStartHeight = appEl.getBoundingClientRect().height;
  appEl.style.transition = 'none';
  resizeHandle.setPointerCapture(e.pointerId);
});

resizeHandle.addEventListener('pointermove', (e) => {
  if (!resizing) return;
  const delta = resizeStartY - e.clientY;
  const newHeight = Math.min(
    window.innerHeight - 8,
    Math.max(320, resizeStartHeight + delta)
  );
  appEl.style.height = `${newHeight}px`;
});

resizeHandle.addEventListener('pointerup', () => {
  resizing = false;
  appEl.style.transition = '';
});

function formatTime() {
  const now = new Date();
  const hh = String(now.getHours()).padStart(2, '0');
  const mm = String(now.getMinutes()).padStart(2, '0');
  return `${hh}:${mm}`;
}

function makeMsgTime() {
  const timeEl = document.createElement('div');
  timeEl.className = 'msg-time';
  timeEl.textContent = formatTime();
  return timeEl;
}

function addUserBubble(text) {
  const row = document.createElement('div');
  row.className = 'row user';
  const bubble = document.createElement('div');
  bubble.className = 'bubble';

  const textEl = document.createElement('span');
  textEl.className = 'bubble-text';
  textEl.textContent = text;

  bubble.appendChild(textEl);
  bubble.appendChild(makeMsgTime());
  row.appendChild(bubble);
  chat.appendChild(row);
}

function addAssistantBubble() {
  const row = document.createElement('div');
  row.className = 'row assistant';
  const bubble = document.createElement('div');
  bubble.className = 'bubble';

  const responseText = document.createElement('span');
  responseText.id = 'response-text';

  const cursor = document.createElement('span');
  cursor.className = 'cursor';

  bubble.appendChild(responseText);
  bubble.appendChild(cursor);
  row.appendChild(bubble);
  chat.appendChild(row);

  return { row, bubble, responseText, cursor };
}

function addGroup(bubble, before) {
  const el = document.createElement('div');
  el.className = 'group expanded';

  const header = document.createElement('div');
  header.className = 'group-header';

  const spinner = document.createElement('span');
  spinner.className = 'spinner';

  const latest = document.createElement('span');
  latest.className = 'group-latest';

  const chevron = document.createElement('span');
  chevron.className = 'group-chevron';
  chevron.textContent = '▾';

  header.appendChild(spinner);
  header.appendChild(latest);
  header.appendChild(chevron);

  const history = document.createElement('ul');
  history.className = 'group-history';

  el.appendChild(header);
  el.appendChild(history);
  bubble.insertBefore(el, before);

  header.addEventListener('click', () => el.classList.toggle('expanded'));

  return { el, latest, history, spinner };
}

const slashMenu = document.getElementById('slashMenu');
const slashItems = Array.from(slashMenu.querySelectorAll('.slash-item'));
let slashActiveIndex = -1;

function setSlashActive(index) {
  slashActiveIndex = index;
  slashItems.forEach((item, i) => item.classList.toggle('active', i === index));
}

function selectSlashItem(index) {
  const item = slashItems[index];
  if (!item) return;
  input.value = item.dataset.text;
  slashMenu.hidden = true;
  form.requestSubmit();
}

input.addEventListener('input', () => {
  const show = input.value === '/';
  slashMenu.hidden = !show;
  setSlashActive(show ? 0 : -1);
});

input.addEventListener('blur', () => {
  slashMenu.hidden = true;
});

input.addEventListener('keydown', (e) => {
  if (slashMenu.hidden) return;

  if (e.key === 'ArrowDown') {
    e.preventDefault();
    setSlashActive((slashActiveIndex + 1) % slashItems.length);
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    setSlashActive((slashActiveIndex - 1 + slashItems.length) % slashItems.length);
  } else if (e.key === 'Enter') {
    e.preventDefault();
    selectSlashItem(slashActiveIndex === -1 ? 0 : slashActiveIndex);
  } else if (e.key === 'Escape') {
    slashMenu.hidden = true;
  }
});

slashItems.forEach((item, index) => {
  item.addEventListener('mousedown', (e) => {
    e.preventDefault();
    selectSlashItem(index);
  });
  item.addEventListener('mouseenter', () => setSlashActive(index));
});

form.addEventListener('submit', (e) => {
  e.preventDefault();
  slashMenu.hidden = true;
  const query = input.value.trim();
  if (!query) return;

  addUserBubble(query);
  input.value = '';
  sendBtn.disabled = true;
  startStream(query);
});

function startStream(query) {
  const { bubble, responseText, cursor } = addAssistantBubble();
  const groups = {};
  const streamStart = performance.now();
  let lastStepTime = streamStart;
  const es = new EventSource(`/chat?query=${encodeURIComponent(query)}`);

  function getGroup(key) {
    if (groups[key]) return groups[key];
    const g = addGroup(bubble, responseText);
    groups[key] = g;
    return g;
  }

  es.addEventListener('status', (e) => {
    const data = JSON.parse(e.data);
    const g = getGroup(data.group || 'default');

    const now = performance.now();
    const stepSeconds = ((now - lastStepTime) / 1000).toFixed(1);
    lastStepTime = now;

    g.latest.textContent = data.message;

    const prevExecuting = g.history.querySelector('li.executing');
    if (prevExecuting) prevExecuting.classList.remove('executing');

    const line = document.createElement('li');
    line.className = 'executing';
    const text = document.createElement('span');
    text.className = 'step-text';
    text.textContent = data.message;
    const time = document.createElement('span');
    time.className = 'step-time';
    time.textContent = `${stepSeconds}s`;
    line.appendChild(text);
    line.appendChild(time);
    g.history.appendChild(line);
  });

  es.addEventListener('token', (e) => {
    responseText.textContent += JSON.parse(e.data).text;
    chat.scrollTop = chat.scrollHeight;
  });

  es.addEventListener('done', () => {
    Object.values(groups).forEach((g) => {
      g.el.classList.add('done');
      const stillExecuting = g.history.querySelector('li.executing');
      if (stillExecuting) stillExecuting.classList.remove('executing');
    });
    cursor.remove();
    bubble.appendChild(makeMsgTime());

    es.close();
    sendBtn.disabled = false;
  });

  es.onerror = () => {
    es.close();
    sendBtn.disabled = false;
  };

  chat.scrollTop = chat.scrollHeight;
}
</script>
</body>
</html>
"""


def sse_event(event_type: str, data: dict):
    return (
        f"event: {event_type}\n"
        f"data: {json.dumps(data)}\n\n"
    )


@app.get("/")
async def root():
    return {"message": "API is running"}


@app.get("/demo", response_class=HTMLResponse)
async def demo():
    return DEMO_HTML


@app.get("/chat")
async def chat(query: str):

    pipeline_steps = [
        "Received request from user",
        "Verifying input with input guardrail...",
        "Classifying intent...",
        "Retrieving information from OpenSearch...",
        "Found related information",
        "Reranking retrieved passages...",
        "Generating response with grounded context...",
        "Running output guardrail checks...",
    ]

    async def event_generator():
        for step in pipeline_steps:
            yield sse_event(
                "status",
                {"message": step, "group": "progress"}
            )
            await asyncio.sleep(random.uniform(0.25, 2))

        for word in "This is a streamed response from the chatbot.".split():
            yield sse_event(
                "token",
                {"text": word + " "}
            )
            await asyncio.sleep(0.2)

        yield sse_event("done", {})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )