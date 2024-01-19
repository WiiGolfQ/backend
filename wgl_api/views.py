from django.shortcuts import get_object_or_404

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import generics

from .models import (
    Game,
    Match,
    Player,
)

from .serializers import (
    FullGameSerializer,
    MatchSerializer,
    PlayerSerializer,
)

class PlayerList(generics.ListCreateAPIView):
    serializer_class = PlayerSerializer
    
    def get_queryset(self):
        queryset = Player.objects.all() 
        
        discord_id = self.request.query_params.get("discord_id", None)
        if discord_id is not None:
            queryset = queryset.filter(discord_id=discord_id)
            
        return queryset

class PlayerDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PlayerSerializer

    def get_object(self):
        discord_id = self.kwargs.get('discord_id')
        return get_object_or_404(Player, discord_id=discord_id)