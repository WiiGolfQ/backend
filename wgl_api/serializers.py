from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from drf_writable_nested.mixins import NestedUpdateMixin, UniqueFieldsMixin

from .models import (
    Player,
    Category,
    Match,
    Challenge,
    Elo,
    Team,
    TeamPlayer,
    Youtube,
    Game,
)


class YoutubeSerializer(
    UniqueFieldsMixin, WritableNestedModelSerializer, serializers.Serializer
):
    class Meta:
        model = Youtube
        fields = ["handle", "video_id"]


class FullPlayerSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
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


class PlayerSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    youtube = YoutubeSerializer(read_only=False, required=False)

    class Meta:
        model = Player
        fields = [
            "discord_id",
            "username",
            "youtube",
        ]


class GameSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ["game_id", "game_name", "categories"]

    def get_categories(self, obj):
        return CategorySerializer(Category.objects.filter(game=obj), many=True).data


class CategorySerializer(UniqueFieldsMixin, serializers.ModelSerializer):
    shortcode = serializers.CharField(required=False)
    category_name = serializers.CharField(required=False)

    class Meta:
        model = Category
        fields = [
            "category_id",
            "shortcode",
            "category_name",
            "game",
            "speedrun",
            "require_livestreams",
            "minimum_livestreamers",
        ]


class TeamPlayerSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = TeamPlayer
        fields = [
            "pk",
            "player",
            "score",
            "score_formatted",
            "video_id",
            "video_timestamp",
            "mu_before",
            "mu_after",
            "mu_delta",
        ]

    read_only_fields = ["score_formatted", "mu_delta"]


class TeamSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    players = TeamPlayerSerializer(many=True, read_only=False)

    class Meta:
        model = Team
        fields = [
            "pk",
            "place",
            "team_num",
            "players",
            "score",
            "score_formatted",
            "forfeited",
        ]

    read_only_fields = ["score_formatted"]


class MatchSerializer(NestedUpdateMixin, serializers.ModelSerializer):
    category = CategorySerializer(read_only=False, required=False)
    teams = TeamSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = Match
        fields = [
            "match_id",
            "discord_thread_id",
            "category",
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

        # put the forfeited teams last, then order the rest by rank
        # (not forfeited with no rank goes in between not forfeited with rank and forfeited)
        representation["teams"] = sorted(
            representation["teams"],
            key=lambda team: (
                team["forfeited"],
                float("inf") if team["place"] is None else team["place"],
            ),
        )

        return representation


class ChallengeSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Challenge
        fields = ["challenge_id", "timestamp", "category", "challenger", "challenged"]


class EloSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)
    rank = serializers.SerializerMethodField()

    class Meta:
        model = Elo
        fields = ["pk", "rank", "player", "mu"]

    def get_rank(self, obj):
        return obj.rank


class ScoreSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    player_rank = serializers.IntegerField()
    overall_rank = serializers.IntegerField()
    non_obsolete_rank = serializers.IntegerField()

    class Meta:
        model = TeamPlayer
        fields = [
            "pk",
            "player",
            "category",
            "match",
            "score",
            "score_formatted",
            "overall_rank",
            "player_rank",
            "non_obsolete_rank",
        ]
