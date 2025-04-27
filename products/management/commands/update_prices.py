from django.core.management.base import BaseCommand
import random
from decimal import Decimal
from products.models import Product

class Command(BaseCommand):
    help = 'Updates product prices with original prices between 9000-12000 and selling prices between 2500-3999'

    def handle(self, *args, **options):
        products = Product.objects.all()
        
        for product in products:
            # Generate original price between 9000 and 12000
            original_price = Decimal(str(random.randint(9000, 12000)))
            # Generate selling price between 2500 and 3999
            selling_price = Decimal(str(random.randint(2500, 3999)))
            
            product.original_price = original_price
            product.selling_price = selling_price
            product.save()
            
            # Calculate discount percentage
            discount = ((original_price - selling_price) / original_price) * 100
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {product.name}:\n'
                    f'Original Price: {original_price}\n'
                    f'Selling Price: {selling_price}\n'
                    f'Discount: {discount:.1f}%'
                )
            ) 