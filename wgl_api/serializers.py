from rest_framework import serializers

from .models import (
    Player,
    Game,
    Match,
    Score,
    Challenge,
    Elo,
)

class FullPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = [
            "discord_id",
            "username",
            "created_timestamp",
            "last_active_timestamp",
            "yt_username",
            "queueing_for",
            "currently_playing_match",
            "accept_challenges",
            "banned",
        ]

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = [
            "discord_id",
            "username",
            "yt_username",
        ]

class FullGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ["game_id", "game_name", "speedrun", "require_livestream", "best_of"]
        
class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ["game_id", "game_name"]
        
class MatchSerializer(serializers.ModelSerializer):
    game = GameSerializer(read_only=True)
    p1 = PlayerSerializer(read_only=True)
    p2 = PlayerSerializer(read_only=True)
    class Meta:
        model = Match
        fields = ["match_id", "game", "timestamp_started", "timestamp_finished", "status", "contest_reason", "p1", "p2", "result", "p1_score", "p2_score", "p1_video_url", "p2_video_url"]
        
class ChallengeSerializer(serializers.ModelSerializer):
    game = GameSerializer(read_only=True)
    class Meta:
        model = Challenge
        fields = ['challenge_id', 'timestamp', 'game', 'challenger', 'challenged']
        
class EloSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)
    class Meta:
        model = Elo
        fields = ["player", "mu"]
        
class ScoreSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)
    class Meta:
        model = Score
        fields = ["player", "score", "match"]