import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (Application, CommandHandler, MessageHandler,
                           filters, ContextTypes)
from config import *
from database import *

logging.basicConfig(level=logging.INFO)

broadcast_mode = {}
reply_mode = {}

LIMIT = 5  # Faqat 5 ta odam

def user_menyu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📱 Kontakt yuborish", request_contact=True)],
        [KeyboardButton("💎 Skidka haqida"), KeyboardButton("❓ Savol")],
    ], resize_keyboard=True)

def admin_menyu():
    return ReplyKeyboardMarkup([
        ["👥 Foydalanuvchilar", "📊 Statistika"],
        ["📢 Xabar yuborish", "📋 Kontaktlar"],
        ["💎 Skidka haqida"],
    ], resize_keyboard=True)

def get_menyu(uid):
    return admin_menyu() if uid == ADMIN_ID else user_menyu()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    uid = user.id
    user_qoshish(uid, user.username, user.first_name)

    jami = jami_kontakt()
    qolgan = LIMIT - jami

    if qolgan <= 0:
        await update.message.reply_text(
            f"😔 Afsuski, chegirmali taklif tugadi!\n\n"
            f"5 ta joy allaqachon band bo'ldi.\n\n"
            f"Keyingi aksiyalar uchun kuzatib boring!\n"
            f"Admin: {ADMIN_USERNAME}"
        )
        return

    await update.message.reply_text(
        f"👋 Assalomu alaykum, {user.first_name}!\n\n"
        f"🔥 MAXSUS TAKLIF!\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"💎 Telegram Premium 1 oy\n\n"
        f"❌ {NARX_ASL:,} so'm\n"
        f"✅ Atigi {Bepul_Premsoni:,} so'm!\n\n"
        f"🎁 Tejash: {NARX_ASL - Bepul_Premsoni:,} so'm!\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔥 Faqat {qolgan} ta joy qoldi!\n\n"
        f"📲 Kontakt yuboring yoki savol yozing!",
        reply_markup=get_menyu(uid)
    )

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    uid = user.id
    phone = update.message.contact.phone_number
    name = user.first_name
    username = f"@{user.username}" if user.username else "yo'q"

    jami = jami_kontakt()

    if jami >= LIMIT:
        await update.message.reply_text(
            f"😔 Kechirasiz, {name}!\n\n"
            f"5 ta joy allaqachon band bo'ldi.\n\n"
            f"Admin: {ADMIN_USERNAME}"
        )
        return

    phone_saqlash(uid, phone)

    qolgan = LIMIT - jami - 1

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📲 YANGI MIJOZ! ({jami+1}/{LIMIT})\n"
             f"━━━━━━━━━━━━━━━━━━\n\n"
             f"👤 Ism: {name}\n"
             f"📌 Username: {username}\n"
             f"📱 Telefon: +{phone}\n"
             f"🆔 ID: {uid}\n\n"
             f"{'⚠️ OXIRGI JOY!' if qolgan == 0 else f'Qolgan: {qolgan} ta joy'}\n\n"
             f"💬 Javob: /reply_{uid}"
    )

    if qolgan == 0:
        tugadi_text = "\n\n⚡ Siz oxirgi lucky o'rindiqni oldingiz!"
    else:
        tugadi_text = f"\n\n🔥 Tezlashing! Yana {qolgan} ta joy qoldi!"

    await update.message.reply_text(
        f"✅ Rahmat, {name}!\n\n"
        f"📞 Tez orada siz bilan bog'lanamiz!\n"
        f"⏳ Kutish vaqti: 5-30 daqiqa"
        f"{tugadi_text}\n\n"
        f"❓ Savol bo'lsa yozing!",
        reply_markup=get_menyu(uid)
    )

async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    uid = user.id
    if uid == ADMIN_ID:
        return
    text = update.message.text
    name = user.first_name
    username = f"@{user.username}" if user.username else "yo'q"

    if text == "💎 Skidka haqida":
        await skidka_haqida(update, context)
        return
    elif text == "❓ Savol":
        await update.message.reply_text(
            "❓ Savolingizni yozing — javob beramiz!\n\n"
            f"⏰ Ish vaqti: 9:00 - 23:00"
        )
        return

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"💬 YANGI XABAR\n"
             f"━━━━━━━━━━━━━━━━━━\n"
             f"👤 {name} ({username})\n"
             f"🆔 ID: {uid}\n\n"
             f"📝 {text}\n\n"
             f"💬 Javob: /reply_{uid}"
    )
    await update.message.reply_text("✅ Xabaringiz qabul qilindi! Tez orada javob beramiz.")

