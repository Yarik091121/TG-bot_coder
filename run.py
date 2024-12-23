import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import TOKEN as _TOKEN
from handlers import router


async def main():
    # Т.к. больше нет диспетчеров в файле, это всё можно переместить в функцию
    bot = Bot(token=_TOKEN)
    dp = Dispatcher()  # Основной роутер, обрабатывает входящие обновления
    # Добавляем диспетчеру роутер
    dp.include_router(router)
    # Запускаем постоянное событие проверки входящих сообщений
    await dp.start_polling(bot)


if __name__ == '__main__':
    # Использовать логирование с выводом в консоль только при дебаге, от 100+ человек будет тормозить бота!
    # Включаем логирование, чтобы не пропустить важные сообщения
    logging.basicConfig(level=logging.INFO)
    # Конфигурируем логирование в консоль
    # Изменяйте уровень логирования на INFO, DEBUG, WARNING, ERROR, CRITICAL
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit (Бот был выключен)')
