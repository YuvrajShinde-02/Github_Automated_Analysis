from django.urls import path
from analyzer.views import index, analyze_repositories

urlpatterns = [
    path('', index, name='index'),
    path('analyze/', analyze_repositories, name='analyze_repositories'),
]
