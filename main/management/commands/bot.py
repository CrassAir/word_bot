import asyncio
import logging
import random

from aiogram import Bot, Dispatcher, F, types, Router
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardRemove
from asgiref.sync import sync_to_async

from django.core.management import BaseCommand

from translator.models import Word, PassedWord, TelegramAccount

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

loop = asyncio.get_event_loop()

bot = Bot(
    token="1979715569:AAFJQwbubYVsDNrfJ62i4wcQCrRU_xLorwM"
)

dp = Dispatcher()
router = Router()
dp.include_router(router)


class Form(StatesGroup):
    account = State()

    learning = State()

    stage1 = State()
    stage2 = State()

    word = State()
    letter_list = State()
    word_stage2 = State()
    word_func = State()
    prev_message = State()
    prev_voice = State()
    passed_count = State()


def get_random_word(acc: TelegramAccount, level: int = 2) -> Word:
    word = random.choice(
        Word.objects.filter(level=level, language='pt', error=False).exclude(passed_words__account=acc,
                                                                             learned_words__account=acc))
    acc.passed.words.add(word)
    return word


def create_or_get_account(t_id: int, username: str):
    acc, create = TelegramAccount.objects.get_or_create(id=t_id, username=username)
    passed_word_obj = PassedWord.objects.get_or_create(account=acc)
    print(passed_word_obj)
    return acc, create


def get_passed_word(acc: TelegramAccount) -> Word:
    word = random.choice(acc.passed.words.filter(error=False))
    return word


def get_passed_words_text(acc: TelegramAccount):
    words = acc.passed.words.filter(error=False)
    answer_text = '*Список пройденных слов:*\n'
    for word in words:
        answer_text += f'{word.original} \-\-\- {word.translate}\n'
    answer_text += f'*Всего пройденно слов: {len(words)}*'
    return answer_text


def get_learned_words_text(acc: TelegramAccount):
    words = acc.passed.learned.filter(error=False)
    answer_text = '*Список изученных слов:*\n'
    for word in words:
        answer_text += f'{word.original} \-\-\- {word.translate}\n'
    answer_text += f'*Всего изученно слов: {len(words)}*'
    return answer_text


def set_learning_word(acc: TelegramAccount, word):
    acc.passed.words.remove(word)
    acc.passed.learned.add(word)


def set_word_error(word: Word):
    word.error = True
    word.save()


async def send_word(message: types.Message, state: FSMContext, start_text):
    data = await state.get_data()
    prev_message = data.get('prev_message')
    prev_voice = data.get('prev_voice')
    passed_count = data.get('passed_count')
    prev_word = data.get('word')
    if prev_voice:
        await prev_voice.delete()
    await prev_message.delete()
    if passed_count >= 15:
        answer_text = f'{prev_word.original} переводится как {prev_word.translate}\n\nХотите повторить пройденые слова?'
        answer = await bot.send_message(message.chat.id, answer_text,
                                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                            [
                                                InlineKeyboardButton(text='Да', callback_data='Да'),
                                                InlineKeyboardButton(text='Нет', callback_data='Нет')
                                            ]
                                        ]))
        await state.update_data(stage1=0, stage2=0, word_stage2='', prev_message=answer, passed_count=0,
                                prev_voice=None)
        return
    word = await sync_to_async(data.get('word_func'))(data.get('account'))
    if not word:
        word = await sync_to_async(get_random_word)(data.get('account'))
        await state.update_data(word_func=get_random_word)
    answer_text = start_text + f'\n\n*{word.original}*\n\nНапишите перевод\.\.\.'
    voice = FSInputFile(word.voice.path)
    voice_answer = await bot.send_voice(message.chat.id, voice, reply_markup=ReplyKeyboardRemove())
    answer = await bot.send_message(message.chat.id, answer_text, parse_mode='MarkdownV2',
                                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                        [InlineKeyboardButton(text='Ошибка в слове', callback_data='word_error'),
                                         InlineKeyboardButton(text='Следующее слово', callback_data='skip_word')]
                                    ]))
    await state.set_state(Form.stage1)
    await state.update_data(stage1=0, stage2=0, word_stage2='', word=word, prev_message=answer,
                            prev_voice=voice_answer, passed_count=passed_count + 1)


@router.message(commands=['menu'])
async def menu(message: types.Message):
    answer_text = f'Добро пожаловать это меню бота'
    await bot.send_message(message.chat.id, answer_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Выбор языка', callback_data='select_language')],
        [InlineKeyboardButton(text='Список пройденных слов', callback_data='passed_words')],
        [InlineKeyboardButton(text='Список изученных слов', callback_data='learned_words')],
    ]))


@router.callback_query(text='select_language')
@router.callback_query(text='passed_words')
@router.callback_query(text='learned_words')
async def menu_processor(query: types.CallbackQuery, state: FSMContext):
    answer_data = query.data
    data = await state.get_data()

    if answer_data == 'passed_words':
        await query.answer('Готово')
        answer_text = await sync_to_async(get_passed_words_text)(data.get('account'))
        await bot.send_message(query.from_user.id, answer_text, parse_mode='MarkdownV2')

    if answer_data == 'learned_words':
        await query.answer('Готово')
        answer_text = await sync_to_async(get_learned_words_text)(data.get('account'))
        await bot.send_message(query.from_user.id, answer_text, parse_mode='MarkdownV2')


