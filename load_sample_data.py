#!/usr/bin/env python
"""
Script to load sample data for the Library Management System.
Run with: python load_sample_data.py
"""

import os
import sys
import django
from datetime import date, timedelta
from django.utils import timezone

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management.settings')
try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    sys.exit(1)

from django.contrib.auth.models import User
from library.models import Book, Member, Loan

def create_sample_data():
    """Create sample data for the library system."""
    
    print("Starting to create sample data...")
    
    # Clear existing data (optional - remove if you want to keep existing data)
    # Book.objects.all().delete()
    # Member.objects.all().delete()
    # Loan.objects.all().delete()
    
    # Create a superuser if doesn't exist
    if not User.objects.filter(username='admin').exists():
        print("Creating admin user...")
        try:
            User.objects.create_superuser(
                username='admin',
                email='admin@library.com',
                password='admin123'
            )
            print("✓ Admin user created")
        except Exception as e:
            print(f"Error creating admin: {e}")
    
    # Create sample books
    books_data = [
        {
            'title': 'The Great Gatsby',
            'author': 'F. Scott Fitzgerald',
            'isbn': '9780743273565',
            'genre': 'FIC',
            'published_date': date(1925, 4, 10),
            'publisher': "Charles Scribner's Sons",
            'description': 'A classic novel of the Jazz Age.',
            'quantity': 5,
            'available_copies': 3,
        },
        {
            'title': 'To Kill a Mockingbird',
            'author': 'Harper Lee',
            'isbn': '9780061120084',
            'genre': 'FIC',
            'published_date': date(1960, 7, 11),
            'publisher': 'J. B. Lippincott & Co.',
            'description': 'A novel about racial injustice in the American South.',
            'quantity': 3,
            'available_copies': 2,
        },
        {
            'title': '1984',
            'author': 'George Orwell',
            'isbn': '9780451524935',
            'genre': 'FIC',
            'published_date': date(1949, 6, 8),
            'publisher': 'Secker & Warburg',
            'description': 'A dystopian social science fiction novel.',
            'quantity': 4,
            'available_copies': 4,
        },
        {
            'title': 'Pride and Prejudice',
            'author': 'Jane Austen',
            'isbn': '9780141439518',
            'genre': 'ROM',
            'published_date': date(1813, 1, 28),
            'publisher': 'T. Egerton',
            'description': 'A romantic novel of manners.',
            'quantity': 3,
            'available_copies': 1,
        },
        {
            'title': 'The Hobbit',
            'author': 'J.R.R. Tolkien',
            'isbn': '9780547928227',
            'genre': 'FAN',
            'published_date': date(1937, 9, 21),
            'publisher': 'George Allen & Unwin',
            'description': 'Fantasy novel and childrens book.',
            'quantity': 6,
            'available_copies': 4,
        },
    ]
    
    books_created = 0
    for book_data in books_data:
        book, created = Book.objects.get_or_create(
            isbn=book_data['isbn'],
            defaults=book_data
        )
        if created:
            books_created += 1
            print(f"✓ Created book: {book.title}")
        else:
            print(f"Book already exists: {book.title}")
    
    # Create sample members
    members_data = [
        {
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'john.smith@email.com',
            'phone': '555-0101',
            'address': '123 Main St, Anytown',
            'membership_type': 'REG',
            'max_books_allowed': 5,
            'current_books_borrowed': 2,
            'is_active': True,
        },
        {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane.doe@email.com',
            'phone': '555-0102',
            'address': '456 Oak Ave, Somewhere',
            'membership_type': 'PRE',
            'max_books_allowed': 15,
            'current_books_borrowed': 0,
            'is_active': True,
        },
        {
            'first_name': 'Robert',
            'last_name': 'Johnson',
            'email': 'robert.johnson@email.com',
            'phone': '555-0103',
            'address': '789 Pine Rd, Nowhere',
            'membership_type': 'STU',
            'max_books_allowed': 10,
            'current_books_borrowed': 5,
            'is_active': True,
        },
    ]
    
    members_created = 0
    for member_data in members_data:
        member, created = Member.objects.get_or_create(
            email=member_data['email'],
            defaults=member_data
        )
        if created:
            members_created += 1
            print(f"✓ Created member: {member.full_name}")
        else:
            print(f"Member already exists: {member.full_name}")
    
    # Get the created books and members
    books = Book.objects.all()
    members = Member.objects.all()
    
    # Create sample loans
    loans_data = [
        {
            'book': books[0],  # The Great Gatsby
            'member': members[0],  # John Smith
            'loan_date': timezone.now().date() - timedelta(days=5),
            'due_date': timezone.now().date() + timedelta(days=9),
            'status': 'ACT',
        },
        {
            'book': books[1],  # To Kill a Mockingbird
            'member': members[0],  # John Smith
            'loan_date': timezone.now().date() - timedelta(days=10),
            'due_date': timezone.now().date() + timedelta(days=4),
            'status': 'ACT',
        },
        {
            'book': books[2],  # 1984
            'member': members[2],  # Robert Johnson
            'loan_date': timezone.now().date() - timedelta(days=20),
            'due_date': timezone.now().date() - timedelta(days=6),
            'status': 'OVE',
            'fine_amount': 6.00,
        },
    ]
    
    loans_created = 0
    for loan_data in loans_data:
        # Check if loan already exists
        existing_loan = Loan.objects.filter(
            book=loan_data['book'],
            member=loan_data['member'],
            loan_date=loan_data['loan_date']
        ).first()
        
        if not existing_loan:
            try:
                loan = Loan.objects.create(**loan_data)
                loans_created += 1
                print(f"✓ Created loan: {loan.book.title} → {loan.member.full_name}")
                
                # Update book availability for active loans
                if loan.status == 'ACT':
                    if loan.book.available_copies > 0:
                        loan.book.available_copies -= 1
                        loan.book.save()
            except Exception as e:
                print(f"Error creating loan: {e}")
        else:
            print(f"Loan already exists: {existing_loan.book.title} → {existing_loan.member.full_name}")
    
    print("\n" + "="*50)
    print("SAMPLE DATA CREATION SUMMARY")
    print("="*50)
    print(f"Books created: {books_created} (Total: {Book.objects.count()})")
    print(f"Members created: {members_created} (Total: {Member.objects.count()})")
    print(f"Loans created: {loans_created} (Total: {Loan.objects.count()})")
    print("\nAdmin credentials (if created):")
    print("Username: admin")
    print("Password: admin123")
    print("="*50)
    print("\nYou can now:")
    print("1. Visit http://127.0.0.1:8000 to see the library dashboard")
    print("2. Login to admin at http://127.0.0.1:8000/admin with above credentials")
    print("3. Check the Books, Members, and Loans sections")

if __name__ == '__main__':
    create_sample_data()