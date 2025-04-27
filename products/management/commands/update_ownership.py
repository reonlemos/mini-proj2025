from django.core.management.base import BaseCommand
import random
from products.models import Product

class Command(BaseCommand):
    help = 'Updates all products with random ownership counts (1, 2, or 3)'

    def handle(self, *args, **options):
        products = Product.objects.all()
        
        for product in products:
            # Randomly assign ownership count (1, 2, or 3)
            ownership_count = random.randint(1, 3)
            product.ownership_count = ownership_count
            product.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Updated {product.name}: {ownership_count} owner(s)'
                )
            ) 