document.addEventListener("DOMContentLoaded", () => {
    let cards = window.cards;

    if (!Array.isArray(cards)) {
        console.error("Cards are not valid.");
        return;
    }

    let current = 0;
    let showingQuestion = true;
    let isShuffled = false;


    // Shuffle function
    function shuffle(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    function renderCard() {
        const flipper = document.getElementById("flipper");

        if (showingQuestion) {
            flipper.classList.remove("flipped");
        } else {
            flipper.classList.add("flipped");
        }

        const card = cards[current];
        document.getElementById("card-front").innerText = card.question;
        document.getElementById("card-back").innerText = card.answer;
    }

    window.flipCard = function () {
        showingQuestion = !showingQuestion;
        renderCard();
    };

    window.nextCard = function () {
        current = (current + 1) % cards.length;
        showingQuestion = true;
        if (current % cards.length == 0 && isShuffled) {
            cards = shuffle(cards)
        }

        const flipper = document.getElementById("flipper");
        if (flipper.classList.contains("flipped")) {
            flipper.classList.remove("flipped");
            setTimeout(() => {
                renderCard();
            }, 600)
        } else {
            renderCard();   
        }
    };


    window.toggleShuffle = function () {
        isShuffled = !isShuffled;

        const toggleBtn = document.getElementById("shuffle-toggle");
        toggleBtn.classList.toggle("btn-secondary", !isShuffled);
        toggleBtn.classList.toggle("btn-primary", isShuffled);
        toggleBtn.innerText = `Shuffle: ${isShuffled ? 'ON' : 'OFF'}`;

        if (isShuffled){
            cards = shuffle(cards)
        }
        current = 0;
        showingQuestion = true;
        renderCard();
    };
    
    renderCard();
});
