# return a queryset with good matches based on who's queuing
from .utils import create_match
from .models import Elo, Player, Match, Game

from itertools import combinations
from .elo import MODEL


def stdev(values):
    mean = sum(values) / len(values)
    return (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5


class Matchmaker:
    def __init__(self):
        self.counter = 0

    def score(self, players, elos, game):
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

    def add_player(self, player):
        players = Player.objects.filter(in_queue=True)
        if (
            not players.filter(discord_id=player.discord_id).exists()
            and players.count() >= 2
        ):
            # self.counter += int(25 * (0.75 ** (len(players) - 2)))
            self.counter += 1

    def matchmake(self):
        # initialize a queryset for matches
        matches = Match.objects.none()

        players = Player.objects.filter(in_queue=True)

        # if not ready to matchmake yet
        if players.count() < 2:
            return matches

        if self.counter > 0:
            self.counter -= 1
            print("counter: ", self.counter)
            return matches

        # for now we are going to assume that all matches are 1v1

        # randomize the order of all games and then check them all
        games = Game.objects.all().order_by("?")
        for game in games:
            game_players = list(players.filter(queues_for=game).order_by("?"))

            if len(game_players) < 2:
                continue

            elos = set()
            for player in game_players:
                elo = Elo.objects.filter(player=player, game=game).first()
                if elo:
                    elos.add(elo)

            possible_matches = set()
            for r in range(2, min(len(game_players), 8) + 1):  # min 2, max 8
                possible_matches.update(comb for comb in combinations(game_players, r))

            match_to_score = {
                matchup: self.score(matchup, elos, game) for matchup in possible_matches
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
                    game_players.remove(player)

                # remove matches that contain the players in the match
                for match in set(match_to_score.keys()):
                    if any(player in match for player in best_match):
                        match_to_score.pop(match)

        # return queryset
        return matches
