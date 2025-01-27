document.addEventListener('DOMContentLoaded', function() {
    // 시스템 테마 감지
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
    // 저장된 테마 불러오기
    const currentTheme = localStorage.getItem('theme');
    
    // 초기 테마 설정
    if (currentTheme) {
        document.documentElement.setAttribute('data-theme', currentTheme);
    } else {
        const systemTheme = prefersDarkScheme.matches ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', systemTheme);
        localStorage.setItem('theme', systemTheme);
    }
    
    // 테마 전환 함수
    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    }

    // 테마 버튼에 이벤트 리스너 추가
    const themeToggler = document.getElementById('theme-toggle');
    if (themeToggler) {
        themeToggler.addEventListener('click', toggleTheme);
    }

    // 시스템 테마 변경 감지
    prefersDarkScheme.addListener((e) => {
        if (!localStorage.getItem('theme')) {
            const newTheme = e.matches ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
        }
    });
});
