// document.addEventListener("DOMContentLoaded", () => {
//     loadTransactions();
// });

// function loadTransactions(query = "") {
//     fetch(`/api/transactions?search=${encodeURIComponent(query)}`, {
//         credentials: "include"
//     })
//     .then(res => res.json())
//     .then(data => {
//         const rows = Array.isArray(data) ? data : (data.transactions || []);
//         const tbody = document.getElementById("transactionTableBody") || document.querySelector("tbody");
//         if (!tbody) return;

//         tbody.innerHTML = "";

//         if (rows.length === 0) {
//             tbody.innerHTML = `
//                 <tr>
//                     <td class="py-6 px-4 text-sm text-gray-500" colspan="5">No transactions found</td>
//                 </tr>
//             `;
//             return;
//         }

//         rows.forEach(tx => {
//             const type = String(tx.type || "").toLowerCase();
//             const isExpense = type === "expense";
//             const amountClass = isExpense ? "text-red-600" : "text-green-600";
//             const amountPrefix = isExpense ? "-" : "+";

//             tbody.innerHTML += `
//                 <tr>
//                     <td>
//                         <strong>${tx.title || ""}</strong><br>
//                         <small>${tx.category || ""}</small>
//                     </td>
//                     <td class="${amountClass}">${amountPrefix}₹${tx.amount}</td>
//                     <td>${tx.date || ""}</td>
//                     <td>${tx.type || ""}</td>
//                     <td>
//                         <a href="edittransaction.html?id=${tx.id}" class="text-primary">Edit</a>
//                         |
//                         <button onclick="deleteTransaction(${tx.id})" class="text-red-600">Delete</button>
//                     </td>
//                 </tr>
//             `;
//         });
//     })
//     .catch(err => console.error("Error loading transactions:", err));
// }

// function deleteTransaction(id) {
//     if (!confirm("Delete this transaction?")) return;

//     fetch(`/api/transactions/${id}`, {
//         method: "DELETE",
//         credentials: "include"
//     })
//     .then(res => res.json())
//     .then(data => {
//         alert(data.message || "Deleted");
//         loadTransactions();
//     })
//     .catch(err => console.error("Error deleting transaction:", err));
// }

// // Search
// const searchInput = document.getElementById("searchInput");
// if (searchInput) {
//     searchInput.addEventListener("input", (e) => {
//         loadTransactions(e.target.value);
//     });
// }


const currency = "\u20B9";
const pageSize = 10;
let currentPage = 1;
let currentQuery = "";

document.addEventListener("DOMContentLoaded", () => {
    loadTransactions();
});

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric"
    });
}

