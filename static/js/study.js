document.addEventListener("DOMContentLoaded", () => {
    const cards = window.cards;

    if (!Array.isArray(cards)) {
        console.error("Cards are not valid.");
        return;
    }

    let current = 0;
    let showingQuestion = true;

    function renderCard() {
        const card = cards[current];
        document.getElementById("card-front").innerText = card.question;
        document.getElementById("card-back").innerText = card.answer;

        const flipper = document.getElementById("card-flipper");
        if (showingQuestion) {
            flipper.classList.remove("flipped");
        } else {
            flipper.classList.add("flipped");
        }
    }

    window.flipCard = function () {
        showingQuestion = !showingQuestion;
        renderCard();
    };

    window.nextCard = function () {
        current = (current + 1) % cards.length;
        showingQuestion = true;
        renderCard();
    };

    renderCard();
});
