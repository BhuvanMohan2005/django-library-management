"""
Models for the Library Management System.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta

class Book(models.Model):
    """
    Model representing a book in the library.
    """
    GENRE_CHOICES = [
        ('FIC', 'Fiction'),
        ('NON', 'Non-Fiction'),
        ('SCI', 'Science'),
        ('HIS', 'History'),
        ('BIO', 'Biography'),
        ('FAN', 'Fantasy'),
        ('MYS', 'Mystery'),
        ('ROM', 'Romance'),
        ('TEC', 'Technology'),
        ('ART', 'Art'),
    ]
    
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField('ISBN', max_length=13, unique=True, 
                          help_text='13-character ISBN number')
    genre = models.CharField(max_length=3, choices=GENRE_CHOICES, default='FIC')
    published_date = models.DateField()
    publisher = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(0)])
    available_copies = models.PositiveIntegerField(default=1, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['title']
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    def save(self, *args, **kwargs):
        """Override save to ensure available_copies doesn't exceed quantity."""
        if self.available_copies > self.quantity:
            self.available_copies = self.quantity
        super().save(*args, **kwargs)
    
    def is_available(self):
        """Check if book has available copies."""
        return self.available_copies > 0
    
    def borrow_book(self):
        """Decrement available copies when borrowed."""
        if self.available_copies > 0:
            self.available_copies -= 1
            self.save()
            return True
        return False
    
    def return_book(self):
        """Increment available copies when returned."""
        if self.available_copies < self.quantity:
            self.available_copies += 1
            self.save()
            return True
        return False


class Member(models.Model):
    """
    Model representing a library member.
    """
    MEMBERSHIP_CHOICES = [
        ('REG', 'Regular'),
        ('PRE', 'Premium'),
        ('STU', 'Student'),
        ('SEN', 'Senior'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    membership_type = models.CharField(max_length=3, choices=MEMBERSHIP_CHOICES, default='REG')
    membership_start_date = models.DateField(auto_now_add=True)
    membership_end_date = models.DateField(blank=True, null=True)
    max_books_allowed = models.PositiveIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(20)])
    current_books_borrowed = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Member'
        verbose_name_plural = 'Members'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def can_borrow_more(self):
        """Check if member can borrow more books."""
        return self.current_books_borrowed < self.max_books_allowed and self.is_active
    
    def increment_borrowed_count(self):
        """Increment count of borrowed books."""
        if self.can_borrow_more():
            self.current_books_borrowed += 1
            self.save()
            return True
        return False
    
    def decrement_borrowed_count(self):
        """Decrement count of borrowed books."""
        if self.current_books_borrowed > 0:
            self.current_books_borrowed -= 1
            self.save()
            return True
        return False


class Loan(models.Model):
    """
    Model representing a book loan transaction.
    """
    STATUS_CHOICES = [
        ('ACT', 'Active'),
        ('RET', 'Returned'),
        ('OVE', 'Overdue'),
        ('CAN', 'Cancelled'),
    ]
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='loans')
    loan_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='ACT')
    fine_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    fine_paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-loan_date']
        verbose_name = 'Loan'
        verbose_name_plural = 'Loans'
        unique_together = ['book', 'member', 'loan_date']
    
    def __str__(self):
        return f"{self.book.title} loaned to {self.member.full_name}"
    
    def save(self, *args, **kwargs):
        """Set due date to 14 days from loan date if not provided."""
        if not self.due_date:
            self.due_date = timezone.now().date() + timedelta(days=14)
        
        # Update status based on dates
        if self.return_date:
            self.status = 'RET'
        elif self.due_date < timezone.now().date():
            self.status = 'OVE'
        
        super().save(*args, **kwargs)
    
    def calculate_fine(self):
        """Calculate fine if book is overdue."""
        if self.status == 'OVE' and not self.fine_paid:
            days_overdue = (timezone.now().date() - self.due_date).days
            if days_overdue > 0:
                self.fine_amount = days_overdue * 1.00  # $1 per day
                self.save()
                return self.fine_amount
        return 0.00
    
    def mark_returned(self):
        """Mark loan as returned."""
        self.return_date = timezone.now().date()
        self.status = 'RET'
        self.save()
        
        # Update book availability
        self.book.return_book()
        
        # Update member's borrowed count
        self.member.decrement_borrowed_count()
        
        return True