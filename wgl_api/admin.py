from django.contrib import admin
import wgl_api.models as models

# Register all models in models


class TeamAdmin(admin.ModelAdmin):
    list_display = ("match", "team_num", "score", "score_formatted")


admin.site.register(models.Youtube)
admin.site.register(models.Player)
admin.site.register(models.Match)
admin.site.register(models.Category)
admin.site.register(models.Game)
admin.site.register(models.Score)
admin.site.register(models.Elo)
admin.site.register(models.Challenge)
admin.site.register(models.Team, TeamAdmin)
admin.site.register(models.TeamPlayer)
