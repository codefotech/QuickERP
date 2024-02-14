from apps.hotspot_customer.tasks import ssh_router_user_add_remove

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        ssh_router_user_add_remove()
