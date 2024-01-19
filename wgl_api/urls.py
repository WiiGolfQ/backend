from django.urls import path, include
from .views import (
    GameApiView,
    MatchApiView,
)

urlpatterns = [
    path('game', GameApiView.as_view()),
    path('match', MatchApiView.as_view()),
]