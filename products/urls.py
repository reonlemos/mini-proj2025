from django.urls import path

from . import views
from .views import PlaceBidView

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='index'),
    path('featured/', views.FeaturedProductListView.as_view(), name='featured'),
    path('category/<slug:slug>/', views.ProductsByCategoryView.as_view(), name='category'),
    path('detail/<slug:slug>/', views.ProductDetailView.as_view(), name='detail'),
    path('detail/<slug:slug>/bid/', PlaceBidView.as_view(), name='place_bid'),
    path('api/variant/', views.get_variant_details, name='get_variant_details'),
    path('<slug:slug>/review/', views.add_review, name='add_review'),
]
