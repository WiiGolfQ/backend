from rest_framework import serializers

from .models import (
    Player,
    Game,
    Match,
    Score,
)

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ["game_id", "game_name", "speedrun", "require_livestream", "best_of", "players_in_queue"]
        
class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ["match_id", "game", "timestamp_started", "timestamp_finished", "status", "contest_reason", "player1", "player2", "result", "player1_score", "player2_score", "player_1_video_url", "player_2_video_url", "timestamp"]