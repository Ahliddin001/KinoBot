import asyncio
import json
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

# --- BOT VA ADMIN SOZLAMALARI ---
BOT_TOKEN = "8950169647:AAE20btjvnl23ksOS83RKd13UkNPl9vJwnk"
ADMIN_ID = 5893335951  # Telegram ID ingiz

# Majburiy obuna kanallari
CHANNELS = [
    {
        "name": "🎬 Kino Kodlari Kanali",
        "url": "https://t.me/filmkodlari_kanal",
        "id": "@filmkodlari_kanal",
    },
    {
        "name": "⚽ Real Madrid Rasmiy",
        "url": "https://t.me/RealMadridCF_Rasmiy",
        "id": "@RealMadridCF_Rasmiy",
    },
]

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
)
dp = Dispatcher(storage=MemoryStorage())

# --- FAYL NOMALARI ---
USERS_FILE = "users.json"
KINOLAR_FILE = "kinolar_info.json"
FILE_IDS_FILE = "file_ids.json"


# --- JSON FAYLLAR BILAN ISHLASH ---
def load_json(filename):
    if not os.path.exists(filename):
        return {} if filename != USERS_FILE else []
    with open(filename, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {} if filename != USERS_FILE else []


def save_user(user_id):
    users = load_json(USERS_FILE)
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)


# --- OBUNANI TEKSHIRISH FUNKSIYASI ---
async def check_subscription(user_id: int) -> bool:
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(
                chat_id=channel["id"], user_id=user_id
            )
            if member.status in ["left", "kicked"]:
                return False
        except Exception:
            return False
    return True


# --- INLINE TUGMALAR TAYYORLASH ---
def get_sub_keyboard(with_check=True):
    builder = InlineKeyboardBuilder()
    for channel in CHANNELS:
        builder.row(
            types.InlineKeyboardButton(
                text=channel["name"], url=channel["url"]
            )
        )
    if with_check:
        builder.row(
            types.InlineKeyboardButton(
                text="✅ Obunani tekshirish", callback_data="check_sub"
            )
        )
    return builder.as_markup()


# --- FSM (XABAR YUBORISH HOLATI) ---
class BroadcastState(StatesGroup):
    waiting_for_message = State()


# 1. START BUYRUG'I
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    save_user(message.from_user.id)

    # Foydalanuvchining ismini olish
    user_name = message.from_user.first_name

    if not await check_subscription(message.from_user.id):
        await message.answer(
            f"👋 Assalomu alaykum {user_name}!\n\n⚠️ Avvalo botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
            reply_markup=get_sub_keyboard(with_check=True),
        )
        return

    await message.answer(
        f"👋 **Xush kelibsiz {user_name}!**\n\nKino ko'rish uchun unga tegishli **kodni** yuboring.\n\nℹ️ Yordam uchun: /help"
    )


# 2. OBUNANI TEKSHIRISH TUGMASI HODISASI
@dp.callback_query(F.data == "check_sub")
async def check_sub_callback(call: types.CallbackQuery):
    user_name = call.from_user.first_name

    if await check_subscription(call.from_user.id):
        await call.answer(
            "✅ Rahmat! Obuna tasdiqlandi.\nEndi botdan bemalol foydalaning!",
            show_alert=True,
        )
        await call.message.edit_text(
            f"👋 **Xush kelibsiz {user_name}!**\n\nKino ko'rish uchun unga tegishli **kodni** yuboring.\n\nℹ️ Yordam uchun: /help"
        )
    else:
        await call.answer(
            "❌ Siz hali barcha kanallarga obuna bo'lmadingiz!\nIltimos, obuna bo'ling.",
            show_alert=True,
        )


# 3. KANAL BUYRUG'I
@dp.message(Command("kanal"))
async def kanal_cmd(message: types.Message):
    save_user(message.from_user.id)
    await message.answer(
        "📢 Kanallarimiz ro'yxati bilan tanishing:",
        reply_markup=get_sub_keyboard(with_check=False),
    )


# 4. HELP BUYRUG'I
@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    save_user(message.from_user.id)

    # Kanalga o'tish tugmasi
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🎬 Kanalga o'tish", url="https://t.me/filmkodlari_kanal"))

    await message.answer(
        "ℹ️ **Yordam bo'limidasiz:**\n\n"
        "1. Pastdagi tugma orqali kanalga kiring.\n"
        "2. U yerdagi kinolardan kodini oling.\n"
        "3. Kodni botga yuboring.\n"
        "4. O'z kinoingizni oling.\n"
        "5. Marhamat, rohatlaning!",
        reply_markup=kb.as_markup()
    )


