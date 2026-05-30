from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import SearchMusic
from .views import SearchNews
from .views import SearchVideo, searchInstrumental




urlpatterns = [
   path('', views.home, name='home_page'),
    path('music/', views.music, name='music_page'),
    path('movies/', views.movie, name='movie_page'),
    path('news/', views.news_page, name='news_page'),
    path('instrumentals/', views.instrumentals, name='instrumentals_page'),
    path('instrumental/<int:pk>/', views.instrumental_post, name='instrumental_details'),
    path('download_instrumental/<int:pk>/', views.download_instrumental, name='download_instrumental'),
    path('post/<int:pk>/', views.post, name='music_details'),
    path('news/<int:pk>/', views.news_Page, name='news_details'),
    path('video/<int:pk>/', views.video_detail, name='video_detail'),
    path('download_video/<int:pk>/', views.download_video, name='download_video'),
    path('download/<int:pk>/', views.download_song, name='download_song'),
    path('search/', SearchMusic.as_view(), name='search_music'),
    path('search_news/', SearchNews.as_view(), name='search_news'),
    path('search_video/', SearchVideo.as_view(), name='search_video'),
    path('instrumental_search/', searchInstrumental.as_view(), name='search_instrumental'),
 
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)