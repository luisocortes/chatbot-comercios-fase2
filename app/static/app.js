const form = document.getElementById('chat-form');
const question = document.getElementById('question');
const messages = document.getElementById('messages');
const send = document.getElementById('send');
const statusEl = document.getElementById('status');

function addMessage(content, role, detail = '') {
  const item = document.createElement('article');
  item.className = `bubble ${role}`;
  item.textContent = content; // Nunca interpretamos contenido como HTML.
  messages.appendChild(item);
  if (detail) {
    const meta = document.createElement('div');
    meta.className = 'meta';
    meta.textContent = detail;
    messages.appendChild(meta);
  }
  messages.scrollTop = messages.scrollHeight;
}

async function ask(text) {
  if (!text.trim() || send.disabled) return;
  addMessage(text, 'user');
  question.value = '';
  send.disabled = true;
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({mensaje: text})
    });
    if (!response.ok) throw new Error('Servicio no disponible');
    const data = await response.json();
    const label = data.accion === 'escalar' ? 'Se recomienda atención humana' : `Tema: ${data.tema} · Confianza: ${Math.round(data.confianza * 100)}%`;
    addMessage(data.respuesta, 'assistant', label);
  } catch (error) {
    addMessage('Ocurrió un problema de conexión. Intenta de nuevo o contacta al soporte oficial.', 'assistant');
  } finally {
    send.disabled = false;
    question.focus();
  }
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  ask(question.value);
});
document.querySelectorAll('[data-question]').forEach(button => {
  button.addEventListener('click', () => ask(button.dataset.question));
});
fetch('/api/health')
  .then(r => r.json())
  .then(d => { statusEl.textContent = d.estado === 'ok' ? 'Servicio activo · 24/7 (demo)' : 'Servicio no disponible'; })
  .catch(() => { statusEl.textContent = 'Sin conexión'; });
