# return a queryset with good matches based on who's queuing
from .utils import create_match
from .models import Player, Match, Game


def matchmake():
    # initialize a queryset for matches
    matches = Match.objects.none()

    # create a match and add it to queryset
    match = create_match(
        [
            [Player.objects.get(discord_id=1234)],
            [Player.objects.get(discord_id=313748055650336772)],
        ],
        Game.objects.get(game_id=1),
    )

    matches = matches.union(Match.objects.filter(match_id=match.match_id))

    # return queryset
    return matches
