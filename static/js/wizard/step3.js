// 전역 변수 삭제
let map;
let directionsService;
let directionsRenderer;
let markers = [];
let scheduleData = {
    unassigned: [],
    days: {}
};
let currentDay = 1;

// Google Maps 초기화 함수만 수정
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

// 유틸리티 함수들
function getCookie(name) {
    // ...existing code...
}

function formatTime(date) {
    // ...existing code...
}

// 페이지 초기화
document.addEventListener('DOMContentLoaded', function() {
    console.log('Step 3 initialized'); // 디버깅용
    
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

    // 장소 데이터 초기화 수정
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

    // 드래그 앤 드롭 초기화
    initializeDragAndDrop('unassignedAttractions');
    initializeDragAndDrop('unassignedAccommodations');

    // 지도 업데이트
    if (scheduleData.unassigned.length > 0) {
        const firstPlace = scheduleData.unassigned[0];
        map.setCenter({
            lat: parseFloat(firstPlace.latitude),
            lng: parseFloat(firstPlace.longitude)
        });
        map.setZoom(13);
    }
});

function initializeSchedule(data) {
    // 날짜 계산
    const startDate = new Date(data.start_date);
    const endDate = new Date(data.end_date);
    const totalDays = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1;

    // 일차별 탭 생성
    createDayTabs(totalDays);
    
    // 미배정 장소 표시
    displayUnassignedPlaces();

    // 첫째 날 일정 표시
    showDaySchedule(1);
}

function createDayTabs(totalDays) {
    const nav = document.getElementById('daysNav');
    nav.innerHTML = '';
    
    for (let i = 1; i <= totalDays; i++) {
        const tab = document.createElement('div');
        tab.className = 'day-tab';
        if (i === 1) tab.classList.add('active');
        
        // 날짜 아이콘 추가
        tab.innerHTML = `
            <i class="fas fa-calendar-day"></i>
            <span>${i}일차</span>
        `;
        
        tab.onclick = () => {
            // 모든 탭의 active 클래스 제거
            document.querySelectorAll('.day-tab').forEach(t => t.classList.remove('active'));
            // 클릭된 탭에만 active 클래스 추가
            tab.classList.add('active');
            showDaySchedule(i);
        };
        
        nav.appendChild(tab);
        
        // 일차별 데이터 초기화
        scheduleData.days[i] = scheduleData.days[i] || [];
    }
}

function initializeDragAndDrop(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        new Sortable(container, {
            group: 'schedule',
            animation: 150,
            onEnd: handleDragEnd
        });
    }
}

function handleDragEnd(evt) {
    const placeId = evt.item.dataset.id;
    const fromList = evt.from.id;
    const toList = evt.to.id;
    
    if (fromList === 'unassignedList' && toList === 'scheduleTimeline') {
        // 미배정 -> 일정 추가
        addToSchedule(placeId, currentDay);
    } else if (fromList === 'scheduleTimeline' && toList === 'unassignedList') {
        // 일정 -> 미배정으로 이동
        removeFromSchedule(placeId, currentDay);
    }
    
    updateRouteDisplay();
}

function addToSchedule(placeId, day) {
    const place = scheduleData.unassigned.find(p => p.id === placeId);
    if (!place) return;
    
    scheduleData.days[day] = scheduleData.days[day] || [];
    scheduleData.days[day].push(place);
    
    scheduleData.unassigned = scheduleData.unassigned.filter(p => p.id !== placeId);
    
    showDaySchedule(day);
    displayUnassignedPlaces();
}

function showDaySchedule(day) {
    currentDay = day;
    
    // 탭 활성화 상태 변경
    document.querySelectorAll('.day-tab').forEach(tab => {
        tab.classList.toggle('active', tab.textContent === `${day}일차`);
    });
    
    // 일정 표시
    const timeline = document.getElementById('scheduleTimeline');
    timeline.innerHTML = '';
    
    const dayPlaces = scheduleData.days[day] || [];
    dayPlaces.forEach((place, index) => {
        timeline.appendChild(createTimelineItem(place, index));
    });
    
    // 경로 표시 업데이트
    updateRouteDisplay();
}

