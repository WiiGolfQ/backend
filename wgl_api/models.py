from django.db import models
from .utils import calculate_elo

# Create your models here.

class Player(models.Model):
        
    discord_id = models.BigIntegerField(primary_key=True, null=False, unique=True)
    
    username = models.CharField(max_length=64, null=False, unique=True)
    
    yt_username = models.CharField(max_length=64, null=False, unique=True)
        
    created_timestamp = models.DateTimeField(auto_now_add=True)
    last_active_timestamp = models.DateTimeField(auto_now_add=True)
        
    elos = models.ManyToManyField("Game", through="Elo")
    
    queueing_for = models.ForeignKey("Game", related_name="players_in_queue", on_delete=models.CASCADE, null=True, blank=True)
    
    @property
    def currently_playing_match(self):
        return (
            Match.objects.filter(status="Ongoing", p1=self).exclude(status__in=["Result contested", "Finished", "Cancelled"]).first() 
            or Match.objects.filter(status="Ongoing", p1=self).exclude(status__in=["Result contested", "Finished", "Cancelled"]).first()
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
    
    p1_mu_before = models.FloatField()
    p1_sigma_before = models.FloatField()
    @property
    def p1_mu_after(self):
        if self.p1_mu_before is None or self.result is None:
            return None
        
        return calculate_elo((self.p1_mu_before, self.p1_sigma_before), (self.p2_mu_before, self.p2_sigma_before), self.result)[0][0]
    
    
    p2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="p2")
    @property
    def p2_score(self):
        score=Score.objects.filter(player=self.p2, game=self.game, match=self).first()
        return score.score if score else None
    p2_video_url = models.URLField(null=True, blank=True)
    
    p2_mu_before = models.FloatField()
    p2_sigma_before = models.FloatField()
    @property
    def p2_mu_after(self):
        if self.p2_mu_before is None or self.result is None:
            return None
        
        return calculate_elo((self.p2_mu_before, self.p2_sigma_before), (self.p1_mu_before, self.p1_sigma_before), self.result)[0][1]
    
    
    status = models.CharField(max_length=16, null=False, default="Ongoing", choices=[
        ("Cancelled", "Cancelled"),
        ("Result contested", "Result contested"),
        ("Finished", "Finished"),
        ("Ongoing", "Ongoing"),
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
    
    mu = models.FloatField(null=False, default=STARTING_ELO)
    sigma = models.FloatField(null=False, default=STARTING_ELO / 3)
    
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
    
    
    
    
    
    
    
    
    