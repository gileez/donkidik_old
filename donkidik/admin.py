from django.contrib import admin
from donkidik.models import *


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass

@admin.register(PostType)
class PostTypeAdmin(admin.ModelAdmin):
    pass