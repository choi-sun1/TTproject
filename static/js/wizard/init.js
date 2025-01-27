document.addEventListener('DOMContentLoaded', function() {
    // AOS 초기화
    AOS.init({
        duration: 800,
        once: true,
        offset: 100
    });

    // 숫자 애니메이션
    const animateValue = (element, start, end, duration) => {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            element.textContent = Math.floor(progress * (end - start) + start).toLocaleString();
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    };

    // 통계 숫자 애니메이션
    document.querySelectorAll('.number').forEach(el => {
        const finalValue = parseInt(el.textContent.replace(/,/g, ''));
        animateValue(el, 0, finalValue, 2000);
    });

    // 모달 기능
    const modal = document.getElementById('examplesModal');
    const closeBtn = document.querySelector('.close');

    window.showExamples = function() {
        modal.style.display = 'block';
        initSwiper();
    };

    if (closeBtn) {
        closeBtn.onclick = function() {
            modal.style.display = 'none';
        };
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    };

    // Swiper 초기화 함수
    function initSwiper() {
        if (!window.exampleSwiper) {
            window.exampleSwiper = new Swiper('.swiper-container', {
                slidesPerView: 1,
                spaceBetween: 30,
                navigation: {
                    nextEl: '.swiper-button-next',
                    prevEl: '.swiper-button-prev',
                },
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true
                }
            });
        }
    }

    // 애니메이션 효과
    const featureCards = document.querySelectorAll('.feature-card');
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    featureCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        observer.observe(card);
    });
});
