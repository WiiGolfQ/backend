from openskill.models import PlackettLuce

from .models import Player, Elo, Game, Match

"""
teams are a list of list of player objects

example:

teams = [ [player1, player2] , [player3, player4] ]
this match was a 2v2. p1/p2 got 1st, p3/p4 got 2nd

"""

def calculate_elo(match):
    
    print('inside')

    STARTING_ELO = 1500

    model = PlackettLuce(
        mu = STARTING_ELO,
        sigma = STARTING_ELO / 3,
        beta = STARTING_ELO / 6,
        tau = STARTING_ELO / 300,
    )
        
    # can draws affect players' elo? check later
    
    if match.result == "1":
        teams = [ [match.player_1], [match.player_2] ]
    elif match.result == "2":
        teams = [ [match.player_2], [match.player_1] ]
    else: 
        return
        
    elo_teams = [[Elo.objects.get_or_create(player=p, game=match.game)[0] for p in team] for team in teams]

    openskill_teams = [[model.rating(mu=elo.mu, sigma=elo.sigma) for elo in team] for team in elo_teams]
        
    openskill_teams = model.rate(openskill_teams)
        
    for i, team in enumerate(elo_teams):
        for j, elo in enumerate(team):
            elo.mu = openskill_teams[i][j].mu
            elo.sigma = openskill_teams[i][j].sigma
            elo.save()
            
    

                
                            
            
                
    
    
    


