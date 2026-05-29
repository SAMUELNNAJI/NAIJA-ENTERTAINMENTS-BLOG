from django.shortcuts import get_object_or_404, redirect, render
from .models import Music, Video, News, Instrumental, Tag, Comment
from django.http import FileResponse, StreamingHttpResponse, HttpResponseBadRequest, HttpResponseServerError
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, parse_qs, unquote, urlsplit, quote as urlquote
import os
from django.utils.text import slugify
from urllib.request import Request, urlopen
from .forms import Comment_Form
from django.core.paginator import Paginator
from django.db.models import F
from django.db.models import Q
from django.views.generic import ListView
from django.template.context_processors import request

from Blog.models import Instrumental
# Create your views here.
def home(request):
    trending_music = Music.objects.filter(categories__name='Trending Music').order_by('-created_at')[:6]
    
    home_videos = Video.objects.filter(categories__name='Trending Videos').order_by('-created_at')[:6]
    
    instrumentals = Instrumental.objects.filter(categories__name = 'Hot Instrumentals').order_by('-created_at')[:6]
    
    news = News.objects.all().order_by('-created_at')[:6]
    return render(request, 'blog/index.html', {
        'trending_music': trending_music,
        'news': news,
        'home_videos': home_videos,
        'instrumentals': instrumentals,
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
    All_Instrumentals = Instrumental.objects.all()
    
    pagination = Paginator(All_Instrumentals, 6)
    page_number = request.GET.get('page')
    page_obj = pagination.get_page(page_number)
    
    context = {
        'All_Instrumentals': All_Instrumentals,
        'page_obj': page_obj,
    }
    return render(request, 'blog/instrumentals.html', context)


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

    # If file is stored via Django storage (may be Cloudinary), try to open via storage
    if song.audio_file:
        filename = f"{song.title}.mp3"
        try:
            fileobj = song.audio_file.storage.open(song.audio_file.name)
        except Exception:
            # Fallback: stream from the public URL
            remote_url = song.audio_file.url
            try:
                req = Request(remote_url, headers={'User-Agent': 'Mozilla/5.0'})
                remote_resp = urlopen(req, timeout=30)
            except (HTTPError, URLError):
                return HttpResponseServerError('Unable to access the audio file.')

            def stream_remote():
                while True:
                    chunk = remote_resp.read(8192)
                    if not chunk:
                        break
                    yield chunk

            response = StreamingHttpResponse(stream_remote(), content_type=remote_resp.headers.get_content_type() or 'audio/mpeg')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            content_length = remote_resp.headers.get('Content-Length')
            if content_length:
                response['Content-Length'] = content_length
            return response

        response = FileResponse(fileobj, as_attachment=True, filename=filename)
        response['Content-Type'] = 'audio/mpeg'
        return response

    # No local file — proxy external URL as attachment
    remote_url = song.audio_url
    if not remote_url:
        return HttpResponseBadRequest('No audio source available.')

    # derive filename from URL
    path = urlsplit(remote_url).path
    name = unquote(path.split('/')[-1]) or f"{song.title}.mp3"

    try:
        req = Request(remote_url, headers={'User-Agent': 'Mozilla/5.0'})
        remote_resp = urlopen(req, timeout=30)
    except (HTTPError, URLError):
        return HttpResponseServerError('Unable to download the audio file.')

    def stream():
        while True:
            chunk = remote_resp.read(8192)
            if not chunk:
                break
            yield chunk

    response = StreamingHttpResponse(stream(), content_type=remote_resp.headers.get_content_type() or 'application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{name}"'
    content_length = remote_resp.headers.get('Content-Length')
    if content_length:
        response['Content-Length'] = content_length
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


def download_instrumental(request, pk):
    """Stream the instrumental audio as an attachment so the browser downloads it."""
    instrumental = get_object_or_404(Instrumental, pk=pk)

    # Prefer uploaded file URL
    remote_url = None
    if instrumental.audio_file:
        try:
            remote_url = instrumental.audio_file.url
        except Exception:
            remote_url = None

    # Fallback to external URL field if present
    if not remote_url:
        # Instrumental model currently doesn't have a separate audio_url field,
        # but leave support here in case of future changes.
        remote_url = getattr(instrumental, 'audio_url', None)

    if not remote_url:
        return HttpResponseBadRequest('No audio source available.')

    try:
        req = Request(remote_url, headers={'User-Agent': 'Mozilla/5.0'})
        remote_resp = urlopen(req, timeout=30)
    except (HTTPError, URLError):
        return HttpResponseServerError('Unable to access the audio file.')

    # Derive filename: use title and producer_name
    parsed = urlparse(remote_url)
    ext = os.path.splitext(parsed.path)[1] or '.mp3'
    safe_title = slugify(instrumental.title) or 'instrumental'
    safe_producer = slugify(instrumental.producer_name) or 'producer'
    name = f"{safe_title}-{safe_producer}{ext}"
    # Use RFC5987 encoded filename* for UTF-8 clients with the readable original
    readable = f"{instrumental.title} - {instrumental.producer_name}{ext}"
    encoded_readable = urlquote(readable)

    def stream():
        while True:
            chunk = remote_resp.read(8192)
            if not chunk:
                break
            yield chunk

    response = StreamingHttpResponse(stream(), content_type=remote_resp.headers.get_content_type() or 'audio/mpeg')
    response['Content-Disposition'] = f"attachment; filename=\"{name}\"; filename*=UTF-8''{encoded_readable}"
    content_length = remote_resp.headers.get('Content-Length')
    if content_length:
        response['Content-Length'] = content_length
    return response



def instrumental_post(request, pk):
    instrumental = get_object_or_404(Instrumental, pk=pk)
    all_instrmentals = Instrumental.objects.all()

    context = {
        'instrumental': instrumental,
        'all_instrmentals': all_instrmentals,
    }

    return render(request, 'blog/instrumental_detail.html', context)


   

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