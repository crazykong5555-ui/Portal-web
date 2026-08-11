let calling = false;
let timerId = null;
let seconds = 0;

const status = document.getElementById('status');
const timer = document.getElementById('timer');
const callButton = document.getElementById('btnCall');
const hangupButton = document.getElementById('btnHangup');
const contactId = document.getElementById('contactId').value;

function setStatus(text, state) {
  status.className = `status-pill ${state}`;
  status.innerHTML = `<i class="fa-solid fa-circle"></i> ${text}`;
}
function renderTimer() {
  const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
  const remainder = (seconds % 60).toString().padStart(2, '0');
  timer.textContent = `${minutes}:${remainder}`;
}
function stopTimer() { clearInterval(timerId); timerId = null; seconds = 0; renderTimer(); }
async function startCall() {
  if (calling) return;
  calling = true; callButton.disabled = true; hangupButton.disabled = false;
  setStatus('Marcando…', 'calling'); seconds = 0; renderTimer();
  timerId = setInterval(() => { seconds += 1; renderTimer(); }, 1000);
  try { const response = await fetch(`/call/start/${contactId}`); const data = await response.json(); if (data.status === 'ok') setStatus('Llamada en curso', 'calling'); } catch (_) { setStatus('Llamada en curso', 'calling'); }
}
async function endCall() {
  if (!calling) return;
  calling = false; callButton.disabled = false; hangupButton.disabled = true; stopTimer(); setStatus('Llamada finalizada', 'ended');
  try { await fetch(`/call/end/${contactId}`); } catch (_) { /* El estado ya fue actualizado localmente. */ }
}
callButton.addEventListener('click', startCall); hangupButton.addEventListener('click', endCall);
document.querySelectorAll('.keypad').forEach(button => button.addEventListener('click', () => { if (calling) button.classList.add('active'); setTimeout(() => button.classList.remove('active'), 120); }));
