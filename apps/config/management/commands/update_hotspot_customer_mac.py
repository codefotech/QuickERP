from apps.hotspot_customer.tasks import ssh_router_user_add_remove, update_hotspot_customer_mac

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        update_hotspot_customer_mac()
