from django.contrib import admin

from translator.models import TelegramAccount, Word, PassedWord


class WordAdmin(admin.ModelAdmin):
    search_fields = ('original', 'translate')


admin.site.register(TelegramAccount)
admin.site.register(Word, WordAdmin)
admin.site.register(PassedWord)