async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    text = update.message.text
    try:
        target_id = int(text.replace("/reply_", ""))
        reply_mode[ADMIN_ID] = target_id
        await update.message.reply_text(
            f"✏️ Javob yozing — ID {target_id} ga yuboriladi.\n"
            f"Bekor qilish: /cancel"
        )
    except:
        await update.message.reply_text("Noto'g'ri format.")

async def admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    if uid != ADMIN_ID:
        return
    text = update.message.text

    if broadcast_mode.get(ADMIN_ID):
        broadcast_mode[ADMIN_ID] = False
        users = barcha_users()
        ok = 0
        xato = 0
        await update.message.reply_text(f"Yuborilmoqda {len(users)} ta foydalanuvchiga...")
        for u in users:
            try:
                await context.bot.send_message(chat_id=u[0], text=text)
                ok += 1
            except:
                xato += 1
        await update.message.reply_text(f"Yuborildi! Muvaffaqiyatli: {ok}, Xato: {xato}")
        return

    if ADMIN_ID in reply_mode:
        target_id = reply_mode.pop(ADMIN_ID)
        try:
            await context.bot.send_message(chat_id=target_id, text=f"👤 Admin javob:\n\n{text}")
            await update.message.reply_text(f"Yuborildi! (ID: {target_id})")
        except:
            await update.message.reply_text("Yuborib bo'lmadi.")
        return

    if text == "👥 Foydalanuvchilar":
        await foydalanuvchilar(update, context)
    elif text == "📊 Statistika":
        await statistika(update, context)
    elif text == "📢 Xabar yuborish":
        broadcast_mode[ADMIN_ID] = True
        await update.message.reply_text("Xabar yozing. Bekor: /cancel")
    elif text == "📋 Kontaktlar":
        await kontaktlar(update, context)
    elif text == "💎 Skidka haqida":
        await skidka_haqida(update, context)

async def skidka_haqida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jami = jami_kontakt()
    qolgan = LIMIT - jami
    await update.message.reply_text(
        f"💎 TELEGRAM PREMIUM 1 OY\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"✨ Premium imkoniyatlari:\n"
        f"• Cheksiz fayl yuklash (4GB)\n"
        f"• Maxsus stikerlar va emoji\n"
        f"• Tezkor yuklab olish\n"
        f"• Reklama yo'q\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"❌ {NARX_ASL:,} so'm\n"
        f"✅ {Bepul_Premsoni:,} so'm\n"
        f"🎁 Tejash: {NARX_ASL - Bepul_Premsoni:,} so'm\n\n"
        f"🔥 Faqat {max(0, qolgan)} ta joy qoldi!\n\n"
        f"📲 Olish uchun kontakt yuboring!"
    )

async def foydalanuvchilar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = barcha_users()
    if not users:
        await update.message.reply_text("Hozircha foydalanuvchilar yo'q.")
        return
    text = f"👥 FOYDALANUVCHILAR ({len(users)} kishi)\n━━━━━━━━━━━━━━━━━━\n\n"
    for i, u in enumerate(users[:30], 1):
        name = u[2] or "Anonim"
        un = f"@{u[1]}" if u[1] else ""
        phone = u[3] or "yo'q"
        text += f"{i}. {name} {un}\n📱 {phone}\n/reply_{u[0]}\n\n"
    await update.message.reply_text(text)

async def kontaktlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = barcha_users()
    phones = [u for u in users if u[3]]
    if not phones:
        await update.message.reply_text("Hozircha kontaktlar yo'q.")
        return
    text = f"📋 KONTAKTLAR ({len(phones)} ta)\n━━━━━━━━━━━━━━━━━━\n\n"
    for i, u in enumerate(phones, 1):
        name = u[2] or "Anonim"
        un = f"@{u[1]}" if u[1] else f"ID:{u[0]}"
        text += f"{i}. {name} ({un})\n📱 +{u[3]}\n/reply_{u[0]}\n\n"
    await update.message.reply_text(text)

async def statistika(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jami = jami_users()
    jami_k = jami_kontakt()
    await update.message.reply_text(
        f"📊 STATISTIKA\n━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Jami foydalanuvchilar: {jami}\n"
        f"📱 Kontakt yuborganlar: {jami_k}/{LIMIT}\n"
        f"🔥 Qolgan joylar: {max(0, LIMIT - jami_k)}"
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    broadcast_mode.pop(ADMIN_ID, None)
    reply_mode.pop(ADMIN_ID, None)
    await update.message.reply_text("Bekor qilindi.", reply_markup=get_menyu(update.message.from_user.id))

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.Regex(r'^/reply_\d+$'), reply_command))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID), admin_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_message))
    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
