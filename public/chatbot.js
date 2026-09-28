(() => {
  // Tự động tải thư viện parse Markdown (Marked)
  if (!document.querySelector('#fmm-marked-script')) {
    const script = document.createElement('script');
    script.id = 'fmm-marked-script';
    script.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
    document.head.appendChild(script);
  }

  // 🆔 Khởi tạo hoặc lấy Session ID cố định cho tab hiện tại
  let sessionId = sessionStorage.getItem('fmm_session_id');
  if (!sessionId) {
    sessionId = Math.random().toString(36).substring(2, 8); // Tạo chuỗi 6 ký tự ngẫu nhiên (ví dụ: "a8f9x2")
    sessionStorage.setItem('fmm_session_id', sessionId);
  }

  const style = document.createElement('style');
  style.textContent = `
    #fmm-chat-toggle {
      position: fixed;
      right: 22px;
      bottom: 22px;
      z-index: 1000;
      border: 0;
      border-radius: 999px;
      background: #7c3aed; /* Violet-600 */
      color: #fff;
      padding: 12px 18px;
      font-weight: 700;
      font-size: 14px;
      box-shadow: 0 4px 20px rgba(124, 58, 237, 0.25);
      cursor: pointer;
      transition: all 0.2s ease-out;
    }
    #fmm-chat-toggle:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(124, 58, 237, 0.45);
      background: #6d28d9; /* Violet-700 */
    }
    #fmm-chat {
      display: none;
      position: fixed;
      right: 22px;
      bottom: 78px;
      width: min(420px, calc(100vw - 32px));
      height: min(600px, calc(100vh - 100px));
      z-index: 1000;
      background: var(--sl-color-bg, #ffffff);
      color: var(--sl-color-text, #0f172a);
      border: 1px solid #ddd6fe; /* Violet-200 */
      border-radius: 14px;
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
      overflow: hidden;
      font-family: system-ui, -apple-system, sans-serif;
    }
    #fmm-chat.open { display: flex; flex-direction: column; }
    #fmm-chat header { padding: 14px 16px; background: #7c3aed; color: #fff; font-weight: 700; display: flex; justify-content: space-between; align-items: center; }
    #fmm-chat header button { background: transparent; color: #fff; border: 0; font-size: 20px; cursor: pointer; opacity: 0.8; transition: opacity 0.2s; }
    #fmm-chat header button:hover { opacity: 1; }
    #fmm-chat-log { flex: 1; overflow-y: auto; padding: 14px; display: flex; flex-direction: column; gap: 12px; background-color: #faf5ff; }
    
    /* Style cho tin nhắn & Markdown */
    .fmm-msg { max-width: 90%; padding: 10px 14px; border-radius: 12px; line-height: 1.5; font-size: 14px; word-break: break-word; }
    .fmm-user { align-self: flex-end; background: #7c3aed; color: #fff; white-space: pre-wrap; border-bottom-right-radius: 2px; }
    .fmm-bot { align-self: flex-start; background: #ffffff; color: #334155; border: 1px solid #ddd6fe; border-bottom-left-radius: 2px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03); }
    
    /* Format các phần tử Markdown trong tin nhắn Bot */
    .fmm-bot p { margin: 0 0 8px 0; } .fmm-bot p:last-child { margin-bottom: 0; }
    .fmm-bot h1, .fmm-bot h2, .fmm-bot h3, .fmm-bot h4 { margin: 12px 0 6px 0; font-size: 15px; font-weight: 700; color: #5b21b6; }
    .fmm-bot ul, .fmm-bot ol { margin: 6px 0; padding-left: 20px; }
    .fmm-bot li { margin-bottom: 4px; }
    .fmm-bot strong { font-weight: 700; color: #4c1d95; }
    .fmm-bot code { background: #f5f3ff; color: #6d28d9; border: 1px solid #ddd6fe; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 13px; }
    .fmm-bot a { color: #7c3aed; font-weight: 600; text-decoration: underline; }
    
    .fmm-chat-form { display: flex; gap: 8px; padding: 10px; border-top: 1px solid #e2e8f0; background: #fff; }
    .fmm-chat-form textarea { resize: none; flex: 1; border: 1px solid #cbd5e1; border-radius: 8px; padding: 8px 10px; font: inherit; outline: none; transition: border-color 0.2s; }
    .fmm-chat-form textarea:focus { border-color: #7c3aed; box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.15); }
    .fmm-chat-form button { border: 0; border-radius: 8px; background: #7c3aed; color: #fff; padding: 0 16px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
    .fmm-chat-form button:hover { background: #6d28d9; }
    .fmm-chat-form button:disabled { opacity: .5; cursor: not-allowed; }
  `;
  document.head.appendChild(style);

  const wrapper = document.createElement('div');
  wrapper.innerHTML = `<button id="fmm-chat-toggle" aria-label="Open FormMail Hub AI">💬 Ask FormMail Hub</button><section id="fmm-chat" aria-label="FormMail Hub AI chatbot"><header>FormMail Hub AI <button aria-label="Close">×</button></header><div id="fmm-chat-log"><div class="fmm-msg fmm-bot">Hello! How can I help you with FormMail Hub today? Feel free to ask about setup, features, or integrations.</div></div><form class="fmm-chat-form"><textarea rows="2" maxlength="4000" placeholder="Type your question... (Enter to send)"></textarea><button type="submit">Send</button></form></section>`;
  document.body.appendChild(wrapper);

  const chat = wrapper.querySelector('#fmm-chat'); 
  const log = wrapper.querySelector('#fmm-chat-log'); 
  const form = wrapper.querySelector('form'); 
  const input = form.querySelector('textarea'); 
  const send = form.querySelector('button'); 
  const history = [];

  wrapper.querySelector('#fmm-chat-toggle').onclick = () => { chat.classList.add('open'); input.focus(); };
  chat.querySelector('header button').onclick = () => chat.classList.remove('open');

  input.onkeydown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      form.requestSubmit();
    }
  };

  // Hàm render Markdown sang HTML an toàn
  const renderMarkdown = (text) => {
    if (window.marked && typeof window.marked.parse === 'function') {
      return window.marked.parse(text, { breaks: true });
    }
    // Fallback nếu thư viện chưa kịp load xong
    return text
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/### (.*)/g, '<h3>$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/^\* (.*)/gm, '<li>$1</li>')
      .replace(/\n/g, '<br>');
  };

  const add = (text, cls, isMarkdown = false) => {
    const el = document.createElement('div');
    el.className = `fmm-msg ${cls}`;
    if (isMarkdown) {
      el.innerHTML = renderMarkdown(text);
    } else {
      el.textContent = text;
    }
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
    return el;
  };

  form.onsubmit = async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message || send.disabled) return;

    add(message, 'fmm-user', false);
    input.value = '';
    send.disabled = true;

    const pending = add('Searching docs…', 'fmm-bot', false);

    try {
      // Trỏ trực tiếp tới Vercel Domain & gửi kèm sessionId
      const response = await fetch('https://doc.formmailhub.com/api/chat', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ message, history, sessionId }) // 👈 Đã thêm sessionId
      });
      const data = await response.json();

      if (data.answer) {
        pending.innerHTML = renderMarkdown(data.answer);
        history.push({ role: 'user', text: message }, { role: 'model', text: data.answer });
        if (history.length > 10) history.splice(0, 2);
      } else {
        pending.textContent = data.error || 'An error occurred.';
      }
    } catch {
      pending.textContent = 'Unable to connect to the chatbot right now.';
    } finally {
      send.disabled = false;
      log.scrollTop = log.scrollHeight;
      input.focus();
    }
  };
})();
