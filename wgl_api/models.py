from django.db import models
from django.core.validators import RegexValidator
from .utils import calculate_elo, calculate_p1_win_prob, ms_to_time
from computedfields.models import ComputedFieldsModel, computed, compute

# Create your models here.

class Player(ComputedFieldsModel):
        
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
    
    def currently_playing_match(self):
        return (
            Match.objects.filter(active=True, p1=self).first() 
            or Match.objects.filter(active=True, p2=self).first()
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
    
class Match(ComputedFieldsModel):
    
    class Meta:
        constraints = [
            # checks that player 1 and 2 are different
            models.CheckConstraint(check=~models.Q(p1=models.F('p2')), name='different_players'),
        ]
    
    match_id = models.AutoField(primary_key=True)
    discord_thread_id = models.BigIntegerField(null=True, blank=True)
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    
    timestamp_started = models.DateTimeField(auto_now_add=True)
    timestamp_finished = models.DateTimeField(null=True, blank=True)
    
    p1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="p1")
    
    @computed(
        models.CharField(max_length=12, null=True),
        depends=[
            ('match_scores', ['player', 'game', 'match'])
        ]
    )
    def p1_score(self):
        score = Score.objects.filter(
            player=self.p1, 
            game=self.game, 
            match__match_id=self.match_id
        ).first()
        return score.score_formatted if score else None
        # return "test"
    p1_video_url = models.URLField(null=True, blank=True)
    
    # we set these values below
    p1_mu_before = models.FloatField(null=False, blank=True)
    p1_sigma_before = models.FloatField(null=False, blank=True)
    
    @computed(
        models.FloatField(null=True, blank=True),
        depends=[
            ('self', ['predictions'])
        ]
    )
    def p1_mu_after(self):
        if self.p1_mu_before is None or self.result is None:
            return None
        
        return self.predictions['elo'][self.result][0][0] # [0][0] = [player 1][mu (as opposed to delta)]
    
    @computed(
        models.FloatField(null=True, blank=True),
        depends=[
            ('self', ['predictions'])
        ]
    )
    def p1_sigma_after(self):
        if self.p2_sigma_before is None or self.result is None:
            return None
        
        return self.predictions['sigma'][0]
    
    
    p2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="p2")

    @computed(
        models.CharField(max_length=12, null=True),
        depends=[
            ('match_scores', ['player', 'game', 'match'])
        ]
    )
    def p2_score(self):
        score = Score.objects.filter(
            player=self.p2, 
            game=self.game, 
            match__match_id=self.match_id
        ).first()
        return score.score_formatted if score else None
        
    p2_video_url = models.URLField(null=True, blank=True)
    
    # we make these null=True but we set them below
    p2_mu_before = models.FloatField(null=False, blank=True)
    p2_sigma_before = models.FloatField(null=False, blank=True)
        
    @computed(
        models.FloatField(null=True, blank=True),
        depends=[
            ('self', ['predictions'])
        ]
    )
    def p2_mu_after(self):
        if self.p2_mu_before is None or self.result is None:
            return None
        
        return self.predictions['elo'][self.result][1][0] # [1][0] = [player 2][mu (as opposed to delta)]
    
    @computed(
        models.FloatField(null=True, blank=True),
        depends=[
            ('self', ['predictions'])
        ]
    )
    def p2_sigma_after(self):
        if self.p2_sigma_before is None or self.result is None:
            return None
        
        return self.predictions['sigma'][1]
    
    @computed(
        models.JSONField(null=True, blank=True),
        depends=[
            ('self', ['p1_mu_before', 'p1_sigma_before', 'p2_mu_before', 'p2_sigma_before'])
        ]
    )
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
        
    @computed(
        models.BooleanField(null=False, blank=True),
        depends=[
            ('self', ['status'])
        ]
    )
    def active(self):
        return self.status not in ["Finished", "Cancelled", "Result contested"]
    
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
            
            self.game.save()
            self.p1.save()
            self.p2.save()
            
            p1_elo = Elo.objects.filter(player=self.p1, game=self.game).first()
            p2_elo = Elo.objects.filter(player=self.p2, game=self.game).first()
            
            if not p1_elo:
                p1_elo = Elo.objects.create(player=self.p1, game=self.game)
            
            if not p2_elo:
                p2_elo = Elo.objects.create(player=self.p2, game=self.game)
              
            self.p1_mu_before, self.p1_sigma_before = p1_elo.mu, p1_elo.sigma
            self.p2_mu_before, self.p2_sigma_before = p2_elo.mu, p2_elo.sigma
            
            self.p1.save()
            self.p2.save()
            
        super().save(*args, **kwargs)
    
class Score(ComputedFieldsModel):   
    
    score_id = models.AutoField(primary_key=True) 
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=False)
    match = models.ForeignKey("Match", related_name="match_scores", on_delete=models.CASCADE, blank=True)
    
    score = models.IntegerField(null=False)
    
    @computed(
        models.CharField(max_length=12, null=False),
        depends=[
            ('self', ['game', 'score'])
        ]
    )
    def score_formatted(self):
        
        if self.game.speedrun:
            return ms_to_time(self.score)
        else:
            score = score - 72
            
            if score > 0:
                return f"+{score}"
            elif score == 0:
                return f"±{score}"
            else:
                return f"{score}"
                
    
    video_url = models.URLField(null=True)
    verified = models.BooleanField(null=False, default=True)
    
    def __str__(self):
        return f"{self.player}:{self.game}:{self.score_formatted}"
    
    
STARTING_ELO = 1500

class Elo(models.Model):
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    
    mu = models.FloatField(null=False, default=STARTING_ELO)
    sigma = models.FloatField(null=False, default=STARTING_ELO/3)
    
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
    
    
    
    
    
    
    
    
    