// =====================================
// PHISHING AWARENESS LAB
// Dashboard JavaScript
// =====================================

document.addEventListener("DOMContentLoaded", () => {

    console.log("Phishing Awareness Lab iniciado!");

    // Navegação do menu lateral
    const menuLinks = document.querySelectorAll(".sidebar nav a");

    menuLinks.forEach(link => {

        link.addEventListener("click", function () {

            menuLinks.forEach(item => {
                item.classList.remove("active");
            });

            this.classList.add("active");

        });

    });

    // Efeito de entrada nos cards
    const cards = document.querySelectorAll(".card");

    cards.forEach((card, index) => {

        card.style.opacity = "0";

        setTimeout(() => {
            card.style.transition = "opacity 0.6s ease";
            card.style.opacity = "1";
        }, index * 200);

    });

    // Data atual
    const data = new Date();

    console.log(
        "Data de acesso:",
        data.toLocaleDateString("pt-BR")
    );

});