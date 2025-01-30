// 전역 변수 선언
let map;                  // Google Maps 객체
let directionsService;    // 경로 계산 서비스
let directionsRenderer;   // 경로 표시 렌더러
let markers = [];         // 지도 마커 배열
let scheduleData = {      // 일정 데이터 저장소
    unassigned: [],      // 미배정 장소 목록
    days: {}            // 일차별 배정된 장소
};
let currentDay = 1;       // 현재 선택된 일차

// Google Maps 초기화 함수
function initMap() {
    try {
        console.log('Initializing map...'); // 디버깅용
        map = new google.maps.Map(document.getElementById('map'), {
            center: { lat: 36.5, lng: 127.5 },
            zoom: 7,
            mapTypeControl: false,
            streetViewControl: false,
            fullscreenControl: false
        });

        directionsService = new google.maps.DirectionsService();
        directionsRenderer = new google.maps.DirectionsRenderer({
            map: map,
            suppressMarkers: true
        });

        console.log('Map initialized successfully');
    } catch (error) {
        console.error('Error initializing map:', error);
    }
}

// CSRF 토큰 가져오기
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        // ...existing code...
    }
    return cookieValue;
}

// 시간 포맷팅 함수 (HH:MM 형식)
function formatTime(date) {
    return date.toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });
}

// DOM 요소 초기화 확인 함수 추가
function validateDOMElements() {
    const requiredElements = [
        'daysNav',
        'map',
        'unassignedAttractions',
        'unassignedAccommodations',
        'scheduleTimeline',
        'nextStep'  // 다음 단계 버튼 추가
    ];
    
    const missingElements = requiredElements.filter(id => !document.getElementById(id));
    
    if (missingElements.length > 0) {
        console.error('Missing DOM elements:', missingElements);
        return false;
    }
    return true;
}

// 페이지 초기화 이벤트 핸들러
document.addEventListener('DOMContentLoaded', function() {
    console.log('Step 3 initialized'); // 디버깅용
    
    // DOM 요소 검증
    if (!validateDOMElements()) {
        alert('페이지 구성 요소가 올바르게 로드되지 않았습니다.');
        return;
    }
    
    // 세션 데이터 로드 및 검증
    const wizardData = wizardStorage.load();
    console.log('Loaded wizard data:', wizardData); // 디버깅용

    if (!wizardData || !wizardData.places) {
        console.error('No wizard data found');
        alert('이전 단계의 데이터가 없습니다. 장소 선택 단계로 이동합니다.');
        window.location.href = '/itineraries/wizard/step2/';
        return;
    }

    // places 데이터의 구조 확인
    const { attractions = [], accommodations = [] } = wizardData.places;
    console.log('Attractions:', attractions); // 디버깅용
    console.log('Accommodations:', accommodations); // 디버깅용

    // 모든 장소를 미배정 목록에 추가
    scheduleData.unassigned = [
        ...attractions.map(place => ({ ...place, type: 'attraction' })),
        ...accommodations.map(place => ({ ...place, type: 'accommodation' }))
    ];

    console.log('Schedule data initialized:', scheduleData); // 디버깅용

    // 일정표 초기화
    if (wizardData.start_date && wizardData.end_date) {
        initializeSchedule({
            start_date: wizardData.start_date,
            end_date: wizardData.end_date
        });
    } else {
        console.error('Missing date information');
        alert('날짜 정보가 없습니다. 기본 정보 입력 단계로 이동합니다.');
        window.location.href = '/itineraries/wizard/step1/';
        return;
    }

    // 미배정 장소 표시
    displayUnassignedPlaces();

    // 지도 업데이트
    if (scheduleData.unassigned.length > 0) {
        const firstPlace = scheduleData.unassigned[0];
        map.setCenter({
            lat: parseFloat(firstPlace.latitude),
            lng: parseFloat(firstPlace.longitude)
        });
        map.setZoom(13);
    }

    // 첫 번째 일차 선택
    currentDay = 1;

    // 일정표 초기화
    if (wizardData.start_date && wizardData.end_date) {
        initializeSchedule({
            start_date: wizardData.start_date,
            end_date: wizardData.end_date
        });
    } else {
        console.error('Missing date information');
        alert('날짜 정보가 없습니다. 기본 정보 입력 단계로 이동합니다.');
        window.location.href = '/itineraries/wizard/step1/';
        return;
    }

    // 첫 번째 일차의 일정 표시
    showDaySchedule(currentDay);

    // 이벤트 리스너 설정
    setupEventListeners();
});

