from rest_framework import pagination

class LeaderboardPagination(pagination.PageNumberPagination):
    page_size = 25