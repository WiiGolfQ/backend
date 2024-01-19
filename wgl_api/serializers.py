from rest_framework import serializers

from .models import (
    Player,
    Game,
    Match,
    Score,
)

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = [
            "discord_id",
            "username",
            "created_timestamp",
            "last_active_timestamp",
            "yt_username",
            "currently_playing_match",
            "accept_challenges",
            "banned",
        ]

class FullGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ["game_id", "game_name", "speedrun", "require_livestream", "best_of", "players_in_queue"]
        
class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ["game_id", "game_name"]
        
class MatchSerializer(serializers.ModelSerializer):
    game = GameSerializer()
    class Meta:
        model = Match
        fields = ["match_id", "game", "timestamp_started", "timestamp_finished", "status", "contest_reason", "player_1", "player_2", "result", "player_1_score", "player_2_score", "player_1_video_url", "player_2_video_url"]