// 일정표 초기화 함수
function initializeSchedule(data) {
    // 총 여행 일수 계산
    const startDate = new Date(data.start_date);
    const endDate = new Date(data.end_date);
    const totalDays = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1;

    createDayTabs(totalDays); // 일차별 탭 생성
    displayUnassignedPlaces(); // 미배정 장소 표시
    showDaySchedule(1); // 첫째 날 일정 표시
}

// 일차별 탭 생성 함수
function createDayTabs(totalDays) {
    const nav = document.getElementById('daysNav');
    nav.innerHTML = '';
    
    // 각 일차별 탭 생성
    for (let i = 1; i <= totalDays; i++) {
        const tab = document.createElement('div');
        tab.className = 'day-tab';
        if (i === 1) tab.classList.add('active');
        
        tab.innerHTML = `
            <i class="fas fa-calendar-day"></i>
            <span>${i}일차</span>
        `;
        
        // 탭 클릭 이벤트 핸들러
        tab.addEventListener('click', () => {
            currentDay = i; // 현재 선택된 일차 업데이트
            document.querySelectorAll('.day-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            showDaySchedule(i);
        });
        
        nav.appendChild(tab);
        scheduleData.days[i] = scheduleData.days[i] || [];
    }
}

// 장소 클릭 이벤트 핸들러로 변경
function handlePlaceClick(placeId, action) {
    console.log('Handle place click:', placeId, action, 'currentDay:', currentDay); // 디버깅용
    
    if (action === 'add') {
        if (!currentDay) {
            alert('먼저 일차를 선택해주세요.');
            return;
        }
        if (!scheduleData.days[currentDay]) {
            scheduleData.days[currentDay] = [];
        }
        addToSchedule(placeId, currentDay);
    } else if (action === 'remove') {
        removeFromSchedule(placeId, currentDay);
    }
    updateRouteDisplay();
}

// 장소 위치 이동 함수 추가
function movePlaceInSchedule(placeId, direction) {
    const dayPlaces = scheduleData.days[currentDay];
    const currentIndex = dayPlaces.findIndex(place => place.id === placeId);
    
    if (currentIndex === -1) return;
    
    if (direction === 'up' && currentIndex > 0) {
        [dayPlaces[currentIndex], dayPlaces[currentIndex - 1]] = 
        [dayPlaces[currentIndex - 1], dayPlaces[currentIndex]];
    } else if (direction === 'down' && currentIndex < dayPlaces.length - 1) {
        [dayPlaces[currentIndex], dayPlaces[currentIndex + 1]] = 
        [dayPlaces[currentIndex + 1], dayPlaces[currentIndex]];
    }
    
    showDaySchedule(currentDay);
    updateRouteDisplay();
}

// 일정에 장소 추가 함수
function addToSchedule(placeId, day) {
    console.log('Adding place to schedule:', placeId, 'day:', day); // 디버깅용
    
    // placeId를 문자열로 변환하여 비교
    const place = scheduleData.unassigned.find(p => String(p.id) === String(placeId));
    if (!place) {
        console.error('Place not found:', placeId);
        return;
    }
    
    // 해당 일차가 없으면 배열 초기화
    if (!scheduleData.days[day]) {
        scheduleData.days[day] = [];
    }
    
    // 해당 일차의 일정에 장소 추가
    scheduleData.days[day].push(place);
    
    // 미배정 목록에서 제거
    scheduleData.unassigned = scheduleData.unassigned.filter(p => p.id !== placeId);
    
    console.log('Updated schedule data:', scheduleData); // 디버깅용
    
    // 화면 업데이트
    showDaySchedule(day);
    displayUnassignedPlaces();
    updateRouteDisplay();
}

// 일정에서 장소 제거 함수 수정
function removeFromSchedule(placeId, day) {
    console.log('Removing place from schedule:', placeId, 'day:', day); // 디버깅용
    
    const dayPlaces = scheduleData.days[day];
    if (!dayPlaces) return;
    
    // placeId를 문자열로 변환하여 비교
    const placeIndex = dayPlaces.findIndex(p => String(p.id) === String(placeId));
    if (placeIndex === -1) return;
    
    // 제거할 장소를 미배정 목록으로 이동
    const removedPlace = dayPlaces.splice(placeIndex, 1)[0];
    
    // 이미 미배정 목록에 있는지 확인
    const isAlreadyUnassigned = scheduleData.unassigned.some(p => String(p.id) === String(placeId));
    if (!isAlreadyUnassigned) {
        scheduleData.unassigned.push(removedPlace);
    }
    
    // 빈 일정인 경우에도 배열은 유지
    if (!scheduleData.days[day]) {
        scheduleData.days[day] = [];
    }
    
    // 화면 업데이트
    showDaySchedule(day);
    displayUnassignedPlaces();
    updateRouteDisplay();
    
    console.log('Updated schedule data:', scheduleData); // 디버깅용
}

// 일차별 일정 표시 함수
function showDaySchedule(day) {
    console.log('Showing schedule for day:', day); // 디버깅용
    currentDay = day;
    
    // 탭 활성화 상태 변경
    document.querySelectorAll('.day-tab').forEach(tab => {
        const dayNumber = parseInt(tab.querySelector('span').textContent);
        tab.classList.toggle('active', dayNumber === day);
    });
    
    // 일정 표시
    const timeline = document.getElementById('scheduleTimeline');
    if (!timeline) {
        console.error('Timeline element not found');
        return;
    }
    
    timeline.innerHTML = '';
    
    const dayPlaces = scheduleData.days[day] || [];
    console.log('Places for day:', day, dayPlaces); // 디버깅용
    
    dayPlaces.forEach((place, index) => {
        timeline.appendChild(createTimelineItem(place, index));
    });
    
    // 경로 표시 업데이트
    updateRouteDisplay();
}

// 타임라인 아이템 생성 함수
function createTimelineItem(place, index) {
    const item = document.createElement('div');
    item.className = 'timeline-item';
    item.dataset.id = String(place.id); // place.id를 문자열로 변환
    item.innerHTML = `
        <div class="time-slot">09:00</div>
        <div class="place-card">
            <div class="move-buttons">
                <button onclick="movePlaceInSchedule('${place.id}', 'up')" 
                        ${index === 0 ? 'disabled' : ''}>
                    <i class="fas fa-chevron-up"></i>
                </button>
                <button onclick="movePlaceInSchedule('${place.id}', 'down')"
                        ${index === scheduleData.days[currentDay].length - 1 ? 'disabled' : ''}>
                    <i class="fas fa-chevron-down"></i>
                </button>
            </div>
            <h4>${place.name}</h4>
            <p>${place.address}</p>
            <div class="duration-control">
                <select onchange="updateDuration(${place.id}, this.value)">
                    <option value="30">30분</option>
                    <option value="60" selected>1시간</option>
                    <option value="90">1시간 30분</option>
                    <option value="120">2시간</option>
                </select>
            </div>
            ${index > 0 ? `<div class="route-info">
                <i class="fas fa-walking"></i>
                <span class="travel-time">이동시간 계산중...</span>
            </div>` : ''}
            <button onclick="handlePlaceClick('${place.id}', 'remove')" class="remove-btn">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    return item;
}

// 경로 표시 업데이트 함수
function updateRouteDisplay() {
    const dayPlaces = scheduleData.days[currentDay] || [];
    if (dayPlaces.length < 2) {
        directionsRenderer.setDirections({routes: []});
        return;
    }

    const waypoints = dayPlaces.map(place => ({
        location: new google.maps.LatLng(place.latitude, place.longitude),
        stopover: true
    }));

    const request = {
        origin: waypoints[0].location,
        destination: waypoints[waypoints.length - 1].location,
        waypoints: waypoints.slice(1, -1),
        travelMode: 'WALKING'
    };

    directionsService.route(request, (result, status) => {
        if (status === 'OK') {
            directionsRenderer.setDirections(result);
            updateTravelTimes(result);
        }
    });
}

// 이벤트 리스너 설정 함수
function setupEventListeners() {
    const nextButton = document.getElementById('nextStep');
    if (nextButton) {
        nextButton.addEventListener('click', saveAndProceed);
    }

    const optimizeButton = document.getElementById('optimizeRoute');
    if (optimizeButton) {
        optimizeButton.addEventListener('click', optimizeRoute);
    }
}

// 경로 최적화 함수 (최단 거리 계산)
function optimizeRoute() {
    const dayPlaces = scheduleData.days[currentDay] || [];
    if (dayPlaces.length < 2) {
        alert('최소 2개 이상의 장소를 배치해주세요.');
        return;
    }

    showLoadingSpinner();

    try {
        // 출발 시간 가져오기
        const startTime = document.getElementById('startTime').value;
        let currentTime = new Date(`2023-01-01T${startTime}`);

        // 거리 매트릭스 계산
        const waypoints = dayPlaces.map(place => ({
            location: new google.maps.LatLng(place.latitude, place.longitude),
            stopover: true
        }));

        const optimizedOrder = calculateOptimalRoute(waypoints);
        const optimizedPlaces = optimizedOrder.map(index => dayPlaces[index]);
        
        // 최적화된 순서로 일정 재배치
        scheduleData.days[currentDay] = optimizedPlaces;
        showDaySchedule(currentDay);
        
        // 이동 시간과 거리 계산
        updateRouteStatistics(optimizedPlaces);
    } catch (error) {
        console.error('Route optimization error:', error);
        alert('경로 최적화 중 오류가 발생했습니다.');
    } finally {
        hideLoadingSpinner();
    }
}

// 최적 경로 계산 함수 (Nearest Neighbor Algorithm)
function calculateOptimalRoute(waypoints) {
    const n = waypoints.length;
    const visited = new Array(n).fill(false);
    const order = [];
    let current = 0; // 첫 번째 장소를 시작점으로

    visited[current] = true;
    order.push(current);

    while (order.length < n) {
        let nearest = -1;
        let minDistance = Infinity;

        for (let i = 0; i < n; i++) {
            if (!visited[i]) {
                const distance = calculateDistance(
                    waypoints[current].location,
                    waypoints[i].location
                );
                if (distance < minDistance) {
                    minDistance = distance;
                    nearest = i;
                }
            }
        }

        if (nearest !== -1) {
            visited[nearest] = true;
            order.push(nearest);
            current = nearest;
        }
    }

    return order;
}

// 두 지점 간 거리 계산 함수
function calculateDistance(p1, p2) {
    return google.maps.geometry.spherical.computeDistanceBetween(p1, p2);
}

// 경로 통계 업데이트 함수
function updateRouteStatistics(places) {
    if (places.length < 2) return;

    const waypoints = places.map(place => ({
        location: new google.maps.LatLng(place.latitude, place.longitude),
    }));

    const request = {
        origin: waypoints[0].location,
        destination: waypoints[waypoints.length - 1].location,
        waypoints: waypoints.slice(1, -1),
        travelMode: 'WALKING',
        optimizeWaypoints: false
    };

    directionsService.route(request, (result, status) => {
        if (status === 'OK') {
            let totalDistance = 0;
            let totalDuration = 0;

            result.routes[0].legs.forEach(leg => {
                totalDistance += leg.distance.value;
                totalDuration += leg.duration.value;
            });

            // 통계 표시 업데이트
            document.getElementById('totalDistance').textContent = 
                (totalDistance / 1000).toFixed(1) + 'km';
            document.getElementById('totalTravelTime').textContent = 
                Math.round(totalDuration / 60) + '분';
        }
    });
}

// 일정 저장 및 다음 단계 이동 함수 수정
async function saveAndProceed() {
    try {
        showLoadingSpinner();

        // CSRF 토큰 확인
        let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // 데이터 유효성 검사 추가
        const totalPlaces = Object.values(scheduleData.days).reduce((sum, day) => sum + day.length, 0);
        if (totalPlaces === 0) {
            throw new Error('최소 1개 이상의 장소를 일정에 배치해주세요.');
        }

        // 모든 일정 데이터 수집
        const scheduleToSave = {
            days: scheduleData.days,
            unassigned: scheduleData.unassigned
        };

        // wizardStorage 업데이트
        const wizardData = wizardStorage.load();
        wizardData.schedule = scheduleToSave;
        wizardStorage.save(wizardData);

        // 서버로 데이터 전송
        const response = await fetch('/itineraries/wizard/step3/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(scheduleToSave)
        });

        if (!response.ok) {
            throw new Error(`서버 응답 오류: ${response.status}`);
        }

        const data = await response.json();
        
        // 성공 시 다음 페이지로 이동
        if (data.status === 'success') {
            // 명시적으로 step4 URL로 이동
            window.location.href = '/itineraries/wizard/step4/';
        } else {
            throw new Error(data.error || '저장에 실패했습니다.');
        }

    } catch (error) {
        console.error('Save error:', error);
        alert(error.message);
    } finally {
        hideLoadingSpinner();
    }
}

// 시간 설정 모달 관련 함수들
function openTimeSettingModal(placeId) {
    const modal = document.getElementById('timeSettingModal');
    modal.style.display = 'block';
    modal.dataset.placeId = placeId;
}

function closeModal() {
    const modal = document.getElementById('timeSettingModal');
    modal.style.display = 'none';
}

function saveTimeSettings() {
    const modal = document.getElementById('timeSettingModal');
    const placeId = modal.dataset.placeId;
    const duration = document.getElementById('visitDuration').value;
    const memo = document.getElementById('visitMemo').value;

    updatePlaceSettings(placeId, {duration, memo});
    closeModal();
    showDaySchedule(currentDay);
}

// displayUnassignedPlaces 함수 수정
function displayUnassignedPlaces() {
    // 중복 제거를 위해 Set 사용
    const uniqueUnassigned = Array.from(new Set(scheduleData.unassigned.map(p => p.id)))
        .map(id => scheduleData.unassigned.find(p => p.id === id));
    
    // 실제 미배정 장소만 필터링
    const attractions = uniqueUnassigned.filter(place => 
        place.type === 'attraction' && !isPlaceAssigned(place.id)
    );
    const accommodations = uniqueUnassigned.filter(place => 
        place.type === 'accommodation' && !isPlaceAssigned(place.id)
    );
    
    // 관광지 표시
    const attractionsContainer = document.getElementById('unassignedAttractions');
    if (attractionsContainer) {
        attractionsContainer.innerHTML = attractions.map(place => `
            <div class="place-item" data-id="${String(place.id)}" data-type="${place.type}">
                <div class="place-info">
                    <h4>${place.name}</h4>
                    <p>${place.address || ''}</p>
                </div>
                <button onclick="handlePlaceClick('${String(place.id)}', 'add')" class="add-btn">
                    <i class="fas fa-plus"></i>
                </button>
            </div>
        `).join('');
        document.getElementById('unassignedAttractionCount').textContent = attractions.length;
    }
    
    // 숙소 표시
    const accommodationsContainer = document.getElementById('unassignedAccommodations');
    if (accommodationsContainer) {
        accommodationsContainer.innerHTML = accommodations.map(place => `
            <div class="place-item" data-id="${String(place.id)}" data-type="${place.type}">
                <div class="place-info">
                    <h4>${place.name}</h4>
                    <p>${place.address || ''}</p>
                </div>
                <button onclick="handlePlaceClick('${String(place.id)}', 'add')" class="add-btn">
                    <i class="fas fa-plus"></i>
                </button>
            </div>
        `).join('');
        document.getElementById('unassignedAccommodationCount').textContent = accommodations.length;
    }
}

// 장소가 이미 배정되었는지 확인하는 함수 수정
function isPlaceAssigned(placeId) {
    // 문자열로 변환하여 비교
    const stringId = String(placeId);
    return Object.values(scheduleData.days).some(dayPlaces => 
        dayPlaces.some(place => String(place.id) === stringId)
    );
}

// CSRF 토큰 가져오기 함수 수정
function getCsrfToken() {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!csrftoken) {
        throw new Error('CSRF token not found');
    }
    return csrftoken.value;
}
