document.addEventListener('DOMContentLoaded', function() {
    // Google Maps 초기화
    window.initMap = function() {
        const mapContainer = document.getElementById('map');
        const markers = [];
        const paths = [];
        
        if (mapContainer) {
            const map = new google.maps.Map(mapContainer, {
                center: { lat: 37.5665, lng: 126.9780 },
                zoom: 12,
                styles: [
                    {
                        featureType: "poi",
                        elementType: "labels",
                        stylers: []
                    }
                ]
            });

            // 모든 장소 마커 생성
            const places = document.querySelectorAll('.place-item');
            if (places.length > 0) {
                const bounds = new google.maps.LatLngBounds();
                
                places.forEach((place, index) => {
                    const lat = parseFloat(place.dataset.lat);
                    const lng = parseFloat(place.dataset.lng);
                    const latlng = new google.maps.LatLng(lat, lng);
                    
                    // 마커 생성
                    const marker = new google.maps.Marker({
                        position: latlng,
                        map: map
                    });

                    // 마커에 번호 표시
                    const content = `<div class="marker-label">${index + 1}</div>`;
                    const customOverlay = new google.maps.OverlayView();
                    customOverlay.onAdd = function() {
                        const div = document.createElement('div');
                        div.innerHTML = content;
                        this.getPanes().overlayLayer.appendChild(div);
                    };
                    customOverlay.draw = function() {
                        const projection = this.getProjection();
                        const position = projection.fromLatLngToDivPixel(latlng);
                        const div = this.getPanes().overlayLayer.firstChild;
                        div.style.left = position.x + 'px';
                        div.style.top = position.y + 'px';
                    };
                    customOverlay.setMap(map);
                    
                    markers.push(marker);
                    bounds.extend(latlng);

                    // 이전 위치가 있으면 경로 그리기
                    if (index > 0) {
                        const prevLat = parseFloat(places[index - 1].dataset.lat);
                        const prevLng = parseFloat(places[index - 1].dataset.lng);
                        const path = [
                            new google.maps.LatLng(prevLat, prevLng),
                            latlng
                        ];

                        const polyline = new google.maps.Polyline({
                            path: path,
                            strokeWeight: 3,
                            strokeColor: '#5C7AEA',
                            strokeOpacity: 0.7,
                            strokeStyle: 'solid'
                        });
                        
                        polyline.setMap(map);
                        paths.push(polyline);
                    }
                });

                map.fitBounds(bounds);
            }
        }
    };

    // 좋아요 기능
    const likeButton = document.getElementById('like-button');
    likeButton?.addEventListener('click', async function() {
        try {
            const response = await apiRequest(
                `/api/v1/itineraries/${this.dataset.itineraryId}/like/`,
                'POST'
            );
            
            if (response.liked) {
                this.classList.add('liked');
            } else {
                this.classList.remove('liked');
            }
            
            const likesCount = document.querySelector('.likes');
            if (likesCount) {
                likesCount.textContent = `좋아요 ${response.likes_count}`;
            }
            
            showNotification(response.message);
        } catch (error) {
            showNotification('오류가 발생했습니다.', 'error');
        }
    });

    // 삭제 기능
    const deleteButton = document.getElementById('delete-itinerary');
    deleteButton?.addEventListener('click', async function() {
        if (confirm('정말 이 일정을 삭제하시겠습니까?')) {
            try {
                const itineraryId = this.closest('[data-itinerary-id]').dataset.itineraryId;
                await apiRequest(`/itineraries/${itineraryId}/`, 'DELETE');
                window.location.href = '/itineraries/';
            } catch (error) {
                console.error('Delete failed:', error);
                alert('삭제에 실패했습니다.');
            }
        }
    });

    // 댓글 기능
    initializeComments();

    // 시간 계산 기능
    const startTimeInput = document.getElementById('start_time');
    const endTimeInput = document.getElementById('end_time');
    const durationDisplay = document.getElementById('duration_display');

    function calculateDuration() {
        if (startTimeInput.value && endTimeInput.value) {
            const start = new Date(`2000-01-01T${startTimeInput.value}`);
            const end = new Date(`2000-01-01T${endTimeInput.value}`);
            let diff = (end - start) / 1000 / 60; // 분 단위로 변환
            
            if (diff < 0) diff += 24 * 60; // 다음날로 넘어가는 경우
            
            const hours = Math.floor(diff / 60);
            const minutes = diff % 60;
            
            durationDisplay.textContent = `${hours}시간 ${minutes}분`;
        }
    }

    startTimeInput?.addEventListener('change', calculateDuration);
    endTimeInput?.addEventListener('change', calculateDuration);

    // 공유 기능 초기화
    initializeSharing();

    // 장소간 예상 이동 시간 표시
    function showRouteInfo(origin, destination) {
        const places = new google.maps.places.PlacesService(map);
        
        // 경로 탐색 서비스
        const directionsService = new google.maps.DirectionsService();
        const directionsRenderer = new google.maps.DirectionsRenderer();
        directionsRenderer.setMap(map);
        
        directionsService.route({
            origin: new google.maps.LatLng(origin.lat, origin.lng),
            destination: new google.maps.LatLng(destination.lat, destination.lng),
            travelMode: google.maps.TravelMode.DRIVING
        }, function(result, status) {
            if (status === google.maps.DirectionsStatus.OK) {
                directionsRenderer.setDirections(result);
                const route = result.routes[0].legs[0];
                // UI에 표시
                const duration = route.duration.text; // 소요 시간
                const distance = route.distance.text; // 거리
            }
        });
    }

    // 장소 드래그 앤 드롭으로 순서 변경
    function initializeSortablePlaces() {
        const timelines = document.querySelectorAll('.places-timeline');
        timelines.forEach(timeline => {
            new Sortable(timeline, {
                animation: 150,
                onEnd: function(evt) {
                    updatePlacesOrder(evt.item.parentNode);
                }
            });
        });
    }

    // 모달이 열릴 때 슬라이더 초기화
    const modal = document.querySelector('.modal');
    modal.addEventListener('shown.bs.modal', function () {
        initImageSlider();
    });

    // 이미지 로딩 상태 처리
    document.querySelectorAll('.modal-image').forEach(img => {
        img.classList.add('loading');
        img.onload = function() {
            this.classList.remove('loading');
        }
    });
});

