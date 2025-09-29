document.addEventListener('DOMContentLoaded', () => {
    const API_URL = 'http://localhost:5000';

    const mainApp = document.getElementById('app'); 
    const modoContainer = document.querySelector('.modo-container');
    const btnEstudar = document.getElementById('btnEstudar');
    const btnRevisao = document.getElementById('btnRevisao');
    const messageArea = document.getElementById('message-area');
    const cardScene = document.getElementById('card-scene');
    const card = document.getElementById('card');
    const cardFront = document.querySelector('.card-front');
    const cardBack = document.querySelector('.card-back');
    const evaluationButtons = document.getElementById('evaluation-buttons');
    const themeToggleButton = document.getElementById('theme-toggle-button');
    // NOVO: Referência ao link do logo
    const logoLink = document.getElementById('logo-link');


    // --- LÓGICA DO TEMA (MODO NOTURNO) ---
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme === 'dark' || currentTheme === null) {
        document.body.classList.add('dark-mode');
        themeToggleButton.textContent = '☀️';
    } else {
        themeToggleButton.textContent = '🌙';
    }

    themeToggleButton.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        let theme = 'light';
        if (document.body.classList.contains('dark-mode')) {
            theme = 'dark';
            themeToggleButton.textContent = '☀️';
        } else {
            themeToggleButton.textContent = '🌙';
        }
        localStorage.setItem('theme', theme);
    });
    
    // --- LÓGICA PRINCIPAL DO APP ---

    let currentCards = [];
    let currentIndex = 0;

    // NOVO: Função para resetar a visualização para a tela inicial
    function resetAppToHomeScreen() {
        mainApp.classList.remove('study-active'); // Remove o estado de estudo ativo
        
        // Esconde todos os elementos de estudo
        cardScene.classList.add('hidden');
        evaluationButtons.classList.add('hidden');
        messageArea.classList.add('hidden');
    }

    async function fetchCards(endpoint) {
        messageArea.classList.remove('hidden');
        showMessage('Carregando cards...');

        try {
            const response = await fetch(API_URL + endpoint);
            if (!response.ok) { throw new Error('Falha ao buscar os dados da API.'); }
            const data = await response.json();

            if (data.status === 'concluido' || data.length === 0) {
                const message = data.status === 'concluido' ? data.message : 'Nenhum card encontrado para esta sessão.';
                showMessage(message);
                cardScene.classList.add('hidden');
                evaluationButtons.classList.add('hidden');
            } 
            else {
                currentCards = data;
                currentIndex = 0;
                mainApp.classList.add('study-active');
                messageArea.classList.add('hidden');
                cardScene.classList.remove('hidden'); 
                evaluationButtons.classList.remove('hidden');
                displayCurrentCard();
            }
        } catch (error) {
            showMessage(`Erro: ${error.message}`, true);
        }
    }

    function displayCurrentCard() {
        if (currentIndex < currentCards.length) {
            const currentCard = currentCards[currentIndex];
            cardFront.textContent = currentCard.frase;
            cardBack.textContent = currentCard.traducao;
            card.classList.remove('is-flipped');
            evaluationButtons.classList.add('disabled');
        } else {
            showMessage('Sessão finalizada!');
            cardScene.classList.add('hidden');
            evaluationButtons.classList.add('hidden');
        }
    }
    
    function flipCard() {
        card.classList.toggle('is-flipped');
        evaluationButtons.classList.remove('disabled');
    }

    async function handleEvaluation(evaluationId) {
        if (evaluationButtons.classList.contains('disabled')) { return; }
        try {
            const currentCard = currentCards[currentIndex];
            await fetch(API_URL + '/avaliar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', },
                body: JSON.stringify({
                    flashcard_id: currentCard.id,
                    avaliacao_id: evaluationId,
                }),
            });
            currentIndex++;
            displayCurrentCard();
        } catch (error) {
            showMessage(`Erro ao salvar avaliação: ${error.message}`, true);
        }
    }

    function showMessage(text, isError = false) {
        messageArea.textContent = text;
        messageArea.style.color = isError ? 'var(--rouge)' : 'var(--bleu)';
        messageArea.classList.remove('hidden');
    }

    // --- EVENT LISTENERS ---

    btnEstudar.addEventListener('click', () => fetchCards('/estudar'));
    btnRevisao.addEventListener('click', () => fetchCards('/flashcards/revisao'));
    card.addEventListener('click', flipCard);
    evaluationButtons.addEventListener('click', (event) => {
        const evalId = event.target.dataset.evalId;
        if (evalId) {
            handleEvaluation(parseInt(evalId));
        }
    });

    // NOVO: Event listener para o clique no logo
    logoLink.addEventListener('click', (event) => {
        event.preventDefault(); // Impede que o link recarregue a página
        resetAppToHomeScreen();
    });
});