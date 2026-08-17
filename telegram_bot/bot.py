import os
from datetime import datetime

from decouple import config
import telebot
from telebot import types
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.core.files.base import ContentFile

from shop.models import Category, MenuItem, Chef, Order, OrderItem, UserProfile, Reservation

BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = config("TELEGRAM_ADMIN_CHAT_ID", default="")
MINIAPP_URL = config("TELEGRAM_MINIAPP_URL", default="")

bot = telebot.TeleBot(BOT_TOKEN)

CANCELLABLE_STATUSES = ["new", "confirmed", "preparing"]
WORKING_HOURS = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00",
                 "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00"]

# Vaqtincha ma'lumot saqlash (chat_id bo'yicha)
checkout_data = {}
reservation_data = {}


# ═══════════════════════════════════════════════════════════════
#  YORDAMCHI FUNKSIYALAR
# ═══════════════════════════════════════════════════════════════
def get_profile_by_chat(chat_id):
    return UserProfile.objects.filter(telegram_chat_id=chat_id).first()


def is_admin(profile):
    return profile and (profile.user.is_staff or profile.user.is_superuser)


def main_menu_markup(profile):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🍽 Menyu", "📦 Buyurtmalarim")
    markup.add("👨‍🍳 Oshpazlar", "👤 Profilim")
    markup.add("📅 Stol bron qilish", "🗓 Bronlarim")
    if is_admin(profile):
        markup.add("⚙️ Admin panel")
    markup.add("🚪 Chiqish")
    return markup


def guest_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📝 Ro'yxatdan o'tish", "🔑 Kirish")
    return markup


# ═══════════════════════════════════════════════════════════════
#  /start
# ═══════════════════════════════════════════════════════════════


def cancel_if_menu_command(message):
    text = message.text or ""
    menu_commands = {
        "🍽 Menyu": menu_handler,
        "📦 Buyurtmalarim": my_orders_handler,
        "👨‍🍳 Oshpazlar": chefs_handler,
        "👤 Profilim": profile_handler,
        "📅 Stol bron qilish": reservation_start,
        "🗓 Bronlarim": my_reservations_handler,
        "⚙️ Admin panel": admin_panel_handler,
        "🚪 Chiqish": logout_handler,
        "📝 Ro'yxatdan o'tish": register_start,
        "🔑 Kirish": login_start,
    }
    if text in menu_commands:
        menu_commands[text](message)
        return True
    if text.startswith("/"):
        if text.startswith("/start"):
            start_handler(message)
        return True
    return False


def guarded_step(func):
    def wrapper(message, *args, **kwargs):
        if cancel_if_menu_command(message):
            return
        return func(message, *args, **kwargs)
    return wrapper



@bot.message_handler(commands=["start"])
def start_handler(message):
    profile = get_profile_by_chat(message.chat.id)

    webapp_markup = None
    if MINIAPP_URL:
        webapp_markup = types.InlineKeyboardMarkup()
        webapp_markup.add(
            types.InlineKeyboardButton(
                "🍽️ Ilovani ochish",
                web_app=types.WebAppInfo(url=MINIAPP_URL)
            )
        )

    if profile:
        bot.send_message(
            message.chat.id,
            f"👋 Xush kelibsiz, <b>{profile.user.first_name or profile.user.username}</b>!\n"
            f"Sarab Restaurant botiga qaytganingizdan xursandmiz 🍔🎉",
            parse_mode="HTML",
            reply_markup=webapp_markup or main_menu_markup(profile),
        )
    else:
        bot.send_message(
            message.chat.id,
            "👋 Assalomu alaykum! <b>Sarab Restaurant</b> botiga xush kelibsiz 🍽️\n\n"
            "Quyidagi tugma orqali ilovani oching yoki ro'yxatdan o'ting:",
            parse_mode="HTML",
            reply_markup=webapp_markup or guest_menu_markup(),
        )

    if webapp_markup:
        bot.send_message(
            message.chat.id,
            "Yoki quyidagi oddiy menyudan foydalaning:",
            reply_markup=main_menu_markup(profile) if profile else guest_menu_markup(),
        )

# ═══════════════════════════════════════════════════════════════
#  🚪 CHIQISH
# ═══════════════════════════════════════════════════════════════
@bot.message_handler(func=lambda m: m.text == "🚪 Chiqish")
def logout_handler(message):
    profile = get_profile_by_chat(message.chat.id)
    if not profile:
        bot.send_message(message.chat.id, "Siz hali kirmagansiz.", reply_markup=guest_menu_markup())
        return

    profile.telegram_chat_id = None
    profile.save()
    bot.send_message(
        message.chat.id,
        "🚪 Tizimdan chiqdingiz. Qayta kirish uchun /start bosing.",
        reply_markup=types.ReplyKeyboardRemove(),
    )


