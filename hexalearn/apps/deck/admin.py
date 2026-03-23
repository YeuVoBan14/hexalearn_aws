from django.contrib import admin
from django.utils.html import format_html
from .models import Card, Deck, Folder, StudyState


# ─── INLINES ─────────────────────────────────────────────────────────────────

class StudyStateInline(admin.TabularInline):
    model = StudyState
    extra = 0
    fields = ['user', 'repetition', 'interval_days', 'last_result', 'next_review', 'review_count', 'last_reviewed']
    readonly_fields = ['user', 'repetition', 'interval_days', 'last_result', 'next_review', 'review_count', 'last_reviewed']
    can_delete = False
    verbose_name = "Study State"
    verbose_name_plural = "Study States (No data if empty)"

    def has_add_permission(self, request, obj=None):
        return False


class CardInline(admin.TabularInline):
    model = Card
    extra = 0
    fields = ['card_id', 'front_text', 'back_text', 'hint', 'created_at']
    readonly_fields = ['card_id', 'created_at']
    show_change_link = True

    @admin.display(description='ID')
    def card_id(self, obj):
        return obj.pk


class DeckInline(admin.TabularInline):
    model = Deck
    extra = 0
    fields = ['title', 'is_public', 'estimated_level', 'source', 'card_count_inline', 'created_at']
    readonly_fields = ['card_count_inline', 'created_at']
    show_change_link = True

    @admin.display(description='Cards')
    def card_count_inline(self, obj):
        return obj.cards.count()


# ─── CARD ────────────────────────────────────────────────────────────────────

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['id', 'front_text', 'back_text', 'deck', 'learner_count', 'created_at']
    list_filter = ['deck__estimated_level', 'deck__source', 'created_at']
    search_fields = ['front_text', 'back_text', 'deck__title']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [StudyStateInline]
    fieldsets = (
        ('Content', {
            'fields': ('deck', 'front_text', 'back_text', 'hint')
        }),
        ('Images', {
            'fields': ('front_image', 'back_image'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Learners')
    def learner_count(self, obj):
        count = obj.study_states.count()
        return count if count > 0 else '—'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'deck', 'deck__estimated_level', 'deck__source'
        ).prefetch_related('study_states')


# ─── DECK ────────────────────────────────────────────────────────────────────

@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'owner', 'folder', 'source', 'estimated_level', 'is_public', 'card_count', 'learner_count', 'created_at']
    list_filter = ['is_public', 'estimated_level', 'source', 'created_at']
    search_fields = ['title', 'owner__username', 'description']
    readonly_fields = ['created_at', 'updated_at', 'learner_count']
    autocomplete_fields = ['owner', 'folder']
    inlines = [CardInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('owner', 'folder', 'title', 'description')
        }),
        ('Settings', {
            'fields': ('source', 'estimated_level', 'is_public')
        }),
        ('Stats', {
            'fields': ('learner_count',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Cards')
    def card_count(self, obj):
        return obj.cards.count()

    @admin.display(description='Learners')
    def learner_count(self, obj):
        count = StudyState.objects.filter(
            card__deck=obj
        ).values('user').distinct().count()
        return count if count > 0 else '—'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'owner', 'folder', 'source', 'estimated_level'
        ).prefetch_related('cards')


# ─── FOLDER ──────────────────────────────────────────────────────────────────

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'owner', 'deck_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'owner__username']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['owner']
    inlines = [DeckInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('owner', 'name', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Decks')
    def deck_count(self, obj):
        return obj.decks.count()

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'owner'
        ).prefetch_related('decks')


# ─── STUDY STATE ─────────────────────────────────────────────────────────────

@admin.register(StudyState)
class StudyStateAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'deck_title', 'card_front', 'repetition', 'interval_days', 'next_review', 'last_result', 'review_count']
    list_filter = ['last_result', 'next_review', 'card__deck__estimated_level', 'card__deck__source']
    search_fields = ['user__username', 'card__front_text', 'card__deck__title']
    readonly_fields = ['last_reviewed']
    fieldsets = (
        ('Relationship', {
            'fields': ('user', 'card')
        }),
        ('SRS State', {
            'fields': ('repetition', 'interval_days', 'next_review', 'last_result', 'review_count')
        }),
        ('Timestamps', {
            'fields': ('last_reviewed',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Deck')
    def deck_title(self, obj):
        return obj.card.deck.title

    @admin.display(description='Card')
    def card_front(self, obj):
        return obj.card.front_text[:30]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'card', 'card__deck', 'card__deck__estimated_level'
        )