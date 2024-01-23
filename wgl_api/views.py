from django.shortcuts import get_object_or_404
from django.db.models import Q

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import generics
from rest_framework.exceptions import APIException
from rest_framework.pagination import PageNumberPagination

from .utils import calculate_elo, create_match

from .models import (
    Game,
    Match,
    Player,
    Challenge,
    Elo,
    Score,
)

from .serializers import (
    FullGameSerializer,
    MatchSerializer,
    PlayerSerializer,
    FullPlayerSerializer,
    ChallengeSerializer,
    EloSerializer,
    ScoreSerializer,
)

from .paginations import LeaderboardPagination

class ChangedQueueingFor(APIException):
    status_code = 400
    default_detail = 'Please use the /api/queue route instead of editing queueing_for directly'
    default_code = 'bad_request'
    
class PlayerInMatch(APIException):
    status_code = 400
    default_detail = 'Player is already in a match'
    default_code = 'bad_request'
    
class PlayerNotInMatch(APIException):
    status_code = 400
    default_detail = 'Player is not in this match'
    default_code = 'bad_request'




class PlayerList(generics.ListCreateAPIView):
    
    serializer_class = FullPlayerSerializer
    
    def get_queryset(self):
        queryset = Player.objects.all() 
        
        discord_id = self.request.query_params.get("discord_id", None)
        if discord_id is not None:
            queryset = queryset.filter(discord_id=discord_id)
            
        return queryset

class PlayerDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FullPlayerSerializer

    def get_object(self):
        discord_id = self.kwargs.get('discord_id')
        return get_object_or_404(Player, discord_id=discord_id)
    
    def update(self, request, *args, **kwargs):
        
        player = self.get_object()
        
        queueing_for = request.data.get("queueing_for")
        
        if queueing_for != None and queueing_for != "":
            queueing_for_id = int(queueing_for)
        else:
            queueing_for_id = None
                        
        if queueing_for_id != player.queueing_for.game_id:
            
            raise ChangedQueueingFor()
            
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
            
        return queryset

class MatchDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MatchSerializer

    def get_object(self):
        match_id = self.kwargs.get('match_id')
        return get_object_or_404(Match, match_id=match_id)
    
    # we need to override the update method to check for a change in result
    def update(self, request, *args, **kwargs):
        
        match = self.get_object()

        # check if result was updated by the request
        result = request.data.get("result")

        
        if result is not None:
                                    
            # if we are entering a result for this match for the first time
            if match.result == "" or match.result is None:
                                
                # update the result then calculate elo
                match.result = result
                match.save()
                calculate_elo(match)
                
            else:
                
                # retroactive result change procedure, just pass for now
                pass
            
        return super(MatchDetail, self).update(request, *args, **kwargs)
    
class ReportScore(generics.ListAPIView):
    
    serializer_class = MatchSerializer
    
    # either create a new score or update an existing one
    
    def get_object(self):
        match_id = self.kwargs.get('match_id')
        return get_object_or_404(Match, match_id=match_id)
    
    def get_queryset(self):
        
        match = self.get_object()
        
        discord_id = self.request.query_params.get("player", None)
        score = self.request.query_params.get("score", None)
        
        player = get_object_or_404(Player, discord_id=discord_id)

        if score is not None:
            
            score = int(score)
            
            if player != match.player_1 and player != match.player_2:
                raise PlayerNotInMatch()
            
            player_score = Score.objects.filter(player=player, game=match.game, match=match).first()
            
            if player_score:
                player_score.score = score
                player_score.save()
            else:
                Score.objects.create(
                    player=player,
                    game=match.game,
                    match=match,
                    score=score,
                )   
                
        return Match.objects.filter(match_id=match.match_id) 
            
            
            
        

        
    
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
        challenge_id = self.kwargs.get('challenge_id')
        return get_object_or_404(Challenge, challenge_id=challenge_id)
    
class QueueList(generics.ListAPIView):
    serializer_class = FullPlayerSerializer
    
    def get_object(self):
        game_id = self.kwargs.get('game_id')
        return get_object_or_404(Game, game_id=game_id)
    
    def get_queryset(self):
        game = self.get_object()
        return Player.objects.filter(queueing_for=game)
    
class QueueAdd(generics.ListAPIView):
    
    serializer_class = MatchSerializer
    
    queryset = Match.objects.none()
    
    def get_object(self):
        game_id = self.kwargs.get('game_id')
        discord_id = self.kwargs.get('discord_id')
        
        if game_id == 0:
            return ( None, get_object_or_404(Player, discord_id=discord_id) )
        
        return ( get_object_or_404(Game, game_id=game_id), get_object_or_404(Player, discord_id=discord_id) )
    
    def get(self, request, *args, **kwargs):
                
        game, player = self.get_object()
        
        if game is None:
            player.queueing_for = None
            player.save()
            return Response(status=status.HTTP_201_CREATED)
        
        # check if the player is in a match
        player_in_match = Match.objects.filter(
            (Q(player_1=player) | Q(player_2=player)) & 
            ~Q(status__in=["Result contested", "Finished"])
        ).first()    
            
        if player_in_match:
            raise PlayerInMatch()
              
        player.queueing_for = game
        player.save()
                
        # TODO: better matchmaking
        
        # is another player queueing for this game?
        # if so, start a match with both players
        
        other_player = Player.objects.filter(queueing_for=game).exclude(discord_id=player.discord_id).first()
                
        if other_player is not None:
            
            # start a match with both players
            match = create_match(player, other_player, game)
            self.queryset = Match.objects.filter(match_id=match.match_id)
            
        serializer = MatchSerializer(self.get_queryset(), many=True)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
class LeaderboardList(generics.ListAPIView):
    
    serializer_class = EloSerializer
    pagination_class = LeaderboardPagination
    
    def get_object(self):
        game_id = self.kwargs.get('game_id')
        return get_object_or_404(Game, game_id=game_id)
    
    def get_queryset(self):
        
        game = self.get_object()
        
        return Elo.objects.filter(game=game).order_by('-mu')
    
class ScoresList(generics.ListAPIView):
    
    serializer_class = ScoreSerializer
    
    def get_object(self):
        
        game_id = self.kwargs.get('game_id')
        
        return get_object_or_404(Game, game_id=game_id)
    
    def get_queryset(self):
        
        game = self.get_object()
        
        return Score.objects.filter(game=game, match__status="Finished").order_by('score')
    
        