def user_profile(request):
    """사용자 프로필 정보를 템플릿에서 사용할 수 있도록 컨텍스트에 추가"""
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            return {
                'user_profile': profile,
                'user_avatar': profile.avatar if profile.avatar else None,
                'user_nickname': profile.nickname or request.user.username,
            }
        except:
            return {}
    return {}