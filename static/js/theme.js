document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;
    const bodyElement = document.body;

    // 저장된 테마 불러오기
    const loadTheme = () => {
        const savedTheme = localStorage.getItem('theme') || 'light';
        applyTheme(savedTheme);
    };

    // 테마 적용 함수
    const applyTheme = (theme) => {
        htmlElement.setAttribute('data-theme', theme);
        bodyElement.setAttribute('data-theme', theme);
        updateThemeIcon(theme);
    };

    // 아이콘 업데이트 함수
    const updateThemeIcon = (theme) => {
        if (!themeToggle) return;

        const sunIcon = themeToggle.querySelector('.fa-sun');
        const moonIcon = themeToggle.querySelector('.fa-moon');
        
        if (sunIcon && moonIcon) {
            if (theme === 'dark') {
                sunIcon.style.display = 'inline-block';
                moonIcon.style.display = 'none';
            } else {
                sunIcon.style.display = 'none';
                moonIcon.style.display = 'inline-block';
            }
        }
    };

    // 초기 테마 로드
    loadTheme();

    // 테마 토글 버튼 이벤트 리스너
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            applyTheme(newTheme);
            localStorage.setItem('theme', newTheme);

            // 쿠키에도 테마 저장 (서버 사이드 렌더링을 위해)
            document.cookie = `darkMode=${newTheme}; path=/; max-age=${365 * 24 * 60 * 60}`;
        });
    }
});
