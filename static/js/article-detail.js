document.addEventListener('DOMContentLoaded', function() {
    const likeButton = document.getElementById('like-button');
    const deleteButton = document.getElementById('delete-article');
    const commentForm = document.getElementById('comment-form');
    
    // 좋아요 기능
    likeButton?.addEventListener('click', async function() {
        try {
            const articleId = this.dataset.articleId;
            const response = await apiRequest(
                `/api/v1/articles/${articleId}/like/`,
                'POST'
            );
            
            if (response.liked) {
                this.classList.add('liked');
            } else {
                this.classList.remove('liked');
            }
            
            document.getElementById('likes-count').textContent = response.likes_count;
            showNotification(response.message);
        } catch (error) {
            showNotification('오류가 발생했습니다.', 'error');
        }
    });

    // 게시글 삭제
    deleteButton?.addEventListener('click', async function() {
        if (confirm('정말 삭제하시겠습니까?')) {
            try {
                const articleId = likeButton.dataset.articleId;
                await apiRequest(
                    `/api/v1/articles/${articleId}/`,
                    'DELETE'
                );
                window.location.href = '/articles/';
            } catch (error) {
                showNotification('삭제에 실패했습니다.', 'error');
            }
        }
    });

    // 댓글 작성
    commentForm?.addEventListener('submit', async function(e) {
        e.preventDefault();
        try {
            const articleId = likeButton.dataset.articleId;
            const content = this.querySelector('textarea').value;
            
            const response = await apiRequest(
                `/api/v1/articles/${articleId}/comments/`,
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

    // 댓글 추가 함수
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
                <span class="comment-date">${new Date(comment.created_at).toLocaleString()}</span>
            </div>
            <div class="comment-content">${comment.content}</div>
            <div class="comment-actions">
                <button class="btn-edit-comment">수정</button>
                <button class="btn-delete-comment">삭제</button>
            </div>
        `;
        
        commentsList.insertBefore(commentElement, commentsList.firstChild);
        updateCommentsCount(1);
    }

    // 댓글 수 업데이트
    function updateCommentsCount(change) {
        const countElement = document.querySelector('.comments-count');
        const currentCount = parseInt(countElement.textContent);
        countElement.textContent = currentCount + change;
    }
});
