// ── MOT DE PASSE VISIBLE / CACHÉ ──
function togglePw(inputId, btn) {
    const input = document.getElementById(inputId);
    const show  = input.type === 'password';
    input.type  = show ? 'text' : 'password';
    btn.textContent = show ? '🙈' : '👁';
}

// ── ONGLETS CONNEXION / INSCRIPTION ──
function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach((b, i) =>
        b.classList.toggle('active', (i === 0) === (tab === 'login'))
    );
    document.getElementById('panel-login').classList.toggle('active', tab === 'login');
    document.getElementById('panel-register').classList.toggle('active', tab === 'register');
}

// ── INSCRIPTION ──
async function register() {
    const user = document.getElementById('reg-username').value.trim();
    const pass = document.getElementById('reg-password').value;
    const msg  = document.getElementById('reg-msg');

    if (!user || !pass) {
        showMsg(msg, 'Remplis tous les champs.', 'error');
        return;
    }

    const fd = new FormData();
    fd.append('username', user);
    fd.append('password', pass);

    try {
        const res  = await fetch('/register', { method: 'POST', body: fd });
        const data = await res.json();
        if (res.ok) {
            showMsg(msg, '✓ Compte créé ! Tu peux te connecter.', 'success');
            setTimeout(() => switchTab('login'), 1200);
        } else {
            showMsg(msg, data.detail || 'Erreur.', 'error');
        }
    } catch {
        showMsg(msg, 'Serveur inaccessible.', 'error');
    }
}

// ── CONNEXION ──
async function login() {
    const user = document.getElementById('login-username').value.trim();
    const pass = document.getElementById('login-password').value;
    const msg  = document.getElementById('login-msg');

    if (!user || !pass) {
        showMsg(msg, 'Remplis tous les champs.', 'error');
        return;
    }

    const fd = new FormData();
    fd.append('username', user);
    fd.append('password', pass);

    try {
        const res  = await fetch('/login', { method: 'POST', body: fd });
        const data = await res.json();
        if (res.ok) {
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('username', data.username);
            enterChat(data.username);
        } else {
            showMsg(msg, data.detail || 'Identifiants incorrects.', 'error');
        }
    } catch {
        showMsg(msg, 'Serveur inaccessible.', 'error');
    }
}

// ── DÉCONNEXION ──
function logout() {
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    sessionStorage.removeItem('guest_questions');
    document.getElementById('guest-banner').style.display = 'none';
    document.getElementById('chat-screen').classList.remove('active');
    document.getElementById('auth-screen').classList.add('active');
    document.getElementById('chat-box').innerHTML = `
        <div class="msg bot">
            <div class="msg-label">GénérIAtion</div>
            <div class="msg-bubble">Bonjour ! Je suis votre conseiller d'orientation. Posez-moi vos questions sur les formations, les métiers, les bourses ou les universités — où que vous soyez dans le monde.</div>
        </div>`;
}

// ── ENTRER DANS LE CHAT ──
function enterChat(username) {
    document.getElementById('auth-screen').classList.remove('active');
    document.getElementById('chat-screen').classList.add('active');
    document.getElementById('sidebar-username').textContent = username;
    document.getElementById('avatar-letter').textContent = username.charAt(0).toUpperCase();
}

// ── MODE INVITÉ ──
const GUEST_LIMIT = 3;

function enterGuest() {
    sessionStorage.setItem('guest_questions', GUEST_LIMIT);
    document.getElementById('auth-screen').classList.remove('active');
    document.getElementById('chat-screen').classList.add('active');
    document.getElementById('sidebar-username').textContent = 'Invité';
    document.getElementById('avatar-letter').textContent = '?';
    document.getElementById('guest-banner').style.display = 'block';
    updateGuestCounter();
}

function updateGuestCounter() {
    const left = parseInt(sessionStorage.getItem('guest_questions') || 0);
    const el = document.getElementById('questions-left');
    if (el) el.textContent = left;
}

function isGuest() {
    return !localStorage.getItem('username') && sessionStorage.getItem('guest_questions') !== null;
}

// ── AFFICHER UN MESSAGE D'ÉTAT ──
function showMsg(el, text, type) {
    el.textContent = text;
    el.className = 'auth-msg ' + type;
}

// ── ENVOYER UN MESSAGE ──
async function sendMessage() {
    const input   = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const sendBtn = document.getElementById('send-btn');
    const message = input.value.trim();

    if (!message) return;

    // Vérification limite invité
    if (isGuest()) {
        const left = parseInt(sessionStorage.getItem('guest_questions') || 0);
        if (left <= 0) {
            const chatBox = document.getElementById('chat-box');
            chatBox.innerHTML += `
                <div class="msg bot">
                    <div class="msg-label">GénérIAtion</div>
                    <div class="msg-bubble" style="border-left-color:#e07070;">
                        Tu as atteint la limite de 3 questions en mode invité. 
                        <strong>Crée un compte gratuitement</strong> pour continuer !
                    </div>
                </div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
            return;
        }
        sessionStorage.setItem('guest_questions', left - 1);
        updateGuestCounter();
    }

    // Message de l'utilisateur
    chatBox.innerHTML += `
        <div class="msg user">
            <div class="msg-label">${localStorage.getItem('username') || 'Vous'}</div>
            <div class="msg-bubble">${escHtml(message)}</div>
        </div>`;
    input.value = '';
    sendBtn.disabled = true;
    chatBox.scrollTop = chatBox.scrollHeight;

    // Animation "L'IA réfléchit..."
    const id = 'think-' + Date.now();
    chatBox.innerHTML += `
        <div class="msg bot" id="${id}">
            <div class="msg-label">GénérIAtion</div>
            <div class="msg-bubble thinking"><span></span><span></span><span></span></div>
        </div>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    // Appel à FastAPI
    try {
        const res  = await fetch(`/ask?question=${encodeURIComponent(message)}`);
        const data = await res.json();
        document.getElementById(id).querySelector('.msg-bubble').innerHTML =
            escHtml(data.bot).replace(/\n/g, '<br>');
    } catch {
        document.getElementById(id).querySelector('.msg-bubble').textContent =
            "Erreur : impossible de joindre l'IA.";
    }

    sendBtn.disabled = false;
    chatBox.scrollTop = chatBox.scrollHeight;
}

// ── ÉCHAPPER LE HTML (sécurité XSS) ──
function escHtml(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

// ── RACCOURCIS CLAVIER ──
document.addEventListener('keydown', e => {
    if (e.key !== 'Enter') return;
    const id = document.activeElement?.id;
    if (id === 'user-input')     sendMessage();
    if (id === 'login-password') login();
    if (id === 'reg-password')   register();
});

// ── AUTO-CONNEXION si déjà connecté ──
const savedUser = localStorage.getItem('username');
if (savedUser) enterChat(savedUser);