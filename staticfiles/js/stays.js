let map;
let markers = [];
let activeInfoWindow = null;

function initMap() {
    const mapContainer = document.getElementById("map");
    const defaultCenter = { lat: 37.5665, lng: 126.9780 }; // 서울 중심점

    // 지도 초기화
    map = new google.maps.Map(mapContainer, {
        zoom: 12,
        center: defaultCenter,
        styles: getMapStyles(),
        mapTypeControl: true,
        mapTypeControlOptions: {
            style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
            position: google.maps.ControlPosition.TOP_RIGHT
        },
        streetViewControl: true,
        streetViewControlOptions: {
            position: google.maps.ControlPosition.RIGHT_BOTTOM
        },
        fullscreenControl: true,
        zoomControl: true,
        zoomControlOptions: {
            position: google.maps.ControlPosition.RIGHT_CENTER
        }
    });

    // 숙소 마커 생성
    const stayCards = document.querySelectorAll('.stay-card');
    if (stayCards.length > 0) {
        const bounds = new google.maps.LatLngBounds();
        
        stayCards.forEach(stay => {
            const lat = parseFloat(stay.dataset.lat);
            const lng = parseFloat(stay.dataset.lng);
            
            if (!isNaN(lat) && !isNaN(lng)) {
                const position = { lat, lng };
                bounds.extend(position);
                
                // 마커 생성
                const marker = new google.maps.Marker({
                    position: position,
                    map: map,
                    title: stay.dataset.name,
                    animation: google.maps.Animation.DROP
                });

                // 정보창 생성
                const infoContent = `
                    <div class="map-info-window">
                        <h3>${stay.dataset.name}</h3>
                        <p class="price">₩${Number(stay.dataset.price).toLocaleString()}/박</p>
                        <p class="rating">
                            <i class="fas fa-star"></i> ${stay.dataset.rating}
                        </p>
                        <a href="/stays/${stay.dataset.id}/" class="map-link">자세히 보기</a>
                    </div>
                `;

                const infoWindow = new google.maps.InfoWindow({
                    content: infoContent,
                    maxWidth: 300
                });

                // 마커 클릭 이벤트
                marker.addListener('click', () => {
                    if (activeInfoWindow) {
                        activeInfoWindow.close();
                    }
                    infoWindow.open(map, marker);
                    activeInfoWindow = infoWindow;

                    // 해당 카드로 스크롤
                    stay.scrollIntoView({ behavior: 'smooth', block: 'center' });
                });

                // 카드에 마우스 오버시 마커 바운스
                stay.addEventListener('mouseenter', () => {
                    marker.setAnimation(google.maps.Animation.BOUNCE);
                    setTimeout(() => {
                        marker.setAnimation(null);
                    }, 750);
                });

                markers.push(marker);
            }
        });

        // 지도 범위 조정
        map.fitBounds(bounds);
        if (markers.length === 1) {
            map.setZoom(15);
        }
    }

    // 검색 결과가 있는 경우 지도 중심점 설정
    const searchLocation = mapContainer.dataset.searchLocation;
    if (searchLocation && markers.length === 0) {
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode({ 
            address: searchLocation + ', South Korea'
        }, (results, status) => {
            if (status === 'OK' && results[0]) {
                map.setCenter(results[0].geometry.location);
                map.setZoom(13);
            }
        });
    }
}

// 기존의 마커 제거 함수
function clearMarkers() {
    markers.forEach(marker => marker.setMap(null));
    markers = [];
    if (activeInfoWindow) {
        activeInfoWindow.close();
    }
}

function searchLocationAndUpdateMap(location) {
    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ address: location + ', South Korea' }, (results, status) => {
        if (status === 'OK') {
            map.setCenter(results[0].geometry.location);
            map.setZoom(12);
        }
    });
}

function initSearchHandlers() {
    const searchForm = document.getElementById('search-form');
    const locationInput = searchForm.querySelector('input[name="location"]');
    
    // 자동 완성 기능 추가
    const autocomplete = new google.maps.places.Autocomplete(locationInput, {
        types: ['(cities)'],
        componentRestrictions: { country: 'kr' }
    });

    // 폼 제출 이벤트
    searchForm.addEventListener('submit', function(e) {
        // 이미 서버로 전송되므로 추가 처리는 필요 없음
    });

    // 필드 변경 시 자동 제출 (UX 개선)
    const dateFields = searchForm.querySelectorAll('input[type="date"]');
    const peopleSelect = searchForm.querySelector('select[name="people"]');

    [...dateFields, peopleSelect].forEach(field => {
        field.addEventListener('change', () => {
            searchForm.submit();
        });
    });
}

// 숙소 목록 무한 스크롤
function initInfiniteScroll() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                loadMoreStays();
            }
        });
    });

    const sentinel = document.querySelector('.scroll-sentinel');
    if (sentinel) observer.observe(sentinel);
}

// 필터링 즉시 적용
function initFilterHandlers() {
    const filters = document.querySelectorAll('.filter-input');
    filters.forEach(filter => {
        filter.addEventListener('change', () => {
            applyFilters();
        });
    });
}

// 가격 범위 슬라이더
function initPriceRangeSlider() {
    const slider = document.querySelector('.price-range');
    if (slider) {
        noUiSlider.create(slider, {
            start: [0, 1000000],
            connect: true,
            range: {
                'min': 0,
                'max': 1000000
            },
            format: {
                to: value => Math.round(value),
                from: value => Math.round(value)
            }
        });
    }
}

