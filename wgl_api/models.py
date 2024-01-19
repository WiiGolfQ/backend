from django.db import models

# Create your models here.

class Player(models.Model):
    
    player_id = models.AutoField(primary_key=True, null=False, editable=False)
    discord_id = models.BigIntegerField(null=False, editable=False)
    
    created_timestamp = models.DateTimeField(auto_now_add=True)
    last_active_timestamp = models.DateTimeField(auto_now_add=True)
    
    stream_platform = models.CharField(max_length=7, null=True, choices=[("twitch", "Twitch"), ("youtube", "YouTube")])
    stream_username = models.CharField(max_length=64, null=True)
    
    elos = models.ManyToManyField("Game", through="Elo")
    
    currently_playing_match = models.ForeignKey("Match", on_delete=models.CASCADE, null=True)
    
    accept_challenges = models.BooleanField(null=False, default=True)
    
    banned = models.BooleanField(null=False, default=False)
    
class Match(models.Model):
    match_id = models.AutoField(primary_key=True, null=False, editable=False)
    
    timestamp_started = models.DateTimeField(auto_now_add=True)
    timestamp_finished = models.DateTimeField(null=True)
    
    player_1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="player_1")
    player_1_score = models.ForeignKey("Score", on_delete=models.CASCADE, related_name="player_1_score")
    player_1_video_url = models.URLField(null=True)
    
    player_2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="player_2")
    player_2_score = models.ForeignKey("Score", on_delete=models.CASCADE, related_name="player_2_score")
    player_2_video_url = models.URLField(null=True)
    
    status = models.CharField(max_length=1, null=False, choices=[
        ("C", "Cancelled"),
        ("D", "Result contested"),
        ("F", "Finished"),
        ("O", "Ongoing"),
    ])
    
    contest_reason = models.CharField(max_length=64, null=True)
    
    result = models.CharField(max_length=1, null=True, choices=[
        ("1", "Player 1"), 
        ("2", "Player 2"), 
        ("D", "Draw"),
    ])
    
class Game(models.Model):
    
    # it might be a good idea to have the discord bot store all games in memory on_ready
    # and have a slash command to update them in case of a change
    
    game_id = models.AutoField(primary_key=True, null=False, editable=False)
    game_name = models.CharField(max_length=64, null=False)
    
    speedrun = models.BooleanField(null=False, default=True)
    require_livestream = models.BooleanField(null=False, default=True)
    best_of = models.SmallIntegerField(null=False, default=1)
    
    # there can be multiple players in queue at a time
    # i will not support matchmaking until later though: for now if 2 people are in queue they get matched up
    players_in_queue = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    
class Score(models.Model):    
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=False)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=False)
    
    score = models.IntegerField(null=False)
    video_url = models.URLField(null=True)
    verified = models.BooleanField(null=False, default=True)
    

class Elo(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    elo = models.DecimalField(max_digits=5, decimal_places=1)
    
    
    
    
    
    
    
    