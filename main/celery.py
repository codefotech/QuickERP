import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
app = Celery('main')
app.conf.timezone = 'UTC'
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {

    'ssh_router_user_add_remove': {
        'task': 'apps.hotspot_customer.tasks.ssh_router_user_add_remove',
        'schedule': 120.0,
    },
    'update_hotspot_customer_mac': {
            'task': 'apps.hotspot_customer.tasks.update_hotspot_customer_mac',
            'schedule': 60.0,
        },
    'update_hotspot_mac_ip': {
            'task': 'apps.hotspot_router.tasks.update_hotspot_mac_ip',
            'schedule': 30.0,
        },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
