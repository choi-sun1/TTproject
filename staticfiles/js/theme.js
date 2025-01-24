document.addEventListener('DOMContentLoaded', function() {
    // 테마 토글 버튼 요소 가져오기
    const themeToggle = document.querySelector('.theme-toggle');
    
    // 저장된 테마 불러오기
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    document.body.setAttribute('data-theme', currentTheme);
    
    // 아이콘 업데이트
    updateThemeIcon(currentTheme);
    
    // 테마 토글 이벤트 리스너
    themeToggle.addEventListener('click', function() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        // HTML과 body에 테마 적용
        document.documentElement.setAttribute('data-theme', newTheme);
        document.body.setAttribute('data-theme', newTheme);
        
        // 로컬 스토리지에 테마 저장
        localStorage.setItem('theme', newTheme);
        
        // 아이콘 업데이트
        updateThemeIcon(newTheme);
    });
});

// 아이콘 업데이트 함수
function updateThemeIcon(theme) {
    const themeToggle = document.querySelector('.theme-toggle');
    const icon = themeToggle.querySelector('i');
    
    if (theme === 'dark') {
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
    } else {
        icon.classList.remove('fa-sun');
        icon.classList.add('fa-moon');
    }
}
