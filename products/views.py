from django.http import Http404, JsonResponse
from django.views.generic import ListView, DetailView
from django.db.models import Exists, OuterRef, Value
from django.db import models
from django.views.decorators.http import require_GET

from categories.models import Category
from wishlist.models import Wishlist
from .models import Product, ProductVariant


class ProductListView(ListView):
    model = Product
    template_name = "products/all.html"
    context_object_name = "products"
    paginate_by = 10

    SORT_OPTIONS = {
        'price_asc': 'selling_price',
        'price_desc': '-selling_price',
        'name': 'name',
        'default': '-created'
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply sorting
        sort_param = self.request.GET.get('sort', 'default')
        order_by = self.SORT_OPTIONS.get(sort_param, self.SORT_OPTIONS['default'])
        queryset = queryset.order_by(order_by)

        # Add wishlist annotation
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_wishlisted=Exists(
                    Wishlist.objects.filter(
                        user=self.request.user, product=OuterRef("pk")
                    )
                )
            )
        else:
            queryset = queryset.annotate(
                is_wishlisted=Value(False, output_field=models.BooleanField())
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "All Products"
        context["sort"] = self.request.GET.get('sort', 'default')
        return context


class FeaturedProductListView(ListView):
    model = Product
    template_name = "products/all.html"
    context_object_name = "products"
    paginate_by = 5

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True, top_featured=True)
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_wishlisted=Exists(
                    Wishlist.objects.filter(user=self.request.user, product=OuterRef("pk"))
                )
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Featured Products"
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "products/detail.html"
    context_object_name = "product"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj is None:
            raise Http404("Product not found")
        obj.is_wishlisted = Wishlist.objects.filter(
            user=self.request.user, product=obj
        ).exists() if self.request.user.is_authenticated else False
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get similar products from the same category
        similar_products = Product.objects.filter(
            category=self.object.category, is_active=True
        ).exclude(id=self.object.id)[:6]

        # Get related products (from all categories)
        related_products = (
            Product.objects.filter(is_active=True)
            .exclude(id=self.object.id)
            .exclude(id__in=[p.id for p in similar_products])[:8]
        )  # Limit to 8 products

        context["similar_products"] = similar_products
        context["related_products"] = related_products
        return context


class ProductsByCategoryView(ListView):
    model = Product
    template_name = "products/all.html"
    context_object_name = "products"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        self.get_category()
        return super().dispatch(request, *args, **kwargs)

    def get_category(self):
        self.category = Category.objects.get(slug=self.kwargs["slug"])
        if self.category is None:
            raise Http404("Category not found")
        return self.category

    def get_queryset(self):
        if self.category:
            queryset = Product.objects.filter(category=self.category)
            if self.request.user.is_authenticated:
                queryset = queryset.annotate(
                    is_wishlisted=Exists(
                        Wishlist.objects.filter(user=self.request.user, product=OuterRef("pk"))
                    )
                )
            return queryset
        return Product.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"List of {self.category.name} Products"
        return context


@require_GET
def get_variant_details(request):
    product_id = request.GET.get('product_id')
    size = request.GET.get('size')
    color = request.GET.get('color')
    
    try:
        variant = ProductVariant.objects.get(
            product_id=product_id,
            size=size,
            color=color
        )
        return JsonResponse({
            'id': variant.id,
            'sku': variant.sku,
            'selling_price': float(variant.selling_price),
            'stock': variant.stock
        })
    except ProductVariant.DoesNotExist:
        return JsonResponse({'error': 'Variant not found'}, status=404)
