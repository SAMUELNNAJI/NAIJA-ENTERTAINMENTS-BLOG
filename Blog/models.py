from django.db import models
from .fields import SummernoteTextField  # your custom one
from django.core.exceptions import ValidationError

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True, null=True)
    
    # Optional: group categories by content type
    CONTENT_TYPE = [
        ('all', 'All'),
        ('music', 'Music'),
        ('video', 'Video'),
        ('news', 'News'),
        ('instrumental', 'Instrumental'),
    ]
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE, default='all')
    
    # Optional: for parent/child categories like "Video > Comedy > Short"
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    # Optional: control order in admin/listings
    order = models.PositiveIntegerField(default=0)
    


    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Categories"
        indexes = [models.Index(fields=['slug'])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.parent.name} > {self.name}" if self.parent else self.name
    
    
# create TAGS here
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    CONTENT_TYPE = [
        ('all', 'All'),
        ('music', 'Music'),
        ('video', 'Video'),
        ('news', 'News'),
        ('instrumental', 'Instrumental'),
    ]
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE, default='all')
    
    def __str__(self):
        return self.name
    
class Music(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    genre = models.CharField(max_length=200)
    # Option 1: Upload file
    audio_file = models.FileField(upload_to='music/', blank=True, null=True)
    
    # Option 2: External URL
    audio_url = models.URLField(max_length=500, blank=True, null=True, help_text="Enter external audio URL (e.g., SoundCloud, YouTube, etc.)")
    cover_image = models.ImageField(upload_to='cover_images/', default='ENTERTAINMENT/media/cover_images/DJ-Tunez-STATE-OF-MIND-Artwork.jpg')
    music_tag = models.ManyToManyField(Tag, related_name= 'music_tags', blank=True)
    description = models.TextField() 
    categories = models.ManyToManyField(Category, related_name='music', blank=True)
    released_date = models.DateField()
    downloads = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def clean(self):
        # Ensure at least one audio source is provided
        if not self.audio_file and not self.audio_url:
            raise ValidationError("Please provide either an audio file or an audio URL.")
        
        # Prevent both being provided (optional - remove if you want to allow both)
        if self.audio_file and self.audio_url:
            raise ValidationError("Please provide only one: either upload a file OR enter a URL, not both.")
        
        return super().clean()

    def get_audio_source(self):
        """Returns the active audio source (file or URL)"""
        if self.audio_file:
            return self.audio_file.url
        return self.audio_url

    def __str__(self):
        return f'{self.title} by {self.artist}'
    
    
class News(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(default="No description")
    news_tags = models.ManyToManyField(Tag, related_name= 'tags', help_text="Enter tags separated by commas", blank=True, null=True)
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    category = models.ManyToManyField(Category, related_name='News', blank=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

        
    def __str__(self):
        return f'{self.title}'
    class Meta:
        verbose_name = 'News'
        verbose_name_plural = 'News'
        
        
class Video (models.Model):
    title = models.CharField( max_length=250)
    description = models.TextField(blank=True, help_text="Brief description of the video.")
    video_file   = models.FileField(upload_to='videos/files/', blank=True, null=True, help_text="Upload a video file directly. Leave blank if using a YouTube URL.")
    video_url = models.URLField(blank=True, null=True, help_text="Enter a Direct Link to the video file.")
    thumbnail = models.ImageField(upload_to='videos/thumbnails/')
    categories = models.ManyToManyField(Category, related_name='videos', blank=True)
    downloads  = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        if not self.video_file and not self.video_url:
            raise ValidationError("Please provide either a video file or a video URL.")
        if self.video_file and self.video_url:
            raise ValidationError("Please provide only one: either upload a file OR enter a URL, not both.")
        return super().clean()
    
    def video_validation(self):
        if self.video_file:
            return self.video_file.url
        return self.video_url
    def __str__(self):
        return (self.title)
    
class Instrumental(models.Model):
    title = models.CharField(max_length=200)
    audio_file = models.FileField(upload_to='instrumental/')
    cover_image = models.ImageField(upload_to='instrumental_images/', blank=True, null=True)
    description = models.TextField(default="No description")
    categories = models.ManyToManyField(Category, related_name='instrumental', blank=True)
    released_date = models.DateField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return title

class Comment(models.Model):
    music = models.ForeignKey(Music, related_name='music_comments', on_delete=models.CASCADE, null=True, blank=True)
    news = models.ForeignKey(News, related_name='news_comments', on_delete=models.CASCADE, null=True, blank=True)
    video = models.ForeignKey(Video, related_name='video_comments', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.music:
            return f'{self.name} commented on {self.music.title}'
        elif self.news:
            return f'{self.name} commented on {self.news.title}'
        elif self.video:
            return f'{self.name} commented on {self.video.title}'
        else:
            return f'{self.name} commented on an unknown item'
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.name} commented on {self.music.title}'
    