from django.contrib import admin
from .models import Category, Music, News, Video, Instrumental, Comment, Tag
from django_summernote.admin import SummernoteModelAdmin

# Register your models here.

admin.site.register(Category),
admin.site.register(Comment),
admin.site.register(Tag),

@admin.register(Video)
class VideoAdmin(SummernoteModelAdmin):
    summernote_fields = ('description',)

@admin.register(Music)
class MusicAdmin(SummernoteModelAdmin):
    summernote_fields = ('description',)

@admin.register(News)
class NewsAdmin(SummernoteModelAdmin):
    summernote_fields = ('description',)
@admin.register(Instrumental)
class InstrumentalAdmin(SummernoteModelAdmin):
    summernote_fields = ('description',)