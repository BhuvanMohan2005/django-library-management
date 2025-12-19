"""
Forms for the Library Management System.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Import models from your app(s)
from .models import Book, Member, Loan

from datetime import date, timedelta



class BookForm(forms.ModelForm):
    """
    Form for creating and updating books.
    """
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'genre', 'published_date', 
                 'publisher', 'description', 'quantity']
        widgets = {
            'published_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_isbn(self):
        """Validate ISBN format."""
        isbn = self.cleaned_data.get('isbn')
        if len(isbn) not in [10, 13]:
            raise forms.ValidationError('ISBN must be 10 or 13 characters long.')
        return isbn
    
    def clean_quantity(self):
        """Ensure quantity is positive."""
        quantity = self.cleaned_data.get('quantity')
        if quantity < 0:
            raise forms.ValidationError('Quantity cannot be negative.')
        return quantity


class MemberForm(forms.ModelForm):
    """
    Form for creating and updating members.
    """
    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'email', 'phone', 
                 'address', 'membership_type', 'max_books_allowed', 'is_active']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_email(self):
        """Validate email uniqueness."""
        email = self.cleaned_data.get('email')
        if Member.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('A member with this email already exists.')
        return email


class LoanForm(forms.ModelForm):
    """
    Form for creating book loans.
    """
    class Meta:
        model = Loan
        fields = ['book', 'member', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available books
        self.fields['book'].queryset = Book.objects.filter(available_copies__gt=0)
        
        # Only show active members who can borrow more
        # Get members who are active and have borrowed less than their max allowed
        active_members = Member.objects.filter(is_active=True)
        
        # Create a list of member IDs who have reached their borrowing limit
        members_at_limit = []
        for member in active_members:
            if member.current_books_borrowed >= member.max_books_allowed:
                members_at_limit.append(member.id)
        
        # Exclude members who have reached their limit
        self.fields['member'].queryset = active_members.exclude(id__in=members_at_limit)
    

    def clean(self):
        """Validate loan conditions."""
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        member = cleaned_data.get('member')
        
        if book and not book.is_available():
            raise forms.ValidationError('This book is not available for loan.')
        
        if member and not member.can_borrow_more():
            raise forms.ValidationError('This member cannot borrow more books.')
        
        return cleaned_data


class ReturnForm(forms.Form):
    """
    Form for returning books.
    """
    return_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text='Any notes about the return condition'
    )
    
    condition_choices = [
        ('GOOD', 'Good - No damage'),
        ('MINOR', 'Minor wear'),
        ('DAMAGED', 'Damaged - Needs repair'),
        ('LOST', 'Lost - Cannot be returned'),
    ]
    
    return_condition = forms.ChoiceField(
        choices=condition_choices,
        initial='GOOD',
        required=True,
        help_text='Condition of the book when returned'
    )
    
    def __init__(self, *args, **kwargs):
        self.loan = kwargs.pop('loan', None)
        super().__init__(*args, **kwargs)


class SearchForm(forms.Form):
    """
    Form for searching books.
    """
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search books...'})
    )
    genre = forms.ChoiceField(
        choices=[('', 'All Genres')] + Book.GENRE_CHOICES,
        required=False
    )
    author = forms.CharField(max_length=100, required=False)


class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration.
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user