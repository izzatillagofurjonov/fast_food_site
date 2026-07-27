# Telegram Bot — Sarab Restaurant

Ushbu papka Django loyihasiga ulangan Telegram botni o'z ichiga oladi.
Bot alohida process yoki API talab qilmaydi — u Django ORM'ga
(`orders.Order`, `menu.Dish`) to'g'ridan-to'g'ri kirib ishlaydi.

## Fayllar tuzilishi

```
telegram_bot/
├── __init__.py
├── apps.py                          — Django app konfiguratsiyasi
├── bot.py                           — botning asosiy logikasi (barcha handlerlar shu yerda)
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       └── runbot.py                — `python manage.py runbot` bilan botni ishga tushiradi
└── README.md                        — ushbu fayl
```

Loyiha ildizida (`manage.py` bilan bir qatorda) yana ikkita fayl bor:

```
.env.example        — .env fayl uchun namuna
requirements.txt     — kerakli kutubxonalar ro'yxati
```

## Har bir fayl nima qiladi

- **`bot.py`** — bot shu yerda "jonlanadi". `/start` komandasi,
  "🍽 Menyu" va "📦 Buyurtmam" tugmalari shu faylda ishlaydi.
  Yangi funksiya qo'shmoqchi bo'lsangiz (masalan yangi buyruq),
  aynan shu faylga yangi `@bot.message_handler(...)` funksiyasi
  qo'shasiz.

- **`apps.py`** — Django'ga "bu ham bitta app" deb tanishtiradi.
  `INSTALLED_APPS` ro'yxatida ishlatiladi.

- **`management/commands/runbot.py`** — bu maxsus Django buyrug'i.
  Uni ishga tushirganingizda (`python manage.py runbot`) Django
  butun loyihani (settings, modellar va h.k.) yuklaydi, keyin
  botni polling rejimida ishga tushiradi. Shu sababli `bot.py`
  ichida `Order.objects...` kabi ORM so'rovlari ishlayveradi.

## O'rnatish qadamlari

### 1. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 2. Bot token olish

1. Telegram'da **@BotFather** botini oching.
2. `/newbot` buyrug'ini yuboring va ko'rsatmalarga amal qiling.
3. Sizga beriladigan tokenni saqlab qo'ying.

### 3. `.env` faylini sozlash

`.env.example` faylidan nusxa oling:

```bash
cp .env.example .env
```

`.env` faylini oching va tokenni kiriting:

```
TELEGRAM_BOT_TOKEN=sizning_haqiqiy_tokeningiz
TELEGRAM_ADMIN_CHAT_ID=123456789
```

> `TELEGRAM_ADMIN_CHAT_ID` — yangi buyurtma haqida xabar
> yubormoqchi bo'lgan admin (yoki restoran egasi)ning shaxsiy
> Telegram chat ID raqami. Buni bilish uchun **@userinfobot**
> ga yozib ko'ring.

### 4. `settings.py`ni sozlash

`.env` fayli o'qilishi uchun loyihangizning asosiy `settings.py`
fayliga quyidagilarni qo'shing:

```python
from decouple import config

TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
TELEGRAM_ADMIN_CHAT_ID = config("TELEGRAM_ADMIN_CHAT_ID", default="")
```

va `INSTALLED_APPS` ro'yxatiga qo'shing:

```python
INSTALLED_APPS = [
    # ...
    "telegram_bot",
]
```

`bot.py` faylidagi `os.environ.get(...)` qatorlari `.env`dagi
qiymatlarni to'g'ridan-to'g'ri o'qiydi, shuning uchun loyihangizda
`.env`ni yuklaydigan mexanizm (masalan `python-decouple` yoki
`django-environ`) borligiga ishonch hosil qiling.

### 5. Model nomlarini moslashtirish

`bot.py` faylining boshida quyidagi importlar bor:

```python
from orders.models import Order
from menu.models import Dish
```

Bu nomlarni **o'z loyihangizdagi haqiqiy app va model nomlariga**
moslang. Shuningdek:

- `Dish.name`, `Dish.price` — menyu modelidagi maydon nomlari
- `Order.id`, `Order.get_status_display()` — buyurtma modelidagi
  maydon va metodlar

haqiqiy loyihangizdagidan farq qilishi mumkin — shunga qarab
`bot.py` ichidagi mos qatorlarni tahrirlang.

## Botni ishga tushirish

```bash
python manage.py runbot
```

Konsolda quyidagi xabarni ko'rasiz:

```
Bot ishga tushdi... To'xtatish uchun CTRL+C bosing.
```

Endi Telegram'da o'z botingizni topib, `/start` yuboring.

## Botning ishlash mantig'i (oqim)

1. Foydalanuvchi `/start` yuboradi → bot ikkita tugmali menyu
   ko'rsatadi: **🍽 Menyu** va **📦 Buyurtmam**.
2. **🍽 Menyu** bosilsa → bot bazadan (`Dish` modelidan) taomlar
   ro'yxatini olib, nomi va narxini ko'rsatadi.
3. **📦 Buyurtmam** bosilsa → bot foydalanuvchidan buyurtma
   raqamini so'raydi, so'ng (`Order` modelidan) topib, holatini
   ko'rsatadi.
4. Har qanday boshqa xabar yuborilsa → bot "tushunmadim,
   /start bosing" deb javob beradi.

## Kengaytirish g'oyalari

- **Yangi buyurtma haqida adminga avtomatik xabar**: `orders/`
  app'ida `signals.py` fayli yarating va quyidagicha yozing:

  ```python
  from django.db.models.signals import post_save
  from django.dispatch import receiver
  from .models import Order
  from telegram_bot import notify_admin_new_order

  @receiver(post_save, sender=Order)
  def order_created(sender, instance, created, **kwargs):
      if created:
          notify_admin_new_order(instance)
  ```

  So'ng `apps.py`da signalni ulang (`ready()` metodida import qiling).

- **Inline tugmalar** (masalan taomni bosib buyurtma berish) —
  `types.InlineKeyboardMarkup` va `bot.callback_query_handler`
  yordamida qo'shiladi.

- **Webhook rejimi** (production uchun, polling o'rniga) —
  server bo'lsa, `bot.infinity_polling()` o'rniga Django view orqali
  webhook qabul qilish tavsiya etiladi.

## Eslatma

Bu bot **hozircha o'quv/demo maqsadida** yozilgan. Production'ga
chiqarishdan oldin: xatoliklarni ushlash (try/except), loglash,
va webhook rejimiga o'tishni ko'rib chiqing.
