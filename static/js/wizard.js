// 일정 생성 마법사 공통 함수들

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showLoadingSpinner() {
    // 로딩 스피너 표시
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner';
    document.body.appendChild(spinner);
}

function hideLoadingSpinner() {
    // 로딩 스피너 제거
    const spinner = document.querySelector('.loading-spinner');
    if (spinner) {
        spinner.remove();
    }
}

function showError(message) {
    // 에러 메시지 표시
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 3000);
}

// ... 추가 유틸리티 함수들 ...
