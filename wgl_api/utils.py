from openskill.models import BradleyTerryFull

def create_match(teams, game):
    
    from .models import Match, Team, TeamPlayer
    
    # this is probably not necessary because you can't queue for a match if you're already playing one
    
    # if p1.currently_playing_match:
    #     raise Exception(f"{p1} is already playing a match")
    # if p2.currently_playing_match:
    #     raise Exception(f"{p2} is already playing a match")
    
    
    # start a match
    match = Match.objects.create(
        game=game,
    )
    
    # add teams to match
    for team in teams:
        t = Team.objects.create()
        for player in team:
            # add players to teams
            team_player = TeamPlayer.objects.create(team=t, player=player)
            t.players.add(team_player)
        match.teams.add(t)
        
    return match
    



STARTING_ELO = 1500

MODEL = BradleyTerryFull(
    mu = STARTING_ELO,
    sigma = STARTING_ELO / 3,
    beta = STARTING_ELO / 6,
    tau = STARTING_ELO / 300,
)

def assign_elo(match):
    
    from .models import Elo
    
    p1 = match.p1
    p2 = match.p2
    
    p1_elo = Elo.objects.filter(player=p1, game=match.game).first()
    p2_elo = Elo.objects.filter(player=p2, game=match.game).first()
    
    if not p1_elo:
        p1_elo = Elo.objects.create(player=p1, game=match.game)
    if not p2_elo:
        p2_elo = Elo.objects.create(player=p2, game=match.game)
        
    p1_elo.mu = match.p1_mu_after
    p1_elo.sigma = match.predictions.get('sigma')[0]
    p1_elo.save()
    
    p2_elo.mu = match.p2_mu_after
    p2_elo.sigma = match.predictions.get('sigma')[1]
    p2_elo.save()
    
# pass in a tuple (mu, sigma) for players
def calculate_elo(p1_elo: tuple, p2_elo: tuple, result):
            
    match result:
        case "1":
            ranks = [ 1,2 ]
        case "2":
            ranks = [ 2,1 ]
        case "D":
            ranks = [ 1,1 ]
            
    model = MODEL
            
    p1 = model.rating(
        mu=p1_elo[0], 
        sigma=p1_elo[1]
    )
    p2 = model.rating(
        mu=p2_elo[0], 
        sigma=p2_elo[1]
    )
    
    teams = [ [p1], [p2] ]
    
    teams = model.rate(teams, ranks=ranks)
    
    # format mu to 3 decimal place, sigma to 3 decimal places
    teams[0][0].mu = round(teams[0][0].mu, 1)
    teams[0][0].sigma = round(teams[0][0].sigma, 3)
    teams[1][0].mu = round(teams[1][0].mu, 1)
    teams[1][0].sigma = round(teams[1][0].sigma, 3)
        
    return (teams[0][0].mu, teams[0][0].sigma), (teams[1][0].mu, teams[1][0].sigma)

def calculate_p1_win_prob(p1_elo, p2_elo):
    
    model = MODEL
    
    p1 = model.rating(mu=p1_elo[0], sigma=p1_elo[1])
    p2 = model.rating(mu=p2_elo[0], sigma=p2_elo[1])
    
    prob = model.predict_win([[p1], [p2]])[0]
    
    return round(prob, 3)

def ms_to_time(ms):
    
    seconds = ms / 1000
    minutes = seconds // 60
    hours = minutes // 60

    seconds = seconds % 60
    minutes = int(minutes % 60)
    hours = int(hours)
    
    if hours != 0:
        return f"{hours}:{minutes:02}:{seconds:06.3f}"
    elif minutes != 0:
        return f"{minutes}:{seconds:06.3f}"
    else:
        return f"{seconds:.3f}"




    
    
            
    

                
                            
            
                
    
    
    


