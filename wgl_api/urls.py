from django.urls import path
from .views import (
    MatchmakeView,
    PlayerList,
    PlayerDetail,
    MatchList,
    MatchDetail,
    ChallengeList,
    ChallengeDetail,
    QueueList,
    # LeaderboardList,
    LeaderboardDetail,
    # ScoresList,
    ScoresDetail,
    GameList,
)

urlpatterns = [
    path("player/", PlayerList.as_view()),
    path("player/<int:discord_id>", PlayerDetail.as_view()),
    path("match/", MatchList.as_view()),
    path("match/<int:match_id>", MatchDetail.as_view()),
    path("challenge/", ChallengeList.as_view()),
    path("challenge/<int:challenge_id>", ChallengeDetail.as_view()),
    path("queue/<int:game_id>", QueueList.as_view()),
    # path("leaderboard/", LeaderboardList.as_view()),
    path("leaderboard/<int:game_id>", LeaderboardDetail.as_view()),
    # path("scores/", ScoresList.as_view()),
    path("scores/<int:game_id>", ScoresDetail.as_view()),
    path("game/", GameList.as_view()),
    path("matchmake/", MatchmakeView.as_view()),
]
