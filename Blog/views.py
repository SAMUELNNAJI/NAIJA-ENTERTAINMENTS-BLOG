from django.shortcuts import get_object_or_404, redirect, render
from .models import Music, Video, News, Instrumental, Tag, Comment
from django.http import FileResponse
from urllib.parse import urlparse, parse_qs
from .forms import Comment_Form
from django.core.paginator import Paginator
from django.db.models import F
from django.db.models import Q
from django.views.generic import ListView

# Create your views here.
def home(request):
    trending_music = Music.objects.filter(categories__name='Trending Music').order_by('-created_at')[:6]
    
    home_videos = Video.objects.filter(categories__name='Trending Videos').order_by('-created_at')[:6]
    
    news = News.objects.all().order_by('-created_at')[:6]
    return render(request, 'blog/index.html', {
        'trending_music': trending_music,
        'news': news,
        'home_videos': home_videos,
    })


def music(request):
    all_music = Music.objects.all().order_by('-id')
    song_of_the_week = Music.objects.filter(categories__name='Song Of The Week').order_by('-id').first()
    gospel_music = Music.objects.filter(categories__name='Gospel').order_by('-id')[:10]

    paginator = Paginator(all_music, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/music.html', {
        'all_music': all_music,
        'song_of_the_week': song_of_the_week,
        'gospel_music': gospel_music,
        'page_obj': page_obj,
    })

def movie(request):
    all_videos = Video.objects.all().order_by('-created_at')
    video_of_the_week = Video.objects.filter(categories__name='VIDEO OF THE WEEK').order_by('-created_at').first()
    
    paginator = Paginator(all_videos, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        'all_videos': all_videos,
        'page_obj': page_obj,
        'video_of_the_week': video_of_the_week,
    }
    
    return render(request, 'blog/videos.html', context)

def news_page(request):
    news = News.objects.all().order_by('-created_at')
    article = News.objects.filter(category__name='Trending News').order_by('-created_at').first()
    return render(request, 'blog/news.html', {'news': news, 'article': article})

def instrumentals(request):
    return render(request, 'blog/instrumentals.html')


def post(request, pk):
    music = get_object_or_404(Music, pk=pk)
    Music.objects.filter(pk=pk).update(downloads=F('downloads') + 1)

    comment_paginator = Paginator(music.music_comments.all(), 3)
    comment_page_number = request.GET.get("comment_page")
    comment_page = comment_paginator.get_page(comment_page_number)

    song_of_the_week = Music.objects.filter(categories__name='Song Of The Week').order_by('-id').first()

    trending_now = Music.objects.filter(categories__name='Trending Music').order_by('-id')[:4]

    music_tags = music.music_tag.all()

    comments = music.music_comments.all().order_by('-created_at')
    form = Comment_Form()
    if request.method == 'POST':
        form = Comment_Form(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.music = music
            comment.save()
            return redirect('music_details', pk=music.pk)

    context = {
        'music': music,
        'comments': comments,
        'form': form,
        'music_tags': music_tags,
        'song_of_the_week': song_of_the_week,
        'trending_now': trending_now,
        'comment_page': comment_page,
    }
    return render(request, 'blog/music_post.html', context)


def download_song(request, pk):
    song = get_object_or_404(Music, pk=pk)
    Music.objects.filter(pk=pk).update(downloads=F('downloads') + 1)

    if song.audio_file:
        source = song.audio_file
        filename = f"{song.title}.mp3"
    else:
        source = song.audio_url
        return redirect(source)

    response = FileResponse(source.open(), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def news_Page(request, pk):
    news = get_object_or_404(News, pk=pk)
    article = News.objects.filter(category__name='Trending News').order_by('-created_at').first()
    celebrity_news = News.objects.filter(news_tags__name='Celebrity News').order_by('-created_at')[:4]
    news_paginator = Paginator(news.news_comments.all(), 3)
    comment_page_number = request.GET.get("comment_page", 1)
    comment_page = news_paginator.get_page(comment_page_number)

    form = Comment_Form()
    if request.method == 'POST':
        form = Comment_Form(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.news = news
            comment.save()
            return redirect('news_details', pk=pk)

    context= {
         'news': news,
         'article': article,
         'celebrity_news': celebrity_news,
         'comment_page': comment_page,
         'form': form,
    }
    return render (request, 'blog/news_details.html', context)


def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)
    trending_video = Video.objects.filter(categories__name= 'Trending Videos').order_by('-created_at')[:6]
    video_of_the_week = Video.objects.filter(categories__name='VIDEO OF THE WEEK').order_by('-created_at').first()
    
    video_comments = video.video_comments.all().order_by('-created_at')
    
    comment_paginator = Paginator(video_comments, 3)
    comment_page_number = request.GET.get("comment_page")
    comment_page = comment_paginator.get_page(comment_page_number)
    
    form = Comment_Form()
    if request.method == 'POST':
        form = Comment_Form(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.video = video
            comment.save()
            return redirect('video_detail', pk=pk)
    
    context = {
        'video': video,
        'video_comments': video_comments,
        'form': form,
        'comment_page': comment_page,
        'trending_video': trending_video,
        'video_of_the_week': video_of_the_week,
    }
    return render(request, 'blog/video_detail.html', context)


def download_video(request, pk):
    video = get_object_or_404(Video, pk=pk)
    if not video.video_file:
        return redirect('video_detail', pk=pk)
    
    # Increment downloads counter
    video.downloads += 1
    video.save()
    
    response = FileResponse(video.video_file.open(), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="{video.title}_video"'
    return response


# SEARCH MUSIC
class SearchMusic(ListView):
    model = Music
    template_name = 'blog/music_list.html'
    context_object_name = 'results'
    paginate_by = 10

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        if search:
            return Music.objects.filter(
                Q(title__icontains=search) |
                Q(artist__icontains=search) |
                Q(genre__icontains=search)
            )
        return Music.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('search', '')
        return context

class SearchNews(ListView):
    model = News
    template_name = 'blog/news_list.html'
    context_object_name = 'results'
    paginate_by = 10

    def get_queryset(self):
        search = self.request.GET.get('search_news', '')
        if search:
            return News.objects.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(news_tags__name__icontains=search)
            ).distinct()
        return News.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('search_news', '')
        return context

class SearchVideo(ListView):
    model = Video
    template_name = 'blog/video_list.html'
    context_object_name = 'results'
    paginate_by = 10
    
    def get_queryset(self):
        search = self.request.GET.get('search_video', '')
        if search:
            return Video.objects.filter(
                Q(title__icontains=search)
            ).distinct()
        return Video.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('search_video', '')
        return context