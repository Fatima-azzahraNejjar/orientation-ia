// --- GESTION DE L'AUTHENTIFICATION ---

async function register() {
    const user = document.getElementById('reg-username').value;
    const pass = document.getElementById('reg-password').value;

    if (!user || !pass) return alert("Choisis un pseudo et un mot de passe !");

    const formData = new FormData();
    formData.append('username', user);
    formData.append('password', pass);

    try {
        const response = await fetch('/register', { method: 'POST', body: formData });
        const data = await response.json();
        alert(data.detail || data.message);
    } catch (error) {
        alert("Erreur lors de l'inscription.");
    }
}

async function login() {
    const user = document.getElementById('login-username').value;
    const pass = document.getElementById('login-password').value;

    if (!user || !pass) return alert("Entre tes identifiants !");

    const formData = new FormData();
    formData.append('username', user);
    formData.append('password', pass);

    try {
        const response = await fetch('/login', { method: 'POST', body: formData });
        const data = await response.json();

        if (response.ok) {
            alert("Connexion réussie ! Bonjour " + data.username);
            // On cache le login et on montre le chat
            document.getElementById('auth-container').style.display = 'none';
            document.getElementById('chat-interface').style.display = 'block';
            
            // On garde le nom et l'ID dans le navigateur
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('username', data.username);
        } else {
            alert(data.detail || "Erreur de connexion");
        }
    } catch (error) {
        alert("Le serveur ne répond pas.");
    }
}

// --- GESTION DU CHAT ---

async function sendMessage() {
    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");
    const message = input.value;

    if (!message) return;

    // 1. Afficher le message de l'utilisateur
    chatBox.innerHTML += `<div class="user-msg"><b>Moi:</b> ${message}</div>`;
    input.value = ""; 

    // 2. Afficher le message de chargement
    const loadingId = "loading-" + Date.now();
    chatBox.innerHTML += `<div class="bot-msg" id="${loadingId}"><i>L'IA réfléchit...</i></div>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        // 3. Appel à FastAPI
        const response = await fetch(`/ask?question=${encodeURIComponent(message)}`);
        const data = await response.json();

        // 4. Afficher la réponse
        document.getElementById(loadingId).innerHTML = `<b>IA:</b> ${data.bot}`;
    } catch (error) {
        document.getElementById(loadingId).innerText = "Erreur : Impossible de joindre l'IA.";
    }

    chatBox.scrollTop = chatBox.scrollHeight;
}

// Bonus : Envoyer avec la touche "Entrée"
document.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        const activeEl = document.activeElement.id;
        if (activeEl === 'user-input') sendMessage();
        if (activeEl === 'login-password') login();
        if (activeEl === 'reg-password') register();
    }
});