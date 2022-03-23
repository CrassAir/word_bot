import random

import requests as r
from django.core.management import BaseCommand

from translator.models import Word
from django.core.files.uploadedfile import SimpleUploadedFile
import requests as r
import time

from telegram import Bot

bot = Bot(
    token="1383879665:AAEemz4FwuG_MauuwXQGWx3i_PT863TKl0I"
)


def clear_word(lang):
    Word.objects.filter(language=lang).delete()


def add_new_word(lang_file_name, lang):
    with open(lang_file_name, 'r', encoding='UTF-8') as f:
        for line in f:
            data = line.rstrip().split(' ')
            try:
                word = data[0].encode('iso-8859-1').decode('iso-8859-1')
                usage_count = data[1]
                translate = data[2]
                bword, create = Word.objects.get_or_create(original=word, language=lang,
                                                           defaults={'usage_count': usage_count})
                if not create:
                    bword.translate = translate.lower()
                    print(translate)
                    bword.save()
            except Exception:
                continue


def get_voice(word):
    data = {
        'data': {
            'text': word.original,
            'voice': 'pt-BR'
        },
        'engine': 'Google'
    }
    resp = r.post('https://api.soundoftext.com/sounds', json=data)
    if resp.status_code != 200:
        print('error resp')
        return
    id_voice = resp.json().get('id')
    if not id_voice:
        print('error voice_id')
        return
    resp = r.get(f'https://storage.soundoftext.com/{id_voice}.mp3')
    voice = SimpleUploadedFile(f'{word.original}.mp3', resp.content)
    word.voice = voice
    word.save()
    # print(resp.json())


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('start work')

        # add_new_word('pt_ru_one.txt', 'pt')

        # Word.objects.filter(usage_count__lte=299).delete()
        # word = Word.objects.first()
        # bot.send_voice(942446475, word.voice)

        # words = Word.objects.filter(voice='')
        # for word in words:
        #     get_voice(word)
        #     time.sleep(0.1)

        words = Word.objects.filter(level=2)
        print(words.count())
        word = random.choice(words)
        print(word.original)
        print(word.translate)

        print('end work')
