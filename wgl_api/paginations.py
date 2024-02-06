from rest_framework.pagination import PageNumberPagination
from django.db.models import Window, F
from django.db.models.functions import Rank

class RankingPagination(PageNumberPagination):
    page_size = 10
    
    