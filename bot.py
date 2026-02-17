import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8490093749:AAGQNGlEGQbr2RwmmRUEB1b0OX6eZjwwSto'
ADMIN_ID = 8533792551  # SHU YERGA O'ZINGIZNING ID RAQAMINGIZNI YOZING (Telegramda @userinfobot orqali bilsangiz bo'ladi)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- Baza ---
db = sqlite3.connect("stars_bot.db")
cursor = db.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users 
               (user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0, 
                referals INTEGER DEFAULT 0, is_verified INTEGER DEFAULT 0, invited_by INTEGER)""")
cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
db.commit()

# --- Tugmalar ---
def get_main_menu(user_id):
    buttons = [
        [KeyboardButton(text="🌟 Stars ishlash")],
        [KeyboardButton(text="💰 Hisobim"), KeyboardButton(text="📥 Stars yechish")],
        [KeyboardButton(text="📩 Murojaat")]
    ]
    if user_id == ADMIN_ID:8533792551
        buttons.append([KeyboardButton(text="⚙️ Boshqarish")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@dp.message(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id
    
    # Kanalga a'zolikni tekshirish
    cursor.execute("SELECT value FROM settings WHERE key = 'channel_id'")
    channel = cursor.fetchone()
    
    if channel:
        try:
            check = await bot.get_chat_member(chat_id=channel[0], user_id=user_id)
            if check.status == 'left':
                inline_sub = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📢 Kanalga a'zo bo'lish", url=f"https://t.me/{channel[0].replace('@','')}")],
                    [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")]
                ])
                return await message.answer("Botdan foydalanish uchun kanalimizga a'zo bo'ling!", reply_markup=inline_sub)
        except:
            pass # Kanal topilmasa yoki bot admin bo'lmasa

    # Ro'yxatdan o'tganini tekshirish (oldingi mantiq)
    cursor.execute("SELECT is_verified FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        args = message.text.split()
        invited_by = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
        cursor.execute("INSERT INTO users (user_id, invited_by) VALUES (?, ?)", (user_id, invited_by))
        db.commit()
        
        kb_contact = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📞 Tasdiqlash", request_contact=True)]], resize_keyboard=True)
        await message.answer("Xush kelibsiz! Raqamingizni yuboring:", reply_markup=kb_contact)
    else:
        await message.answer("Bosh menyu:", reply_markup=get_main_menu(user_id))

@dp.message(F.text == "⚙️ Boshqarish", F.from_user.id == ADMIN_ID)
async def admin_panel(message: types.Message):
    kb_admin = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📣 Kanalni sozlash", callback_data="set_channel")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="stats")]
    ])
    await message.answer("Admin panelga xush kelibsiz:", reply_markup=kb_admin)

@dp.callback_query(F.data == "set_channel")
async def set_channel_prompt(call: types.CallbackQuery):
    await call.message.answer("Majburiy obuna uchun kanal yuzerini yuboring.\nMasalan: `@kanal_nomi`")

@dp.message(F.text.startswith("@"), F.from_user.id == ADMIN_ID)
async def save_channel(message: types.Message):
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('channel_id', ?)", (message.text,))
    db.commit()
    await message.answer(f"✅ Majburiy obuna kanali {message.text} ga o'zgartirildi!")

# (Qolgan xabar va kontakt funksiyalari avvalgi koddagidek qoladi...)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())