from django.contrib import admin
from .models import Level, Source, UserProfile
# Register your models here.

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'native_language', 'daily_ai_limit', 'reading_level')
    search_fields = ('user__username', 'native_language')
    list_filter = ('native_language', 'reading_level')
    
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'difficulty_rank')
    search_fields = ('name', 'code')
    list_filter = ('difficulty_rank',)
    
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    
admin.site.register(Level, LevelAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(UserProfile, UserProfileAdmin)