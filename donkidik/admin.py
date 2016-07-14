from django.contrib import admin
from donkidik.models import *


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass

@admin.register(PostType)
class PostTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(PostMeta)
class PostMetaAdmin(admin.ModelAdmin):
    pass

@admin.register(Spot)
class SpotAdmin(admin.ModelAdmin):
    pass

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    pass