from django.core.management.base import BaseCommand
from products.models import Bid

class Command(BaseCommand):
    help = 'Clears all bids from the database'

    def handle(self, *args, **options):
        # Delete all bids
        count = Bid.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully cleared all bids. {count[0]} records deleted.')) 