function addMarker(position, name, price, id) {
    const marker = new google.maps.Marker({
        position,
        map,
        title: name
    });

    const infoWindow = new google.maps.InfoWindow({
        content: `
            <div class="map-info-window">
                <h3>${name}</h3>
                <p>₩${price}/박</p>
                <a href="/stays/${id}/" class="map-link">자세히 보기</a>
            </div>
        `
    });

    marker.addListener('click', () => {
        infoWindow.open(map, marker);
    });

    markers.push(marker);
}

function getMapStyles() {
    return [
        {
            featureType: "poi",
            elementType: "labels",
            stylers: [{ visibility: "off" }]
        }
    ];
}

// 지도 마커 및 범위 업데이트 개선
function updateMap(stays) {
    // 기존 마커와 정보창 제거
    clearMarkers();

    const bounds = new google.maps.LatLngBounds();
    let hasValidMarkers = false;

    stays.forEach(stay => {
        const position = {
            lat: parseFloat(stay.dataset.lat),
            lng: parseFloat(stay.dataset.lng)
        };
        
        if (!isNaN(position.lat) && !isNaN(position.lng)) {
            hasValidMarkers = true;
            bounds.extend(position);
            addMarkerWithAnimation(position, stay);
        }
    });

    if (hasValidMarkers) {
        map.fitBounds(bounds);
        
        // 검색 결과가 1개일 때 적절한 줌 레벨 설정
        if (markers.length === 1) {
            google.maps.event.addListenerOnce(map, 'bounds_changed', () => {
                map.setZoom(15);
            });
        }
    }
}

// 마커 생성 함수 수정
function addMarkerWithAnimation(position, stay) {
    const marker = new google.maps.Marker({
        position,
        map,
        title: stay.dataset.name,
        animation: google.maps.Animation.DROP
    });

    // Street View 가용성 확인
    const streetViewService = new google.maps.StreetViewService();
    streetViewService.getPanorama(
        { location: position, radius: 50 },
        (data, status) => {
            const infoContent = createInfoWindowContent(stay, status === google.maps.StreetViewStatus.OK);
            const infoWindow = new google.maps.InfoWindow({ content: infoContent });

            marker.addListener('click', () => {
                if (activeInfoWindow) {
                    activeInfoWindow.close();
                }
                infoWindow.open(map, marker);
                activeInfoWindow = infoWindow;
                
                // 해당 카드로 스크롤
                stay.scrollIntoView({ behavior: 'smooth', block: 'center' });
            });
        }
    );

    // 카드에 마우스오버 시 마커 바운스 효과
    stay.addEventListener('mouseenter', () => {
        marker.setAnimation(google.maps.Animation.BOUNCE);
        setTimeout(() => {
            marker.setAnimation(null);
        }, 750);
    });

    markers.push(marker);
}

// 개선된 정보창 생성 함수
function createInfoWindow(stay) {
    const content = `
        <div class="map-info-window">
            <h3>${stay.dataset.name}</h3>
            <div class="info-price">₩${Number(stay.dataset.price).toLocaleString()}/박</div>
            <div class="info-rating">
                <i class="fas fa-star"></i> ${stay.dataset.rating || '0.0'}
            </div>
            <a href="/stays/${stay.dataset.id}/" class="map-link">자세히 보기</a>
        </div>
    `;
    
    return new google.maps.InfoWindow({
        content: content,
        maxWidth: 300
    });
}

// 정보창 컨텐츠 생성 함수 수정
function createInfoWindowContent(stay, hasStreetView) {
    let streetViewBtn = '';
    if (hasStreetView) {
        streetViewBtn = `
            <button onclick="showStreetView(
                ${stay.dataset.lat}, 
                ${stay.dataset.lng}, 
                '${stay.dataset.name}'
            )" class="street-view-btn">
                <i class="fas fa-street-view"></i> 거리뷰
            </button>
        `;
    }

    return `
        <div class="map-info-window">
            <h3>${stay.dataset.name}</h3>
            <div class="info-price">₩${Number(stay.dataset.price).toLocaleString()}/박</div>
            <div class="info-rating">
                <i class="fas fa-star"></i> ${stay.dataset.rating || '0.0'}
            </div>
            <div class="info-actions">
                ${streetViewBtn}
                <a href="/stays/${stay.dataset.id}/" class="map-link">자세히 보기</a>
            </div>
        </div>
    `;
}

// Street View 표시 함수 추가
function showStreetView(lat, lng, name) {
    const position = { lat, lng };
    const panorama = new google.maps.StreetViewPanorama(
        document.getElementById('map'),
        {
            position: position,
            pov: { heading: 0, pitch: 0 },
            zoom: 1,
            addressControl: true,
            fullscreenControl: true,
            motionTracking: false
        }
    );
    
    // Street View 종료 버튼 추가
    const exitButton = document.createElement('button');
    exitButton.className = 'exit-street-view';
    exitButton.innerHTML = '<i class="fas fa-times"></i> 지도로 돌아가기';
    exitButton.onclick = () => {
        map.setStreetView(null);
        exitButton.remove();
    };
    
    document.querySelector('.map-container').appendChild(exitButton);
}

// 검색 폼 제출 시 지도 업데이트
document.getElementById('search-form').addEventListener('submit', function(e) {
    const stayCards = document.querySelectorAll('.stay-card');
    updateMap(stayCards);
});

// 검색 필터 변경 시 자동 제출 (선택적)
const filterInputs = document.querySelectorAll('#search-form input, #search-form select');
filterInputs.forEach(input => {
    input.addEventListener('change', function() {
        document.getElementById('search-form').submit();
    });
});