@router.callback_query(text='skip_word')
@router.callback_query(text='clear_word')
async def menu_processor(query: types.CallbackQuery, state: FSMContext):
    answer_data = query.data
    data = await state.get_data()
    prev_word = data.get('word')

    if answer_data == 'skip_word':
        start_text = f'{prev_word.original} переводится как {prev_word.translate}\n\nВот следующее слово:'
        await send_word(query.message, state, start_text)

    if answer_data == 'clear_word':
        prev_mess = data.get('prev_voice')
        await prev_mess.delete()
        await state.update_data(word_stage2='')


@router.callback_query(text='Нет')
@router.callback_query(text='Да')
async def refuse_passed(query: types.CallbackQuery, state: FSMContext):
    answer_data = query.data

    if answer_data == 'Да':
        await state.update_data(word_func=get_passed_word)
        start_text = f'Ну что повторим\nПервое слово:'

    else:
        await state.update_data(word_func=get_random_word)
        start_text = f'Хорошо тогда продолжим\.\n\nСледующие слово:'

    await send_word(query.message, state, start_text)


@router.message(Form.stage1)
async def stage_first(message: types.Message, state: FSMContext):
    await message.delete()

    data = await state.get_data()
    prev_word: Word = data.get('word')
    prev_message: types.Message = data.get('prev_message')
    prev_voice = data.get('prev_voice')
    try_count = data.get('stage1')

    if try_count > 1:
        start_text = f'*{prev_word.original} переводится как {prev_word.translate}\.*\n' \
                     f'Вы написали {message.text}'
        await send_word(message, state, start_text)
        return

    if prev_word and prev_word.translate == message.text.lower():
        answer_text = f'{message.text}\n\nВсе верно, теперь составте слово из букв'
        list_btn = [KeyboardButton(text=letter) for letter in set(prev_word.original)]
        random.shuffle(list_btn)
        keyboard = ReplyKeyboardMarkup(keyboard=[list_btn])

        await prev_message.delete()
        await prev_voice.delete()
        answer = await bot.send_message(message.chat.id, answer_text, parse_mode='MarkdownV2', reply_markup=keyboard)

        await state.update_data(state1=0, stage2=0, prev_message=answer, letter_list=list_btn, prev_voice=None)
        await state.set_state(Form.stage2)
        return

    answer_text = f'{message.text}\n\n{prev_word.original}\n\nПока что не правильно, попробуйте еще раз'
    await prev_message.edit_text(answer_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Ошибка в слове', callback_data='word_error'),
         InlineKeyboardButton(text='Следующее слово', callback_data='skip_word')]
    ]))
    await state.update_data(stage1=try_count + 1)


@router.message(Form.stage2)
async def stage_second(message: types.Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    prev_word: Word = data.get('word')
    prev_letter_list = data.get('letter_list')
    prev_message: types.Message = data.get('prev_message')
    prev_voice: types.Message = data.get('prev_voice')
    try_count = data.get('stage2')
    word_stage2 = data.get('word_stage2', '') + message.text

    if len(word_stage2) == len(prev_word.original):
        if word_stage2 == prev_word.original:
            await sync_to_async(set_learning_word)(data.get('account'), prev_word)
            start_text = f'Все правильно\.\nСледующее слово:'
            await send_word(message, state, start_text)
            return

        if prev_voice:
            await prev_voice.delete()
        await prev_message.delete()
        answer_text = f'{prev_word.translate}\n\nНе правильно, попробуйте еще раз'
        list_btn = [KeyboardButton(text=letter) for letter in set(prev_word.original)]
        random.shuffle(list_btn)
        keyboard = ReplyKeyboardMarkup(keyboard=[list_btn])
        answer = await bot.send_message(message.chat.id, answer_text, reply_markup=keyboard)
        await state.update_data(word_stage2='', letter_list=list_btn, prev_message=answer)
        return

    answer_text = f'{word_stage2}'
    keyborad = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Пропустить', callback_data='skip_word'),
            InlineKeyboardButton(text='Сбросить', callback_data='clear_word')
        ]
    ])
    if len(word_stage2) == 1:
        answer = await bot.send_message(message.chat.id, answer_text, reply_markup=keyborad)
        await state.update_data(word_stage2=word_stage2, letter_list=prev_letter_list, prev_voice=answer)
    else:
        await prev_voice.edit_text(answer_text, reply_markup=keyborad)
        await state.update_data(word_stage2=word_stage2, letter_list=prev_letter_list)


@router.message(commands=["start"])
@router.message()
async def letter_sending(message: types.Message, state: FSMContext):
    await message.delete()

    account, create = await sync_to_async(create_or_get_account)(message.chat.id, message.chat.username)
    await state.update_data(account=account, passed_count=0)
    welcome_text = 'Вас приветствует бот для изучения иностранных слов.\n' \
                   'Для более удобной работы выключите звук уведомлений в чате с ботом.\n\n'
    if create:
        start_text = welcome_text + f'Ну что же начнем изучать слова\nВот первое слово:'
        await send_word(message, state, start_text)
        return

    answer_text = welcome_text + 'Вы вернулись, ну что продолжим!\nХотите повторить пройденые слова?'
    answer = await bot.send_message(message.chat.id, answer_text,
                                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                        [
                                            InlineKeyboardButton(text='Да', callback_data='Да'),
                                            InlineKeyboardButton(text='Нет', callback_data='Нет')
                                        ]
                                    ]))
    await state.update_data(prev_message=answer, prev_voice=None)
    return


class Command(BaseCommand):

    def handle(self, *args, **options):
        dp.run_polling(bot)
