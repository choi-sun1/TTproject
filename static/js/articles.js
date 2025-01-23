document.addEventListener('DOMContentLoaded', function() {
    // 좋아요 기능
    document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const articleId = this.dataset.articleId;
            
            try {
                const response = await apiRequest(
                    `/api/v1/articles/${articleId}/like/`,
                    'POST'
                );
                
                const likeCount = this.querySelector('.like-count');
                likeCount.textContent = response.likes_count;
                
                this.classList.toggle('liked');
                showNotification(response.message);
            } catch (error) {
                showNotification('오류가 발생했습니다.', 'error');
            }
        });
    });

    // 댓글 작성
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const articleId = this.dataset.articleId;
            const content = this.querySelector('textarea').value;
            
            try {
                const response = await apiRequest(
                    `/api/v1/articles/${articleId}/comments/`,
                    'POST',
                    { content }
                );
                
                // 새 댓글 추가
                const commentsContainer = document.querySelector('.comments-list');
                commentsContainer.insertAdjacentHTML('beforeend', `
                    <div class="comment">
                        <p>${response.content}</p>
                        <small>${response.author_nickname}</small>
                    </div>
                `);
                
                this.reset();
                showNotification('댓글이 작성되었습니다.');
            } catch (error) {
                showNotification('댓글 작성에 실패했습니다.', 'error');
            }
        });
    }
});
