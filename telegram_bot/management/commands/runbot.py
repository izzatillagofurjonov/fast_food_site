from django.core.management.base import BaseCommand
import telegram_bot.bot as bot_module


class Command(BaseCommand):
    help = "Telegram botni polling rejimida ishga tushiradi"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Bot ishga tushdi... To'xtatish uchun CTRL+C bosing."))
        bot_module.bot.infinity_polling()