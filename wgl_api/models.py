from django.db import models

# Create your models here.

class Player(models.Model):
        
    discord_id = models.BigIntegerField(primary_key=True, null=False, unique=True)
    
    username = models.CharField(max_length=64, null=False, unique=True)
    
    yt_username = models.CharField(max_length=64, null=False, unique=True)
        
    created_timestamp = models.DateTimeField(auto_now_add=True)
    last_active_timestamp = models.DateTimeField(auto_now_add=True)
        
    elos = models.ManyToManyField("Game", through="Elo")
    
    queueing_for = models.ForeignKey("Game", related_name="players_in_queue", on_delete=models.CASCADE, null=True, blank=True)
    currently_playing_match = models.ForeignKey("Match", on_delete=models.CASCADE, null=True, blank=True)
    
    accept_challenges = models.BooleanField(null=False, default=True)
    
    banned = models.BooleanField(null=False, default=False)
    
    def __str__(self):
        return f"{self.username}"
    
class Match(models.Model):
    
    class Meta:
        constraints = [
            models.CheckConstraint(check=~models.Q(player_1=models.F('player_2')), name='different_players'),
        ]
    
    match_id = models.AutoField(primary_key=True)
    
    game = models.ForeignKey("Game", on_delete=models.CASCADE)
    
    timestamp_started = models.DateTimeField(auto_now_add=True)
    timestamp_finished = models.DateTimeField(null=True, blank=True)
    
    player_1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="player_1")
    @property
    def player_1_score(self):
        score =  Score.objects.filter(player=self.player_1, game=self.game, match=self).first()
        return score.score if score else None
    player_1_video_url = models.URLField(null=True, blank=True)
    
    player_2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="player_2")
    @property
    def player_2_score(self):
        score=Score.objects.filter(player=self.player_2, game=self.game, match=self).first()
        return score.score if score else None
    player_2_video_url = models.URLField(null=True, blank=True)
    
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
        return f"{self.match_id}: {self.player_1} vs {self.player_2} - {self.game.game_name}"


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
    
class Score(models.Model):   
    
    score_id = models.AutoField(primary_key=True) 
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=False)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, blank=True)
    
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
    
    
    
    
    
    
    
    
    