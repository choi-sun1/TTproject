document.addEventListener('DOMContentLoaded', function() {
    const startDateInput = document.getElementById('id_start_date');
    const endDateInput = document.getElementById('id_end_date');
    const durationText = document.getElementById('duration-text');
    const form = document.getElementById('itinerary-form');

    // 날짜 제한 설정
    const today = new Date().toISOString().split('T')[0];
    startDateInput.min = today;
    endDateInput.min = today;

    // 날짜 변경 이벤트 핸들러
    function updateDuration() {
        if (startDateInput.value && endDateInput.value) {
            const start = new Date(startDateInput.value);
            const end = new Date(endDateInput.value);
            const diffTime = Math.abs(end - start);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

            if (diffDays > 0) {
                durationText.textContent = `${diffDays}일간의 여행`;
                durationText.style.color = 'var(--text-primary)';
            } else {
                durationText.textContent = '종료일은 시작일보다 빠를 수 없습니다.';
                durationText.style.color = 'var(--error-color)';
            }
        }
    }

    // 시작일 변경 시 종료일 최소값 설정
    startDateInput?.addEventListener('change', function() {
        endDateInput.min = this.value;
        if (endDateInput.value && endDateInput.value < this.value) {
            endDateInput.value = this.value;
        }
        updateDuration();
    });

    // 종료일 변경 시 기간 업데이트
    endDateInput?.addEventListener('change', function() {
        if (this.value < startDateInput.value) {
            this.value = startDateInput.value;
            showError('종료일은 시작일보다 빠를 수 없습니다.');
        }
        updateDuration();
    });

    // 폼 제출 전 유효성 검사
    form?.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const title = document.getElementById('id_title').value.trim();
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;

        if (!title) {
            showError('제목을 입력해주세요.');
            return;
        }

        if (!startDate || !endDate) {
            showError('여행 기간을 선택해주세요.');
            return;
        }

        if (new Date(endDate) < new Date(startDate)) {
            showError('종료일은 시작일보다 빠를 수 없습니다.');
            return;
        }

        const scheduleData = [];
        document.querySelectorAll('.schedule-item').forEach(schedule => {
            const dayNumber = schedule.dataset.day;
            const timeslots = [];
            
            schedule.querySelectorAll('.time-slot').forEach(slot => {
                timeslots.push({
                    start_time: slot.querySelector('input[name="start_time[]"]').value,
                    end_time: slot.querySelector('input[name="end_time[]"]').value,
                    activity: slot.querySelector('input[name="activity[]"]').value,
                    category: slot.querySelector('select[name="category[]"]').value,
                    estimated_cost: slot.querySelector('input[name="estimated_cost[]"]').value,
                    note: slot.querySelector('textarea[name="note[]"]').value
                });
            });
            
            scheduleData.push({
                day_number: dayNumber,
                timeslots: timeslots
            });
        });
        
        // 숨겨진 입력 필드에 일정 데이터 저장
        const scheduleInput = document.createElement('input');
        scheduleInput.type = 'hidden';
        scheduleInput.name = 'schedule_data';
        scheduleInput.value = JSON.stringify(scheduleData);
        this.appendChild(scheduleInput);

        this.submit();
    });

    // 에러 메시지 표시
    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.textContent = message;
        
        const formHeader = document.querySelector('.form-header');
        const existingError = document.querySelector('.alert-danger');
        
        if (existingError) {
            existingError.remove();
        }
        
        formHeader.insertAdjacentElement('afterend', errorDiv);

        setTimeout(() => {
            errorDiv.remove();
        }, 3000);
    }

    // 공개 설정 토글 애니메이션
    const visibilityToggle = document.querySelector('.visibility-toggle input');
    if (visibilityToggle) {
        visibilityToggle.addEventListener('change', function() {
            const label = this.parentElement.querySelector('.toggle-label');
            label.textContent = this.checked ? '공개' : '비공개';
        });
    }

    // 페이지 로드 시 초기 기간 계산
    if (startDateInput?.value && endDateInput?.value) {
        updateDuration();
    }

    initializeScheduleManager();

    // 일차 탭 생성
    function createDayTabs() {
        const startDate = new Date(startDateInput.value);
        const endDate = new Date(endDateInput.value);
        const dayTabs = document.getElementById('day-tabs');
        dayTabs.innerHTML = '';

        let currentDate = new Date(startDate);
        let dayCount = 1;

        while (currentDate <= endDate) {
            const tab = document.createElement('div');
            tab.className = 'day-tab';
            tab.dataset.day = dayCount;
            tab.textContent = `${dayCount}일차`;
            tab.addEventListener('click', () => switchDay(dayCount));
            dayTabs.appendChild(tab);

            currentDate.setDate(currentDate.getDate() + 1);
            dayCount++;
        }

        // 첫 번째 탭 활성화
        if (dayTabs.firstChild) {
            dayTabs.firstChild.classList.add('active');
        }
    }

    // 일차 변경
    function switchDay(dayNumber) {
        document.querySelectorAll('.day-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-day="${dayNumber}"]`).classList.add('active');
        loadDaySchedule(dayNumber);
    }

    // 장소 검색
    const searchInput = document.getElementById('place-search');
    const searchResults = document.getElementById('search-results');
    
    let searchTimeout;
    searchInput?.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(async () => {
            const query = searchInput.value;
            if (query.length < 2) return;

            try {
                const response = await fetch(`/api/places/search/?query=${query}`);
                const data = await response.json();
                displaySearchResults(data);
            } catch (error) {
                console.error('Search failed:', error);
            }
        }, 300);
    });

    function displaySearchResults(places) {
        searchResults.innerHTML = places.map(place => `
            <div class="search-result-item" data-place-id="${place.id}">
                <div class="place-name">${place.name}</div>
                <div class="place-address">${place.address}</div>
            </div>
        `).join('');
    }

    // 장소 선택 시 빠른 추가 모달 표시
    searchResults?.addEventListener('click', (e) => {
        const item = e.target.closest('.search-result-item');
        if (item) {
            const placeId = item.dataset.placeId;
            showQuickAddModal(placeId);
        }
    });
});

