const currency = "\u20B9";
const amountFormatter = new Intl.NumberFormat("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
});

document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
    loadDashboardCharts();
});

let monthlyChartInstance = null;
let categoryChartInstance = null;

function loadDashboard() {
    fetch("/dashboard-data", {
        credentials: "include"
    })
    .then(res => res.json())
    .then(data => {
        if (!data || data.error) {
            console.error("Dashboard load failed", data && data.error);
            return;
        }

        // Stats
        const totalIncomeEl = document.getElementById("totalIncome");
        const totalExpenseEl = document.getElementById("totalExpense");
        const currentBalanceEl = document.getElementById("currentBalance");

        if (totalIncomeEl) totalIncomeEl.innerText = currency + amountFormatter.format(data.total_income)
        if (totalExpenseEl) totalExpenseEl.innerText = currency + data.total_expense;
        if (currentBalanceEl) currentBalanceEl.innerText = currency + data.balance;

        // Budget
        const spendingPercentEl = document.getElementById("spendingPercent");
        const spendingBarEl = document.getElementById("spendingBar");
        const monthlyBudgetEl = document.getElementById("monthlyBudget");

        const budgetPercent = data.budget_used_percent || 0;
        if (spendingPercentEl) spendingPercentEl.innerText = budgetPercent + "% Used";
        if (spendingBarEl) spendingBarEl.style.width = budgetPercent + "%";
        if (monthlyBudgetEl) {
            monthlyBudgetEl.innerText = `${currency}${data.budget_spent} / ${currency}${data.budget_total} spent`;
        }

        // Recent transactions
        renderRecentTransactions(data.recent_transactions || [], currency);
    })
    .catch(err => console.error(err));
}

function loadDashboardCharts() {
    fetch("/dashboard-charts", {
        credentials: "include"
    })
    .then(res => res.json())
    .then(data => {
        if (!data || data.error) {
            console.error("Dashboard charts load failed", data && data.error);
            return;
        }

        renderMonthlyChart(data.months || [], data.income || [], data.expense || []);
        renderCategoryChart(data.categories || [], data.category_total || 0);
    })
    .catch(err => console.error("Dashboard charts load failed", err));
}

function renderMonthlyChart(labels, incomeData, expenseData) {
    const canvas = document.getElementById("monthlyChart");
    if (!canvas || typeof Chart === "undefined") {
        return;
    }

    if (monthlyChartInstance) {
        monthlyChartInstance.destroy();
    }

    monthlyChartInstance = new Chart(canvas, {
        type: "bar",
        data: {
            labels,
            datasets: [
                {
                    label: "Income",
                    data: incomeData,
                    backgroundColor: "#50E3C2",
                    borderRadius: 6
                },
                {
                    label: "Expense",
                    data: expenseData,
                    backgroundColor: "#F5A623",
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => `${currency}${amountFormatter.format(value)}`
                    }
                }
            },
            plugins: {
                legend: {
                    position: "bottom"
                }
            }
        }
    });
}

function renderCategoryChart(categories, total) {
    const canvas = document.getElementById("categoryChart");
    const legend = document.getElementById("categoryLegend");
    const totalEl = document.getElementById("categoryTotal");

    if (!canvas || typeof Chart === "undefined") {
        return;
    }

    const safeTotal = Number(total) || 0;
    if (totalEl) {
        totalEl.innerText = `${currency}${amountFormatter.format(safeTotal)}`;
    }

    const labels = categories.map(item => item.category || "Uncategorized");
    const values = categories.map(item => Number(item.total) || 0);

    const colors = ["#F5A623", "#8B5CF6", "#34D399", "#60A5FA", "#FBBF24", "#10B981", "#3B82F6"];
    const backgroundColors = labels.map((_, index) => colors[index % colors.length]);

    if (categoryChartInstance) {
        categoryChartInstance.destroy();
    }

    categoryChartInstance = new Chart(canvas, {
        type: "doughnut",
        data: {
            labels,
            datasets: [
                {
                    data: values,
                    backgroundColor: backgroundColors,
                    borderWidth: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "70%",
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });

    if (legend) {
        if (!values.length || safeTotal === 0) {
            legend.innerHTML = "<span class=\"text-text-light-secondary dark:text-text-dark-secondary\">No expense data</span>";
            return;
        }

        legend.innerHTML = labels.map((label, index) => {
            const value = values[index];
            const percent = safeTotal ? Math.round((value / safeTotal) * 100) : 0;
            return `
                <div class="flex items-center gap-2">
                    <span class="size-2.5 rounded-full" style="background-color: ${backgroundColors[index]}"></span>
                    <span>${label} (${percent}%)</span>
                </div>
            `;
        }).join("");
    }
}

function renderRecentTransactions(transactions, currency) {
    const tbody = document.getElementById("recentTransactionsBody") || document.querySelector("tbody");
    if (!tbody) {
        return;
    }

    tbody.innerHTML = "";

    if (!transactions.length) {
        tbody.innerHTML = `
            <tr>
                <td class="py-6 pl-6 pr-3 text-sm text-text-light-secondary dark:text-text-dark-secondary" colspan="4">
                    No recent transactions
                </td>
            </tr>
        `;
        return;
    }

    transactions.forEach(tx => {
        const typeLabel = tx.type || "";
        const isExpense = String(typeLabel).toLowerCase() === "expense";
        const amountPrefix = isExpense ? "-" : "+";
        const amountClass = isExpense ? "text-sm font-medium" : "text-sm font-medium text-green-500";
        const badgeClass = isExpense ? "bg-warning/10 text-warning" : "bg-success/10 text-success";

        tbody.innerHTML += `
            <tr>
                <td class="whitespace-nowrap py-4 pl-6 pr-3 text-sm">
                    <div class="font-medium">${tx.title || ""}</div>
                    <div class="text-text-light-secondary dark:text-text-dark-secondary">${tx.category || ""}</div>
                </td>
                <td class="whitespace-nowrap px-3 py-4 ${amountClass}">${amountPrefix}${currency}${tx.amount}</td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-text-light-secondary dark:text-text-dark-secondary">${tx.date || ""}</td>
                <td class="whitespace-nowrap px-3 py-4 text-sm">
                    <span class="inline-flex items-center rounded-full ${badgeClass} px-2 py-1 text-xs font-medium">${typeLabel}</span>
                </td>
            </tr>
        `;
    });
}
