from django.core.management.base import BaseCommand
from products.models import Product, ProductVariant

class Command(BaseCommand):
    help = 'Removes variants from the Nike Air Force 1 product and sets it to have a single price'

    def handle(self, *args, **options):
        # Find the Nike Air Force 1 product
        product = Product.objects.get(name="Nike Air Force 1 '07")
        
        # Delete all variants
        ProductVariant.objects.filter(product=product).delete()
        
        # Set has_variants to False
        product.has_variants = False
        product.save()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully removed variants from {product.name}')
        ) 