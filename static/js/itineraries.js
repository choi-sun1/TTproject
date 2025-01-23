document.addEventListener('DOMContentLoaded', function() {
    // 지도 관련 기능
    const mapContainer = document.getElementById('map');
    if (mapContainer) {
        const map = new kakao.maps.Map(mapContainer, {
            center: new kakao.maps.LatLng(37.5665, 126.9780),
            level: 3
        });

        // 장소 검색 기능
        const searchForm = document.getElementById('place-search-form');
        searchForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const keyword = this.querySelector('input').value;
            try {
                const response = await apiRequest(
                    '/api/v1/itineraries/places/search/',
                    'POST',
                    { keyword }
                );
                updatePlacesList(response.places);
            } catch (error) {
                showNotification('장소 검색 중 오류가 발생했습니다.', 'error');
            }
        });
    }

    const sortSelect = document.getElementById('sort-select');
    const searchInput = document.getElementById('search-input');
    let searchTimeout;

    // 정렬 변경 이벤트
    sortSelect?.addEventListener('change', function() {
        fetchItineraries({
            sort: this.value,
            search: searchInput.value
        });
    });

    // 검색어 입력 이벤트 (디바운싱 적용)
    searchInput?.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            fetchItineraries({
                sort: sortSelect.value,
                search: this.value
            });
        }, 300);
    });

    async function fetchItineraries(params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            const response = await fetch(`/api/v1/itineraries/?${queryString}`);
            const data = await response.json();
            
            if (response.ok) {
                updateItinerariesList(data.results);
            } else {
                showNotification('일정을 불러오는데 실패했습니다.', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('오류가 발생했습니다.', 'error');
        }
    }

    function updateItinerariesList(itineraries) {
        const container = document.getElementById('itineraries-container');
        if (!container) return;

        container.innerHTML = itineraries.length ? itineraries.map(itinerary => `
            <div class="itinerary-card">
                <div class="itinerary-header">
                    <span class="dates">${formatDate(itinerary.start_date)} ~ ${formatDate(itinerary.end_date)}</span>
                    <span class="duration">${calculateDuration(itinerary.start_date, itinerary.end_date)}일간</span>
                </div>
                <h3><a href="/itineraries/${itinerary.id}/">${itinerary.title}</a></h3>
                <div class="itinerary-meta">
                    <span class="author">${itinerary.author_nickname}</span>
                    <span class="views">조회 ${itinerary.views}</span>
                    <span class="likes">좋아요 ${itinerary.likes_count}</span>
                </div>
                ${itinerary.places.length ? `
                    <div class="itinerary-places">
                        ${itinerary.places.slice(0, 3).map(place => `
                            <span class="place">${place.name}</span>
                        `).join('')}
                        ${itinerary.places.length > 3 ? `
                            <span class="more">+${itinerary.places.length - 3}</span>
                        ` : ''}
                    </div>
                ` : ''}
            </div>
        `).join('') : '<div class="no-itineraries"><p>검색 결과가 없습니다.</p></div>';
    }

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('ko-KR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        });
    }

    function calculateDuration(startDate, endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        return Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;
    }
});
