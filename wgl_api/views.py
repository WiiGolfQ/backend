from datetime import datetime

from django.shortcuts import get_object_or_404
from django.db.models import (
    Window,
    F,
    Q,
    Case,
    When,
    Value,
    IntegerField,
    Subquery,
    Prefetch,
)
from django.db.models.functions import Rank

from django_cte import With

from rest_framework import status, permissions, generics, mixins
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from .utils import create_match, assign_elo

from .models import (
    Game,
    Match,
    Player,
    Challenge,
    Elo,
    Score,
    Team,
    TeamPlayer,
    Youtube,
)

from .serializers import (
    GameSerializer,
    MatchSerializer,
    FullPlayerSerializer,
    ChallengeSerializer,
    EloSerializer,
    ScoreSerializer,
    TeamPlayerSerializer,
)

from .paginations import RankingPagination

from .matchmaking import matchmake


class PlayerInMatch(APIException):
    status_code = 400
    default_detail = "Player is already in a match"
    default_code = "bad_request"


class PlayerNotInMatch(APIException):
    status_code = 400
    default_detail = "Player is not in this match"
    default_code = "bad_request"


class DuplicateYTUsername(APIException):
    status_code = 400
    default_detail = "This YouTube username is already in use"
    default_code = "bad_request"


class PlayerList(generics.ListCreateAPIView):
    serializer_class = FullPlayerSerializer

    def create(self, request, *args, **kwargs):
        discord_id = request.data.get("discord_id")
        username = request.data.get("username")
        youtube = request.data.get("youtube")

        if discord_id is None or username is None or youtube is None:
            return Response(
                {"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST
            )

        player, created = Player.objects.get_or_create(discord_id=discord_id)

        if (
            Player.objects.filter(username=username)
            .exclude(discord_id=discord_id)
            .exists()
        ):
            return Response(
                {"error": "Username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Youtube.objects.filter(handle=youtube.get("handle")).exists():
            return Response(
                {"error": "YouTube username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        player.username = username

        if created:
            player.created_timestamp = datetime.now()
            youtube = Youtube.objects.create(
                handle=youtube.get("handle"), video_id=youtube.get("video_id")
            )
            player.youtube = youtube
        else:
            player.youtube.handle = youtube.get("handle")

        player.save()

        serializer = self.get_serializer(player)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class PlayerDetail(generics.RetrieveUpdateDestroyAPIView, mixins.CreateModelMixin):
    serializer_class = FullPlayerSerializer

    def get_object(self):
        discord_id = self.kwargs.get("discord_id")
        return get_object_or_404(Player, discord_id=discord_id)

    def post(self, request, *args, **kwargs):
        player = Player.objects.filter(
            discord_id=request.data.get("discord_id")
        ).first()

        # if it needs to be created
        if not player:
            return self.create(request, *args, **kwargs)

        # update the existing player
        youtube_data = request.data.pop("youtube")
        handle = youtube_data.get("handle")
        video_id = youtube_data.get("video_id")

        if handle is not None:
            player.youtube.handle = handle
        if video_id is not None:
            player.youtube.video_id = video_id

        player.youtube.save()

        return super(PlayerDetail, self).update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # player = self.get_object()

        # # is another player queueing for this game?
        # # if so, start a match with both players

        # other_player = Player.objects.filter(queueing_for=queueing_for).first()

        # if other_player is not None:

        #     # start a match with both players
        #     match = create_match(player, other_player, queueing_for_game)

        #     # return the match
        #     # TODO: we need a more permanent way to do this
        #     return Response(MatchSerializer(match).data, status=status.HTTP_201_CREATED)

        return super(PlayerDetail, self).update(request, *args, **kwargs)


class MatchList(generics.ListCreateAPIView):
    serializer_class = MatchSerializer

    def get_queryset(self):
        queryset = Match.objects.all()

        game_id = self.request.query_params.get("game_id", None)
        if game_id is not None:
            queryset = queryset.filter(game=game_id)

        active = self.request.query_params.get("active", None)
        if active is not None:
            queryset = queryset.filter(active=True)

        return queryset.order_by("-timestamp_started")


class MatchDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MatchSerializer

    def get_object(self):
        match_id = self.kwargs.get("match_id")
        return get_object_or_404(Match, match_id=match_id)

    def update(self, request, *args, **kwargs):
        match = self.get_object()

        data = request.data

        old_status = match.status

        # check if the status was updated to "Finished"
        if match.status == "Finished":
            # update finish timestamp
            match.timestamp_finished = datetime.now()

            if old_status == "Result contested":
                # retroactive result change procedure, just pass for now
                pass
            else:
                # assign player elos based on the match result
                assign_elo(match)

        serializer = self.get_serializer(match, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        match.save()

        return super(MatchDetail, self).update(request, *args, **kwargs)


class MatchmakeView(generics.ListAPIView):
    serializer_class = MatchSerializer
    queryset = None


# OBSOLETE
class ReportScore(generics.RetrieveAPIView):
    serializer_class = MatchSerializer

    # either create a new score or update an existing one

    def get_object(self):
        match_id = self.kwargs.get("match_id")
        return get_object_or_404(Match, match_id=match_id)

    def get(self, request, *args, **kwargs):
        match = self.get_object()

        discord_id = self.request.query_params.get("player", None)

        score = self.request.query_params.get("score", None)
        score = int(score) if score is not None else None

        player = get_object_or_404(Player, discord_id=discord_id)

        if score is not None:
            if player != match.p1 and player != match.p2:
                raise PlayerNotInMatch()

            player_score = Score.objects.filter(
                player=player, game=match.game, match=match
            ).first()

            # we need to check if a score object already exists,
            # so we can either update it or create a new one

            if player_score:
                player_score.score = score
                player_score.save()

                # hack to get the computed fields to update before returning the match
                # TODO: try and find a way to delete this
                match = player_score.match
                match.save()

            else:
                new_score = Score.objects.create(
                    player=player,
                    game=match.game,
                    match=match,
                    score=score,
                )

                # hack to get the computed fields to update before returning the match
                # TODO: try and find a way to delete this
                match.save()

        serializer = self.get_serializer(match)
        return Response(serializer.data)


class ChallengeList(generics.ListCreateAPIView):
    serializer_class = ChallengeSerializer

    def get_queryset(self):
        queryset = Challenge.objects.filter(accepted=None)

        game_id = self.request.query_params.get("game_id", None)
        if game_id is not None:
            queryset = queryset.filter(game=game_id)

        return queryset


class ChallengeDetail(generics.RetrieveDestroyAPIView):
    serializer_class = ChallengeSerializer

    def get_object(self):
        challenge_id = self.kwargs.get("challenge_id")
        return get_object_or_404(Challenge, challenge_id=challenge_id)


class QueueList(generics.ListAPIView):
    serializer_class = FullPlayerSerializer

    def get_object(self):
        game_id = self.kwargs.get("game_id")
        return get_object_or_404(Game, game_id=game_id)

    def get_queryset(self):
        game = self.get_object()
        return Player.objects.filter(queueing_for=game)


# class QueueAdd(generics.ListAPIView):
#     serializer_class = MatchSerializer

#     queryset = Match.objects.none()

#     def get_object(self):
#         game_id = self.kwargs.get("game_id")
#         discord_id = self.kwargs.get("discord_id")

#         if game_id == 0:
#             return (None, Player.objects.filter(discord_id=discord_id).first())

#         return (
#             get_object_or_404(Game, game_id=game_id),
#             Player.objects.filter(discord_id=discord_id).first(),
#         )

#     def get(self, request, *args, **kwargs):
#         game, player = self.get_object()

#         # check if the player is in a match
#         player_in_match = (
#             Match.objects.filter(teams__teamplayer__player=player)
#             .exclude(status__in=["Result contested", "Finished"])
#             .first()
#         )

#         if player_in_match:
#             raise PlayerInMatch()

#         player.queueing_for = game
#         player.save()

#         # is another player queueing for this game?
#         # if so, start a match with both players
#         # TODO: more complex matchmaking

#         queuing = Player.objects.filter(queueing_for__is_null=False)
#         for teams, game in matchmake(queuing):
#             create_match(teams, game)

#         serializer = MatchSerializer(self.get_queryset(), many=True)

#         return Response(serializer.data, status=status.HTTP_201_CREATED)


class LeaderboardDetail(generics.ListAPIView):
    serializer_class = EloSerializer
    pagination_class = RankingPagination

    def get_object(self):
        game_id = self.kwargs.get("game_id")
        return get_object_or_404(Game, game_id=game_id)

    def get_queryset(self):
        game = self.get_object()

        return (
            Elo.objects.filter(game=game)
            .annotate(rank=Window(expression=Rank(), order_by=F("mu").desc()))
            .order_by("-mu")
        )


class ScoresDetail(generics.ListAPIView):
    serializer_class = ScoreSerializer
    pagination_class = RankingPagination

    def get_object(self):
        game_id = self.kwargs.get("game_id")

        return get_object_or_404(Game, game_id=game_id)

    def get_queryset(self):
        game = self.get_object()

        """
        temporary score ranking code.
        planning on replacing this with custom logic
        
        because i dont want to run the window functions
        every time someone wants a score list, or a single score
        """

        player = self.request.query_params.get("player", None)
        obsolete = self.request.query_params.get("obsolete", None)

        # annotate an overall_rank and player_rank onto all scores
        scores = (
            Score.objects.filter(game=game, match__status="Finished")
            .order_by("score")
            .annotate(
                overall_rank=Window(
                    expression=Rank(),
                    order_by=F("score").asc(),
                ),
                player_rank=Window(
                    expression=Rank(),
                    order_by=F("score").asc(),
                    partition_by=F("player"),
                ),
            )
        )

        # filter by every player's best score
        # (1 per player because of ties)
        best_scores_per_player = scores.order_by("player", "-score").distinct("player")

        # annotate a non_obsolete_rank onto all best scores per player, else null
        scores = scores.annotate(
            non_obsolete_rank=Case(
                When(
                    pk__in=Subquery(best_scores_per_player.values("pk")),
                    then=Window(
                        expression=Rank(),
                        order_by=F("score").asc(),
                    ),
                ),
                default=Value(None),
                output_field=IntegerField(),
            )
        )

        # create a cte so that we don't affect the ranks we just made
        cte = With(scores)
        scores = cte.queryset().with_cte(cte)

        if player is not None:
            scores = scores.filter(player__discord_id=player)

        if (
            obsolete is None and player is None
        ):  # if we don't want to show obsolete scores
            # only show ones that have a non-obsolete rank
            scores = scores.filter(non_obsolete_rank__isnull=False)

        return scores


class GameList(generics.ListAPIView):
    serializer_class = GameSerializer

    def get_queryset(self):
        return Game.objects.all()
