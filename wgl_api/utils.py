from openskill.models import PlackettLuce

def create_match(p1, p2, game):
    
    from .models import Match
    
    if p1.currently_playing_match:
        raise Exception(f"{p1} is already playing a match")
    if p2.currently_playing_match:
        raise Exception(f"{p2} is already playing a match")
    
    p1.queueing_for = None
    p1.save()
    
    p2.queueing_for = None
    p2.save()
    
    # start a match with both players
    return Match.objects.create(
        game=game,
        p1=p1,
        p2=p2,
        status="Ongoing",
    )
    


"""
TODO: support multiplayer

example:

teams = [ [player1, player2] , [player3, player4] ]
this match was a 2v2. p1/p2 got 1st, p3/p4 got 2nd

"""

STARTING_ELO = 1500

MODEL = PlackettLuce(
    mu = STARTING_ELO,
    sigma = STARTING_ELO / 3,
    beta = STARTING_ELO / 6,
    tau = STARTING_ELO / 300,
)

# pass in a tuple (mu, sigma)
def calculate_elo(p1_elo: tuple, p2_elo: tuple, result):
    
    match result:
        case "1":
            ranks = [ 1,2 ]
        case "2":
            ranks = [ 2,1 ]
        case "draw":
            ranks = [ 1,1 ]
            
    model = MODEL
            
    p1 = model.rating(mu=p1_elo[0], sigma=p1_elo[1])
    p2 = model.rating(mu=p2_elo[0], sigma=p2_elo[1])
    
    teams = [ [p1], [p2] ]
    
    teams = model.rate(teams, ranks=ranks)
    
    return (teams[0][0].mu, teams[0][0].sigma), (teams[1][0].mu, teams[1][0].sigma)

def assign_elo(match):
    
    pass
    
    
            
    

                
                            
            
                
    
    
    


