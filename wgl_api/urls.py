from django.urls import path, include
from .views import (
    PlayerList,
    PlayerDetail,
    MatchList,
    MatchDetail,
    ChallengeList,
    ChallengeDetail,
)

urlpatterns = [
    path('player/', PlayerList.as_view()),
    path('player/<int:discord_id>/', PlayerDetail.as_view()),
    path('match/', MatchList.as_view()),
    path('match/<int:match_id>/', MatchDetail.as_view()),
    path('challenge/', ChallengeList.as_view()),
    path('challenge/<int:challenge_id>/', ChallengeDetail.as_view()),
]