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

function formatTime(date) {
    return date.toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });
}

function calculateDuration(start, end) {
    const startTime = new Date(`1970-01-01T${start}`);
    const endTime = new Date(`1970-01-01T${end}`);
    const diff = endTime - startTime;
    return Math.round(diff / (1000 * 60)); // 분 단위로 반환
}

function applyDurationToSelectedPlaces() {
    const duration = parseInt(document.getElementById('visitDuration').value);
    const timeline = document.getElementById('scheduleTimeline');
    const items = timeline.querySelectorAll('.timeline-item');
    
    let currentTime = new Date();
    currentTime.setHours(9, 0, 0); // 시작 시간을 09:00로 설정
    
    items.forEach(item => {
        const startTime = formatTime(currentTime);
        currentTime.setMinutes(currentTime.getMinutes() + duration);
        const endTime = formatTime(currentTime);
        
        item.dataset.startTime = startTime;
        item.dataset.endTime = endTime;
        item.querySelector('.time-info').textContent = `${startTime} - ${endTime}`;
        
        // 이동 시간 추가 (30분)
        currentTime.setMinutes(currentTime.getMinutes() + 30);
    });
    
    updateScheduleData();
}

// 이벤트 리스너 등록
document.getElementById('applyDuration').addEventListener('click', applyDurationToSelectedPlaces);
