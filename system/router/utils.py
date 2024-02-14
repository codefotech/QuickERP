from apps.hotspot_router.models import HotspotRouter
from apps.router.router_os.routing import is_router_port_active


def check_hotspot_router_status(id=None):
    if id:
        router = HotspotRouter.objects.get(id=id)
        return is_router_port_active(router.ip_address, router.api_port)
