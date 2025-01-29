document.addEventListener('DOMContentLoaded', function() {
    // 현재 페이지 URL에 해당하는 nav-link에 active 클래스 추가
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // 모바일 메뉴 토글 기능
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const navMenu = document.querySelector('.nav-menu');
    
    if (mobileMenuButton) {
        mobileMenuButton.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            mobileMenuButton.classList.toggle('active');
        });
    }

    // 드롭다운 메뉴 기능
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const dropdown = this.nextElementSibling;
            
            // 다른 열린 드롭다운 닫기
            dropdownToggles.forEach(otherToggle => {
                if (otherToggle !== this) {
                    otherToggle.nextElementSibling.classList.remove('show');
                    otherToggle.classList.remove('active');
                }
            });
            
            // 현재 드롭다운 토글
            dropdown.classList.toggle('show');
            this.classList.toggle('active');
        });
    });

    // 스크롤 시 네비게이션 바 스타일 변경
    let lastScroll = 0;
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > lastScroll && currentScroll > 100) {
            // 아래로 스크롤
            navbar.classList.add('navbar-hidden');
        } else {
            // 위로 스크롤
            navbar.classList.remove('navbar-hidden');
        }
        
        // 스크롤 위치에 따른 배경색 변경
        if (currentScroll > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
        
        lastScroll = currentScroll;
    });

    // 문서 클릭 시 드롭다운 닫기
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.nav-item')) {
            dropdownToggles.forEach(toggle => {
                toggle.nextElementSibling.classList.remove('show');
                toggle.classList.remove('active');
            });
        }
    });

    // 현재 활성 메뉴 표시
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
            // 부모 드롭다운이 있는 경우 활성화
            const parentDropdown = link.closest('.dropdown');
            if (parentDropdown) {
                parentDropdown.querySelector('.dropdown-toggle').classList.add('active');
            }
        }
    });

    // 알림 메시지 자동 숨김
    const messages = document.querySelectorAll('.alert');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
});
