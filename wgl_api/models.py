from django.db import models
from django.core.validators import RegexValidator
from .utils import calculate_elo, calculate_p1_win_prob

# Create your models here.

class Player(models.Model):
        
    discord_id = models.BigIntegerField(primary_key=True, null=False, unique=True)
    
    username = models.CharField(max_length=64, null=False, unique=True)
    
    yt_username = models.CharField(max_length=30, null=False, unique=True, validators=[
        RegexValidator(
            regex=r'^[\w.-]+$',
            message='Username can only contain alphanumeric characters, underscores, hyphens, and periods.',
            code='invalid_username'
        ),
    ])
        
    created_timestamp = models.DateTimeField(auto_now_add=True)
    last_active_timestamp = models.DateTimeField(auto_now_add=True)
        
    elos = models.ManyToManyField("Game", through="Elo")
    
    queueing_for = models.ForeignKey("Game", related_name="players_in_queue", on_delete=models.CASCADE, null=True, blank=True)
    
    @property
    def currently_playing_match(self):
        return (
            Match.objects.filter(status="Ongoing", p1=self).exclude(status__in=["Result contested", "Finished", "Cancelled"]).first() 
            or Match.objects.filter(status="Ongoing", p2=self).exclude(status__in=["Result contested", "Finished", "Cancelled"]).first()
        )
    
    accept_challenges = models.BooleanField(null=False, default=True)
    
    banned = models.BooleanField(null=False, default=False)
    
    def __str__(self):
        return f"{self.username}"
    
class Game(models.Model):
    
    # it might be a good idea to have the discord bot store all games in memory on_ready
    # and have a slash command to update them in case of a change
    
    game_id = models.AutoField(primary_key=True) 
    game_name = models.CharField(max_length=64, null=False)
    
    speedrun = models.BooleanField(null=False, default=True)
    require_livestream = models.BooleanField(null=False, default=True)
    best_of = models.SmallIntegerField(null=False, default=1)
    
    def __str__(self):
        return f"{self.game_name}" 
    