function createTimelineItem(place, index) {
    const item = document.createElement('div');
    item.className = 'timeline-item';
    item.dataset.id = place.id;
    item.innerHTML = `
        <div class="time-slot">09:00</div>
        <div class="place-card">
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
        </div>
    `;
    return item;
}

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

function setupEventListeners() {
    // 최적화 버튼
    document.getElementById('optimizeRoute').addEventListener('click', optimizeRoute);
    
    // 다음 단계 버튼
    document.getElementById('nextStep').addEventListener('click', saveAndProceed);
}

// 경로 최적화 함수
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

// 최적 경로 계산 (Nearest Neighbor Algorithm)
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

// 두 지점 간 거리 계산
function calculateDistance(p1, p2) {
    return google.maps.geometry.spherical.computeDistanceBetween(p1, p2);
}

// 이동 시간과 거리 통계 업데이트
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

// 일정 저장 및 다음 단계로 이동
async function saveAndProceed() {
    try {
        showLoadingSpinner();

        // 모든 일정 데이터 수집
        const scheduleToSave = {
            days: scheduleData.days,
            unassigned: scheduleData.unassigned
        };

        // 세션 스토리지 업데이트
        const wizardData = JSON.parse(sessionStorage.getItem('wizard_data') || '{}');
        wizardData.schedule = scheduleToSave;
        sessionStorage.setItem('wizard_data', JSON.stringify(wizardData));

        // 서버로 데이터 전송
        const response = await fetch('/itineraries/wizard/step3/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(scheduleToSave)
        });

        const data = await response.json();
        if (data.status === 'success') {
            window.location.href = '/itineraries/wizard/step4/';
        } else {
            throw new Error(data.error || '저장에 실패했습니다.');
        }
    } catch (error) {
        console.error('Save error:', error);
        alert('저장 중 오류가 발생했습니다.');
    } finally {
        hideLoadingSpinner();
    }
}

// 방문 시간 설정 모달 관련 함수들
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

// 나머지 필요한 유틸리티 함수들...
// ...existing code...

function displayUnassignedPlaces() {
    const attractions = scheduleData.unassigned.filter(place => place.type === 'attraction');
    const accommodations = scheduleData.unassigned.filter(place => place.type === 'accommodation');
    
    // 관광지 표시
    const attractionsContainer = document.getElementById('unassignedAttractions');
    if (attractionsContainer) {
        attractionsContainer.innerHTML = attractions.map(place => createPlaceCard(place, 'unassigned')).join('');
        document.getElementById('unassignedAttractionCount').textContent = attractions.length;
    }
    
    // 숙소 표시
    const accommodationsContainer = document.getElementById('unassignedAccommodations');
    if (accommodationsContainer) {
        accommodationsContainer.innerHTML = accommodations.map(place => createPlaceCard(place, 'unassigned')).join('');
        document.getElementById('unassignedAccommodationCount').textContent = accommodations.length;
    }
}

function createPlaceCard(place, mode = 'unassigned') {
    const isUnassigned = mode === 'unassigned';
    return `
        <div class="place-item" draggable="true" 
             data-id="${place.id}" 
             data-type="${place.type}"
             onclick="${isUnassigned ? `addToSchedule('${place.id}', ${currentDay})` : ''}"
             style="cursor: ${isUnassigned ? 'pointer' : 'move'}">
            <div class="place-info">
                <h4>${place.name}</h4>
                <p>${place.address || ''}</p>
            </div>
            <div class="place-type-badge ${place.type}">
                <i class="fas fa-${place.type === 'attraction' ? 'map-marker-alt' : 'bed'}"></i>
                ${isUnassigned ? '<span class="add-hint">클릭하여 추가</span>' : ''}
            </div>
        </div>
    `;
}
