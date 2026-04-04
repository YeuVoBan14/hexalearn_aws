from django.contrib import admin
from django.utils.html import format_html
from .models import Passage, Paragraph, ParagraphTranslation, ReadingNote, Topic, UserReadingProgress


class TopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')
    search_fields = ('name', 'code')
    list_per_page = 50


class ParagraphTranslationInline(admin.TabularInline):
    model = ParagraphTranslation
    extra = 0
    fields = ('language', 'translation')
    verbose_name = 'Translation'
    verbose_name_plural = 'Translations'


class ParagraphInline(admin.StackedInline):
    model = Paragraph
    extra = 0
    fields = ('id', 'index', 'content', 'note', 'image', 'paragraph_image_preview', 'translation_languages')
    readonly_fields = ('id', 'translation_languages', 'paragraph_image_preview')
    show_change_link = True

    def translation_languages(self, obj):
        if not obj or not obj.pk:
            return '-'
        languages = obj.translations.values_list('language__name', flat=True).distinct()
        return ', '.join(languages) if languages else '-'
    translation_languages.short_description = 'Translation Languages'

    def paragraph_image_preview(self, obj):
        if not obj or not obj.pk or not obj.image:
            return '-'
        url = obj.image.file_url
        if url:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-height:80px; border-radius:4px;" />'
                '</a>',
                url, url
            )
        return '-'
    paragraph_image_preview.short_description = 'Image Preview'


class PassageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'language', 'level', 'topic',
                    'cover_image_preview', 'translation_languages')
    search_fields = ('title', 'description', 'topic__name', 'source__name')
    list_filter = ('language', 'level', 'topic')
    readonly_fields = ('cover_image_preview', 'translation_languages')
    inlines = (ParagraphInline,)
    list_per_page = 50

    def cover_image_preview(self, obj):
        if not obj.cover_image:
            return '-'
        url = obj.cover_image.file_url
        if url:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-height:100px; border-radius:6px;" />'
                '</a>',
                url, url
            )
        return '-'
    cover_image_preview.short_description = 'Cover Image'

    def translation_languages(self, obj):
        languages = obj.paragraphs.filter(
            translations__isnull=False
        ).values_list('translations__language__name', flat=True).distinct()
        return ', '.join(languages) if languages else '-'
    translation_languages.short_description = 'Translation Languages'


class ParagraphAdmin(admin.ModelAdmin):
    list_display = ('id', 'passage', 'index', 'paragraph_image_preview',
                    'content_preview', 'translation_languages')
    list_filter = ('passage',)
    search_fields = ('content', 'note', 'passage__title')
    readonly_fields = ('paragraph_image_preview',)
    inlines = (ParagraphTranslationInline,)
    raw_id_fields = ('passage',)
    list_per_page = 50

    def paragraph_image_preview(self, obj):
        if not obj.image:
            return '-'
        url = obj.image.file_url
        if url:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-height:80px; border-radius:4px;" />'
                '</a>',
                url, url
            )
        return '-'
    paragraph_image_preview.short_description = 'Image'

    def content_preview(self, obj):
        if not obj.content:
            return '-'
        return obj.content[:80] + '...' if len(obj.content) > 80 else obj.content
    content_preview.short_description = 'Content Preview'

    def translation_languages(self, obj):
        languages = obj.translations.values_list('language__name', flat=True).distinct()
        return ', '.join(languages) if languages else '-'
    translation_languages.short_description = 'Translation Languages'


class ParagraphTranslationAdmin(admin.ModelAdmin):
    list_display = ('id', 'paragraph', 'language', 'created_at')
    list_filter = ('language',)
    search_fields = ('paragraph__passage__title', 'paragraph__content', 'language__name')
    list_per_page = 50

class ReadingNoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'paragraph', 'created_at')
    list_filter = ('user',)
    search_fields = ('paragraph__content', 'user__username')
    list_per_page = 50
    
class UserReadingProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'passage', 'status', 'percentage_read', 'last_paragraph_index')
    list_filter = ('status',)
    search_fields = ('user__username', 'passage__title')
    list_per_page = 50

admin.site.register(Passage, PassageAdmin)
admin.site.register(Paragraph, ParagraphAdmin)
admin.site.register(ParagraphTranslation, ParagraphTranslationAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(ReadingNote, ReadingNoteAdmin)
admin.site.register(UserReadingProgress, UserReadingProgressAdmin)