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

// 서버 응답 처리 유틸리티 함수 추가
function handleServerResponse(response) {
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
}

// 로딩 관련 함수들
function showLoadingSpinner() {
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner';
    spinner.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    document.body.appendChild(spinner);
}

function hideLoadingSpinner() {
    const spinner = document.querySelector('.loading-spinner');
    if (spinner) spinner.remove();
}

function showError(message) {
    hideLoadingSpinner();
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 3000);
}

// 세션 스토리지 관련 유틸리티 함수들
const wizardStorage = {
    save: function(data) {
        sessionStorage.setItem('wizard_data', JSON.stringify(data));
    },

    load: function() {
        return JSON.parse(sessionStorage.getItem('wizard_data') || '{}');
    },

    clear: function() {
        sessionStorage.removeItem('wizard_data');
    }
};

// wizardData 전역 인터페이스 정의
const wizardDataStructure = {
    title: '',
    destination: '',
    startDate: '',
    endDate: '', 
    travelStyle: '',
    places: {
        attractions: [],
        accommodations: []
    },
    schedule: {
        days: {},
        unassigned: []
    },
    details: {
        budgets: {},
        checklist: [],
        notes: '',
        isPublic: true
    }
};

// 데이터 유효성 검사 함수
function validateWizardData(step) {
    const data = wizardStorage.load();
    
    switch(step) {
        case 2:
            return data.destination && data.start_date && data.end_date;
        case 3:
            return data.places && data.places.length > 0;
        case 4:
            return data.schedule && Object.keys(data.schedule).length > 0;
        default:
            return false;
    }
}

// 에러 처리 함수
function handleWizardError(error) {
    console.error('Wizard Error:', error);
    alert(error.message || '처리 중 오류가 발생했습니다.');
}

// 날짜 포맷팅 함수
function formatDate(date) {
    return new Date(date).toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// 시간 계산 함수
function calculateTimeDifference(start, end) {
    const startTime = new Date(`1970-01-01T${start}`);
    const endTime = new Date(`1970-01-01T${end}`);
    return (endTime - startTime) / (1000 * 60); // 분 단위 반환
}

// 스케줄 유효성 검사
function validateSchedule(schedule) {
    for (const day in schedule) {
        if (schedule[day].length === 0) {
            return false;
        }
    }
    return true;
}

// ... 추가 유틸리티 함수들 ...
