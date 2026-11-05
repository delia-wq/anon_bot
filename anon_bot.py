import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession

# 1. ВАШ ТОКЕН НОВОГО БОТА (создайте его в BotFather)
TOKEN = "9033325286:AAHjb5o8mFDvQDyTy4rb3H4E7VM8QXmCnJM"

# 2. ВАШ ЛИЧНЫЙ ID (куда бот будет присылать сообщения и откуда вы будете отвечать)
# Чтобы узнать свой ID, напишите боту @userinfobot
ADMIN_ID = 8525832121  # Замените на ваши цифры!

logging.basicConfig(level=logging.INFO)

# Настройка прокси (ваш Happ)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Здесь мы будем запоминать, кому отвечаем в данный момент
# Формат: {"id_админа": id_пользователя}
reply_mode = {}

# ==========================================
# 1. ПРИЕМ СООБЩЕНИЙ ОТ ПОЛЬЗОВАТЕЛЕЙ
# ==========================================
@dp.message(F.chat.type == "private", Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "⚜️ <b>АДМИН-ПАНЕЛЬ</b> ⚜️\n\n"
            "Чтобы ответить пользователю, используйте команду:\n"
            "<code>/reply [ID_пользователя] [текст]</code>\n"
            "Например: <code>/reply 123456789 Привет!</code>"
        )
    else:
        await message.answer(
            "⚜️ <b>Анонимный канал REGNUM</b> ⚜️\n\n"
            "Здесь ты можешь отправить сообщение, и оно уйдет владельцу <b>без твоего имени</b>.\n"
            "Просто напиши текст (или прикрепи фото/видео) прямо сюда."
        )

@dp.message(F.chat.type == "private")
async def handle_message(message: types.Message):
    # Если пишет админ (и это не команда reply)
    if message.from_user.id == ADMIN_ID:
        if not message.text.startswith("/reply"):
            await message.answer("Чтобы ответить пользователю, напишите: /reply [ID] [текст]")
        return

    # Если пишет обычный пользователь
    user_id = message.from_user.id
    
    # Пересылаем админу
    try:
        # Текст сообщения
        if message.text:
            await bot.send_message(
                ADMIN_ID, 
                f"📩 <b>Новое анонимное сообщение</b>\n"
                f"ID: <code>{user_id}</code>\n\n"
                f"{message.text}", 
                parse_mode="HTML"
            )
        # Медиа (фото, видео, стикеры)
        elif message.photo or message.video or message.sticker:
            await message.forward(ADMIN_ID)
            await bot.send_message(ADMIN_ID, f"👆 Медиа от ID: <code>{user_id}</code>", parse_mode="HTML")
        else:
            await bot.send_message(ADMIN_ID, f"📩 Пользователь <code>{user_id}</code> отправил вложение, которое нельзя переслать текстом.")
            
        await message.answer("✅ Твое сообщение отправлено. Ожидай ответа.")
    except Exception as e:
        await message.answer("❌ Ошибка. Возможно, вы заблокировали бота.")
        print(e)

# ==========================================
# 2. ОТВЕТ ОТ АДМИНА (Команда /reply)
# ==========================================
@dp.message(F.chat.type == "private", Command("reply"))
async def cmd_reply(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
        
    # Разбираем текст команды: /reply 123456789 Привет
    parts = message.text.split(maxsplit=2)
    
    if len(parts) < 3:
        await message.answer("❌ Неверный формат. Напиши: /reply [ID] [текст]")
        return
        
    target_id = parts[1]
    reply_text = parts[2]
    
    try:
        # Отправляем ответ анонимно
        await bot.send_message(
            int(target_id), 
            f"📜 <b>Ответ от владельца:</b>\n\n{reply_text}", 
            parse_mode="HTML"
        )
        await message.answer("✅ Ответ успешно отправлен!")
    except Exception as e:
        await message.answer(f"❌ Не удалось отправить. Возможно, пользователь заблокировал бота.\nОшибка: {e}")

# ==========================================
# ЗАПУСК
# ==========================================
async def main():
    print("Анонимный бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен.")