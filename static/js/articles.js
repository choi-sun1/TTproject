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

    const sortSelect = document.getElementById('sort-select');
    const searchInput = document.getElementById('search-input');
    let searchTimeout;

    // 정렬 변경 이벤트
    sortSelect?.addEventListener('change', function() {
        fetchArticles({
            sort: this.value,
            search: searchInput.value
        });
    });

    // 검색어 입력 이벤트 (디바운싱 적용)
    searchInput?.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            fetchArticles({
                sort: sortSelect.value,
                search: this.value
            });
        }, 300);
    });

    // 게시글 목록 가져오기
    async function fetchArticles(params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            const response = await fetch(`/api/v1/articles/?${queryString}`);
            const data = await response.json();
            
            if (response.ok) {
                updateArticlesList(data.results);
            } else {
                showNotification('게시글을 불러오는데 실패했습니다.', 'error');
            }
        } catch (error) {
            console.error('Error fetching articles:', error);
            showNotification('오류가 발생했습니다.', 'error');
        }
    }

    // 게시글 목록 업데이트
    function updateArticlesList(articles) {
        const container = document.getElementById('articles-container');
        if (!container) return;

        container.innerHTML = articles.length ? articles.map(article => `
            <article class="article-card">
                ${article.image ? `
                    <div class="article-image">
                        <img src="${article.image}" alt="${article.title}">
                    </div>
                ` : ''}
                <div class="article-content">
                    <h3><a href="/articles/${article.id}/">${article.title}</a></h3>
                    <div class="article-meta">
                        <span class="author">${article.author_nickname}</span>
                        <span class="date">${new Date(article.created_at).toLocaleDateString()}</span>
                        <span class="views">조회 ${article.views}</span>
                        <span class="likes">좋아요 ${article.likes_count}</span>
                    </div>
                    <p class="article-excerpt">${article.content.substring(0, 100)}...</p>
                    ${article.tags.length ? `
                        <div class="article-tags">
                            ${article.tags.map(tag => `
                                <span class="tag">${tag.name}</span>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            </article>
        `).join('') : '<div class="no-articles"><p>검색 결과가 없습니다.</p></div>';
    }
});
