import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management.settings')
django.setup()

from library.models import Book, Member
from datetime import date

# Create a book
Book.objects.create(
    title='Test Book 1',
    author='Author 1',
    isbn='1111111111',
    genre='FIC',
    published_date=date(2020, 1, 1),
    publisher='Publisher 1',
    description='Test description',
    quantity=3,
    available_copies=2
)

print(f"Books in database: {Book.objects.count()}")
print(f"Members in database: {Member.objects.count()}")