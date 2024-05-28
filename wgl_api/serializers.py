from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from drf_writable_nested.mixins import NestedUpdateMixin, UniqueFieldsMixin

from .models import (
    Player,
    Game,
    Match,
    Score,
    Challenge,
    Elo,
    Team,
    TeamPlayer,
    Youtube,
)


class YoutubeSerializer(
    UniqueFieldsMixin, WritableNestedModelSerializer, serializers.Serializer
):
    class Meta:
        model = Youtube
        fields = ["handle", "video_id"]


class FullPlayerSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    currently_playing_match = serializers.SerializerMethodField()

    youtube = YoutubeSerializer(read_only=False, required=False)

    class Meta:
        model = Player
        fields = [
            "discord_id",
            "username",
            "created_timestamp",
            "last_active_timestamp",
            "youtube",
            "in_queue",
            "queues_for",
            "currently_playing_match",
            "accept_challenges",
            "banned",
        ]

    def get_currently_playing_match(self, obj):
        match = obj.currently_playing_match()
        if match:
            return match.match_id
        return None


class PlayerSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    youtube = YoutubeSerializer(read_only=False, required=False)

    class Meta:
        model = Player
        fields = [
            "discord_id",
            "username",
            "youtube",
        ]


class GameSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
    shortcode = serializers.CharField(required=False)
    game_name = serializers.CharField(required=False)

    class Meta:
        model = Game
        fields = ["game_id", "shortcode", "game_name", "speedrun"]


class TeamPlayerSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = TeamPlayer
        fields = [
            "pk",
            "match",
            "player",
            "score",
            "score_formatted",
            "video_id",
            "video_timestamp",
            "mu_before",
            "mu_after",
        ]


class TeamSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    players = TeamPlayerSerializer(many=True, read_only=False)

    class Meta:
        model = Team
        fields = [
            "pk",
            "match",
            "place",
            "team_num",
            "players",
            "score",
            "score_formatted",
            "predictions",
        ]


class MatchSerializer(NestedUpdateMixin, serializers.ModelSerializer):
    game = GameSerializer(read_only=False, required=False)
    teams = TeamSerializer(many=True, read_only=False, required=False)

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

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # order the teams by place and then team_num
        representation["teams"] = sorted(
            representation["teams"],
            key=lambda team: ((team["place"] is None, team["place"]), team["team_num"]),
        )

        return representation


class ChallengeSerializer(serializers.ModelSerializer):
    game = GameSerializer(read_only=True)

    class Meta:
        model = Challenge
        fields = ["challenge_id", "timestamp", "game", "challenger", "challenged"]


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
        fields = [
            "player",
            "score",
            "score_formatted",
            "match",
            "overall_rank",
            "player_rank",
            "non_obsolete_rank",
        ]
