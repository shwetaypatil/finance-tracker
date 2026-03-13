// language.js

const translations = {
    en: {
        dashboard: "Dashboard",
        transactions: "Transactions",
        settings: "Settings",
        logout: "Logout",
        // Add more keys...
    },
    hi: {
        dashboard: "डैशबोर्ड",
        transactions: "लेन-देन",
        settings: "सेटिंग्स",
        logout: "लॉग आउट",
    },
    mr: {
        dashboard: "डॅशबोर्ड",
        transactions: "व्यवहार",
        settings: "सेटिंग्ज",
        logout: "लॉग आउट",
    }
};

function translatePage() {
    const lang = localStorage.getItem("language") || "en";
    
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (translations[lang] && translations[lang][key]) {
            el.textContent = translations[lang][key];
        }
    });
}
