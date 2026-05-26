from django.contrib import admin
from .models import Category, Music, News, Video, Instrumental, Comment, Tag
from django_summernote.admin import SummernoteModelAdmin
from Blog.models import Category

# Register your models here.


admin.site.register(Comment),
admin.site.register(Tag),
admin.site.register(Music, SummernoteModelAdmin),
admin.site.register(News, SummernoteModelAdmin),
admin.site.register(Video, SummernoteModelAdmin),
admin.site.register(Instrumental, SummernoteModelAdmin),

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        "slug": ("name",)
    }

class SummernoteModelAdmin(SummernoteModelAdmin):
    summernote_fields = ('description',)
