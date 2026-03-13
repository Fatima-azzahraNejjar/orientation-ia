async function sendMessage() {
    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");
    const message = input.value;

    if (!message) return;

    // Afficher le message de l'utilisateur
    chatBox.innerHTML += `<div class="user-msg">${message}</div>`;
    input.value = ""; // Vider l'entrée

    // Afficher un petit message de chargement
    const loadingId = "loading-" + Date.now();
    chatBox.innerHTML += `<div class="bot-msg" id="${loadingId}">L'IA réfléchit...</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        // Appeler ton API FastAPI
        const response = await fetch(`/ask?question=${encodeURIComponent(message)}`);
        const data = await response.json();

        // Remplacer le chargement par la vraie réponse
        document.getElementById(loadingId).innerText = data.bot;
    } catch (error) {
        document.getElementById(loadingId).innerText = "Erreur : Impossible de joindre l'IA.";
    }

    chatBox.scrollTop = chatBox.scrollHeight;
}