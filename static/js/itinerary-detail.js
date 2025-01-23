document.addEventListener('DOMContentLoaded', function() {
    // 지도 초기화
    const mapContainer = document.getElementById('map');
    const markers = [];
    const paths = [];
    let map;

    if (mapContainer) {
        map = new kakao.maps.Map(mapContainer, {
            center: new kakao.maps.LatLng(37.5665, 126.9780),
            level: 3
        });

        // 모든 장소 마커 생성
        const places = document.querySelectorAll('.place-item');
        if (places.length > 0) {
            const bounds = new kakao.maps.LatLngBounds();
            
            places.forEach((place, index) => {
                const lat = parseFloat(place.dataset.lat);
                const lng = parseFloat(place.dataset.lng);
                const latlng = new kakao.maps.LatLng(lat, lng);
                
                // 마커 생성
                const marker = new kakao.maps.Marker({
                    position: latlng,
                    map: map
                });

                // 마커에 번호 표시
                const content = `<div class="marker-label">${index + 1}</div>`;
                const customOverlay = new kakao.maps.CustomOverlay({
                    position: latlng,
                    content: content
                });
                
                markers.push(marker);
                customOverlay.setMap(map);
                bounds.extend(latlng);

                // 이전 위치가 있으면 경로 그리기
                if (index > 0) {
                    const prevLat = parseFloat(places[index - 1].dataset.lat);
                    const prevLng = parseFloat(places[index - 1].dataset.lng);
                    const path = [
                        new kakao.maps.LatLng(prevLat, prevLng),
                        latlng
                    ];

                    const polyline = new kakao.maps.Polyline({
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

            map.setBounds(bounds);
        }
    }

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
                const itineraryId = likeButton.dataset.itineraryId;
                await apiRequest(
                    `/api/v1/itineraries/${itineraryId}/`,
                    'DELETE'
                );
                window.location.href = '/web/itineraries/';
            } catch (error) {
                showNotification('삭제에 실패했습니다.', 'error');
            }
        }
    });

    // 댓글 기능
    initializeComments();
});

function initializeComments() {
    const commentForm = document.getElementById('comment-form');
    const commentsList = document.querySelector('.comments-list');

    commentForm?.addEventListener('submit', async function(e) {
        e.preventDefault();
        const itineraryId = document.querySelector('#like-button').dataset.itineraryId;
        const content = this.querySelector('textarea').value;

        try {
            const response = await apiRequest(
                `/api/v1/itineraries/${itineraryId}/comments/`,
                'POST',
                { content }
            );
            
            addNewComment(response);
            this.reset();
            showNotification('댓글이 작성되었습니다.');
        } catch (error) {
            showNotification('댓글 작성에 실패했습니다.', 'error');
        }
    });

    // 댓글 삭제 이벤트 위임
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
    
    commentElement.innerHTML = `
        <div class="comment-header">
            <div class="comment-author">
                ${comment.author.profile_image ? 
                    `<img src="${comment.author.profile_image}" alt="${comment.author.nickname}">` : 
                    ''}
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
