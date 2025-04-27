import random
from decimal import Decimal
from products.models import Product

def update_product_prices():
    # Get all products
    products = Product.objects.all()
    
    # Update each product's prices
    for product in products:
        # Generate random price between 2500 and 3999
        new_price = Decimal(str(random.randint(2500, 3999)))
        
        # Update both original and selling price
        product.original_price = new_price
        product.selling_price = new_price
        product.save()
        
        print(f"Updated {product.name}: {new_price}")

if __name__ == "__main__":
    update_product_prices() 