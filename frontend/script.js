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
    const logoLink = document.getElementById('logo-link');
    const cardCounter = document.getElementById('card-counter');
    const cardInfoContainer = document.querySelector('.card-info-container'); // NOVO: Referência ao novo contêiner
    const btnToggleView = document.getElementById('btn-toggle-view');


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

    function resetAppToHomeScreen() {
        mainApp.classList.remove('study-active');
        
        cardScene.classList.add('hidden');
        messageArea.classList.add('hidden');
        cardInfoContainer.classList.add('hidden'); // Esconde o contêiner de info (com contador)
        evaluationButtons.classList.add('hidden'); // Esconde os botões de avaliação
        btnToggleView.classList.add('hidden'); // Esconde o botão de toggle view
        btnToggleView.classList.remove('active'); // Garante que o estado ativo seja removido
        cardScene.classList.remove('side-by-side-active'); // Reseta a view lado a lado
    }

    async function fetchCards(endpoint) {
        messageArea.classList.remove('hidden');
        showMessage('Carregando cards...');
        cardInfoContainer.classList.add('hidden'); // Garante que o contador esteja escondido ao carregar
        evaluationButtons.classList.add('hidden'); // Garante que os botões de avaliação estejam escondidos

        try {
            const response = await fetch(API_URL + endpoint);
            if (!response.ok) { throw new Error('Falha ao buscar os dados da API.'); }
            const data = await response.json();

            if (data.status === 'concluido' || data.length === 0) {
                const message = data.status === 'concluido' ? data.message : 'Nenhum card encontrado para esta sessão.';
                showMessage(message);
                cardScene.classList.add('hidden');
                evaluationButtons.classList.add('hidden');
                btnToggleView.classList.add('hidden'); // Esconde o botão se não houver cards
                btnToggleView.classList.remove('active'); // Reseta o estado
                cardScene.classList.remove('side-by-side-active'); // Reseta a view
            } 
            else {
                currentCards = data;
                currentIndex = 0;
                mainApp.classList.add('study-active');
                messageArea.classList.add('hidden');
                cardScene.classList.remove('hidden'); 
                cardInfoContainer.classList.remove('hidden'); // Mostra o contêiner de info (com contador)
                evaluationButtons.classList.remove('hidden'); // Mostra os botões de avaliação
                btnToggleView.classList.remove('hidden'); // Mostra o botão de toggle view
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
            
            // LÓGICA DE RESET DO ESTADO DO CARD
            card.classList.remove('is-flipped');
            // NOVO: Apenas se o modo lado a lado NÃO estiver ativo por padrão ao carregar
            // Se você quiser que o modo lado a lado persista entre os cards, remova as duas linhas abaixo
            cardScene.classList.remove('side-by-side-active'); 
            btnToggleView.classList.remove('active'); // Desativa o feedback visual do botão

            evaluationButtons.classList.add('disabled'); // Desabilita botões de avaliação até virar o card
            cardCounter.textContent = `${currentIndex + 1} / ${currentCards.length}`;
        } else {
            showMessage('Sessão finalizada!');
            cardScene.classList.add('hidden');
            cardInfoContainer.classList.add('hidden'); // Esconde ao finalizar
            evaluationButtons.classList.add('hidden'); // Esconde ao finalizar
            btnToggleView.classList.add('hidden'); // Esconde o botão ao finalizar
            btnToggleView.classList.remove('active'); // Reseta o estado
            cardScene.classList.remove('side-by-side-active'); // Reseta a view
        }
    }
    
    function flipCard() {
        // Permitir virar apenas se NÃO estiver no modo lado a lado
        if (!cardScene.classList.contains('side-by-side-active')) {
            card.classList.toggle('is-flipped');
            // Apenas habilita os botões de avaliação se o card estiver virado
            evaluationButtons.classList.toggle('disabled', !card.classList.contains('is-flipped'));
        }
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

    // CORREÇÃO: Restaurado para a versão simples que chama a função flipCard diretamente.
    card.addEventListener('click', flipCard);

    evaluationButtons.addEventListener('click', (event) => {
        const evalId = event.target.dataset.evalId;
        if (evalId) {
            handleEvaluation(parseInt(evalId));
        }
    });

    btnToggleView.addEventListener('click', () => {
        // Se o modo lado a lado for ativado, garanta que o card esteja "virado" logicamente
        // para que a face de trás seja visível.
        if (!cardScene.classList.contains('side-by-side-active')) {
            card.classList.add('is-flipped'); // Garante que a face de trás esteja "ativa"
            evaluationButtons.classList.remove('disabled'); // Habilita os botões de avaliação
        } else {
            // Se o modo lado a lado for desativado, o card volta ao normal
            // e os botões de avaliação só devem ser habilitados se o card estiver virado
            evaluationButtons.classList.toggle('disabled', !card.classList.contains('is-flipped'));
        }

        cardScene.classList.toggle('side-by-side-active');
        btnToggleView.classList.toggle('active'); // Alterna o estado visual do botão
    });

    logoLink.addEventListener('click', (event) => {
        event.preventDefault();
        resetAppToHomeScreen();
    });
});