from django.urls import path, include
from .views import (
    PlayerList,
    PlayerDetail,
    MatchList,
    MatchDetail,
    ChallengeList,
    ChallengeDetail,
    QueueList,
    QueueAdd,
    LeaderboardList,
    ScoresList,
    ReportScore,
    GameList,
)

urlpatterns = [
    path('player/', PlayerList.as_view()),
    path('player/<int:discord_id>', PlayerDetail.as_view()),
    path('match/', MatchList.as_view()),
    path('match/<int:match_id>', MatchDetail.as_view()),
    path('challenge/', ChallengeList.as_view()),
    path('challenge/<int:challenge_id>', ChallengeDetail.as_view()),
    path('queue/<int:game_id>', QueueList.as_view()),
    path('queue/<int:game_id>/<int:discord_id>', QueueAdd.as_view()),
    path('leaderboard/<int:game_id>', LeaderboardList.as_view()),
    path('scores/<int:game_id>', ScoresList.as_view()),
    path('report/<int:match_id>', ReportScore.as_view()),
    path('game/', GameList.as_view()),
]