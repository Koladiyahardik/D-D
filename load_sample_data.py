#!/usr/bin/env python
"""
Script to load sample data for D&D Salon Products
Run this after setting up the database and creating a superuser
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dd_salon.settings')
django.setup()

from django.contrib.auth.models import User
from products.models import Category, Product
from django.utils import timezone

def create_categories():
    """Create sample categories"""
    categories_data = [
        {
            'name': 'Hair Care',
            'description': 'Premium hair care products including shampoos, conditioners, treatments, and styling products.'
        },
        {
            'name': 'Skin Care',
            'description': 'Professional skin care products for cleansing, moisturizing, and treating various skin types.'
        },
        {
            'name': 'Nail Care',
            'description': 'Complete nail care solutions including polishes, treatments, and manicure tools.'
        },
        {
            'name': 'Men\'s Grooming',
            'description': 'Specialized grooming products designed specifically for men\'s needs.'
        },
        {
            'name': 'Body & Spa',
            'description': 'Luxurious body care and spa products for relaxation and rejuvenation.'
        },
        {
            'name': 'Salon Equipment',
            'description': 'Professional salon equipment and tools for commercial use.'
        }
    ]
    
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"Created category: {category.name}")
        else:
            print(f"Category already exists: {category.name}")
    
    return Category.objects.all()

def create_products(categories):
    """Create sample products"""
    products_data = [
        # Hair Care Products
        {
            'name': 'Professional Hair Shampoo - Moisturizing',
            'description': 'Deep moisturizing shampoo for dry and damaged hair. Enriched with keratin and argan oil.',
            'price': 850,
            'discount_price': 750,
            'stock': 50,
            'category': 'Hair Care',
            'is_featured': True
        },
        {
            'name': 'Keratin Hair Treatment',
            'description': 'Professional keratin treatment for smooth, frizz-free hair. Lasts up to 3 months.',
            'price': 2500,
            'discount_price': 2200,
            'stock': 25,
            'category': 'Hair Care',
            'is_featured': True
        },
        {
            'name': 'Color Protection Conditioner',
            'description': 'Specialized conditioner to protect and maintain colored hair vibrancy.',
            'price': 950,
            'stock': 40,
            'category': 'Hair Care',
            'is_featured': False
        },
        
        # Skin Care Products
        {
            'name': 'Gentle Face Cleanser',
            'description': 'pH-balanced cleanser suitable for all skin types. Removes makeup and impurities gently.',
            'price': 650,
            'discount_price': 580,
            'stock': 60,
            'category': 'Skin Care',
            'is_featured': True
        },
        {
            'name': 'Hydrating Face Moisturizer',
            'description': 'Lightweight moisturizer with hyaluronic acid for deep hydration without greasiness.',
            'price': 1200,
            'stock': 45,
            'category': 'Skin Care',
            'is_featured': True
        },
        {
            'name': 'Vitamin C Serum',
            'description': 'Brightening serum with 20% vitamin C for radiant, even-toned skin.',
            'price': 1800,
            'discount_price': 1600,
            'stock': 30,
            'category': 'Skin Care',
            'is_featured': False
        },
        
        # Nail Care Products
        {
            'name': 'Professional Nail Polish Set',
            'description': 'Set of 12 premium nail polishes in trending colors. Long-lasting and chip-resistant.',
            'price': 1500,
            'discount_price': 1300,
            'stock': 20,
            'category': 'Nail Care',
            'is_featured': True
        },
        {
            'name': 'Cuticle Oil Treatment',
            'description': 'Nourishing cuticle oil with vitamin E and jojoba oil for healthy nail beds.',
            'price': 450,
            'stock': 35,
            'category': 'Nail Care',
            'is_featured': False
        },
        
        # Men's Grooming
        {
            'name': 'Men\'s Grooming Kit',
            'description': 'Complete grooming kit including beard oil, aftershave, and styling products.',
            'price': 2200,
            'discount_price': 1900,
            'stock': 25,
            'category': 'Men\'s Grooming',
            'is_featured': True
        },
        {
            'name': 'Beard Growth Serum',
            'description': 'Natural beard growth serum with biotin and essential oils for thicker, fuller beard.',
            'price': 1800,
            'stock': 30,
            'category': 'Men\'s Grooming',
            'is_featured': False
        },
        
        # Body & Spa
        {
            'name': 'Luxury Body Scrub',
            'description': 'Exfoliating body scrub with sea salt and essential oils for smooth, glowing skin.',
            'price': 950,
            'discount_price': 850,
            'stock': 40,
            'category': 'Body & Spa',
            'is_featured': True
        },
        {
            'name': 'Aromatherapy Massage Oil',
            'description': 'Relaxing massage oil with lavender and eucalyptus for stress relief.',
            'price': 1200,
            'stock': 25,
            'category': 'Body & Spa',
            'is_featured': False
        }
    ]
    
    category_map = {cat.name: cat for cat in categories}
    
    for prod_data in products_data:
        category = category_map[prod_data['category']]
        
        product, created = Product.objects.get_or_create(
            name=prod_data['name'],
            defaults={
                'description': prod_data['description'],
                'price': prod_data['price'],
                'discount_price': prod_data.get('discount_price'),
                'stock': prod_data['stock'],
                'category': category,
                'is_featured': prod_data['is_featured']
            }
        )
        
        if created:
            print(f"Created product: {product.name}")
        else:
            print(f"Product already exists: {product.name}")

def main():
    print("Loading sample data for D&D Salon Products...")
    print("=" * 50)
    
    # Create categories
    print("\nCreating categories...")
    categories = create_categories()
    
    # Create products
    print("\nCreating products...")
    create_products(categories)
    
    print("\n" + "=" * 50)
    print("Sample data loaded successfully!")
    print("\nYou can now:")
    print("1. Access the admin panel at http://localhost:8000/admin")
    print("2. Start the development server: python manage.py runserver")
    print("3. Browse products and test the e-commerce functionality")

if __name__ == '__main__':
    main()
