from time import strftime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from categories.models import Category
from utils.common_utils import generate_file_name


def product_image_directory_path(instance, filename):
    return "products/{0}/{1}".format(
        strftime("%Y/%m/%d"), generate_file_name() + "." + filename.split(".")[-1]
    )


class Product(TimeStampedModel):
    class StockUnitChoices(models.IntegerChoices):
        KG = 1, "kg"
        GM = 2, "gm"
        LTR = 3, "ltr"
        ML = 4, "ml"
        UNIT = 5, "unit"

    class OwnershipStatusChoices(models.TextChoices):
        FIRST_OWNER = "first", _("First Owner")
        SECOND_HAND = "second", _("Second Hand")
        THIRD_HAND = "third", _("Third Hand")

    name = models.CharField(max_length=255, verbose_name=_("Product name"))
    description = models.TextField(help_text=_("Main product description"))
    additional_details = models.TextField(
        blank=True, help_text=_("Additional details about the product")
    )

    # Price fields using DecimalField
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_active = models.BooleanField(
        default=True, help_text=_("Whether the product is available for sale")
    )
    brand = models.CharField(max_length=200, null=True, blank=True)

    # Inventory fields
    stock = models.IntegerField(
        help_text=_("Available quantity in stock"), verbose_name=_("Stock")
    )
    stock_unit = models.IntegerField(
        choices=StockUnitChoices.choices,
        help_text=_("Unit of measurement for the stock"),
    )
    minimum_stock = models.IntegerField(
        default=0, help_text=_("Minimum stock level before reorder")
    )

    top_featured = models.BooleanField(
        default=False, help_text=_("Whether the product is featured")
    )
    # SKU and Barcodes
    sku = models.CharField(
        max_length=50, unique=True, help_text=_("Stock Keeping Unit")
    )
    barcode = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Product barcode (ISBN, UPC, etc.)"),
    )
    # SEO and URLs
    slug = models.SlugField(
        unique=True, help_text=_("URL-friendly version of the product name")
    )
    # Meta Information
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Meta Keywords"),
        help_text=_("Comma-separated keywords for SEO"),
    )
    meta_description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Meta Description"),
        help_text=_("Short description for SEO"),
    )

    # Shipping fields
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Product weight for shipping calculations"),
    )
    is_free_shipping = models.BooleanField(
        default=False, help_text=_("Whether the product ships free")
    )
    has_variants = models.BooleanField(
        default=False, help_text=_("Whether this product has different variants")
    )

    ownership_count = models.PositiveIntegerField(default=1, help_text=_('Number of times this product has been owned (1 = first owner, 2 = second hand, etc.)'))
    ownership_status = models.CharField(
        max_length=10,
        choices=OwnershipStatusChoices.choices,
        default=OwnershipStatusChoices.FIRST_OWNER,
        help_text=_("Current ownership status of the product")
    )

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["sku"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.name

    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.original_price and self.selling_price:
            discount = (
                (self.original_price - self.selling_price) / self.original_price
            ) * 100
            return round(discount, 2)
        return 0

    @property
    def primary_image(self):
        """Returns the primary image or the first image if no primary is set"""
        return self.images.filter(is_primary=True).first() or self.images.first()

    @property
    def needs_restock(self):
        """Check if product needs restocking"""
        return self.stock <= self.minimum_stock

    @property
    def total_stock(self):
        """Get total stock across all variants"""
        if self.has_variants:
            return sum(variant.stock for variant in self.variants.all())
        return self.stock

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)

    def get_rating_count(self, rating):
        """Get the count of reviews for a specific rating"""
        return self.reviews.filter(rating=rating).count()


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(
        upload_to=product_image_directory_path, verbose_name=_("Product Image")
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductVariant(TimeStampedModel):
    class SizeChoices(models.TextChoices):
        EXTRA_SMALL = "XS", _("Extra Small")
        SMALL = "S", _("Small")
        MEDIUM = "M", _("Medium")
        LARGE = "L", _("Large")
        EXTRA_LARGE = "XL", _("Extra Large")
        DOUBLE_EXTRA_LARGE = "XXL", _("Double Extra Large")
        TRIPLE_EXTRA_LARGE = "XXXL", _("Triple Extra Large")

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    size = models.CharField(
        max_length=10, choices=SizeChoices.choices, blank=True, null=True
    )
    color = models.CharField(max_length=50, blank=True, null=True)

    # Each variant has its own stock and price
    stock = models.IntegerField(help_text=_("Available quantity in stock"))
    stock_unit = models.IntegerField(
        choices=Product.StockUnitChoices.choices,
        help_text=_("Unit of measurement for stock"),
    )
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Variant specific SKU
    sku = models.CharField(
        max_length=50, unique=True, help_text=_("Stock Keeping Unit")
    )

    class Meta:
        verbose_name = _("Product Variant")
        verbose_name_plural = _("Product Variants")

    def __str__(self):
        variant_details = []
        if self.size:
            variant_details.append(f"Size: {self.size}")
        if self.color:
            variant_details.append(f"Color: {self.color}")
        return f"{self.product.name} ({', '.join(variant_details)})"


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], help_text='Rating from 1 to 5 stars')
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # One review per user per product

    def __str__(self):
        return f"{self.user.username}'s review for {self.product.name}"


class Bid(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_winner = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    auction_end_time = models.DateTimeField(null=True, blank=True)
    payment_processed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-amount', '-created']

    def __str__(self):
        return f"{self.user} bid {self.amount} on {self.product}"


class PaymentTransaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    bid = models.OneToOneField('Bid', on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Payment for {self.bid.product.name} - {self.amount}"

    class Meta:
        ordering = ['-created_at']
