document.addEventListener("DOMContentLoaded", () => {
    const saveBtn = document.getElementById("saveBudgetBtn");
    const input = document.getElementById("budgetInput");

    if (!saveBtn || !input) {
        console.error("Budget elements not found");
        return;
    }

    // 🔹 Load current budget on page load
    loadBudget();

    // 🔹 Save budget
    saveBtn.addEventListener("click", async () => {
        const amount = Number(input.value);

        if (!Number.isFinite(amount) || amount <= 0) {
            showAlert("dangerAlert", "Enter a valid budget amount");
            return;
        }

        try {
            const res = await fetch("/api/budget", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ amount })
            });

            const data = await res.json();

            if (!res.ok) {
                showAlert("dangerAlert", data.error || "Server error. Try again.");
                return;
            }

            showAlert("successAlert", "Budget saved successfully!");

            // Reload updated budget values
            loadBudget();

        } catch (err) {
            console.error(err);
            showAlert("dangerAlert", "Server error. Try again.");
        }
    });
});


/* =============================
   Load current budget from API
   ============================= */
async function loadBudget() {
    try {
        const res = await fetch("/api/budget/current", {
            credentials: "include"
        });

        if (!res.ok) return;

        const data = await res.json();

        document.getElementById("totalBudget").textContent =
            "₹" + (data.amount || 0).toFixed(2);

        document.getElementById("amountUsed").textContent =
            "₹" + (data.used || 0).toFixed(2);

        document.getElementById("amountRemaining").textContent =
            "₹" + (data.remaining || 0).toFixed(2);

        const progressBar = document.getElementById("budgetProgressBar");
        const percentText = document.getElementById("budgetPercentText");
        const budgetInput = document.getElementById("budgetInput");

        if (budgetInput) {
            budgetInput.value = data.amount ? Number(data.amount).toFixed(2) : "";
        }

        if (progressBar && percentText) {
            const percent = data.percent || 0;

            progressBar.style.width = percent + "%";
            percentText.textContent = percent.toFixed(0) + "% Used";

            // Change color dynamically
            if (percent < 50) {
                progressBar.className = "bg-green-500 h-4 rounded-full transition-all duration-500";
            } else if (percent < 80) {
                progressBar.className = "bg-yellow-500 h-4 rounded-full transition-all duration-500";
            } else {
                progressBar.className = "bg-red-500 h-4 rounded-full transition-all duration-500";
            }
        }
    } catch (err) {
        console.error("Error loading budget:", err);
    }
}


/* =============================
   Alert helper
   ============================= */
function showAlert(id, message) {
    ["warningAlert", "dangerAlert", "successAlert"].forEach(a =>
        document.getElementById(a)?.classList.add("hidden")
    );

    const box = document.getElementById(id);
    if (!box) return;

    box.querySelector("p").innerText = message;
    box.classList.remove("hidden");

    setTimeout(() => {
        box.classList.add("hidden");
    }, 3000);
}
