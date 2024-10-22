document.addEventListener("DOMContentLoaded", () => {
    const lines = document.querySelectorAll(".line");
    const background = document.querySelector(".background");
    let currentIndex = 0;

    function showLine(index) {
        if (index === 0 || index === 5 || index === 8) background.style.background = "#343751";
        else if (index === 7) background.style.background = "#000000";
        else background.style.background = "url(\"assets/background-" + index + ".png\") no-repeat center center/cover";
        lines.forEach((line, i) => {
            line.classList.remove("visible", "exit");
            if (i === index) line.classList.add("visible");
            else if (i === index - 1 || (index === 0 && i === lines.length - 1)) line.classList.add("exit");
        });
    }

    window.addEventListener("scroll", () => {
        const scrollPosition = window.scrollY;
        const blurValue = Math.min(scrollPosition / 100, 10);
        background.style.filter = "blur(" + blurValue + "px)";

        const newIndex = Math.floor(scrollPosition / window.innerHeight);
        if (newIndex !== currentIndex) {
            currentIndex = newIndex;
            showLine(currentIndex);
        }
    });

    showLine(currentIndex);
    document.body.style.height = (lines.length * window.innerHeight) + "px";
});
