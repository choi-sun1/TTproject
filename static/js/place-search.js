class PlaceSearch {
    constructor(options = {}) {
        this.searchInput = document.getElementById(options.searchInputId || 'placeSearch');
        this.resultsContainer = document.getElementById(options.resultsContainerId || 'searchResults');
        this.selectedContainer = document.getElementById(options.selectedContainerId || 'selectedPlacesList');
        this.selectedPlaces = new Map();
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // 검색 입력 이벤트
        this.searchInput.addEventListener('input', this.debounce(() => {
            const query = this.searchInput.value.trim();
            if (query.length > 1) {
                this.searchPlaces(query);
            }
        }, 300));

        // 검색 결과 클릭 이벤트 위임
        this.resultsContainer.addEventListener('click', (e) => {
            const placeItem = e.target.closest('.place-item');
            if (placeItem) {
                const placeId = placeItem.dataset.placeId;
                const placeData = JSON.parse(placeItem.dataset.place);
                this.addPlace(placeData);
            }
        });
    }

    async searchPlaces(query) {
        try {
            const response = await fetch(`/api/places/search/?query=${encodeURIComponent(query)}`);
            const data = await response.json();
            this.displaySearchResults(data);
        } catch (error) {
            console.error('장소 검색 중 오류 발생:', error);
            this.showError('장소를 검색하는 중 문제가 발생했습니다.');
        }
    }

    displaySearchResults(places) {
        this.resultsContainer.innerHTML = places.map(place => `
            <div class="place-item" 
                 data-place-id="${place.id}"
                 data-place='${JSON.stringify(place)}'>
                <h4>${place.name}</h4>
                <p>${place.address}</p>
                <div class="place-type">${place.place_type}</div>
            </div>
        `).join('');
    }

    addPlace(place) {
        if (!this.selectedPlaces.has(place.id)) {
            this.selectedPlaces.set(place.id, place);
            this.updateSelectedPlacesList();
            
            // 검색 입력창 초기화
            this.searchInput.value = '';
            this.resultsContainer.innerHTML = '';
        }
    }

    removePlace(placeId) {
        this.selectedPlaces.delete(placeId);
        this.updateSelectedPlacesList();
    }

    updateSelectedPlacesList() {
        this.selectedContainer.innerHTML = Array.from(this.selectedPlaces.values())
            .map(place => `
                <div class="selected-place" data-place-id="${place.id}">
                    <div class="place-info">
                        <h4>${place.name}</h4>
                        <p>${place.address}</p>
                    </div>
                    <button type="button" 
                            class="btn-remove" 
                            onclick="placeSearch.removePlace('${place.id}')">
                        ×
                    </button>
                </div>
            `).join('');
    }

    getSelectedPlaces() {
        return Array.from(this.selectedPlaces.values());
    }

    debounce(func, wait) {
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

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        this.resultsContainer.parentNode.insertBefore(errorDiv, this.resultsContainer);
        setTimeout(() => errorDiv.remove(), 3000);
    }
}