# ═══════════════════════════════════════════════════════════════
#  RO'YXATDAN O'TISH
# ═══════════════════════════════════════════════════════════════
@bot.message_handler(func=lambda m: m.text == "📝 Ro'yxatdan o'tish")
def register_start(message):
    if get_profile_by_chat(message.chat.id):
        bot.send_message(message.chat.id, "Siz allaqachon ro'yxatdan o'tgansiz ✅")
        return
    msg = bot.send_message(message.chat.id, "👤 Ismingiz va familiyangizni yuboring (masalan: Aliyev Vali):")
    bot.register_next_step_handler(msg, register_get_fullname)

@guarded_step
def register_get_fullname(message):
    data = {"full_name": message.text.strip()}
    msg = bot.send_message(message.chat.id, "📱 Telefon raqamingizni yuboring (masalan: +998901234567):")
    bot.register_next_step_handler(msg, register_get_phone, data)

@guarded_step
def register_get_phone(message, data):
    data["phone"] = message.text.strip()
    msg = bot.send_message(message.chat.id, "🏠 Yashash manzilingizni yuboring:")
    bot.register_next_step_handler(msg, register_get_address, data)

@guarded_step
def register_get_address(message, data):
    data["address"] = message.text.strip()
    msg = bot.send_message(message.chat.id, "🔑 O'zingizga username (login) o'ylab yuboring:")
    bot.register_next_step_handler(msg, register_get_username, data)

@guarded_step
def register_get_username(message, data):
    username = message.text.strip()
    if User.objects.filter(username=username).exists():
        msg = bot.send_message(message.chat.id, "❗ Bu username band. Boshqa username yuboring:")
        bot.register_next_step_handler(msg, register_get_username, data)
        return
    data["username"] = username
    msg = bot.send_message(message.chat.id, "🔒 Parol o'ylab yuboring (kamida 6 ta belgi):")
    bot.register_next_step_handler(msg, register_get_password, data)

@guarded_step
def register_get_password(message, data):
    password = message.text.strip()
    if len(password) < 6:
        msg = bot.send_message(message.chat.id, "❗ Parol juda qisqa. Kamida 6 ta belgidan iborat parol yuboring:")
        bot.register_next_step_handler(msg, register_get_password, data)
        return

    full_name_parts = data["full_name"].split(" ", 1)
    first_name = full_name_parts[0]
    last_name = full_name_parts[1] if len(full_name_parts) > 1 else ""

    user = User.objects.create(
        username=data["username"],
        first_name=first_name,
        last_name=last_name,
        password=make_password(password),
    )
    UserProfile.objects.create(
        user=user,
        phone=data["phone"],
        address=data["address"],
        telegram_chat_id=message.chat.id,
    )

    profile = UserProfile.objects.get(user=user)
    bot.send_message(
        message.chat.id,
        f"🎉 Tabriklaymiz, <b>{first_name}</b>! Ro'yxatdan muvaffaqiyatli o'tdingiz.\n"
        f"Endi buyurtma berishingiz mumkin 🍔✅",
        parse_mode="HTML",
        reply_markup=main_menu_markup(profile),
    )


# ═══════════════════════════════════════════════════════════════
#  KIRISH
# ═══════════════════════════════════════════════════════════════
@bot.message_handler(func=lambda m: m.text == "🔑 Kirish")
def login_start(message):
    msg = bot.send_message(message.chat.id, "👤 Username kiriting:")
    bot.register_next_step_handler(msg, login_get_username)

@guarded_step
def login_get_username(message):
    username = message.text.strip()
    user = User.objects.filter(username=username).first()
    if not user:
        msg = bot.send_message(message.chat.id, "❗ Bunday username topilmadi. Qaytadan urinib ko'ring:")
        bot.register_next_step_handler(msg, login_get_username)
        return
    msg = bot.send_message(message.chat.id, "🔒 Parolingizni kiriting:")
    bot.register_next_step_handler(msg, login_get_password, username)

@guarded_step
def login_get_password(message, username):
    user = User.objects.filter(username=username).first()
    if not check_password(message.text.strip(), user.password):
        msg = bot.send_message(message.chat.id, "❗ Parol noto'g'ri. Qaytadan urinib ko'ring:")
        bot.register_next_step_handler(msg, login_get_password, username)
        return

    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.telegram_chat_id = message.chat.id
    profile.save()

    bot.send_message(
        message.chat.id,
        f"✅ Xush kelibsiz, <b>{user.first_name or user.username}</b>!",
        parse_mode="HTML",
        reply_markup=main_menu_markup(profile),
    )


