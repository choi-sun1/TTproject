document.addEventListener('DOMContentLoaded', function() {
    const themeToggleBtn = document.querySelector('.theme-toggle-btn');
    
    // 테마 전환 함수
    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        document.body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        updateThemeIcon(newTheme);
    }

    // 아이콘 업데이트 함수
    function updateThemeIcon(theme) {
        const sunIcon = themeToggleBtn.querySelector('.fa-sun');
        const moonIcon = themeToggleBtn.querySelector('.fa-moon');
        
        if (theme === 'dark') {
            sunIcon.style.display = 'inline-block';
            moonIcon.style.display = 'none';
        } else {
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'inline-block';
        }
    }

    // 테마 버튼 이벤트 리스너
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }

    // 초기 테마 설정
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    document.body.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
});