// 일정 관리 기능 추가
function initializeScheduleManager() {
    const addScheduleBtn = document.getElementById('add-schedule');
    const dailySchedules = document.getElementById('daily-schedules');
    const scheduleTemplate = document.getElementById('schedule-template');
    const timeslotTemplate = document.getElementById('timeslot-template');
    
    // 일정 추가
    addScheduleBtn.addEventListener('click', () => {
        const scheduleCount = dailySchedules.children.length + 1;
        const newSchedule = scheduleTemplate.content.cloneNode(true);
        
        // 일차 번호 설정
        newSchedule.querySelector('.day-number').textContent = scheduleCount;
        newSchedule.querySelector('.schedule-item').dataset.day = scheduleCount;
        
        // 삭제 버튼 이벤트
        newSchedule.querySelector('.btn-remove-schedule').addEventListener('click', function() {
            this.closest('.schedule-item').remove();
            updateDayNumbers();
        });
        
        // 시간대 추가 버튼 이벤트
        newSchedule.querySelector('.btn-add-timeslot').addEventListener('click', function() {
            addTimeSlot(this.previousElementSibling);
        });
        
        dailySchedules.appendChild(newSchedule);
    });
    
    // 시간대 추가
    function addTimeSlot(container) {
        const newTimeslot = timeslotTemplate.content.cloneNode(true);
        
        // 삭제 버튼 이벤트
        newTimeslot.querySelector('.btn-remove-timeslot').addEventListener('click', function() {
            this.closest('.time-slot').remove();
        });
        
        // 시간 입력 자동 정렬
        const timeInputs = newTimeslot.querySelectorAll('input[type="time"]');
        timeInputs[0].addEventListener('change', function() {
            if (!timeInputs[1].value) {
                timeInputs[1].value = this.value;
            }
        });
        
        container.appendChild(newTimeslot);
    }
    
    // 일차 번호 업데이트
    function updateDayNumbers() {
        document.querySelectorAll('.schedule-item').forEach((item, index) => {
            item.querySelector('.day-number').textContent = index + 1;
            item.dataset.day = index + 1;
        });
    }
}
