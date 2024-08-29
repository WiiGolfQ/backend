from django.urls import path, include

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
    CategoryList,
    CategoryDetail,
)

urlpatterns = [
    path("auth/", include("dj_rest_auth.urls")),
    path("player", PlayerList.as_view()),
    path("player/<int:discord_id>", PlayerDetail.as_view()),
    path("match", MatchList.as_view()),
    path("match/<int:match_id>", MatchDetail.as_view()),
    path("challenge", ChallengeList.as_view()),
    path("challenge/<int:challenge_id>", ChallengeDetail.as_view()),
    path("queue/<int:category_id>", QueueList.as_view()),
    # path("leaderboard/", LeaderboardList.as_view()),
    path("leaderboard/<int:category_id>", LeaderboardDetail.as_view()),
    # path("scores/", ScoresList.as_view()),
    path("scores/<int:category_id>", ScoresDetail.as_view()),
    path("category", CategoryList.as_view()),
    path("category/<str:shortcode>", CategoryDetail.as_view()),
    path("matchmake", MatchmakeView.as_view()),
]
