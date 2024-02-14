from django.core.management.base import BaseCommand
from apps.hotspot_router.tasks import update_hotspot_mac_ip


class Command(BaseCommand):
    def handle(self, *args, **options):
        update_hotspot_mac_ip()
