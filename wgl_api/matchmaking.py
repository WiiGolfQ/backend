# return a queryset with good matches based on who's queuing
from .utils import create_match
from .models import Elo, Player, Match, Game

from itertools import combinations
from .elo import MODEL


def stdev(values):
    mean = sum(values) / len(values)
    return (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5


def score(players, elos, game):
    """
    also for now let's make it simple and do a formula that only takes into account

    - number of players (more = good)
    - stdev of elo (less = good)
    - stdev of sigma values (less = good)
    """

    n = len(players)
    try:
        mu_stdev = stdev([elo.mu for elo in elos if elo.player in players])
    except ZeroDivisionError:
        mu_stdev = 0

    try:
        sigma_stdev = stdev([elo.sigma for elo in elos if elo.player in players])
    except ZeroDivisionError:
        sigma_stdev = 0

    # normalize stdevs with starting values
    mu_stdev = mu_stdev / MODEL.mu
    sigma_stdev = sigma_stdev / MODEL.sigma

    # i have no idea if this is gonna work well so we'll see
    score = n**2 / (mu_stdev + (sigma_stdev / 5) + 1)

    return score


def matchmake():
    # initialize a queryset for matches
    matches = Match.objects.none()

    # for now we are going to assume that all matches are 1v1

    # randomize the order of all games and then check them all
    games = Game.objects.all().order_by("?")
    for game in games:
        players = set(Player.objects.filter(in_queue=True, queues_for=game))

        if len(players) < 2:
            continue

        elos = set()
        for player in players:
            elo = Elo.objects.filter(player=player, game=game).first()
            if elo:
                elos.add(elo)

        possible_matches = set()
        for r in range(2, min(len(players), 8) + 1):  # min 2, max 8
            possible_matches.update(comb for comb in combinations(players, r))

        match_to_score = {
            players: score(players, elos, game) for players in possible_matches
        }

        del possible_matches  # save memory

        while len(players) > 1 and match_to_score:
            # get the match with the highest score
            best_match = max(match_to_score, key=match_to_score.get)

            print("best match players: ", best_match)
            print("best match score: ", match_to_score[best_match])

            match_to_score.pop(best_match)

            # create the match
            teams = [[player] for player in best_match]
            match = create_match(teams, game)
            matches |= Match.objects.filter(match_id=match.match_id)

            # remove players from the pool
            for player in best_match:
                players.remove(player)

            # remove matches that contain the players in the match
            for match in set(match_to_score.keys()):
                if any(player in match for player in best_match):
                    match_to_score.pop(match)

    # return queryset
    return matches
