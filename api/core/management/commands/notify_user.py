import logging
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.helpers import vehicle_documents_expiry_notification, driver_documents_expiry_notification

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Notify the User about their document expirations'

    def handle(self, *args, **options):
        date_range = [datetime.date(timezone.now()), (datetime.date(timezone.now()) + timedelta(days=7))]
        vehicle_documents_expiry_notification(date_range)
        driver_documents_expiry_notification(date_range)
