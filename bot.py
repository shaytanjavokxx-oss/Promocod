import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (Application, CommandHandler, MessageHandler,
                           filters, ContextTypes)
from config import *
from database import *

logging.basicConfig(level=logging.INFO)

broadcast_mode = {}

# ═══════════════════════════════════════
#         MENYULAR
# ═══════════════════════════════════════
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

# ═══════════════════════════════════════
#         /START
# ═══════════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    uid = user.id
    user_qoshish(uid, user.username, user.first_name)

    await update.message.reply_text(
        f"👋 Assalomu alaykum, {user.first_name}!\n\n"
        f"🔥 MAXSUS TAKLIF!\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"💎 Telegram Premium 1 oy\n\n"
        f"~~{NARX_ASL:,} so'm~~ ❌\n"
        f"✅ Atigi {NARX_SKIDKA:,} so'm!\n\n"
        f"🎁 Chegirma: {NARX_ASL - NARX_SKIDKA:,} so'm tejaysiz!\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📲 Yutuqni qo'lga kiritish uchun\n"
        f"telefon raqamingizni yuboring!\n\n"
        f"👇 Pastdagi tugmani bosing:",
        reply_markup=user_menyu() if uid != ADMIN_ID else admin_menyu()
    )

# ═══════════════════════════════════════
#         KONTAKT
# ═══════════════════════════════════════
async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    uid = user.id
    phone = update.message.contact.phone_number
    phone_saqlash(uid, phone)
    name = user.first_name
    username = f"@{user.username}" if user.username else "yo'q"

    # Adminga xabar
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📲 YANGI MIJOZ!\n"
             f"━━━━━━━━━━━━━━━━━━\n\n"
             f"👤 Ism: {name}\n"
             f"📌 Username: {username}\n"
             f"📱 Telefon: +{phone}\n"
             f"🆔 ID: {uid}\n\n"
             f"💬 Bog'lanish uchun:\n"
             f"tg://user?id={uid}"
    )

    await update.message.reply_text(
        f"✅ Rahmat, {name}!\n\n"
        f"📞 Tez orada siz bilan bog'lanamiz\n"
        f"va Telegram Premium ni faollashtirамиз!\n\n"
        f"⏳ Kutish vaqti: 5-30 daqiqa\n\n"
        f"Savollar uchun: {ADMIN_USERNAME}",
        reply_markup=get_menyu(uid)
    )

# ═══════════════════════════════════════
#         SKIDKA HAQIDA
# ═══════════════════════════════════════
async def skidka_haqida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"💎 TELEGRAM PREMIUM 1 OY\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"✨ Premium imkoniyatlari:\n"
        f"• Cheksiz fayl yuklash (4GB)\n"
        f"• Maxsus stikerlar va emoji\n"
        f"• Tezkor yuklab olish\n"
        f"• Reklama yo'q\n"
        f"• Va yana ko'p narsalar!\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 Narx: ~~{NARX_ASL:,}~~ → {NARX_SKIDKA:,} so'm\n"
        f"🎁 Tejash: {NARX_ASL - NARX_SKIDKA:,} so'm\n\n"
        f"📲 Olish uchun kontakt yuboring!"
    )

# ═══════════════════════════════════════
#         SAVOL
# ═══════════════════════════════════════
async def savol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"❓ Savollaringiz uchun:\n\n"
        f"📞 {ADMIN_USERNAME} ga yozing\n\n"
        f"⏰ Ish vaqti: 9:00 - 23:00"
    )

# ═══════════════════════════════════════
#         ADMIN — FOYDALANUVCHILAR
# ═══════════════════════════════════════
async def foydalanuvchilar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    users = barcha_users()
    if not users:
        await update.message.reply_text("Hozircha foydalanuvchilar yo'q.")
        return
    text = f"👥 FOYDALANUVCHILAR ({len(users)} kishi)\n━━━━━━━━━━━━━━━━━━\n\n"
    for i, u in enumerate(users[:30], 1):
        name = u[2] or "Anonim"
        un = f"@{u[1]}" if u[1] else ""
        phone = u[3] or "yo'q"
        text += f"{i}. {name} {un}\n📱 {phone}\n\n"
    if len(users) > 30:
        text += f"... va yana {len(users)-30} kishi"
    await update.message.reply_text(text)

# ═══════════════════════════════════════
#         ADMIN — KONTAKTLAR
# ═══════════════════════════════════════
async def kontaktlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    users = barcha_users()
    phones = [u for u in users if u[3]]
    if not phones:
        await update.message.reply_text("Hozircha kontaktlar yo'q.")
        return
    text = f"📋 KONTAKTLAR ({len(phones)} ta)\n━━━━━━━━━━━━━━━━━━\n\n"
    for i, u in enumerate(phones, 1):
        name = u[2] or "Anonim"
        un = f"@{u[1]}" if u[1] else f"ID:{u[0]}"
        text += f"{i}. {name} ({un})\n📱 +{u[3]}\n\n"
    await update.message.reply_text(text)

# ═══════════════════════════════════════
#         ADMIN — STATISTIKA
# ═══════════════════════════════════════
async def statistika(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    jami = jami_users()
    users = barcha_users()
    phones = len([u for u in users if u[3]])
    await update.message.reply_text(
        f"📊 STATISTIKA\n━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Jami foydalanuvchilar: {jami}\n"
        f"📱 Kontakt yuborganlar: {phones}\n"
        f"❓ Kutayotganlar: {jami - phones}"
    )

# ═══════════════════════════════════════
#         ADMIN — BROADCAST
# ═══════════════════════════════════════
async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    broadcast_mode[ADMIN_ID] = True
    await update.message.reply_text(
        "📢 Xabar yozing — barcha foydalanuvchilarga yuboriladi.\n"
        "Bekor qilish: /cancel"
    )

async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    broadcast_mode[ADMIN_ID] = False
    users = barcha_users()
    text = update.message.text
    ok = 0
    xato = 0
    await update.message.reply_text(f"Yuborilmoqda {len(users)} ta foydalanuvchiga...")
    for u in users:
        try:
            await context.bot.send_message(chat_id=u[0], text=text)
            ok += 1
        except:
            xato += 1
    await update.message.reply_text(
        f"✅ Yuborildi!\nMuvaffaqiyatli: {ok}\nXato: {xato}"
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    broadcast_mode[ADMIN_ID] = False
    await update.message.reply_text("Bekor qilindi.", reply_markup=get_menyu(update.message.from_user.id))

# ═══════════════════════════════════════
#         XABAR HANDLER
# ═══════════════════════════════════════
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    uid = update.message.from_user.id
    text = update.message.text

    if broadcast_mode.get(uid) and uid == ADMIN_ID:
        await broadcast_send(update, context)
        return

    if text == "💎 Skidka haqida":
        await skidka_haqida(update, context)
    elif text == "❓ Savol":
        await savol(update, context)
    elif text == "👥 Foydalanuvchilar" and uid == ADMIN_ID:
        await foydalanuvchilar(update, context)
    elif text == "📊 Statistika" and uid == ADMIN_ID:
        await statistika(update, context)
    elif text == "📢 Xabar yuborish" and uid == ADMIN_ID:
        await broadcast_start(update, context)
    elif text == "📋 Kontaktlar" and uid == ADMIN_ID:
        await kontaktlar(update, context)

# ═══════════════════════════════════════
#         MAIN
# ═══════════════════════════════════════
def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("✅ Skidka Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
