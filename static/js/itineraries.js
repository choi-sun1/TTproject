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
});
