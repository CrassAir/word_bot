from django.contrib.auth.models import User
from django.db import models


class TelegramAccount(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    level = models.IntegerField(default=1)

    def __str__(self):
        if self.username:
            return f'{self.id} / {self.username} / {self.level}'
        return f'{self.id} / {self.level}'


class Word(models.Model):
    class Meta:
        ordering = ('pk',)

    original = models.CharField(max_length=100, unique=True)
    translate = models.CharField(max_length=100)
    voice = models.FileField(max_length=100)

    language = models.CharField(max_length=100)
    usage_count = models.IntegerField(default=1)
    level = models.IntegerField(default=1)
    error = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.language} / {self.original} / {self.level} / {self.usage_count}'


class PassedWord(models.Model):
    account = models.OneToOneField(TelegramAccount, related_name='passed', on_delete=models.CASCADE)
    words = models.ManyToManyField(Word, related_name='passed_words')
    learned = models.ManyToManyField(Word, related_name='learned_words')

    def __str__(self):
        return f'{self.account}'

