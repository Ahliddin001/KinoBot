import asyncio
import json
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramBadRequest, TelegramEntityTooLarge
from aiogram.filters import Command
from aiogram.types import (
    BotCommand,
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)




'''
 
'''

TOKEN = "8950169647:AAE20btjvnl23ksOS83RKd13UkNPl9vJwnk"

# Kanallar ro'yxati (Username va Linklar)
KANAL1_ID = "@filmkodlari_kanal"
KANAL1_URL = "https://t.me/filmkodlari_kanal"

KANAL2_ID = "@RealMadridCF_Rasmiy"
KANAL2_URL = "https://t.me/RealMadridCF_Rasmiy"

CHANNELS = [KANAL1_ID, KANAL2_ID]

KINOLAR_DIR = "kinolar"
CACHE_FILE = "file_ids.json"
INFO_FILE = "kinolar_info.json"

session = AiohttpSession(timeout=300)
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()


def load_json(file_path):
  if os.path.exists(file_path):
    try:
      with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception:
      return {}
  return {}


def save_json(file_path, data):
  with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


# Obuna bo'lish tugmalari
def get_sub_keyboard():
  return InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="1-Kanalga a'zo bo'lish 📢", url=KANAL1_URL
              )
          ],
          [
              InlineKeyboardButton(
                  text="2-Kanalga a'zo bo'lish 📢", url=KANAL2_URL
              )
          ],
          [
              InlineKeyboardButton(
                  text="✅ Tekshirish", callback_data="check_sub"
              )
          ],
      ]
  )


# Video va ma'lumotlar ostidagi tugmalar
def get_channel_keyboard():
  return InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="🔍 1-Kinokodi kanali", url=KANAL1_URL
              )
          ],
          [InlineKeyboardButton(text="📢 2-Rasmiy kanalimiz", url=KANAL2_URL)],
      ]
  )


# Obunani aniq tekshirish funksiyasi
async def check_subscription(user_id: int) -> bool:
  for channel in CHANNELS:
    try:
      member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
      # Agar foydalanuvchi kanalda bo'lmasa yoki haydalgan bo'lsa
      if member.status in ["left", "kicked"]:
        return False
    except Exception as e:
      print(f"❌ [{channel}] kanalini tekshirishda xatolik: {e}")
      # Bot kanalda admin bo'lmasa yoki kanal nomi xato bo'lsa false qaytaradi
      return False
  return True


def get_caption(code):
  current_info = load_json(INFO_FILE)
  caption = ""

  if code in current_info:
    info = current_info[code]
    if isinstance(info, dict):
      caption = (
          f"🎬 <b>{info.get('nomi', 'Kino')}</b>\n\n"
          f"📅 <b>Yili:</b> {info.get('yili', '-')}\n"
          f"🌍 <b>Davlat:</b> {info.get('davlat', '-')}\n"
          f"🎭 <b>Janr:</b> {info.get('janr', '-')}\n"
          f"🗣 <b>Tili:</b> {info.get('tili', '-')}\n"
      )
    elif isinstance(info, str):
      caption = f"{info}\n"
  else:
    caption = f"🎬 Kino kodi: <b>{code}</b>\n"

  caption += f"\n📢 <b>Bizning kanallar:</b>\n{KANAL1_ID} | {KANAL2_ID}"
  return caption


async def set_bot_commands(bot: Bot):
  commands = [
      BotCommand(command="start", description="Botni qayta ishga tushirish"),
      BotCommand(command="kanal", description="Kino kodlarini topish uchun"),
      BotCommand(command="help", description="Yordam va yo'riqnoma"),
  ]
  await bot.set_my_commands(commands)


# ================= HANDLERLAR =================


@dp.message(Command("start"))
@dp.message(F.text.in_({"/start", "\\start", "start"}))
async def start_handler(message: types.Message):
  is_subscribed = await check_subscription(message.from_user.id)
  if not is_subscribed:
    await message.answer(
        "⚠️ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:</b>",
        parse_mode="HTML",
        reply_markup=get_sub_keyboard(),
    )
    return

  await message.answer(
      "🍿 <b>Salom! Kino kodini yuboring</b>",
      parse_mode="HTML",
      reply_markup=get_channel_keyboard(),
  )


