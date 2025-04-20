import logging

from django.core.management.base import BaseCommand

from core.helpers import create_system_roles

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        create_system_roles()
