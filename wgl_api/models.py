from django.db import models

# Create your models here.

class Player(models.Model):
    
    player_id = models.AutoField(primary_key=True)
    
    username = models.CharField(max_length=64, null=False, blank=True, unique=True)
    discord_id = models.BigIntegerField(null=False, unique=True)
    
    created_timestamp = models.DateTimeField(auto_now_add=True)
    last_active_timestamp = models.DateTimeField(auto_now_add=True)
    
    stream_platform = models.CharField(max_length=7, null=True, choices=[("twitch", "Twitch"), ("youtube", "YouTube")])
    stream_username = models.CharField(max_length=64, null=True)
    
    elos = models.ManyToManyField("Game", through="Elo")
    
    currently_playing_match = models.ForeignKey("Match", on_delete=models.CASCADE, null=True, blank=True)
    
    accept_challenges = models.BooleanField(null=False, default=True)
    
    banned = models.BooleanField(null=False, default=False)
    
    def __str__(self):
        return f"{self.username}"
    
class Match(models.Model):
    
    class Meta:
        constraints = [
            models.CheckConstraint(check=~models.Q(player_1=models.F('player_2')), name='different_players'),
            models.CheckConstraint(check=~models.Q(player_1_score=models.F('player_2_score')), name='different_scores'),
            models.CheckConstraint(check=~models.Q(player_1_video_url=models.F('player_2_video_url')), name='different_video_urls'),
        ]
    
    match_id = models.AutoField(primary_key=True)
    
    game = models.ForeignKey("Game", on_delete=models.CASCADE)
    
    timestamp_started = models.DateTimeField(auto_now_add=True)
    timestamp_finished = models.DateTimeField(null=True)
    
    player_1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="player_1")
    player_1_score = models.ForeignKey("Score", on_delete=models.CASCADE, related_name="player_1_score", null=True, blank=True)
    player_1_video_url = models.URLField(null=True, blank=True)
    
    player_2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="player_2")
    player_2_score = models.ForeignKey("Score", on_delete=models.CASCADE, related_name="player_2_score", null=True, blank=True)
    player_2_video_url = models.URLField(null=True, blank=True)
    
    status = models.CharField(max_length=1, null=False, choices=[
        ("C", "Cancelled"),
        ("D", "Result contested"),
        ("F", "Finished"),
        ("O", "Ongoing"),
    ])
    
    contest_reason = models.CharField(max_length=64, null=True, blank=True)
    
    result = models.CharField(max_length=1, null=True, blank=True, choices=[
        ("1", "Player 1"), 
        ("2", "Player 2"), 
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
    
    # there can be multiple players in queue at a time
    # i will not support matchmaking until later though: for now if 2 people are in queue they get matched up
    players_in_queue = models.ForeignKey(Player, on_delete=models.CASCADE, blank=True, null=True)
    
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
    

class Elo(models.Model):
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    elo = models.DecimalField(max_digits=5, decimal_places=1)
    
    def __str__(self):
        return f"{self.player}:{self.game}:{self.elo} elo"
    
class Challenge(models.Model):
    
    challenge_id = models.AutoField(primary_key=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    challenger = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="challenger")
    challenged = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="challenged")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=False)
        
    accepted = models.BooleanField(null=True)
    
    def __str__(self):
        return f"{self.challenge_id}: {self.challenger} challenged {self.challenged} to {self.game}"
    
    
    
    
    
    
    
    