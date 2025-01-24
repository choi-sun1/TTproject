document.addEventListener('DOMContentLoaded', function() {
    // 현재 페이지 URL에 해당하는 nav-link에 active 클래스 추가
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // 모바일 메뉴 토글 기능
    const navbar = document.querySelector('.navbar');
    const navbarMenu = document.querySelector('.navbar-menu');
    let lastScrollTop = 0;

    // 스크롤 시 네비게이션 바 숨김/표시
    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > lastScrollTop) {
            // 아래로 스크롤
            navbar.style.transform = 'translateY(-100%)';
        } else {
            // 위로 스크롤
            navbar.style.transform = 'translateY(0)';
        }
        lastScrollTop = scrollTop;
    });

    // 드롭다운 메뉴 클릭 이벤트
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            const dropdown = toggle.parentElement;
            dropdown.classList.toggle('active');
        });
    });

    // 드롭다운 메뉴 외부 클릭 시 닫기
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown.active').forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        }
    });

    const mobileMenuButton = document.querySelector('.mobile-menu-button');

    mobileMenuButton.addEventListener('click', function() {
        navbarMenu.classList.toggle('active');
    });

    // 화면 크기가 변경될 때 메뉴 상태 초기화
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            navbarMenu.classList.remove('active');
        }
    });
});