// 지도 초기화
function initMap() {
    const map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        mapTypeControl: false,
        streetViewControl: false
    });

    // 경로 표시
    const directionsService = new google.maps.DirectionsService();
    const directionsRenderer = new google.maps.DirectionsRenderer({
        map: map,
        suppressMarkers: true
    });

    // 마커와 경로 표시
    showPlacesOnMap(map, places, directionsRenderer, directionsService);
}

// 장소들을 지도에 표시
function showPlacesOnMap(map, places, directionsRenderer, directionsService) {
    if (places.length === 0) return;

    const bounds = new google.maps.LatLngBounds();
    const markers = [];

    // 마커 생성
    places.forEach((place, index) => {
        const position = { lat: place.lat, lng: place.lng };
        const marker = new google.maps.Marker({
            position: position,
            map: map,
            label: String(index + 1),
            title: place.name
        });
        markers.push(marker);
        bounds.extend(position);
    });

    // 지도 범위 조정
    map.fitBounds(bounds);

    // 경로 표시
    if (places.length >= 2) {
        const waypoints = places.slice(1, -1).map(place => ({
            location: new google.maps.LatLng(place.lat, place.lng),
            stopover: true
        }));

        directionsService.route({
            origin: new google.maps.LatLng(places[0].lat, places[0].lng),
            destination: new google.maps.LatLng(places[places.length - 1].lat, places[places.length - 1].lng),
            waypoints: waypoints,
            optimizeWaypoints: false,
            travelMode: 'DRIVING'
        }, (response, status) => {
            if (status === 'OK') {
                directionsRenderer.setDirections(response);
            }
        });
    }
}

// 좋아요 기능
document.getElementById('likeBtn')?.addEventListener('click', async function() {
    try {
        const response = await fetch(`/itineraries/${itineraryId}/like/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });
        const data = await response.json();
        
        // 좋아요 상태 업데이트
        this.classList.toggle('btn-danger', data.liked);
        this.classList.toggle('btn-outline-danger', !data.liked);
        document.getElementById('likeCount').textContent = data.likes_count;
    } catch (error) {
        console.error('Error:', error);
    }
});

// 댓글 기능
document.getElementById('submitComment')?.addEventListener('click', async function() {
    const content = document.getElementById('commentText').value.trim();
    if (!content) return;

    try {
        const response = await fetch(`/itineraries/${itineraryId}/comments/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ content })
        });

        const data = await response.json();
        if (response.ok) {
            // 새 댓글 추가
            const commentsList = document.getElementById('commentsList');
            commentsList.insertAdjacentHTML('afterbegin', createCommentHTML(data));
            document.getElementById('commentText').value = '';
        }
    } catch (error) {
        console.error('Error:', error);
    }
});