function loadTransactions(query = "", page = 1) {
    currentQuery = query;
    currentPage = page;

    fetch(`/api/transactions?search=${encodeURIComponent(query)}&page=${page}&page_size=${pageSize}`, {
        credentials: "include"
    })
    .then(res => res.json())
    .then(data => {

        const rows = Array.isArray(data) ? data : (data.transactions || []);
        const total = Array.isArray(data) ? rows.length : (data.total || rows.length);
        const pageSizeFromApi = Array.isArray(data) ? rows.length || pageSize : (data.page_size || pageSize);
        const pageFromApi = Array.isArray(data) ? 1 : (data.page || 1);
        const totalPages = Math.max(1, Math.ceil(total / pageSizeFromApi));

        if (pageFromApi > totalPages && totalPages > 0) {
            loadTransactions(query, totalPages);
            return;
        }

        if (data && data.month_summary) {
            updateSummaryCardsFromSummary(data.month_summary);
        } else {
            updateSummaryCards(rows);
        }

        const tbody = document.getElementById("transactionTableBody");

        if (!tbody) return;

        tbody.innerHTML = "";

        if (rows.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center py-6 text-gray-400">
                        No transactions found
                    </td>
                </tr>
            `;
            if (!data || !data.month_summary) {
                updateSummaryCards([]);
            }
            renderPagination(total, pageFromApi, pageSizeFromApi);
            return;
        }

        renderPagination(total, pageFromApi, pageSizeFromApi);

        rows.forEach(tx => {
            const typeLabel = String(tx.type || "");
            const isExpense = typeLabel.toLowerCase() === "expense";
            const amountClass = isExpense ? "text-red-500" : "text-green-500";
            const badgeClass = isExpense
                ? "bg-red-100 text-red-800"
                : "bg-green-100 text-green-800";

            const row = `
                <tr class="border-b dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td class="p-4">
                        <input type="checkbox" class="w-4 h-4 text-primary">
                    </td>

                    <td class="px-6 py-4">
                        <div class="font-medium">${tx.title}</div>
                        <div class="text-xs text-gray-500">${tx.category}</div>
                    </td>

                    <td class="px-6 py-4 font-semibold ${amountClass}">
                        ${isExpense ? "-" : "+"}${currency}${tx.amount}
                    </td>

                    <td class="px-6 py-4">
                        ${formatDate(tx.date)}
                    </td>

                    <td class="px-6 py-4">
                        <span class="px-2 py-1 rounded-full text-xs ${badgeClass}">
                            ${typeLabel}
                        </span>
                    </td>

                    <td class="px-6 py-4 text-right space-x-2">
                        <a href="/edittransaction?id=${tx.id}" 
                            class="text-blue-500 hover:underline">
                            Edit
                        </a>
                        <button onclick="deleteTransaction(${tx.id})"
                            class="text-red-500 hover:underline">
                            Delete
                        </button>
                    </td>

                </tr>
            `;

            tbody.innerHTML += row;
        });
    })
    .catch(err => console.error("Error loading transactions:", err));
}

function updateSummaryCards(rows) {
    const totalIncomeEl = document.getElementById("totalIncomeMonth");
    const totalExpenseEl = document.getElementById("totalExpenseMonth");
    const balanceEl = document.getElementById("balanceMonth");

    if (!totalIncomeEl && !totalExpenseEl && !balanceEl) {
        return;
    }

    const now = new Date();
    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();

    let income = 0;
    let expense = 0;

    rows.forEach(tx => {
        const date = new Date(tx.date);
        if (Number.isNaN(date.getTime())) {
            return;
        }

        if (date.getMonth() !== currentMonth || date.getFullYear() !== currentYear) {
            return;
        }

        const type = String(tx.type || "").toLowerCase();
        const amount = Number(tx.amount) || 0;

        if (type === "expense") {
            expense += amount;
        } else if (type === "income") {
            income += amount;
        }
    });

    const balance = income - expense;
    const formatter = new Intl.NumberFormat("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    if (totalIncomeEl) totalIncomeEl.innerText = `${currency}${formatter.format(income)}`;
    if (totalExpenseEl) totalExpenseEl.innerText = `${currency}${formatter.format(expense)}`;
    if (balanceEl) balanceEl.innerText = `${currency}${formatter.format(balance)}`;
}

function updateSummaryCardsFromSummary(summary) {
    const totalIncomeEl = document.getElementById("totalIncomeMonth");
    const totalExpenseEl = document.getElementById("totalExpenseMonth");
    const balanceEl = document.getElementById("balanceMonth");

    if (!totalIncomeEl && !totalExpenseEl && !balanceEl) {
        return;
    }

    const income = Number(summary.income) || 0;
    const expense = Number(summary.expense) || 0;
    const balance = Number(summary.balance) || (income - expense);

    const formatter = new Intl.NumberFormat("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    if (totalIncomeEl) totalIncomeEl.innerText = `${currency}${formatter.format(income)}`;
    if (totalExpenseEl) totalExpenseEl.innerText = `${currency}${formatter.format(expense)}`;
    if (balanceEl) balanceEl.innerText = `${currency}${formatter.format(balance)}`;
}

function renderPagination(total, page, pageSize) {
    const list = document.getElementById("transactionsPaginationList");
    const info = document.getElementById("transactionsPaginationInfo");

    if (!list) return;

    const totalPages = Math.max(1, Math.ceil(total / pageSize));
    const start = total === 0 ? 0 : (page - 1) * pageSize + 1;
    const end = total === 0 ? 0 : Math.min(total, page * pageSize);

    if (info) {
        info.textContent = `Showing ${start}-${end} of ${total}`;
    }

    list.innerHTML = "";

    const createItem = (label, targetPage, disabled, active) => {
        const li = document.createElement("li");
        const btn = document.createElement("button");
        btn.type = "button";
        btn.textContent = label;
        btn.className = "flex items-center justify-center px-3 h-8 leading-tight border border-gray-300 dark:border-gray-700";

        if (active) {
            btn.className += " text-primary bg-primary/10 dark:bg-gray-700 dark:text-white";
        } else {
            btn.className += " text-gray-500 bg-white hover:bg-gray-100 hover:text-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white";
        }

        if (disabled) {
            btn.disabled = true;
            btn.className += " opacity-50 cursor-not-allowed";
        } else {
            btn.addEventListener("click", () => loadTransactions(currentQuery, targetPage));
        }

        li.appendChild(btn);
        return li;
    };

    list.appendChild(createItem("Previous", Math.max(1, page - 1), page === 1, false));

    let startPage = Math.max(1, page - 2);
    let endPage = Math.min(totalPages, startPage + 4);
    startPage = Math.max(1, endPage - 4);

    for (let p = startPage; p <= endPage; p += 1) {
        list.appendChild(createItem(String(p), p, false, p === page));
    }

    list.appendChild(createItem("Next", Math.min(totalPages, page + 1), page === totalPages, false));
}

function deleteTransaction(id) {
    if (!confirm("Delete this transaction?")) return;

    fetch(`/api/transactions/${id}`, {
        method: "DELETE",
        credentials: "include"
    })
    .then(res => res.json())
    .then(() => {
        loadTransactions(currentQuery, currentPage);
    })
    .catch(err => console.error("Error deleting transaction:", err));
}

const searchInput = document.getElementById("searchInput");
if (searchInput) {
    searchInput.addEventListener("input", (e) => {
        loadTransactions(e.target.value, 1);
    });
}