class Match(models.Model):
    
    class Meta:
        constraints = [
            # checks that player 1 and 2 are different
            models.CheckConstraint(check=~models.Q(p1=models.F('p2')), name='different_players'),
        ]
    
    match_id = models.AutoField(primary_key=True)
    
    
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    
    timestamp_started = models.DateTimeField(auto_now_add=True)
    timestamp_finished = models.DateTimeField(null=True, blank=True)
    
    p1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="p1")
    
    @property
    def p1_score(self):
        score =  Score.objects.filter(player=self.p1, game=self.game, match=self).first()
        return score.score if score else None
    p1_video_url = models.URLField(null=True, blank=True)
    
    # we set these values below
    p1_mu_before = models.FloatField(null=False, blank=True)
    p1_sigma_before = models.FloatField(null=False, blank=True)
    
    @property
    def p1_mu_after(self):
        if self.p1_mu_before is None or self.result is None:
            return None
        
        return self.predictions['elo'][self.result][0][0] # [0][0] = [player 1][mu (as opposed to delta)]
    
    @property
    def p1_sigma_after(self):
        if self.p2_sigma_before is None or self.result is None:
            return None
        
        return self.predictions['sigma'][0]
    
    
    p2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="p2")
    @property
    def p2_score(self):
        score=Score.objects.filter(player=self.p2, game=self.game, match=self).first()
        return score.score if score else None
    p2_video_url = models.URLField(null=True, blank=True)
    
    # we make these null=True but we set them below
    p2_mu_before = models.FloatField(null=False, blank=True)
    p2_sigma_before = models.FloatField(null=False, blank=True)
        
    @property
    def p2_mu_after(self):
        if self.p2_mu_before is None or self.result is None:
            return None
        
        return self.predictions['elo'][self.result][1][0] # [1][0] = [player 2][mu (as opposed to delta)]
    
    @property
    def p2_sigma_after(self):
        if self.p2_sigma_before is None or self.result is None:
            return None
        
        return self.predictions['sigma'][1]
    
    @property
    def predictions(self):
        
        def format_delta(x):
            
            x = round(x, 1)
            
            if x > 0:
                return f"+{x}"
            elif x == 0:
                return f"±{x}"
            else:
                return f"{x}"
        
        if self.p1_mu_before is None or self.p2_mu_before is None:
            return None
        
        result_choices = [choice[0] for choice in self._meta.get_field('result').choices]
        
        elo_predictions = {}
        
        for choice in result_choices:
            (p1_mu, p1_sigma), (p2_mu, p2_sigma) = calculate_elo((self.p1_mu_before, self.p1_sigma_before), (self.p2_mu_before, self.p2_sigma_before), choice)
            
            p1_delta = format_delta(p1_mu - self.p1_mu_before)
            p2_delta = format_delta(p2_mu - self.p2_mu_before)
            
            elo_predictions[choice] = ( (p1_mu, p1_delta) , (p2_mu, p2_delta) )
            
        return {
            "p1_win_prob": calculate_p1_win_prob((self.p1_mu_before, self.p1_sigma_before), (self.p2_mu_before, self.p2_sigma_before)),
            "sigma": [p1_sigma, p2_sigma],
            "elo": elo_predictions,
        }
    
    status = models.CharField(max_length=23, null=False, default="Waiting for livestreams", choices=[
        ("Cancelled", "Cancelled"),
        ("Result contested", "Result contested"),
        ("Finished", "Finished"),
        ("Ongoing", "Ongoing"),
        ("Waiting for livestreams", "Waiting for livestreams"),
        ("Waiting for agrees", "Waiting for agrees")
    ])
    
    contest_reason = models.CharField(max_length=64, null=True, blank=True)
    
    result = models.CharField(max_length=1, null=True, blank=True, choices=[
        ("1", "Player 1 wins"), 
        ("2", "Player 2 wins"), 
        ("D", "Draw"),
    ])
    
    def __str__(self):
        return f"{self.match_id}: {self.p1} vs {self.p2} - {self.game.game_name}"


    def save(self, *args, **kwargs): # we need this part to set default values for starting elos

        if not self.pk: # if this is a newly created match
            
            p1_elo = Elo.objects.filter(player=self.p1, game=self.game).first()
            p2_elo = Elo.objects.filter(player=self.p2, game=self.game).first()
              
            self.p1_mu_before, self.p1_sigma_before = p1_elo.mu, p1_elo.sigma
            self.p2_mu_before, self.p2_sigma_before = p2_elo.mu, p2_elo.sigma
            
        super().save(*args, **kwargs)
    
class Score(models.Model):   
    
    score_id = models.AutoField(primary_key=True) 
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=False)
    match = models.ForeignKey("Match", on_delete=models.CASCADE, blank=True)
    
    score = models.IntegerField(null=False)
    video_url = models.URLField(null=True)
    verified = models.BooleanField(null=False, default=True)
    
    def __str__(self):
        return f"{self.player}:{self.game}:{self.score}"
    
    
STARTING_ELO = 1500

class Elo(models.Model):
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    
    mu = models.DecimalField(null=False, default=STARTING_ELO, max_digits=5, decimal_places=1)
    sigma = models.DecimalField(null=False, default=STARTING_ELO/3, max_digits=5, decimal_places=2)
    
    def __str__(self):
        return f"{self.player}:{self.game}:{'{:.1f}'.format(self.mu)} elo"
    

    
class Challenge(models.Model):
    
    challenge_id = models.AutoField(primary_key=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    challenger = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="challenger")
    challenged = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="challenged")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=False)
        
    accepted = models.BooleanField(null=True)
    
    def __str__(self):
        return f"{self.challenge_id}: {self.challenger} challenged {self.challenged} to {self.game}"
    
    
    
    
    
    
    
    
    