@dp.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery):
  is_subscribed = await check_subscription(callback.from_user.id)
  if is_subscribed:
    await callback.message.delete()
    await callback.message.answer(
        "✅ <b>Rahmat! Obuna tasdiqlandi.Marhamat kino kodini"
        " yuborishingiz mumkin:</b>",
        parse_mode="HTML",
        reply_markup=get_channel_keyboard(),
    )
  else:
    await callback.answer(
        """❌ Siz hali barcha kanallarga a'zo bo'lmadingiz!
        Avvalo barcha kanallarga obuna bo'ling va obunani tekshiring""", show_alert=True
    )


@dp.message(Command("kanal"))
@dp.message(F.text.in_({"/kanal", "\\kanal", "kanal"}))
async def kanal_handler(message: types.Message):
  await message.answer(
      f"📢 <b>Bizning rasmiy kanallarimiz:</b>\n\n"
      f"1️⃣ {KANAL1_ID}\n"
      f"2️⃣ {KANAL2_ID}\n\n"
      f"Kanalga o'tish uchun pastdagi tugmalarni bosing:",
      parse_mode="HTML",
      reply_markup=get_channel_keyboard(),
  )


@dp.message(Command("help"))
@dp.message(F.text.in_({"/help", "\\help", "help"}))
async def help_handler(message: types.Message):
  await message.answer(
      "❓ <b>Yordam bo'limi:</b>\n\n"
      "• Kinoni olish uchun shunchaki uning kodini yuboring (masalan: 005).\n"
      f"• Kanallarimiz: {KANAL1_ID} | {KANAL2_ID}",
      parse_mode="HTML",
      reply_markup=get_channel_keyboard(),
  )


@dp.message(F.video)
async def get_video_file_id(message: types.Message):
  file_id = message.video.file_id
  file_size_mb = round(message.video.file_size / (1024 * 1024), 2)

  await message.reply(
      f"✅ <b>Videoning file_id si olindi!</b>\n\n"
      f"<b>Hajmi:</b> {file_size_mb} MB\n"
      f"<b>file_id:</b>\n<code>{file_id}</code>\n\n"
      f"<i>Ushbu ID ni <code>file_ids.json</code> fayliga kiriting.</i>",
      parse_mode="HTML",
  )


@dp.message(F.text)
async def get_movie_handler(message: types.Message):
  is_subscribed = await check_subscription(message.from_user.id)
  if not is_subscribed:
    await message.answer(
        "⚠️ <b>Kinoni ko'rish uchun avval kanallarga obuna bo'ling:</b>",
        parse_mode="HTML",
        reply_markup=get_sub_keyboard(),
    )
    return

  code = message.text.strip()
  caption_text = get_caption(code)
  current_cache = load_json(CACHE_FILE)

  if code in current_cache and isinstance(current_cache[code], str):
    await message.answer_video(
        video=current_cache[code],
        caption=caption_text,
        parse_mode="HTML",
        reply_markup=get_channel_keyboard(),
    )
    return

  video_path = os.path.abspath(os.path.join(KINOLAR_DIR, f"{code}.mp4"))

  if os.path.exists(video_path):
    status_msg = await message.answer("⏳ Kino yuklanmoqda, kuting...")
    video_file = FSInputFile(video_path)

    try:
      sent_message = await message.answer_video(
          video=video_file,
          caption=caption_text,
          parse_mode="HTML",
          reply_markup=get_channel_keyboard(),
      )
      current_cache[code] = sent_message.video.file_id
      save_json(CACHE_FILE, current_cache)
      await status_msg.delete()

    except TelegramEntityTooLarge:
      await status_msg.delete()
      await message.answer(
          "❌ <b>Bu videoning hajmi 50 MB dan katta!</b>\n\n"
          "Iltimos, videoni botga yuborib, olingan <code>file_id</code> ni"
          " <code>file_ids.json</code> ga kiriting.",
          parse_mode="HTML",
      )
  else:
    await message.answer(
        f"❌ <b>{code}</b> kodli kino topilmadi.",
        parse_mode="HTML",
        reply_markup=get_channel_keyboard(),
    )


async def main():
  await set_bot_commands(bot)
  print("""
  aiogram ishlamoqda
  /start kommand ishlamoqda
  /kanal kommand ishlamoqda
  /help kommand ishlamoqda
  KANAL1_ID = succesful
  KANAL1_URL = successful
  KANAL2_ID = successful
  KANAL2_URL = successful
  ishlamoqda
  CHANNELS ishlamoqda
  inline_buttons ishlamoqda
  kinolar_info.json ishlamoqda
  file_id.json ishlamoqda
  Ahliddin, 
  🎬 KinoBot ishga tushdi!\n""")

  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())