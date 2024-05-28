from openskill.models import BradleyTerryFull

STARTING_ELO = 1500

MODEL = BradleyTerryFull(
    mu=STARTING_ELO,
    sigma=STARTING_ELO / 3,
    beta=STARTING_ELO / 6,
    tau=STARTING_ELO / 300,
)


def calculate_elo(match):
    teams = [
        [
            MODEL.rating(mu=tp.mu_before, sigma=tp.sigma_before)
            for tp in team.players.all()
        ]
        for team in match.teams.all()
    ]
    ranks = [team.place for team in match.teams.all()]

    teams = MODEL.rate(teams, ranks=ranks)

    for i, team in enumerate(match.teams.all()):
        for j, tp in enumerate(team.players.all()):
            tp.mu_after = round(teams[i][j].mu)
            tp.sigma_after = teams[i][j].sigma
            tp.save()


def assign_elo(match):
    from .models import Elo

    for team in match.teams.all():
        for tp in team.players.all():
            if tp.mu_after:
                elo = Elo.objects.filter(player=tp.player, game=match.game).first()
                elo.mu = tp.mu_after
                elo.sigma = tp.sigma_after
                elo.save()
