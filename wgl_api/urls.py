from django.urls import path, include
from .views import (
    PlayerList,
    PlayerDetail,
)

urlpatterns = [
    path('player/', PlayerList.as_view()),
    path('player/<int:discord_id>/', PlayerDetail.as_view()),
]