# 5. ADMIN PANEL BUYRUG'I
@dp.message(Command("admin"), F.from_user.id == ADMIN_ID)
async def admin_panel(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="📊 Statistika"),
        types.KeyboardButton(text="📢 Xabar Tarqatish"),
    )
    await message.answer(
        "👑 Admin panelga xush kelibsiz!",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


# 6. ADMIN PANEL STATISTIKA
@dp.message(F.text == "📊 Statistika", F.from_user.id == ADMIN_ID)
async def show_stats(message: types.Message):
    users = load_json(USERS_FILE)
    status_msg = await message.answer("📊 Statistika hisoblanmoqda, kuting...")

    active_count = 0
    blocked_count = 0

    for user_id in users:
        try:
            # Foydalanuvchi botni bloklaganini tekshirish
            await bot.send_chat_action(chat_id=user_id, action="typing")
            active_count += 1
        except Exception:
            blocked_count += 1
        await asyncio.sleep(0.03)

    await status_msg.edit_text(
        "🤖 **Bot nomi:** @FilmKodlariBot\n"
        "📅 **Yaratilgan:** 09.01.2026\n\n"
        f"📊 **Barcha foydalanuvchilar:** {len(users)} ta\n"
        f"✅ **Aktiv foydalanuvchilar:** {active_count} ta\n"
        f"🚫 **Bloklagan foydalanuvchilar:** {blocked_count} ta"
    )


# 7. ADMIN XABAR TARQATISH
@dp.message(F.text == "📢 Xabar Tarqatish", F.from_user.id == ADMIN_ID)
async def start_broadcast(message: types.Message, state: FSMContext):
    await state.set_state(BroadcastState.waiting_for_message)
    await message.answer(
        "Siz **📢 Xabar Tarqatish** bo'limidasiz.\n"
        "Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yuboring\n"
        "(Matn, Rasm yoki Rasm+Matn):"
    )


@dp.message(BroadcastState.waiting_for_message, F.from_user.id == ADMIN_ID)
async def send_broadcast(message: types.Message, state: FSMContext):
    await state.clear()
    users = load_json(USERS_FILE)
    sent_count = 0
    blocked_count = 0

    status_msg = await message.answer(
        f"🚀 Xabar yuborish boshlandi...\nJami foydalanuvchilar: {len(users)} ta"
    )

    for user_id in users:
        try:
            if message.photo:
                caption = message.caption if message.caption else None
                await bot.send_photo(
                    chat_id=user_id,
                    photo=message.photo[-1].file_id,
                    caption=caption,
                )
            elif message.text:
                await bot.send_message(chat_id=user_id, text=message.text)
            sent_count += 1
            await asyncio.sleep(0.05)
        except Exception:
            blocked_count += 1

    await status_msg.edit_text(
        f"✅ **Xabar tarqatish yakunlandi!**\n\n"
        f"📥 Muvaffaqiyatli yetib bordi: {sent_count} ta\n"
        f"🚫 Botni bloklaganlar: {blocked_count} ta"
    )


# 8. KINO KODINI QABUL QILISH (Video ostida faqat kanallar tugmalari chiqadi)
@dp.message(F.text)
async def get_movie_by_code(message: types.Message):
    save_user(message.from_user.id)

    # Kanal obunasini tekshirish
    if not await check_subscription(message.from_user.id):
        await message.answer(
            "⚠️ Kino ko'rishdan oldin kanallarga obuna bo'lishingiz kerak:",
            reply_markup=get_sub_keyboard(with_check=True),
        )
        return

    code = message.text.strip()
    file_ids = load_json(FILE_IDS_FILE)
    kinolar_info = load_json(KINOLAR_FILE)

    if code in file_ids:
        movie_file_id = file_ids[code]

        emoji_map = {
            "nomi": "🎬",
            "janri": "🎭",
            "janr": "🎭",
            "til": "🌐",
            "sifat": "💿",
            "yili": "📅",
            "yil": "📅",
            "davlat": "🌍",
        }

        if isinstance(kinolar_info, dict) and code in kinolar_info:
            info = kinolar_info[code]
            if isinstance(info, dict):
                lines = []
                for k, v in info.items():
                    emoji = emoji_map.get(str(k).lower(), "📌")
                    lines.append(f"{emoji} **{str(k).capitalize()}**: {v}")
                caption_text = "\n".join(lines)
            else:
                caption_text = str(info)
        else:
            caption_text = f"🎬 **Siz izlagan kino** (Kod: {code})"

        await bot.send_video(
            chat_id=message.chat.id,
            video=movie_file_id,
            caption=caption_text,
            reply_markup=get_sub_keyboard(with_check=False),
        )
    else:
        await message.answer(
            f"⚠️ Bunday kodli ({code}) kino topilmadi.\n\n"
            "Kino kodlarini olish uchun: https://t.me/filmkodlari_kanal\n"
            "Yordam olish uchun: /help"
        )


async def main():
    print("Ahliddin\n🎬 KinoBot ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
