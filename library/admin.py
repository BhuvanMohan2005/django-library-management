"""
Admin configuration for the library app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Book, Member, Loan


class BookAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Book model.
    """
    list_display = ['title', 'author', 'genre', 'quantity', 'available_copies', 'is_available_display']
    list_filter = ['genre', 'created_at']
    search_fields = ['title', 'author', 'isbn']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'isbn', 'genre')
        }),
        ('Publication Details', {
            'fields': ('published_date', 'publisher', 'description')
        }),
        ('Inventory', {
            'fields': ('quantity', 'available_copies')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_available_display(self, obj):
        """Display availability status with color coding."""
        if obj.is_available():
            return format_html('<span style="color: green;">✓ Available</span>')
        return format_html('<span style="color: red;">✗ Unavailable</span>')
    is_available_display.short_description = 'Availability'
    


class MemberAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Member model.
    """
    list_display = ['full_name', 'email', 'membership_type', 'is_active', 'books_borrowed']
    list_filter = ['membership_type', 'is_active', 'membership_start_date']
    search_fields = ['first_name', 'last_name', 'email']
    readonly_fields = ['membership_start_date', 'books_borrowed_display']
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'address')
        }),
        ('Membership', {
            'fields': ('membership_type', 'membership_start_date', 'membership_end_date', 'is_active')
        }),
        ('Borrowing Limits', {
            'fields': ('max_books_allowed', 'current_books_borrowed', 'books_borrowed_display')
        }),
    )
    
    def books_borrowed(self, obj):
        """Display books borrowed count."""
        return f"{obj.current_books_borrowed}/{obj.max_books_allowed}"
    books_borrowed.short_description = 'Books Borrowed'
    
    def books_borrowed_display(self, obj):
        """Display borrowing status."""
        if obj.can_borrow_more():
            return format_html('<span style="color: green;">Can borrow more books</span>')
        return format_html('<span style="color: red;">Borrowing limit reached</span>')
    books_borrowed_display.short_description = 'Borrowing Status'


class LoanAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Loan model.
    """
    list_display = ['book_title', 'member_name', 'loan_date', 'due_date', 'status_display', 'fine_display']
    list_filter = ['status', 'loan_date', 'due_date']
    search_fields = ['book__title', 'member__first_name', 'member__last_name']
    readonly_fields = ['loan_date', 'status', 'fine_amount', 'fine_paid']
    date_hierarchy = 'loan_date'
    
    def book_title(self, obj):
        """Display book title."""
        return obj.book.title
    book_title.short_description = 'Book'
    
    def member_name(self, obj):
        """Display member name."""
        return obj.member.full_name
    member_name.short_description = 'Member'
    
    def status_display(self, obj):
        """Display status with color coding."""
        status_colors = {
            'ACT': 'blue',
            'RET': 'green',
            'OVE': 'red',
            'CAN': 'gray',
        }
        color = status_colors.get(obj.status, 'black')
        status_text = dict(Loan.STATUS_CHOICES).get(obj.status, obj.status)
        return format_html(f'<span style="color: {color};">{status_text}</span>')
    status_display.short_description = 'Status'
    
    def fine_display(self, obj):
        """Display fine amount with color coding."""
        if obj.fine_amount > 0:
            if obj.fine_paid:
                return format_html(f'<span style="color: green;">${obj.fine_amount} (Paid)</span>')
            return format_html(f'<span style="color: red;">${obj.fine_amount}</span>')
        return "$0.00"
    fine_display.short_description = 'Fine'
    
    actions = ['mark_as_returned', 'calculate_fines']
    
    def mark_as_returned(self, request, queryset):
        """Admin action to mark loans as returned."""
        updated = 0
        for loan in queryset.filter(status='ACT'):
            loan.mark_returned()
            updated += 1
        self.message_user(request, f'{updated} loan(s) marked as returned.')
    mark_as_returned.short_description = "Mark selected loans as returned"
    
    def calculate_fines(self, request, queryset):
        """Admin action to calculate fines for overdue loans."""
        total_fines = 0
        for loan in queryset.filter(status='OVE', fine_paid=False):
            fine = loan.calculate_fine()
            total_fines += fine
        self.message_user(request, f'Calculated ${total_fines:.2f} in fines.')
    calculate_fines.short_description = "Calculate fines for selected loans"


# Register models with custom admin classes
admin.site.register(Book, BookAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Loan, LoanAdmin)