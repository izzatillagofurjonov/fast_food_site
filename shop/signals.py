from django.db.models.signals import post_save
from django.dispatch import receiver

from shop.models import Order
from telegram_bot.bot import notify_admin_new_order


@receiver(post_save, sender=Order)
def order_created_notify(sender, instance, created, **kwargs):
    if created:
        notify_admin_new_order(instance)

