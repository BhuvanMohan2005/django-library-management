"""
Views for the Library Management System.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from .models import Book, Member, Loan
from .forms import BookForm, MemberForm, LoanForm, ReturnForm, SearchForm


def home(request):
    """
    Home page view showing library statistics.
    """
    total_books = Book.objects.count()
    total_members = Member.objects.filter(is_active=True).count()
    active_loans = Loan.objects.filter(status='ACT').count()
    overdue_loans = Loan.objects.filter(status='OVE').count()
    
    # Recent additions
    recent_books = Book.objects.order_by('-created_at')[:5]
    recent_loans = Loan.objects.select_related('book', 'member').order_by('-loan_date')[:5]
    
    context = {
        'total_books': total_books,
        'total_members': total_members,
        'active_loans': active_loans,
        'overdue_loans': overdue_loans,
        'recent_books': recent_books,
        'recent_loans': recent_loans,
    }
    return render(request, 'index.html', context)


# Book Views
def book_list(request):
    """
    List all books with search and filter functionality.
    """
    books = Book.objects.all()
    search_form = SearchForm(request.GET)
    
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        genre = search_form.cleaned_data.get('genre')
        author = search_form.cleaned_data.get('author')
        
        if query:
            books = books.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(isbn__icontains=query)
            )
        
        if genre:
            books = books.filter(genre=genre)
        
        if author:
            books = books.filter(author__icontains=author)
    
    # Pagination
    paginator = Paginator(books, 10)  # 10 books per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'genres': Book.GENRE_CHOICES,
    }
    return render(request, 'books/book_list.html', context)


def book_detail(request, pk):
    """
    View details of a specific book.
    """
    book = get_object_or_404(Book, pk=pk)
    loan_history = book.loans.select_related('member').order_by('-loan_date')[:10]
    
    context = {
        'book': book,
        'loan_history': loan_history,
    }
    return render(request, 'books/book_detail.html', context)


@login_required
def book_create(request):
    """
    Create a new book.
    """
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.available_copies = book.quantity
            book.save()
            messages.success(request, f'Book "{book.title}" added successfully!')
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm()
    
    context = {'form': form}
    return render(request, 'books/book_form.html', context)


@login_required
def book_update(request, pk):
    """
    Update an existing book.
    """
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            # Calculate new available copies based on quantity change
            old_quantity = book.quantity
            book = form.save(commit=False)
            
            # If quantity increased, increase available copies proportionally
            if book.quantity > old_quantity:
                book.available_copies += (book.quantity - old_quantity)
            # If quantity decreased below available copies, adjust
            elif book.available_copies > book.quantity:
                book.available_copies = book.quantity
            
            book.save()
            messages.success(request, f'Book "{book.title}" updated successfully!')
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    
    context = {'form': form, 'book': book}
    return render(request, 'books/book_form.html', context)


@login_required
def book_delete(request, pk):
    """
    Delete a book.
    """
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        book_title = book.title
        book.delete()
        messages.success(request, f'Book "{book_title}" deleted successfully!')
        return redirect('book_list')
    
    context = {'book': book}
    return render(request, 'books/book_confirm_delete.html', context)


# Member Views
def member_list(request):
    """
    List all members.
    """
    members = Member.objects.all().order_by('last_name', 'first_name')
    
    context = {
        'members': members,
        'membership_types': Member.MEMBERSHIP_CHOICES,
    }
    return render(request, 'members/member_list.html', context)


def member_detail(request, pk):
    """
    View details of a specific member.
    """
    member = get_object_or_404(Member, pk=pk)
    current_loans = member.loans.filter(status='ACT').select_related('book')
    loan_history = member.loans.exclude(status='ACT').select_related('book').order_by('-loan_date')[:10]
    
    context = {
        'member': member,
        'current_loans': current_loans,
        'loan_history': loan_history,
    }
    return render(request, 'members/member_detail.html', context)


@login_required
def member_create(request):
    """
    Create a new member.
    """
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            messages.success(request, f'Member "{member.full_name}" added successfully!')
            return redirect('member_detail', pk=member.pk)
    else:
        form = MemberForm()
    
    context = {
        'form': form,
        'title': 'Add New Member'
    }
    return render(request, 'members/member_form.html', context)


@login_required
def member_update(request, pk):
    """
    Update an existing member.
    """
    member = get_object_or_404(Member, pk=pk)
    
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            member = form.save()
            messages.success(request, f'Member "{member.full_name}" updated successfully!')
            return redirect('member_detail', pk=member.pk)
    else:
        form = MemberForm(instance=member)
    
    context = {'form': form, 'member': member}
    return render(request, 'members/member_form.html', context)


@login_required
def member_delete(request, pk):
    """
    Delete a member.
    """
    member = get_object_or_404(Member, pk=pk)
    
    if request.method == 'POST':
        member_name = member.full_name
        member.delete()
        messages.success(request, f'Member "{member_name}" deleted successfully!')
        return redirect('member_list')
    
    context = {'member': member}
    return render(request, 'members/member_confirm_delete.html', context)


@login_required
def loan_list(request):
    """
    List all loans with filters.
    """
    status_filter = request.GET.get('status', '')
    
    loans = Loan.objects.select_related('book', 'member').all()
    
    if status_filter:
        loans = loans.filter(status=status_filter)
    
    # Calculate fines for overdue loans
    for loan in loans.filter(status='OVE'):
        loan.calculate_fine()
    
    # Calculate statistics
    total_loans = loans.count()
    
    # Count active loans
    active_count = 0
    overdue_count = 0
    total_fines = 0
    
    for loan in loans:
        if loan.status == 'ACT':
            active_count += 1
        elif loan.status == 'OVE':
            overdue_count += 1
            if not loan.fine_paid:
                total_fines += float(loan.fine_amount)
    
    context = {
        'loans': loans,
        'status_choices': Loan.STATUS_CHOICES,
        'current_status': status_filter,
        'total_loans': total_loans,
        'active_loans': active_count,
        'overdue_loans': overdue_count,
        'total_fines': f"{total_fines:.2f}",
    }
    return render(request, 'loans/loan_list.html', context)


@login_required
def loan_create(request):
    """
    Create a new loan.
    """
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            
            # Update book availability
            if loan.book.borrow_book():
                # Update member's borrowed count
                if loan.member.increment_borrowed_count():
                    loan.save()
                    messages.success(request, f'Book "{loan.book.title}" loaned to {loan.member.full_name} successfully!')
                    return redirect('loan_list')
                else:
                    # Rollback book borrow if member can't borrow
                    loan.book.return_book()
                    messages.error(request, 'Member cannot borrow more books.')
            else:
                messages.error(request, 'Book is not available for loan.')
    else:
        form = LoanForm()
    
    context = {'form': form}
    return render(request, 'loans/loan_form.html', context)


@login_required
def loan_return(request, pk):
    """
    Return a book loan.
    """
    loan = get_object_or_404(Loan, pk=pk)
    
    if request.method == 'POST':
        form = ReturnForm(request.POST, loan=loan)
        if form.is_valid():
            # Mark loan as returned
            loan.return_date = timezone.now().date()
            loan.status = 'RET'
            loan.notes = form.cleaned_data.get('return_notes', '')
            
            # Handle fine payment if overdue
            if loan.status == 'OVE' and request.POST.get('mark_fine_paid'):
                loan.fine_paid = True
            
            loan.save()
            
            # Update book availability
            loan.book.available_copies += 1
            loan.book.save()
            
            # Update member's borrowed count
            if loan.member.current_books_borrowed > 0:
                loan.member.current_books_borrowed -= 1
                loan.member.save()
            
            messages.success(request, f'Book "{loan.book.title}" returned successfully!')
            return redirect('loan_list')
    else:
        form = ReturnForm(loan=loan)
    
    context = {
        'form': form,
        'loan': loan,
    }
    return render(request, 'loans/loan_return.html', context)


def book_availability(request, pk):
    """
    Check book availability and due dates.
    """
    book = get_object_or_404(Book, pk=pk)
    active_loans = book.loans.filter(status='ACT').select_related('member')
    
    context = {
        'book': book,
        'active_loans': active_loans,
    }
    return render(request, 'books/book_availability.html', context)

