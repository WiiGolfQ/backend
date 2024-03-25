from rest_framework import serializers

from .models import (
    Player,
    Game,
    Match,
    Score,
    Challenge,
    Elo,
    Team,
    TeamPlayer,
)

class FullPlayerSerializer(serializers.ModelSerializer):
    
    currently_playing_match = serializers.SerializerMethodField()
    
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
        
    def get_currently_playing_match(self, obj):
        match = obj.currently_playing_match()
        if match:
            return match.match_id
        return None

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = [
            "discord_id",
            "username",
            "yt_username",
        ]
        
class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ["game_id", "shortcode", "game_name", "speedrun"]
        
class TeamPlayerSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)
    class Meta:
        model = TeamPlayer
        fields = [
            "player",
            "score",
            "score_formatted",
            "video_id",
            "video_timestamp",
            "mu_before",
            "mu_after",
            "predictions",
        ]
        
class TeamSerializer(serializers.ModelSerializer):
    players = TeamPlayerSerializer(many=True, read_only=False)
    class Meta:
        model = Team
        fields = [
            "place",
            "team_num",
            "player_ids",
            "players",
            "score",
            "score_formatted",
            "predictions",
        ]
        
class MatchSerializer(serializers.ModelSerializer):
    game = GameSerializer(read_only=True)
    teams = TeamSerializer(many=True, read_only=False)

    class Meta:
        model = Match
        fields = [
            "match_id",
            "discord_thread_id",
            "game",
            "timestamp_started",
            "timestamp_finished",
            "num_teams",
            "players_per_team",
            "teams",
            "active",
            "status",
        ]
        
class ChallengeSerializer(serializers.ModelSerializer):
    game = GameSerializer(read_only=True)
    class Meta:
        model = Challenge
        fields = ['challenge_id', 'timestamp', 'game', 'challenger', 'challenged']
        
class EloSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)
    rank = serializers.SerializerMethodField()    
    
    class Meta:
        model = Elo
        fields = ["rank", "player", "mu"]
        
    def get_rank(self, obj):
        return obj.rank
        
class ScoreSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)
    
    player_rank = serializers.IntegerField()
    overall_rank = serializers.IntegerField()
    non_obsolete_rank = serializers.IntegerField()
    
    class Meta:
        model = Score
        fields = ["player", "score", "score_formatted", "match", 'overall_rank', 'player_rank', 'non_obsolete_rank']