// 댓글 HTML 생성
function createCommentHTML(comment) {
    return `
        <div class="comment-item">
            <div class="comment-header">
                <span class="author">${comment.author.nickname}</span>
                <span class="date">${comment.created_at}</span>
            </div>
            <div class="comment-content">${comment.content}</div>
            <button class="delete-comment" data-comment-id="${comment.id}">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
}

// 댓글 기능 초기화
function initializeComments() {
    const commentForm = document.getElementById('comment-form');
    
    commentForm?.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const itineraryId = this.dataset.itineraryId;
        const content = this.querySelector('textarea[name="content"]').value;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        try {
            const response = await fetch(`/itineraries/${itineraryId}/comments/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({ content })
            });

            if (!response.ok) {
                throw new Error('댓글 작성에 실패했습니다.');
            }

            const data = await response.json();
            addNewComment(data);
            this.reset();
            
            const commentsCount = document.querySelector('.comments-count');
            if (commentsCount) {
                commentsCount.textContent = parseInt(commentsCount.textContent) + 1;
            }

            showNotification('댓글이 작성되었습니다.', 'success');
            
        } catch (error) {
            console.error('댓글 작성 실패:', error);
            showNotification('댓글 작성에 실패했습니다.', 'error');
        }
    });

    // 댓글 삭제 이벤트 위임
    const commentsList = document.querySelector('.comments-list');
    commentsList?.addEventListener('click', async function(e) {
        if (e.target.classList.contains('btn-delete-comment')) {
            const comment = e.target.closest('.comment');
            const commentId = comment.dataset.commentId;
            const itineraryId = document.querySelector('#like-button').dataset.itineraryId;

            if (confirm('댓글을 삭제하시겠습니까?')) {
                try {
                    await apiRequest(
                        `/api/v1/itineraries/${itineraryId}/comments/${commentId}/`,
                        'DELETE'
                    );
                    comment.remove();
                    updateCommentsCount(-1);
                    showNotification('댓글이 삭제되었습니다.');
                } catch (error) {
                    showNotification('댓글 삭제에 실패했습니다.', 'error');
                }
            }
        }
    });
}

function addNewComment(comment) {
    const commentsList = document.querySelector('.comments-list');
    const commentElement = document.createElement('div');
    commentElement.className = 'comment';
    commentElement.dataset.commentId = comment.id;
    
    const profileImage = comment.author.profile_image ? 
        `<img src="${comment.author.profile_image}" alt="${comment.author.nickname}" class="author-avatar">` : 
        `<img src="/static/images/default-avatar.png" alt="${comment.author.nickname}" class="author-avatar">`;
    
    commentElement.innerHTML = `
        <div class="comment-header">
            <div class="comment-author">
                ${profileImage}
                <span>${comment.author.nickname}</span>
            </div>
            <span class="comment-date">${new Date().toLocaleString()}</span>
        </div>
        <div class="comment-content">${comment.content}</div>
        <div class="comment-actions">
            <button class="btn-delete-comment">삭제</button>
        </div>
    `;
    
    commentsList.insertBefore(commentElement, commentsList.firstChild);
    updateCommentsCount(1);
}

function updateCommentsCount(change) {
    const countElement = document.querySelector('.comments-count');
    if (countElement) {
        const currentCount = parseInt(countElement.textContent);
        countElement.textContent = currentCount + change;
    }
}

// 공유 기능
function initializeSharing() {
    const shareBtn = document.getElementById('share-itinerary');
    const shareModal = document.getElementById('share-modal');
    const closeBtn = shareModal.querySelector('.btn-close');
    
    shareBtn?.addEventListener('click', () => {
        shareModal.style.display = 'block';
    });

    closeBtn?.addEventListener('click', () => {
        shareModal.style.display = 'none';
    });

    const shareBtns = document.querySelectorAll('.share-btn');
    shareBtns.forEach(btn => {
        btn.addEventListener('click', async () => {
            const platform = btn.dataset.platform;
            const url = window.location.href;
            const title = document.querySelector('h1').textContent;
            
            switch(platform) {
                case 'kakao':
                    shareKakao(url, title);
                    break;
                case 'facebook':
                    shareFacebook(url);
                    break;
                case 'twitter':
                    shareTwitter(url, title);
                    break;
                case 'link':
                    await copyToClipboard(url);
                    showNotification('링크가 복사되었습니다.');
                    break;
            }
        });
    });
}

// 카카오톡 공유
function shareKakao(url, title) {
    Kakao.Link.sendDefault({
        objectType: 'feed',
        content: {
            title: title,
            description: '여행 일정을 확인해보세요!',
            imageUrl: '/static/images/og-image.jpg',
            link: {
                mobileWebUrl: url,
                webUrl: url
            }
        },
        buttons: [{
            title: '일정 보기',
            link: {
                mobileWebUrl: url,
                webUrl: url
            }
        }]
    });
}

// 클립보드 복사
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
    } catch (err) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
    }
}

// API 요청 헬퍼 함수 추가
async function apiRequest(url, method = 'GET', data = null) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    const options = {
        method,
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return method === 'DELETE' ? null : await response.json();
}

// 이미지 슬라이더 초기화
function initImageSlider() {
    new Swiper('.image-slider', {
        slidesPerView: 1,
        spaceBetween: 30,
        loop: true,
        lazy: {
            loadPrevNext: true,
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        keyboard: {
            enabled: true,
        },
        effect: 'fade',
        fadeEffect: {
            crossFade: true
        },
    });
}

// 알림 표시 함수
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // 3초 후 자동으로 사라짐
    setTimeout(() => {
        notification.remove();
    }, 3000);
}