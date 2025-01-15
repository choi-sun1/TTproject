from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Post, Comment
from .forms import PostForm
from .models import Post, PostImage
from django.contrib import messages

def post_list(request):
    sort = request.GET.get('sort', 'latest')
    page_number = request.GET.get('page', '1')
    
    # 정렬 기준에 따른 쿼리셋 생성
    if sort == 'likes':
        posts = Post.objects.annotate(
            like_count=Count('likes')
        ).order_by('-like_count', '-created_at')
    elif sort == 'views':
        posts = Post.objects.order_by('-views', '-created_at')
    else:  # 최신순
        posts = Post.objects.order_by('-created_at')

    # 페이지네이션
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(page_number)

    context = {
        'posts': page_obj,
        'current_sort': sort,
        'current_page': page_number,
    }
    return render(request, 'board/list.html', context)

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.views += 1
    post.save()
    return render(request, 'board/detail.html', {'post': post})

@login_required
def post_write(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        files = request.FILES.getlist('images')  # 파일은 별도로 처리
        
        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.author = request.user
                post.save()

                # 이미지 파일 처리
                for image in files:
                    if len(files) > 10:
                        messages.error(request, '이미지는 최대 10개까지만 업로드할 수 있습니다.')
                        post.delete()
                        return render(request, 'board/write.html', {'form': form})

                    if image.size > 5 * 1024 * 1024:  # 5MB
                        messages.error(request, '각 이미지의 크기는 5MB를 초과할 수 없습니다.')
                        post.delete()
                        return render(request, 'board/write.html', {'form': form})
                    
                    # 이미지 파일 타입 검사
                    if not image.content_type.startswith('image/'):
                        messages.error(request, '이미지 파일만 업로드할 수 있습니다.')
                        post.delete()
                        return render(request, 'board/write.html', {'form': form})
                    
                    PostImage.objects.create(post=post, image=image)

                messages.success(request, '게시글이 작성되었습니다.')
                return redirect('board:detail', pk=post.pk)
            except Exception as e:
                messages.error(request, f'게시글 작성 중 오류가 발생했습니다: {str(e)}')
                return render(request, 'board/write.html', {'form': form})
    else:
        form = PostForm()
    
    return render(request, 'board/write.html', {'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        # HTML을 마크다운으로 변환하지 않고 원본 상태로 저장
        post.title = request.POST['title']
        post.content = request.POST['content']
        
        # 삭제할 이미지 처리
        delete_images = request.POST.getlist('delete_images')
        if delete_images:
            PostImage.objects.filter(id__in=delete_images, post=post).delete()
        
        # 새 이미지 추가
        new_images = request.FILES.getlist('images')
        current_images = post.images.count()
        if current_images + len(new_images) > 10:
            messages.error(request, '이미지는 최대 10개까지만 업로드할 수 있습니다.')
            return render(request, 'board/edit.html', {'post': post})
            
        for image in new_images:
            if image.size > 5 * 1024 * 1024:  # 5MB
                messages.error(request, '각 이미지의 크기는 5MB를 초과할 수 없습니다.')
                return render(request, 'board/edit.html', {'post': post})
                
            if not image.content_type.startswith('image/'):
                messages.error(request, '이미지 파일만 업로드할 수 있습니다.')
                return render(request, 'board/edit.html', {'post': post})
            
            PostImage.objects.create(post=post, image=image)
        
        post.save()
        messages.success(request, '게시글이 수정되었습니다.')
        return redirect('board:detail', pk=post.pk)
    else:
        # 수정 페이지에서는 원본 마크다운 텍스트 표시
        return render(request, 'board/edit.html', {
            'post': post,
            'content': post.content  # HTML이 아닌 원본 마크다운 전달
        })

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('board:list')
    return redirect('board:detail', pk=pk)

@login_required
def comment_create(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        comment = Comment(
            post=post,
            author=request.user,
            content=request.POST['content']
        )
        comment.save()
    return redirect('board:detail', pk=post_id)

@login_required
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'count': post.likes.count()
    })
