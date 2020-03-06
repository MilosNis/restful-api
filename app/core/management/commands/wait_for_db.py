from django.db import connections
from django.db.utils import OperationalError
import time
from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        """Server app stop execution while database is not available"""
        db_conn = None
        self.stdout.write('Waiting for database...')
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('Database unavailable, '
                                  'waiting for 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available!'))
