// theme.js - управление темами
class ThemeManager {
    constructor() {
        this.themeToggle = document.getElementById('themeToggle');
        this.init();
    }

    init() {
        // Загружаем сохраненную тему или устанавливаем светлую по умолчанию
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.applyTheme(savedTheme);
        
        // Добавляем обработчик клика на кнопку
        if (this.themeToggle) {
            this.themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
        this.saveTheme(newTheme);
    }

    applyTheme(theme) {
        // Устанавливаем атрибут для CSS
        document.documentElement.setAttribute('data-theme', theme);
        
        // Обновляем кнопку
        this.updateButton(theme);
    }

    updateButton(theme) {
        if (!this.themeToggle) return;
        
        const icon = this.themeToggle.querySelector('i');
        if (theme === 'dark') {
            icon.className = 'bi bi-sun-fill';
            this.themeToggle.innerHTML = `<i class="bi bi-sun-fill"></i> Светлая`;
        } else {
            icon.className = 'bi bi-moon-fill';
            this.themeToggle.innerHTML = `<i class="bi bi-moon-fill"></i> Тёмная`;
        }
    }

    saveTheme(theme) {
        localStorage.setItem('theme', theme);
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    new ThemeManager();
});
