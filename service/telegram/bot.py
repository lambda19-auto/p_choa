'''
Telegram-bot for neuro-finance
'''
import asyncio
from os import getenv
from pathlib import Path

from aiohttp import web
from dotenv import find_dotenv, load_dotenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, BufferedInputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

try:
    from ..ai import ChoaAI
    from ..avatar import Avatar
    from ..cfs import CFS
    from ..logging_setup import get_logger, setup_logging
except ImportError:
    from ai import ChoaAI
    from avatar import Avatar
    from cfs import CFS
    from logging_setup import get_logger, setup_logging

logger = get_logger(__name__)

load_dotenv(find_dotenv())
choa = ChoaAI()
avatar = Avatar()
BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / 'content'

# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv('BOT_TOKEN')
WEBHOOK_BASE_URL = getenv('WEBHOOK_BASE_URL')
WEBHOOK_PATH = getenv('WEBHOOK_PATH', '/telegram/webhook')
WEBHOOK_SECRET_TOKEN = getenv('WEBHOOK_SECRET_TOKEN')
WEB_SERVER_HOST = getenv('WEB_SERVER_HOST', '0.0.0.0')
WEB_SERVER_PORT = int(getenv('WEB_SERVER_PORT', '8080'))

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    '''
    This handler receives messages with `/start` command
    '''
    await message.answer(f'Hello, {html.bold(message.from_user.full_name)}! \nМеня зовут 초아. Нажмите /help, чтобы узнать больше о моих способностях.')  # type: ignore


@dp.message(Command('help'))
async def cmd_help(message: Message) -> None:
    '''
    This handler receives messages with `/help` command
    '''
    await message.answer('Список команд: \n/help - список команд;\n/about - обо мне и моих задачах;\n/journal - скачать журнал операции;\n/cfs - скачать ОДДС.')


@dp.message(Command('about'))
async def cmd_about(message: Message) -> None:
    '''
    This handler receives messages with `/about` command
    '''
    await message.answer('Я нейро-финансист в торговой компании. В мои обязанности входит ведение журнала операции для ОДДС. А также написание аналитических записок по просьбам руководства.\n\nДля заполнения журнала, пожалуйста, отправьте информацию о переводе: дата, сумма, счёт операции и контрагента.\n\nДля получения аналитической записки, просто напишите об этом ассистенту.')


@dp.message(Command('journal'))
async def cmd_download_journal(message: Message) -> None:
    '''
    This handler receives messages with `/d_journal` command
    '''
    file_path = CONTENT_DIR / 'journal.csv'
    document = FSInputFile(file_path)

    await message.bot.send_document(chat_id=message.chat.id,  # type: ignore
                                    document=document,
                                    caption='Журнал операции')


@dp.message(Command('cfs'))
async def cmd_download_cfs(message: Message) -> None:
    '''
    This handler receives messages with `/d_CFS` command
    '''
    # send already prepared file
    document = FSInputFile(CFS.CFS_PATH)
    await message.bot.send_document(  # type:ignore
        chat_id=message.chat.id,
        document=document,
        caption='Отчет о движении денежных средств')


@dp.message()
async def text(message: Message) -> None:
    '''
    This handler receives messages with text
    '''
    response = await choa.neuro_finansist(message.from_user.id, message.text)  # type: ignore

    if response['module'] == 'analyze':
        await message.answer('Идет подготовка ...')

        try:
            video_file = await avatar.create_video(response['text'])

            video_file.seek(0)
            input_video = BufferedInputFile(video_file.read(), filename='video.mp4')

            await message.bot.send_video(  # type: ignore
                chat_id=message.chat.id,
                video=input_video
            )

        except Exception as e:
            error_text = str(e)
            logger.exception('Ошибка генерации видео: %s', error_text)

            # 💸 нет кредитов HeyGen
            if 'Insufficient credit' in error_text:
                await message.answer(
                    '⚠️ Видео сейчас недоступно (закончились кредиты).\n'
                    'Но я всё равно подготовила ответ:\n\n'
                    f"{response['text']}"
                )

            # ❌ любая другая ошибка
            else:
                await message.answer(
                    '😔 Не удалось сгенерировать видео.\n\n'
                    '📄 Вот текст ответа:\n\n'
                    f"{response['text']}"
                )
    else:
        await message.answer(response['text'])


async def on_startup(bot: Bot) -> None:
    if not WEBHOOK_BASE_URL:
        raise RuntimeError('WEBHOOK_BASE_URL is required to run bot in webhook mode')

    webhook_url = f'{WEBHOOK_BASE_URL.rstrip("/")}{WEBHOOK_PATH}'
    await bot.set_webhook(webhook_url, secret_token=WEBHOOK_SECRET_TOKEN)
    logger.info('Webhook is set: %s', webhook_url)


async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=False)
    logger.info('Webhook is deleted')




dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)

async def main() -> None:
    setup_logging()

    if not TOKEN:
        raise RuntimeError('BOT_TOKEN is not set')

    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    app = web.Application()
    setup_application(app, dp, bot=bot)
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET_TOKEN,
    ).register(app, path=WEBHOOK_PATH)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
    await site.start()

    logger.info('Webhook server started on %s:%s%s', WEB_SERVER_HOST, WEB_SERVER_PORT, WEBHOOK_PATH)

    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()


if __name__ == '__main__':
    setup_logging()
    logger.info('Bot is starting in webhook mode...')
    asyncio.run(main())
