document.addEventListener('DOMContentLoaded', function() {
    // WYSIWYG 에디터 테마 설정
    if (document.getElementById('content')) {
        ClassicEditor
            .create(document.getElementById('content'), {
                // 에디터 테마 설정
                toolbar: {
                    shouldNotGroupWhenFull: true
                },
                ui: {
                    viewportOffset: { top: 80 }
                }
            })
            .then(editor => {
                // 다크 모드 변경 감지 및 에디터 스타일 업데이트
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        if (mutation.attributeName === 'data-theme') {
                            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
                            const editorElement = editor.ui.view.element;
                            if (isDark) {
                                editorElement.style.backgroundColor = 'var(--surface-bg)';
                                editorElement.style.color = 'var(--text-color)';
                            } else {
                                editorElement.style.backgroundColor = '#ffffff';
                                editorElement.style.color = '#333333';
                            }
                        }
                    });
                });

                observer.observe(document.documentElement, {
                    attributes: true,
                    attributeFilter: ['data-theme']
                });
            })
            .catch(error => {
                console.error(error);
            });
    }

    // 폼 제출 전 유효성 검사
    const articleForm = document.querySelector('.article-form');
    if (articleForm) {
        articleForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const title = document.getElementById('id_title').value.trim();
            const content = document.getElementById('id_content').value.trim();
            
            if (!title) {
                alert('제목을 입력해주세요.');
                return;
            }
            
            if (!content) {
                alert('내용을 입력해주세요.');
                return;
            }

            // 이미지 유효성 검사
            const images = document.getElementById('id_images').files;
            if (images.length > 5) {
                alert('이미지는 최대 5개까지만 업로드할 수 있습니다.');
                return;
            }

            // 모든 검증을 통과하면 폼 제출
            this.submit();
        });
    }

    // 이미지 미리보기
    const imageInput = document.getElementById('id_images');
    const previewContainer = document.createElement('div');
    previewContainer.className = 'image-previews';
    
    if (imageInput) {
        imageInput.after(previewContainer);
        
        imageInput.addEventListener('change', function(e) {
            previewContainer.innerHTML = '';
            const files = Array.from(e.target.files);
            
            files.forEach(file => {
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    const preview = document.createElement('div');
                    preview.className = 'image-preview';
                    
                    reader.onload = function(e) {
                        preview.innerHTML = `
                            <img src="${e.target.result}" alt="Preview">
                            <button type="button" class="remove-image">×</button>
                        `;
                        previewContainer.appendChild(preview);
                    };
                    
                    reader.readAsDataURL(file);
                }
            });
        });
        
        // 미리보기 이미지 삭제
        previewContainer.addEventListener('click', function(e) {
            if (e.target.classList.contains('remove-image')) {
                e.target.closest('.image-preview').remove();
            }
        });
    }

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
            <article class="article-card" style="background-color: var(--surface-bg); color: var(--text-color);">
                ${article.image ? `
                    <div class="article-image">
                        <img src="${article.image}" alt="${article.title}">
                    </div>
                ` : ''}
                <div class="article-content">
                    <h3><a href="/articles/${article.id}/" style="color: var(--text-primary);">${article.title}</a></h3>
                    <div class="article-meta" style="color: var(--text-secondary);">
                        <span class="author">${article.author_nickname}</span>
                        <span class="date">${new Date(article.created_at).toLocaleDateString()}</span>
                        <span class="views">조회 ${article.views}</span>
                        <span class="likes">좋아요 ${article.likes_count}</span>
                    </div>
                    <p class="article-excerpt" style="color: var(--text-secondary);">${article.content.substring(0, 100)}...</p>
                    ${article.tags.length ? `
                        <div class="article-tags">
                            ${article.tags.map(tag => `
                                <span class="tag" style="background-color: var(--primary-color);">${tag.name}</span>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            </article>
        `).join('') : '<div class="no-articles"><p style="color: var(--text-secondary);">검색 결과가 없습니다.</p></div>';
    }
});
