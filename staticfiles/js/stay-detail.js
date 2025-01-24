let map;
let marker;

function initMap() {
    const mapElement = document.getElementById('map');
    
    // 데이터 속성에서 위치 정보 가져오기
    const lat = parseFloat(mapElement.dataset.lat);
    const lng = parseFloat(mapElement.dataset.lng);
    const name = mapElement.dataset.name;
    const address = mapElement.dataset.address;

    // 좌표가 유효한지 확인
    if (isNaN(lat) || isNaN(lng)) {
        console.error('Invalid coordinates');
        mapElement.innerHTML = '위치 정보를 불러올 수 없습니다.';
        return;
    }

    const location = { lat, lng };

    // 지도 옵션
    const mapOptions = {
        zoom: 15,
        center: location,
        mapTypeControl: true,
        mapTypeControlOptions: {
            style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
            position: google.maps.ControlPosition.TOP_RIGHT
        },
        fullscreenControl: true,
        streetViewControl: true,
        zoomControl: true
    };

    // 지도 생성
    map = new google.maps.Map(mapElement, mapOptions);

    // 마커 생성
    marker = new google.maps.Marker({
        position: location,
        map: map,
        title: name,
        animation: google.maps.Animation.DROP
    });

    // 정보창 생성
    const infowindow = new google.maps.InfoWindow({
        content: `
            <div class="map-info-window">
                <h3>${name}</h3>
                <p>${address}</p>
            </div>
        `
    });

    // 마커 클릭시 정보창 표시
    marker.addListener('click', () => {
        infowindow.open(map, marker);
    });

    // 주변 장소 검색 초기화
    initNearbyPlaces(location);
}

// 주변 장소 검색 초기화
function initNearbyPlaces(location) {
    const service = new google.maps.places.PlacesService(map);
    const nearbySearchTypes = [
        { type: 'restaurant', label: '음식점' },
        { type: 'subway_station', label: '지하철역' },
        { type: 'bus_station', label: '버스정류장' },
        { type: 'convenience_store', label: '편의점' }
    ];

    nearbySearchTypes.forEach(({ type, label }) => {
        const request = {
            location: location,
            radius: 500,
            type: type
        };

        service.nearbySearch(request, (results, status) => {
            if (status === google.maps.places.PlacesServiceStatus.OK) {
                displayNearbyPlaces(results, label);
            }
        });
    });
}

// 주변 장소 표시
function displayNearbyPlaces(places, category) {
    const listContainer = document.getElementById('nearby-places-list');
    const categoryDiv = document.createElement('div');
    categoryDiv.className = 'nearby-category';
    categoryDiv.innerHTML = `
        <h4>${category}</h4>
        <ul class="nearby-places-items">
            ${places.slice(0, 3).map(place => `
                <li>
                    <span class="place-name">${place.name}</span>
                    <span class="place-distance">${calculateDistance(place.geometry.location)}</span>
                </li>
            `).join('')}
        </ul>
    `;
    listContainer.appendChild(categoryDiv);
}

// 거리 계산
function calculateDistance(placeLocation) {
    const stayLocation = marker.getPosition();
    const distance = google.maps.geometry.spherical.computeDistanceBetween(stayLocation, placeLocation);
    return distance < 1000 ? 
        `${Math.round(distance)}m` : 
        `${(distance/1000).toFixed(1)}km`;
}

// Google Maps API 로드 실패시
function handleMapError() {
    const mapElement = document.getElementById('map');
    mapElement.innerHTML = `
        <div class="map-error">
            <p>지도를 불러오는데 실패했습니다.</p>
            <p>잠시 후 다시 시도해주세요.</p>
        </div>
    `;
}

// Google Maps API 스크립트 로드 확인
if (typeof google === 'undefined') {
    handleMapError();
}
