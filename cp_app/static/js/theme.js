// theme.js - управление темами
class ThemeManager {
    constructor() {
        this.themeToggle = document.getElementById('themeToggle');
        this.init();
    }

    init() {
        // Тема уже применена inline скриптом, просто обновляем кнопку
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        this.updateButton(currentTheme);
        
        // Добавляем обработчик клика
        if (this.themeToggle) {
            this.themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        // Применяем новую тему
        document.documentElement.setAttribute('data-theme', newTheme);
        
        // Сохраняем и обновляем кнопку
        this.saveTheme(newTheme);
        this.updateButton(newTheme);
    }

    updateButton(theme) {
        if (!this.themeToggle) return;
        
        const iconClass = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
        const buttonText = theme === 'dark' ? 'Светлая' : 'Тёмная';
        
        this.themeToggle.innerHTML = `<i class="${iconClass}"></i> ${buttonText}`;
    }

    saveTheme(theme) {
        try {
            localStorage.setItem('theme', theme);
        } catch (e) {
            console.log('Failed to save theme:', e);
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    new ThemeManager();
});