# ═══════════════════════════════════════════════════════════════
#  🍽 MENYU → KATEGORIYA → TAOM → TO'LIQ MA'LUMOT → BUYURTMA BERISH
# ═══════════════════════════════════════════════════════════════
@bot.message_handler(func=lambda m: m.text == "🍽 Menyu")
def menu_handler(message):
    categories = Category.objects.all().order_by("order")
    if not categories:
        bot.send_message(message.chat.id, "😔 Hozircha kategoriyalar qo'shilmagan.")
        return

    markup = types.InlineKeyboardMarkup()
    for cat in categories:
        markup.add(types.InlineKeyboardButton(f"📂 {cat.name}", callback_data=f"cat_{cat.id}"))

    bot.send_message(message.chat.id, "🍽️ <b>Kategoriyani tanlang:</b>", parse_mode="HTML", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def category_items_handler(call):
    category_id = call.data.replace("cat_", "")
    items = MenuItem.objects.filter(category_id=category_id, is_available=True)

    if not items:
        bot.answer_callback_query(call.id, "Bu kategoriyada hozircha taom yo'q.")
        return

    bot.answer_callback_query(call.id)

    markup = types.InlineKeyboardMarkup()
    for item in items:
        markup.add(types.InlineKeyboardButton(f"🍴 {item.name} — {item.price} so'm", callback_data=f"item_{item.id}"))

    bot.send_message(call.message.chat.id, "Taomni tanlang:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("item_"))
def item_detail_handler(call):
    item_id = call.data.replace("item_", "")
    item = MenuItem.objects.filter(id=item_id).first()

    if not item:
        bot.answer_callback_query(call.id, "Taom topilmadi.")
        return

    bot.answer_callback_query(call.id)

    badge_emojis = {"hot": "🔥", "new": "✨", "bestseller": "⭐", "chefs_pick": "👨‍🍳"}
    badge = badge_emojis.get(item.badge, "")

    caption = (
        f"{badge} <b>{item.name}</b>\n\n"
        f"{item.description}\n\n"
        f"💵 Narx: <b>{item.price} so'm</b>\n"
        f"⭐ Reyting: {item.rating} ({item.review_count} sharh)\n"
        f"🔥 Kaloriya: {item.calories}\n"
        f"⏱ Tayyorlanish vaqti: {item.prep_time} daqiqa"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛒 Buyurtma berish", callback_data=f"order_{item.id}"))

    try:
        if item.image and os.path.exists(item.image.path):
            with open(item.image.path, "rb") as photo:
                bot.send_photo(call.message.chat.id, photo, caption=caption, parse_mode="HTML", reply_markup=markup)
                return
    except Exception:
        pass
    bot.send_message(call.message.chat.id, caption, parse_mode="HTML", reply_markup=markup)


# ═══════════════════════════════════════════════════════════════
#  BUYURTMA BERISH (checkout)
# ═══════════════════════════════════════════════════════════════
@bot.callback_query_handler(func=lambda call: call.data.startswith("order_"))
def order_start_handler(call):
    profile = get_profile_by_chat(call.message.chat.id)
    if not profile:
        bot.answer_callback_query(call.id, "Avval ro'yxatdan o'ting yoki kiring.")
        bot.send_message(call.message.chat.id, "❗ Buyurtma berish uchun avval tizimga kiring.", reply_markup=guest_menu_markup())
        return

    item = MenuItem.objects.filter(id=call.data.replace("order_", "")).first()
    if not item:
        bot.answer_callback_query(call.id, "Taom topilmadi.")
        return

    bot.answer_callback_query(call.id)

    checkout_data[call.message.chat.id] = {
        "menu_item_id": item.id,
        "full_name": f"{profile.user.first_name} {profile.user.last_name}".strip(),
        "phone": profile.phone,
        "address": profile.address,
    }

    msg = bot.send_message(
        call.message.chat.id,
        f"🛒 <b>{item.name}</b> — nechta dona buyurtma qilmoqchisiz?",
        parse_mode="HTML",
    )
    bot.register_next_step_handler(msg, checkout_get_quantity)

@guarded_step
def checkout_get_quantity(message):
    if not message.text.strip().isdigit() or int(message.text.strip()) < 1:
        msg = bot.send_message(message.chat.id, "❗ Iltimos, musbat son kiriting (masalan: 2):")
        bot.register_next_step_handler(msg, checkout_get_quantity)
        return

    data = checkout_data.get(message.chat.id)
    data["quantity"] = int(message.text.strip())

    msg = bot.send_message(
        message.chat.id,
        f"👤 Qabul qiluvchi ismi (hozirgi: {data['full_name']}).\n"
        f"O'zgartirmoqchi bo'lmasangiz, xuddi shu ismni qayta yuboring:",
    )
    bot.register_next_step_handler(msg, checkout_get_fullname)

@guarded_step
def checkout_get_fullname(message):
    data = checkout_data.get(message.chat.id)
    data["full_name"] = message.text.strip()
    msg = bot.send_message(message.chat.id, f"📱 Telefon raqami (hozirgi: {data['phone']}):")
    bot.register_next_step_handler(msg, checkout_get_phone)

@guarded_step
def checkout_get_phone(message):
    data = checkout_data.get(message.chat.id)
    data["phone"] = message.text.strip()
    msg = bot.send_message(message.chat.id, f"🏠 Yetkazib berish manzili (hozirgi: {data['address']}):")
    bot.register_next_step_handler(msg, checkout_get_address)

@guarded_step
def checkout_get_address(message):
    data = checkout_data.get(message.chat.id)
    data["address"] = message.text.strip()
    msg = bot.send_message(message.chat.id, "💬 Buyurtmaga izoh (bo'lmasa \"yo'q\" deb yozing):")
    bot.register_next_step_handler(msg, checkout_get_comment)

@guarded_step
def checkout_get_comment(message):
    data = checkout_data.get(message.chat.id)
    data["comment"] = "" if message.text.strip().lower() in ("yo'q", "yoq") else message.text.strip()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💵 Naqd pul", callback_data="pay_cash"))
    markup.add(types.InlineKeyboardButton("💳 Karta (Payme/Click)", callback_data="pay_card"))
    bot.send_message(message.chat.id, "💰 To'lov usulini tanlang:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_"))
def checkout_finish_handler(call):
    data = checkout_data.get(call.message.chat.id)
    if not data:
        bot.answer_callback_query(call.id, "Xatolik: buyurtma ma'lumotlari topilmadi. Qaytadan boshlang.")
        return

    payment_method = "cash" if call.data == "pay_cash" else "card"
    profile = get_profile_by_chat(call.message.chat.id)
    item = MenuItem.objects.filter(id=data["menu_item_id"]).first()

    if not item:
        bot.answer_callback_query(call.id, "Xatolik: taom topilmadi.")
        return

    total = item.price * data["quantity"]

    order = Order.objects.create(
        user=profile.user,
        full_name=data["full_name"],
        phone=data["phone"],
        address=data["address"],
        comment=data["comment"],
        payment_method=payment_method,
        total_price=total,
        status="new",
    )
    OrderItem.objects.create(
        order=order,
        menu_item=item,
        item_name=item.name,
        item_price=item.price,
        quantity=data["quantity"],
    )

    bot.answer_callback_query(call.id, "Buyurtma qabul qilindi! ✅")
    bot.send_message(
        call.message.chat.id,
        f"✅ <b>Buyurtmangiz rasmiylashtirildi!</b>\n\n"
        f"📦 Buyurtma #{order.id}\n"
        f"🍴 {item.name} x {data['quantity']}\n"
        f"💵 Umumiy narx: {total} so'm\n"
        f"📍 Manzil: {data['address']}\n\n"
        f"Tez orada siz bilan bog'lanamiz 🎉",
        parse_mode="HTML",
        reply_markup=main_menu_markup(profile),
    )

    notify_admin_new_order(order)
    checkout_data.pop(call.message.chat.id, None)


# ═══════════════════════════════════════════════════════════════
#  📦 BUYURTMALARIM
# ═══════════════════════════════════════════════════════════════
@bot.message_handler(func=lambda m: m.text == "📦 Buyurtmalarim")
def my_orders_handler(message):
    profile = get_profile_by_chat(message.chat.id)
    if not profile:
        bot.send_message(message.chat.id, "❗ Avval ro'yxatdan o'ting yoki kiring.", reply_markup=guest_menu_markup())
        return

    orders = Order.objects.filter(user=profile.user).exclude(status="cancelled").order_by("-created_at")[:10]
    if not orders:
        bot.send_message(message.chat.id, "📭 Sizda faol buyurtmalar yo'q.")
        return

    markup = types.InlineKeyboardMarkup()
    for order in orders:
        markup.add(types.InlineKeyboardButton(
            f"#{order.id} — {order.get_status_display()}",
            callback_data=f"vieworder_{order.id}"
        ))
    bot.send_message(message.chat.id, "📦 <b>Sizning faol buyurtmalaringiz:</b>", parse_mode="HTML", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("vieworder_"))
def view_order_handler(call):
    order = Order.objects.filter(id=call.data.replace("vieworder_", "")).first()
    if not order:
        bot.answer_callback_query(call.id, "Buyurtma topilmadi.")
        return

    profile = get_profile_by_chat(call.message.chat.id)

    text = (
        f"📦 <b>Buyurtma #{order.id}</b>\n"
        f"Holati: {order.get_status_display()}\n"
        f"Umumiy narx: <b>{order.total_price} so'm</b>\n\n"
        f"<b>Tarkibi:</b>\n"
    )
    for item in order.items.all():
        text += f"• {item.item_name} x {item.quantity} — {item.total_price} so'm\n"

    markup = types.InlineKeyboardMarkup()
    if order.status in CANCELLABLE_STATUSES:
        markup.add(types.InlineKeyboardButton("❌ Bekor qilish", callback_data=f"cancel_{order.id}"))
    if is_admin(profile):
        markup.add(types.InlineKeyboardButton("🗑 O'chirish (admin)", callback_data=f"delorder_{order.id}"))

    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text, parse_mode="HTML", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_"))
def cancel_order_handler(call):
    order = Order.objects.filter(id=call.data.replace("cancel_", "")).first()

    if not order:
        bot.answer_callback_query(call.id, "Buyurtma topilmadi.")
        return
    if order.status not in CANCELLABLE_STATUSES:
        bot.answer_callback_query(call.id, "Bu buyurtmani endi bekor qilib bo'lmaydi.")
        return

    order.status = "cancelled"
    order.save()

    bot.answer_callback_query(call.id, "Buyurtma bekor qilindi.")
    bot.edit_message_text(
        f"❌ <b>Buyurtma #{order.id} bekor qilindi.</b>",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML",
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("delorder_"))
def delete_order_handler(call):
    profile = get_profile_by_chat(call.message.chat.id)
    if not is_admin(profile):
        bot.answer_callback_query(call.id, "Ruxsat yo'q.")
        return

    order = Order.objects.filter(id=call.data.replace("delorder_", "")).first()
    if not order:
        bot.answer_callback_query(call.id, "Buyurtma topilmadi.")
        return

    order_id = order.id
    order.delete()
    bot.answer_callback_query(call.id, "Buyurtma o'chirildi.")
    bot.edit_message_text(
        f"🗑 <b>Buyurtma #{order_id} butunlay o'chirildi.</b>",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML",
    )


# ═══════════════════════════════════════════════════════════════
#  📅 STOL BRON QILISH
# ═══════════════════════════════════════════════════════════════
@bot.message_handler(func=lambda m: m.text == "📅 Stol bron qilish")
def reservation_start(message):
    profile = get_profile_by_chat(message.chat.id)
    if not profile:
        bot.send_message(message.chat.id, "❗ Avval ro'yxatdan o'ting yoki kiring.", reply_markup=guest_menu_markup())
        return

    reservation_data[message.chat.id] = {}
    msg = bot.send_message(
        message.chat.id,
        "📅 Bron qilmoqchi bo'lgan sanani kiriting.\n"
        "Format: <b>kun.oy.yil</b> (masalan: 25.07.2026)",
        parse_mode="HTML",
    )
    bot.register_next_step_handler(msg, reservation_get_date)

@guarded_step
def reservation_get_date(message):
    text = message.text.strip()
    try:
        date_obj = datetime.strptime(text, "%d.%m.%Y").date()
    except ValueError:
        msg = bot.send_message(message.chat.id, "❗ Sana formati noto'g'ri. Masalan: 25.07.2026 ko'rinishida yuboring:")
        bot.register_next_step_handler(msg, reservation_get_date)
        return

    if date_obj < datetime.now().date():
        msg = bot.send_message(message.chat.id, "❗ O'tgan sanani tanlab bo'lmaydi. Qaytadan kiriting:")
        bot.register_next_step_handler(msg, reservation_get_date)
        return

    reservation_data[message.chat.id]["date"] = date_obj
    show_available_times(message.chat.id, date_obj)


def show_available_times(chat_id, date_obj):
    booked_times = set(Reservation.objects.filter(date=date_obj).values_list("time", flat=True))
    booked_times_str = {t.strftime("%H:%M") for t in booked_times}

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    for slot in WORKING_HOURS:
        if slot in booked_times_str:
            buttons.append(types.InlineKeyboardButton(f"🔴 {slot}", callback_data="slot_taken"))
        else:
            buttons.append(types.InlineKeyboardButton(f"🟢 {slot}", callback_data=f"slot_{slot}"))
    markup.add(*buttons)

    bot.send_message(
        chat_id,
        f"📅 <b>{date_obj.strftime('%d.%m.%Y')}</b> kuni uchun bo'sh vaqtlar:\n"
        f"🟢 — bo'sh   🔴 — band",
        parse_mode="HTML",
        reply_markup=markup,
    )


@bot.callback_query_handler(func=lambda call: call.data == "slot_taken")
def slot_taken_handler(call):
    bot.answer_callback_query(call.id, "❗ Bu vaqt band. Boshqa vaqtni tanlang.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("slot_") and call.data != "slot_taken")
def slot_selected_handler(call):
    time_str = call.data.replace("slot_", "")
    data = reservation_data.get(call.message.chat.id)

    if not data or "date" not in data:
        bot.answer_callback_query(call.id, "Xatolik. Qaytadan /start bosing.")
        return

    time_obj = datetime.strptime(time_str, "%H:%M").time()
    already_taken = Reservation.objects.filter(date=data["date"], time=time_obj).exists()
    if already_taken:
        bot.answer_callback_query(call.id, "❗ Afsuski, bu vaqtni boshqa mijoz band qilib ulgurdi.")
        show_available_times(call.message.chat.id, data["date"])
        return

    data["time"] = time_obj
    bot.answer_callback_query(call.id)

    markup = types.InlineKeyboardMarkup()
    for value, label in Reservation.GUEST_CHOICES:
        markup.add(types.InlineKeyboardButton(label, callback_data=f"guests_{value}"))
    bot.send_message(call.message.chat.id, "👥 Nechta kishi bo'lasiz?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("guests_"))
def reservation_get_guests(call):
    guests_value = call.data.replace("guests_", "")
    data = reservation_data.get(call.message.chat.id)
    if not data:
        bot.answer_callback_query(call.id, "Xatolik. Qaytadan /start bosing.")
        return

    data["guests"] = guests_value
    bot.answer_callback_query(call.id)

    msg = bot.send_message(call.message.chat.id, "💬 Maxsus so'rovlaringiz bormi? (bo'lmasa \"yo'q\" deb yozing):")
    bot.register_next_step_handler(msg, reservation_get_requests)


@guarded_step
def reservation_get_requests(message):
    data = reservation_data.get(message.chat.id)
    if not data:
        bot.send_message(message.chat.id, "Xatolik. Qaytadan /start bosing.")
        return

    special_requests = "" if message.text.strip().lower() in ("yo'q", "yoq") else message.text.strip()
    profile = get_profile_by_chat(message.chat.id)

    if Reservation.objects.filter(date=data["date"], time=data["time"]).exists():
        bot.send_message(message.chat.id, "❗ Afsuski, bu vaqt band bo'lib qoldi. Qaytadan /start orqali urinib ko'ring.")
        reservation_data.pop(message.chat.id, None)
        return

    reservation = Reservation.objects.create(
        full_name=f"{profile.user.first_name} {profile.user.last_name}".strip(),
        phone=profile.phone,
        email=profile.user.email or "no-email@example.com",
        guests=data["guests"],
        date=data["date"],
        time=data["time"],
        special_requests=special_requests,
        is_confirmed=False,
    )

    bot.send_message(
        message.chat.id,
        f"✅ <b>Bron qabul qilindi!</b>\n\n"
        f"📅 Sana: {reservation.date.strftime('%d.%m.%Y')}\n"
        f"⏰ Vaqt: {reservation.time.strftime('%H:%M')}\n"
        f"👥 Mehmonlar: {reservation.get_guests_display()}\n\n"
        f"Tez orada tasdiqlaymiz 🎉",
        parse_mode="HTML",
        reply_markup=main_menu_markup(profile),
    )

    notify_admin_new_reservation(reservation)
    reservation_data.pop(message.chat.id, None)


def notify_admin_new_reservation(reservation):
    if not ADMIN_CHAT_ID:
        return
    try:
        bot.send_message(
            ADMIN_CHAT_ID,
            f"📅 <b>Yangi stol broni!</b>\n"
            f"{reservation.full_name} — {reservation.date.strftime('%d.%m.%Y')} {reservation.time.strftime('%H:%M')}\n"
            f"👥 {reservation.get_guests_display()}",
            parse_mode="HTML",
        )
    except Exception as e:
        print(f"Adminga xabar yuborilmadi: {e}")

# ═══════════════════════════════════════════════════════════════
#  🗓 BRONLARIM
# ═══════════════════════════════════════════════════════════════
@bot.message_handler(func=lambda m: m.text == "🗓 Bronlarim")
def my_reservations_handler(message):
    profile = get_profile_by_chat(message.chat.id)
    if not profile:
        bot.send_message(message.chat.id, "❗ Avval ro'yxatdan o'ting yoki kiring.", reply_markup=guest_menu_markup())
        return

    reservations = Reservation.objects.filter(
        phone=profile.phone, date__gte=datetime.now().date()
    ).order_by("date", "time")

    if not reservations:
        bot.send_message(message.chat.id, "📭 Sizda faol bronlar yo'q.")
        return

    markup = types.InlineKeyboardMarkup()
    for r in reservations:
        status = "✅" if r.is_confirmed else "⏳"
        markup.add(types.InlineKeyboardButton(
            f"{status} {r.date.strftime('%d.%m.%Y')} {r.time.strftime('%H:%M')} — {r.get_guests_display()}",
            callback_data=f"viewres_{r.id}"
        ))
    bot.send_message(message.chat.id, "🗓 <b>Sizning bronlaringiz:</b>", parse_mode="HTML", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("viewres_"))
def view_reservation_handler(call):
    reservation = Reservation.objects.filter(id=call.data.replace("viewres_", "")).first()
    if not reservation:
        bot.answer_callback_query(call.id, "Bron topilmadi.")
        return

    text = (
        f"📅 <b>Bron</b>\n"
        f"Sana: {reservation.date.strftime('%d.%m.%Y')}\n"
        f"Vaqt: {reservation.time.strftime('%H:%M')}\n"
        f"Mehmonlar: {reservation.get_guests_display()}\n"
        f"Holati: {'✅ Tasdiqlangan' if reservation.is_confirmed else '⏳ Kutilmoqda'}\n"
    )
    if reservation.special_requests:
        text += f"So'rov: {reservation.special_requests}\n"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Bekor qilish", callback_data=f"cancelres_{reservation.id}"))

    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text, parse_mode="HTML", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cancelres_"))
def cancel_reservation_handler(call):
    reservation = Reservation.objects.filter(id=call.data.replace("cancelres_", "")).first()
    if not reservation:
        bot.answer_callback_query(call.id, "Bron topilmadi.")
        return

    reservation.delete()
    bot.answer_callback_query(call.id, "Bron bekor qilindi.")
    bot.edit_message_text(
        "❌ <b>Bron bekor qilindi.</b>",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML",
    )


# ═══════════════════════════════════════════════════════════════
#  👨‍🍳 OSHPAZLAR
# ═══════════════════════════════════════════════════════════════
@bot.message_handler(func=lambda m: m.text == "👨‍🍳 Oshpazlar")
def chefs_handler(message):
    chefs = Chef.objects.all().order_by("order")
    if not chefs:
        bot.send_message(message.chat.id, "😔 Hozircha oshpazlar qo'shilmagan.")
        return

    for chef in chefs:
        caption = f"👨‍🍳 <b>{chef.name}</b>\n{chef.role}\n🏅 Tajriba: {chef.experience} yil"
        try:
            if chef.photo and os.path.exists(chef.photo.path):
                with open(chef.photo.path, "rb") as photo:
                    bot.send_photo(message.chat.id, photo, caption=caption, parse_mode="HTML")
                    continue
        except Exception:
            pass
        bot.send_message(message.chat.id, caption, parse_mode="HTML")


# ═══════════════════════════════════════════════════════════════
#  👤 PROFILIM
# ═══════════════════════════════════════════════════════════════
@bot.message_handler(func=lambda m: m.text == "👤 Profilim")
def profile_handler(message):
    profile = get_profile_by_chat(message.chat.id)
    if not profile:
        bot.send_message(message.chat.id, "❗ Avval ro'yxatdan o'ting.", reply_markup=guest_menu_markup())
        return

    bot.send_message(
        message.chat.id,
        f"👤 <b>{profile.user.first_name} {profile.user.last_name}</b>\n"
        f"📱 {profile.phone}\n"
        f"🏠 {profile.address}",
        parse_mode="HTML",
    )


# ═══════════════════════════════════════════════════════════════
#  ⚙️ ADMIN PANEL
# ═══════════════════════════════════════════════════════════════
@bot.message_handler(func=lambda m: m.text == "⚙️ Admin panel")
def admin_panel_handler(message):
    profile = get_profile_by_chat(message.chat.id)
    if not is_admin(profile):
        bot.send_message(message.chat.id, "❗ Sizda admin huquqi yo'q.")
        return

    active_orders = Order.objects.exclude(status="cancelled").count()
    upcoming_reservations = Reservation.objects.filter(date__gte=datetime.now().date()).count()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ Mahsulot qo'shish", callback_data="admin_add_item"))
    markup.add(types.InlineKeyboardButton("➕ Kategoriya qo'shish", callback_data="admin_add_category"))
    markup.add(types.InlineKeyboardButton("➕ Oshpaz qo'shish", callback_data="admin_add_chef"))
    markup.add(types.InlineKeyboardButton(f"📋 Buyurtmalar ({active_orders})", callback_data="admin_all_orders"))
    markup.add(types.InlineKeyboardButton(f"📅 Bronlar ({upcoming_reservations})", callback_data="admin_all_reservations"))
    bot.send_message(message.chat.id, "⚙️ <b>Admin panel</b>", parse_mode="HTML", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "admin_add_category")
def admin_add_category_start(call):
    profile = get_profile_by_chat(call.message.chat.id)
    if not is_admin(profile):
        bot.answer_callback_query(call.id, "Ruxsat yo'q.")
        return
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "📂 Kategoriya nomini kiriting:")
    bot.register_next_step_handler(msg, admin_add_category_name)


@guarded_step
def admin_add_category_name(message):
    name = message.text.strip()
    slug = name.lower().replace(" ", "-")
    order = Category.objects.count()
    Category.objects.create(name=name, slug=slug, order=order)
    bot.send_message(message.chat.id, f"✅ <b>{name}</b> kategoriyasi qo'shildi.", parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data == "admin_add_chef")
def admin_add_chef_start(call):
    profile = get_profile_by_chat(call.message.chat.id)
    if not is_admin(profile):
        bot.answer_callback_query(call.id, "Ruxsat yo'q.")
        return
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "👨‍🍳 Oshpazning to'liq ismini kiriting:")
    bot.register_next_step_handler(msg, admin_chef_get_name)


@guarded_step
def admin_chef_get_name(message):
    data = {"name": message.text.strip()}
    msg = bot.send_message(message.chat.id, "💼 Lavozimini kiriting (masalan: Head Chef):")
    bot.register_next_step_handler(msg, admin_chef_get_role, data)


@guarded_step
def admin_chef_get_role(message, data):
    data["role"] = message.text.strip()
    msg = bot.send_message(message.chat.id, "🏅 Tajribasini yil bilan kiriting (masalan: 5):")
    bot.register_next_step_handler(msg, admin_chef_get_experience, data)


@guarded_step
def admin_chef_get_experience(message, data):
    if not message.text.strip().isdigit():
        msg = bot.send_message(message.chat.id, "❗ Faqat son kiriting:")
        bot.register_next_step_handler(msg, admin_chef_get_experience, data)
        return
    data["experience"] = int(message.text.strip())
    order = Chef.objects.count()
    Chef.objects.create(name=data["name"], role=data["role"], experience=data["experience"], order=order)
    bot.send_message(message.chat.id, f"✅ Oshpaz <b>{data['name']}</b> qo'shildi.", parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data == "admin_add_item")
def admin_add_item_start(call):
    profile = get_profile_by_chat(call.message.chat.id)
    if not is_admin(profile):
        bot.answer_callback_query(call.id, "Ruxsat yo'q.")
        return

    categories = Category.objects.all()
    if not categories:
        bot.answer_callback_query(call.id, "Avval kategoriya qo'shing.")
        return

    bot.answer_callback_query(call.id)
    markup = types.InlineKeyboardMarkup()
    for cat in categories:
        markup.add(types.InlineKeyboardButton(cat.name, callback_data=f"admincat_{cat.id}"))
    bot.send_message(call.message.chat.id, "📂 Qaysi kategoriyaga qo'shmoqchisiz?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("admincat_"))
@guarded_step
def admin_item_get_category(call):
    category_id = call.data.replace("admincat_", "")
    data = {"category_id": category_id}
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "🍴 Taom nomini kiriting:")
    bot.register_next_step_handler(msg, admin_item_get_name, data)

@guarded_step
def admin_item_get_name(message, data):
    data["name"] = message.text.strip()
    msg = bot.send_message(message.chat.id, "📝 Tavsifini kiriting:")
    bot.register_next_step_handler(msg, admin_item_get_description, data)

@guarded_step
def admin_item_get_description(message, data):
    data["description"] = message.text.strip()
    msg = bot.send_message(message.chat.id, "💵 Narxini kiriting (faqat son, masalan: 25000):")
    bot.register_next_step_handler(msg, admin_item_get_price, data)

@guarded_step
def admin_item_get_price(message, data):
    try:
        data["price"] = float(message.text.strip())
    except ValueError:
        msg = bot.send_message(message.chat.id, "❗ Iltimos, faqat son kiriting:")
        bot.register_next_step_handler(msg, admin_item_get_price, data)
        return
    msg = bot.send_message(message.chat.id, "🖼 Taom rasmini yuboring:")
    bot.register_next_step_handler(msg, admin_item_get_photo, data)

@guarded_step
def admin_item_get_photo(message, data):
    if not message.photo:
        msg = bot.send_message(message.chat.id, "❗ Iltimos, rasm yuboring:")
        bot.register_next_step_handler(msg, admin_item_get_photo, data)
        return

    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded = bot.download_file(file_info.file_path)

    item = MenuItem.objects.create(
        category_id=data["category_id"],
        name=data["name"],
        description=data["description"],
        price=data["price"],
    )
    file_name = f"menu_{item.id}.jpg"
    item.image.save(file_name, ContentFile(downloaded), save=True)

    bot.send_message(message.chat.id, f"✅ <b>{item.name}</b> menyuga qo'shildi!", parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data == "admin_all_orders")
def admin_all_orders_handler(call):
    profile = get_profile_by_chat(call.message.chat.id)
    if not is_admin(profile):
        bot.answer_callback_query(call.id, "Ruxsat yo'q.")
        return

    bot.answer_callback_query(call.id)
    orders = Order.objects.exclude(status="cancelled").order_by("-created_at")[:15]
    if not orders:
        bot.send_message(call.message.chat.id, "📭 Hozircha faol buyurtmalar yo'q.")
        return

    markup = types.InlineKeyboardMarkup()
    for order in orders:
        markup.add(types.InlineKeyboardButton(
            f"#{order.id} — {order.full_name} — {order.get_status_display()}",
            callback_data=f"vieworder_{order.id}"
        ))
    bot.send_message(call.message.chat.id, "📋 <b>Barcha faol buyurtmalar:</b>", parse_mode="HTML", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "admin_all_reservations")
def admin_all_reservations_handler(call):
    profile = get_profile_by_chat(call.message.chat.id)
    if not is_admin(profile):
        bot.answer_callback_query(call.id, "Ruxsat yo'q.")
        return

    bot.answer_callback_query(call.id)
    reservations = Reservation.objects.filter(date__gte=datetime.now().date()).order_by("date", "time")[:15]
    if not reservations:
        bot.send_message(call.message.chat.id, "📭 Hozircha bronlar yo'q.")
        return

    markup = types.InlineKeyboardMarkup()
    for r in reservations:
        status = "✅" if r.is_confirmed else "⏳"
        markup.add(types.InlineKeyboardButton(
            f"{status} {r.date.strftime('%d.%m.%Y')} {r.time.strftime('%H:%M')} — {r.full_name}",
            callback_data=f"viewres_{r.id}"
        ))
    bot.send_message(call.message.chat.id, "📅 <b>Barcha bronlar:</b>", parse_mode="HTML", reply_markup=markup)


# ═══════════════════════════════════════════════════════════════
#  Noma'lum xabarlar
# ═══════════════════════════════════════════════════════════════
@bot.message_handler(func=lambda m: True)
def fallback_handler(message):
    profile = get_profile_by_chat(message.chat.id)
    markup = main_menu_markup(profile) if profile else guest_menu_markup()
    bot.send_message(message.chat.id, "🤔 Tushunmadim. Quyidagi tugmalardan foydalaning:", reply_markup=markup)


# ═══════════════════════════════════════════════════════════════
#  Adminga yangi buyurtma haqida xabar
# ═══════════════════════════════════════════════════════════════
def notify_admin_new_order(order):
    if not ADMIN_CHAT_ID:
        return
    try:
        bot.send_message(
            ADMIN_CHAT_ID,
            f"🆕 <b>Yangi buyurtma!</b>\n"
            f"Buyurtma #{order.id} — {order.full_name}\n"
            f"Holati: {order.get_status_display()}\n"
            f"Narx: {order.total_price} so'm",
            parse_mode="HTML",
        )
    except Exception as e:
        print(f"Adminga xabar yuborilmadi: {e}")
