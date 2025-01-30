// 디바운스 함수 추가
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 전역 변수 선언
let selectedAttractions = [];
let selectedAccommodations = [];
let map;
let marker;

// Google Maps 초기화 함수를 전역 스코프에 노출
window.initMap = function() {
    const defaultCenter = { lat: 36.5, lng: 127.5 }; // 한국 중심 좌표
    map = new google.maps.Map(document.getElementById('map'), {
        center: defaultCenter,
        zoom: 7,
        mapTypeControl: false,
        streetViewControl: false
    });
    marker = new google.maps.Marker({ map: map });
};

// 지도 업데이트 함수들을 전역 스코프에 노출
window.updateMap = function(lat, lng, name) {
    if (!lat || !lng) return;
    const position = { lat: parseFloat(lat), lng: parseFloat(lng) };
    map.panTo(position);
    map.setZoom(15);
    marker.setPosition(position);
    marker.setTitle(name);
};

window.resetMap = function() {
    const defaultCenter = { lat: 36.5, lng: 127.5 };
    map.panTo(defaultCenter);
    map.setZoom(7);
    marker.setPosition(null);
};

document.addEventListener('DOMContentLoaded', function() {
    // 이전 단계 데이터 로드
    const wizardData = wizardStorage.load();
    console.log('Loaded wizard data:', wizardData); // 디버깅용

    // 이전에 저장된 장소 데이터가 있다면 복원
    if (wizardData.places) {
        if (Array.isArray(wizardData.places.attractions)) {
            selectedAttractions = wizardData.places.attractions;
            updateSelectedList('attraction');
        }
        if (Array.isArray(wizardData.places.accommodations)) {
            selectedAccommodations = wizardData.places.accommodations;
            updateSelectedList('accommodation');
        }
        // 다음 단계 버튼 상태 업데이트
        validateNextStep();
    }
    
    // 자동 초기 검색 (이전 단계에서의 destination 사용)
    if (wizardData.destination) {
        searchPlaces(wizardData.destination, 'attraction');
        searchPlaces(wizardData.destination, 'accommodation');
    }

    // 관광지 검색 입력 이벤트
    document.getElementById('attractionSearch').addEventListener('input', debounce(function(e) {
        const query = e.target.value.trim();
        if (query.length > 1) {
            searchPlaces(query, 'attraction');
        }
    }, 300));

    // 숙소 검색 입력 이벤트
    document.getElementById('accommodationSearch').addEventListener('input', debounce(function(e) {
        const query = e.target.value.trim();
        if (query.length > 1) {
            searchPlaces(query, 'accommodation');
        }
    }, 300));

    // 다음 단계 버튼 활성화 조건 검사
    function validateNextStep() {
        const hasAttractions = selectedAttractions.length > 0;
        const hasAccommodations = selectedAccommodations.length > 0;
        const nextButton = document.getElementById('nextStep');
        
        nextButton.disabled = !(hasAttractions && hasAccommodations);
        if (hasAttractions && hasAccommodations) {
            nextButton.classList.add('active');
        } else {
            nextButton.classList.remove('active');
        }
    }

    // 장소 검색 함수
    async function searchPlaces(query, type) {
        const resultsDiv = document.getElementById(`${type}Results`);
        resultsDiv.innerHTML = '<div class="loading">검색 중...</div>';

        try {
            const searchUrl = `/itineraries/api/places/search/?query=${encodeURIComponent(query)}&type=${type}`;
            console.log('Searching:', searchUrl);  // 디버깅용
            
            const response = await fetch(searchUrl, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });

            console.log('Response status:', response.status);  // 디버깅용
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Search results:', data);  // 디버깅용
            
            if (Array.isArray(data)) {
                if (data.length === 0) {
                    resultsDiv.innerHTML = '<div class="no-results">검색 결과가 없습니다.</div>';
                    return;
                }
                displaySearchResults(data, type);
            } else {
                throw new Error('Invalid response format');
            }
            
        } catch (error) {
            console.error('Search error:', error);
            resultsDiv.innerHTML = `<div class="error-message">
                검색 중 오류가 발생했습니다: ${error.message}
            </div>`;
        }
    }

    // 검색 결과 표시 함수
    function displaySearchResults(places, type) {
        const resultsDiv = document.getElementById(`${type}Results`);
        
        if (!places.length) {
            resultsDiv.innerHTML = '<div class="no-results">검색 결과가 없습니다.</div>';
            return;
        }

        const selectedIds = type === 'attraction' ? 
            selectedAttractions.map(p => p.id) : 
            selectedAccommodations.map(p => p.id);

        resultsDiv.innerHTML = places.map(place => `
            <div class="place-item ${selectedIds.includes(place.id) ? 'selected' : ''}" 
                 data-id="${place.id}"
                 data-lat="${place.latitude}"
                 data-lng="${place.longitude}"
                 onmouseover="updateMap(${place.latitude}, ${place.longitude}, '${place.name}')"
                 onmouseout="resetMap()">
                <div class="place-info">
                    <h4>${place.name}</h4>
                    <p>${place.address || ''}</p>
                </div>
                <button onclick="togglePlace(${JSON.stringify(place).replace(/"/g, '&quot;')}, '${type}')" 
                        class="place-btn ${selectedIds.includes(place.id) ? 'remove-btn' : 'add-btn'}"
                        title="${selectedIds.includes(place.id) ? '제거' : '추가'}">
                    <i class="fas fa-${selectedIds.includes(place.id) ? 'minus' : 'plus'}"></i>
                </button>
            </div>
        `).join('');
    }

    // 장소 토글 함수
    window.togglePlace = function(place, type) {
        const selectedList = type === 'attraction' ? selectedAttractions : selectedAccommodations;
        const index = selectedList.findIndex(p => p.id === place.id);
        
        if (index === -1) {
            selectedList.push(place);
        } else {
            selectedList.splice(index, 1);
        }
        
        updateSelectedList(type);
        validateNextStep();
        
        // 검색 결과에서 해당 장소의 버튼 상태 업데이트
        const placeItem = document.querySelector(`[data-id="${place.id}"]`);
        if (placeItem) {
            const btn = placeItem.querySelector('.place-btn');
            btn.className = `place-btn ${index === -1 ? 'remove-btn' : 'add-btn'}`;
            btn.innerHTML = `<i class="fas fa-${index === -1 ? 'minus' : 'plus'}"></i>`;
        }
    }
    
    // 선택된 장소 목록 업데이트
    function updateSelectedList(type) {
        const listDiv = document.getElementById(`selected${type.charAt(0).toUpperCase() + type.slice(1)}s`);
        const selectedList = type === 'attraction' ? selectedAttractions : selectedAccommodations;
        
        listDiv.innerHTML = selectedList.map((place, index) => `
            <div class="selected-place" 
                 draggable="true"
                 data-lat="${place.latitude}"
                 data-lng="${place.longitude}"
                 onmouseover="updateMap(${place.latitude}, ${place.longitude}, '${place.name}')"
                 onmouseout="resetMap()">
                <div class="place-info">
                    <h4>${place.name}</h4>
                    <p>${place.address || ''}</p>
                </div>
                <button onclick="togglePlace(${JSON.stringify(place).replace(/"/g, '&quot;')}, '${type}')" 
                        class="remove-btn">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
        
        document.getElementById(`${type}Count`).textContent = `(${selectedList.length})`;
    }

    // 다음 단계로 이동하는 함수를 window 객체에 바인딩
    window.goToNextStep = async function() {
        try {
            showLoadingSpinner(); // 로딩 표시

            const selectedData = collectSelectedPlaces();
            
            if (!validateSelectedData(selectedData)) {
                return;
            }

            await saveDataAndProceed(selectedData);
        } catch (error) {
            handleWizardError(error);
        } finally {
            hideLoadingSpinner(); // 로딩 숨김
        }
    };

    // 선택된 장소 데이터 수집 함수
    function collectSelectedPlaces() {
        const attractions = Array.from(document.querySelectorAll('#selectedAttractions .selected-place'))
            .map(convertElementToPlaceData);
        
        const accommodations = Array.from(document.querySelectorAll('#selectedAccommodations .selected-place'))
            .map(convertElementToPlaceData);

        return { attractions, accommodations };
    }

    // DOM 요소를 장소 데이터로 변환하는 함수
    function convertElementToPlaceData(element) {
        return {
            id: element.dataset.id,
            name: element.querySelector('h4').textContent,
            address: element.querySelector('p').textContent,
            latitude: parseFloat(element.dataset.lat),
            longitude: parseFloat(element.dataset.lng)
        };
    }

    // 데이터 유효성 검사 함수
    function validateSelectedData(data) {
        if (data.attractions.length === 0) {
            alert('최소 1개 이상의 관광지를 선택해주세요.');
            return false;
        }
        if (data.accommodations.length === 0) {
            alert('최소 1개 이상의 숙소를 선택해주세요.');
            return false;
        }
        return true;
    }

    // 데이터 저장 및 페이지 이동 함수 수정
    async function saveDataAndProceed() {
        try {
            showLoadingSpinner();
            
            // 선택된 장소 데이터 수집
            const placeData = {
                attractions: selectedAttractions.map(place => ({
                    ...place,
                    type: 'attraction'
                })),
                accommodations: selectedAccommodations.map(place => ({
                    ...place,
                    type: 'accommodation'
                }))
            };

            // wizardStorage를 사용하여 데이터 저장
            const wizardData = wizardStorage.load();
            const selectedData = {
                attractions: selectedAttractions,
                accommodations: selectedAccommodations
            };
            wizardData.places = selectedData;
            wizardStorage.save(wizardData);

            console.log('Saved wizard data:', wizardData); // 디버깅용

            // 서버로 데이터 전송
            const response = await fetch('/itineraries/wizard/step2/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(placeData)
            });

            const data = await response.json();
            if (data.status === 'success') {
                window.location.href = '/itineraries/wizard/step3/';
            } else {
                throw new Error(data.error || '저장에 실패했습니다.');
            }
        } catch (error) {
            console.error('Save error:', error);
            showError(error.message);
        } finally {
            hideLoadingSpinner();
        }
    }

    // 다음 단계 버튼에 이벤트 리스너 추가
    document.getElementById('nextStep').addEventListener('click', async function() {
        try {
            showLoadingSpinner();
            
            const selectedData = {
                attractions: selectedAttractions,
                accommodations: selectedAccommodations
            };

            // 데이터 검증
            if (!validateSelectedData(selectedData)) {
                hideLoadingSpinner();
                return;
            }

            // wizardData에 선택한 장소들 저장
            const wizardData = wizardStorage.load();
            wizardData.places = selectedData;
            wizardStorage.save(wizardData);

            console.log('Saving place data:', selectedData); // 디버깅용

            // 서버로 데이터 전송
            const response = await fetch('/itineraries/wizard/step2/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                credentials: 'same-origin',
                body: JSON.stringify(selectedData)
            });

            console.log('Server response:', response); // 디버깅용

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Response data:', data); // 디버깅용

            if (data.status === 'success') {
                window.location.href = '/itineraries/wizard/step3/';
            } else {
                throw new Error(data.message || '저장에 실패했습니다.');
            }

        } catch (error) {
            console.error('Next step error:', error);
            showError(error.message);
        } finally {
            hideLoadingSpinner();
        }
    });

    async function saveAndProceed() {
        try {
            showLoadingSpinner();
            
            // 선택된 장소 데이터 수집
            const placeData = {
                attractions: selectedAttractions,
                accommodations: selectedAccommodations
            };

            // 세션 스토리지에 데이터 저장
            const wizardData = JSON.parse(sessionStorage.getItem('wizard_data') || '{}');
            wizardData.places = {
                attractions: selectedAttractions,
                accommodations: selectedAccommodations
            };
            sessionStorage.setItem('wizard_data', JSON.stringify(wizardData));

            // 서버로 데이터 전송
            const response = await fetch('/itineraries/wizard/step2/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(placeData)
            });

            const data = await response.json();
            if (data.status === 'success') {
                window.location.href = '/itineraries/wizard/step3/';
            } else {
                throw new Error(data.error || '저장에 실패했습니다.');
            }
        } catch (error) {
            console.error('Save error:', error);
            showError(error.message);
        } finally {
            hideLoadingSpinner();
        }
    }

    function validateSelectedData(data) {
        if (data.attractions.length === 0) {
            showError('최소 1개 이상의 관광지를 선택해주세요.');
            return false;
        }
        if (data.accommodations.length === 0) {
            showError('최소 1개 이상의 숙소를 선택해주세요.');
            return false;
        }
        return true;
    }

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
});
