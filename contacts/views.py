"""
All views for authentication and contact management.
Each view handles one specific page/action.
"""

import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse

from .models import Contact
from .forms import SignupForm, LoginForm, ContactForm


# ─── HOME VIEW ─────────────────────────────────────────────────────────────────

def home_view(request):
    """Landing page - redirect to dashboard if logged in."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


# ─── AUTH VIEWS ────────────────────────────────────────────────────────────────

def signup_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after signup
            messages.success(request, f'Welcome, {user.username}! Your account is ready.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = SignupForm()

    return render(request, 'auth/signup.html', {'form': form})


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    """Log out and redirect to login."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# ─── CONTACT VIEWS ─────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    """Show all contacts for the logged-in user, with optional search and category filter."""
    query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '').strip()
    contacts = Contact.objects.filter(user=request.user)

    # Get all unique categories for this user
    all_categories = Contact.objects.filter(user=request.user).exclude(category='').values_list('category', flat=True).distinct().order_by('category')

    # Filter by category if specified
    if category_filter:
        contacts = contacts.filter(category=category_filter)

    # Search across name, phone, email, and address
    if query:
        contacts = contacts.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query) |
            Q(address__icontains=query)
        )
    
    # Separate emergency, favorites and regular contacts
    emergency_contacts = contacts.filter(is_emergency=True)
    favorites = contacts.filter(is_favorite=True, is_emergency=False)
    regular_contacts = contacts.filter(is_favorite=False, is_emergency=False)

    return render(request, 'contacts/dashboard.html', {
        'emergency_contacts': emergency_contacts,
        'favorites': favorites,
        'regular_contacts': regular_contacts,
        'query': query,
        'category_filter': category_filter,
        'all_categories': all_categories,
        'total': Contact.objects.filter(user=request.user).count(),
    })


@login_required
def add_contact(request):
    """Show form to add a new contact."""
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user  # Link to current user
            contact.save()
            messages.success(request, f'"{contact.name}" has been added!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = ContactForm(user=request.user)

    return render(request, 'contacts/contact_form.html', {
        'form': form,
        'title': 'Add Contact',
        'button_label': 'Add Contact',
    })


@login_required
def edit_contact(request, pk):
    """Show pre-filled form to edit an existing contact."""
    # get_object_or_404 ensures user can only edit THEIR contacts
    contact = get_object_or_404(Contact, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES, instance=contact, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{contact.name}" has been updated!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = ContactForm(instance=contact, user=request.user)

    return render(request, 'contacts/contact_form.html', {
        'form': form,
        'contact': contact,
        'title': f'Edit {contact.name}',
        'button_label': 'Save Changes',
    })


@login_required
def delete_contact(request, pk):
    """Delete a contact (POST only for safety)."""
    contact = get_object_or_404(Contact, pk=pk, user=request.user)

    if request.method == 'POST':
        name = contact.name
        # Delete the profile image file if it exists
        if contact.image:
            contact.image.delete(save=False)
        contact.delete()
        messages.success(request, f'"{name}" has been deleted.')

    return redirect('dashboard')


@login_required
def toggle_favorite(request, pk):
    """Toggle favorite status of a contact."""
    contact = get_object_or_404(Contact, pk=pk, user=request.user)
    
    contact.is_favorite = not contact.is_favorite
    contact.save()
    
    if contact.is_favorite:
        messages.success(request, f'"{contact.name}" added to favorites!')
    else:
        messages.info(request, f'"{contact.name}" removed from favorites.')
    
    return redirect('dashboard')


@login_required
def export_contacts(request):
    """Export all contacts to CSV file."""
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contacts_export.csv"'
    
    writer = csv.writer(response)
    # Write header row
    writer.writerow(['Name', 'Phone', 'Email', 'Address', 'Category', 'Notes', 'Favorite', 'Emergency', 'Has Reminder', 'Reminder Date', 'Reminder Note'])
    
    # Write contact data
    contacts = Contact.objects.filter(user=request.user).order_by('name')
    for contact in contacts:
        writer.writerow([
            contact.name,
            contact.phone,
            contact.email,
            contact.address,
            contact.category,
            contact.notes,
            'Yes' if contact.is_favorite else 'No',
            'Yes' if contact.is_emergency else 'No',
            'Yes' if contact.has_reminder else 'No',
            contact.reminder_date.strftime('%Y-%m-%d %H:%M') if contact.reminder_date else '',
            contact.reminder_note
        ])
    
    messages.success(request, f'{contacts.count()} contacts exported successfully!')
    return response


@login_required
def export_single_contact(request, pk):
    """Export a single contact as vCard (.vcf) file."""
    contact = get_object_or_404(Contact, pk=pk, user=request.user)
    
    # Create vCard content (version 3.0 format)
    vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{contact.name}
TEL;TYPE=CELL:{contact.phone}"""
    
    if contact.email:
        vcard += f"\nEMAIL:{contact.email}"
    
    if contact.address:
        vcard += f"\nADR;TYPE=HOME:;;{contact.address.replace(chr(10), ' ')};;;;"
    
    if contact.category:
        vcard += f"\nCATEGORIES:{contact.category}"
    
    if contact.notes:
        vcard += f"\nNOTE:{contact.notes.replace(chr(10), ' ')}"
    
    vcard += "\nEND:VCARD"
    
    # Create response
    response = HttpResponse(vcard, content_type='text/vcard')
    safe_name = ''.join(c for c in contact.name if c.isalnum() or c in (' ', '_')).strip()
    response['Content-Disposition'] = f'attachment; filename="{safe_name}.vcf"'
    
    messages.success(request, f'"{contact.name}" downloaded as vCard!')
    return response


@login_required
def export_single_contact_csv(request, pk):
    """Export a single contact as CSV file."""
    contact = get_object_or_404(Contact, pk=pk, user=request.user)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    safe_name = ''.join(c for c in contact.name if c.isalnum() or c in (' ', '_')).strip()
    response['Content-Disposition'] = f'attachment; filename="{safe_name}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Phone', 'Email', 'Address', 'Category', 'Notes', 'Favorite', 'Emergency', 'Has Reminder', 'Reminder Date', 'Reminder Note'])
    
    writer.writerow([
        contact.name,
        contact.phone,
        contact.email,
        contact.address,
        contact.category,
        contact.notes,
        'Yes' if contact.is_favorite else 'No',
        'Yes' if contact.is_emergency else 'No',
        'Yes' if contact.has_reminder else 'No',
        contact.reminder_date.strftime('%Y-%m-%d %H:%M') if contact.reminder_date else '',
        contact.reminder_note
    ])
    
    messages.success(request, f'"{contact.name}" exported successfully!')
    return response


@login_required
def import_contacts(request):
    """Import contacts from CSV file."""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # Validate file extension
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a valid CSV file.')
            return redirect('dashboard')
        
        try:
            # Decode and read CSV
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            imported_count = 0
            skipped_count = 0
            
            for row in reader:
                # Validate required fields
                name = row.get('Name', '').strip()
                phone = row.get('Phone', '').strip()
                
                if not name or not phone:
                    skipped_count += 1
                    continue
                
                # Parse boolean fields
                is_favorite = row.get('Favorite', '').strip().lower() in ['yes', 'true', '1']
                is_emergency = row.get('Emergency', '').strip().lower() in ['yes', 'true', '1']
                has_reminder = row.get('Has Reminder', '').strip().lower() in ['yes', 'true', '1']
                
                # Parse reminder date
                reminder_date = None
                reminder_date_str = row.get('Reminder Date', '').strip()
                if reminder_date_str and has_reminder:
                    try:
                        from datetime import datetime
                        from django.utils import timezone
                        # Try to parse the date
                        dt = datetime.strptime(reminder_date_str, '%Y-%m-%d %H:%M')
                        reminder_date = timezone.make_aware(dt)
                    except:
                        pass  # Skip invalid dates
                
                # Create contact
                Contact.objects.create(
                    user=request.user,
                    name=name,
                    phone=phone,
                    email=row.get('Email', '').strip(),
                    address=row.get('Address', '').strip(),
                    category=row.get('Category', '').strip(),
                    notes=row.get('Notes', '').strip(),
                    is_favorite=is_favorite,
                    is_emergency=is_emergency,
                    has_reminder=has_reminder,
                    reminder_date=reminder_date,
                    reminder_note=row.get('Reminder Note', '').strip()
                )
                imported_count += 1
            
            if imported_count > 0:
                messages.success(request, f'{imported_count} contacts imported successfully!')
            if skipped_count > 0:
                messages.warning(request, f'{skipped_count} rows skipped (missing name or phone).')
            
        except Exception as e:
            messages.error(request, f'Error importing CSV: {str(e)}')
        
        return redirect('dashboard')
    
    return redirect('dashboard')


@login_required
def delete_all_contacts(request):
    """Delete all contacts for the current user."""
    if request.method == 'POST':
        confirmation = request.POST.get('confirmation', '').strip()
        
        # Double-check confirmation text
        if confirmation == 'DELETE ALL':
            contacts = Contact.objects.filter(user=request.user)
            count = contacts.count()
            
            # Delete all profile images first
            for contact in contacts:
                if contact.image:
                    contact.image.delete(save=False)
            
            # Delete all contacts
            contacts.delete()
            
            messages.success(request, f'All {count} contacts have been deleted.')
        else:
            messages.error(request, 'Confirmation text did not match. No contacts were deleted.')
    
    return redirect('dashboard')


@login_required
def reminders_view(request):
    """Show all upcoming reminders for the logged-in user."""
    from django.utils import timezone
    
    now = timezone.now()
    
    # Get all contacts with reminders
    upcoming = Contact.objects.filter(
        user=request.user, 
        has_reminder=True,
        reminder_date__gte=now
    ).order_by('reminder_date')
    
    past = Contact.objects.filter(
        user=request.user, 
        has_reminder=True,
        reminder_date__lt=now
    ).order_by('-reminder_date')
    
    # Get today's reminders
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    today = Contact.objects.filter(
        user=request.user,
        has_reminder=True,
        reminder_date__gte=today_start,
        reminder_date__lte=today_end
    ).order_by('reminder_date')
    
    return render(request, 'contacts/reminders.html', {
        'upcoming': upcoming,
        'past': past,
        'today': today,
        'total': Contact.objects.filter(user=request.user, has_reminder=True).count(),
    })


@login_required
def check_reminders_api(request):
    """API endpoint to check for due reminders (returns JSON for browser notifications)."""
    from django.utils import timezone
    from django.http import JsonResponse
    from datetime import timedelta
    
    now = timezone.now()
    
    # Check for reminders due in the next 15 minutes
    upcoming_window = now + timedelta(minutes=15)
    
    due_soon = Contact.objects.filter(
        user=request.user,
        has_reminder=True,
        reminder_date__gte=now,
        reminder_date__lte=upcoming_window
    ).order_by('reminder_date')
    
    reminders_data = []
    for contact in due_soon:
        time_until = contact.reminder_date - now
        minutes_until = int(time_until.total_seconds() / 60)
        
        reminders_data.append({
            'id': contact.pk,
            'name': contact.name,
            'phone': contact.phone,
            'reminder_date': contact.reminder_date.strftime('%Y-%m-%d %H:%M:%S'),
            'reminder_note': contact.reminder_note or '',
            'minutes_until': minutes_until,
            'edit_url': f'/edit/{contact.pk}/'
        })
    
    return JsonResponse({
        'count': len(reminders_data),
        'reminders': reminders_data
    })




@login_required
def chatbot_view(request):
    """Chatbot assistant page."""
    return render(request, 'contacts/chatbot.html', {
        'total_contacts': Contact.objects.filter(user=request.user).count(),
        'emergency_contacts': Contact.objects.filter(user=request.user, is_emergency=True).count(),
        'reminders': Contact.objects.filter(user=request.user, has_reminder=True).count(),
    })


@login_required
def chatbot_api(request):
    """AI Chatbot API endpoint that responds to user queries."""
    from django.http import JsonResponse
    from django.utils import timezone
    from datetime import timedelta
    import json
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=400)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').lower().strip()
    except:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    if not user_message:
        return JsonResponse({'error': 'Message is required'}, status=400)
    
    # Get user's contacts
    contacts = Contact.objects.filter(user=request.user)
    
    # AI Response Logic
    response = ""
    suggestions = []
    
    # Search for contact by name
    if any(word in user_message for word in ['find', 'search', 'look for', 'show me', 'who is']):
        # Extract potential name
        words = user_message.split()
        query = ' '.join(words[1:]) if len(words) > 1 else ''
        
        if query:
            found_contacts = contacts.filter(name__icontains=query)
            if found_contacts.exists():
                contact_list = []
                for c in found_contacts[:5]:
                    contact_list.append(f"📞 **{c.name}** - {c.phone}")
                    if c.email:
                        contact_list[-1] += f" | ✉️ {c.email}"
                    if c.is_emergency:
                        contact_list[-1] += " 🚨"
                
                response = f"I found {found_contacts.count()} contact(s):\n\n" + "\n".join(contact_list)
                suggestions = ["Show all contacts", "Add new contact", "Show emergency contacts"]
            else:
                response = f"❌ I couldn't find any contacts matching '{query}'.\n\nWould you like to add a new contact?"
                suggestions = ["Add new contact", "Show all contacts", "Import contacts"]
        else:
            response = "🔍 Please tell me the name you're looking for. For example: 'Find John' or 'Search for Maria'"
    
    # Count contacts
    elif any(word in user_message for word in ['how many', 'count', 'total']):
        total = contacts.count()
        emergency = contacts.filter(is_emergency=True).count()
        favorites = contacts.filter(is_favorite=True).count()
        reminders = contacts.filter(has_reminder=True).count()
        
        response = f"📊 **Your Contact Statistics:**\n\n"
        response += f"• Total Contacts: **{total}**\n"
        response += f"• Emergency Contacts: **{emergency}** 🚨\n"
        response += f"• Favorite Contacts: **{favorites}** ⭐\n"
        response += f"• Reminders Set: **{reminders}** 🔔"
        suggestions = ["Show all contacts", "Show emergency contacts", "Show reminders"]
    
    # Emergency contacts
    elif any(word in user_message for word in ['emergency', 'urgent']):
        emergency_contacts = contacts.filter(is_emergency=True)
        if emergency_contacts.exists():
            contact_list = []
            for c in emergency_contacts:
                contact_list.append(f"🚨 **{c.name}** - {c.phone}")
            
            response = f"📋 **Your {emergency_contacts.count()} Emergency Contact(s):**\n\n" + "\n".join(contact_list)
            suggestions = ["Show all contacts", "Add emergency contact"]
        else:
            response = "⚠️ You don't have any emergency contacts set up yet.\n\nIt's important to have emergency contacts! Would you like to add one?"
            suggestions = ["Add new contact", "How to add emergency contact"]
    
    # Reminders
    elif any(word in user_message for word in ['reminder', 'remind', 'upcoming']):
        now = timezone.now()
        upcoming = contacts.filter(has_reminder=True, reminder_date__gte=now).order_by('reminder_date')
        
        if upcoming.exists():
            reminder_list = []
            for c in upcoming[:5]:
                time_str = c.reminder_date.strftime('%b %d, %Y at %I:%M %p')
                reminder_list.append(f"🔔 **{c.name}** - {time_str}")
                if c.reminder_note:
                    reminder_list[-1] += f"\n   💡 {c.reminder_note}"
            
            response = f"📅 **Your {upcoming.count()} Upcoming Reminder(s):**\n\n" + "\n\n".join(reminder_list)
            suggestions = ["View all reminders", "Add new reminder", "Show dashboard"]
        else:
            response = "📭 You don't have any upcoming reminders.\n\nWould you like to set a reminder for a contact?"
            suggestions = ["Add reminder", "Show all contacts"]
    
    # Help or greeting
    elif any(word in user_message for word in ['help', 'what can you', 'how to', 'guide']):
        response = """👋 **Hi! I'm your Contactify Assistant!**

I can help you with:

🔍 **Search Contacts**
• "Find John"
• "Search for Maria"

📊 **Statistics**
• "How many contacts do I have?"
• "Show my stats"

🚨 **Emergency Contacts**
• "Show emergency contacts"
• "List urgent contacts"

🔔 **Reminders**
• "Show my reminders"
• "Upcoming reminders"

📱 **Quick Actions**
• "Add new contact"
• "Export contacts"
• "Import contacts"

Just ask me anything! 😊"""
        suggestions = ["Find a contact", "Show statistics", "Show emergency contacts", "View reminders"]
    
    # Add contact
    elif any(word in user_message for word in ['add', 'create', 'new contact']):
        response = "➕ **Let's add a new contact!**\n\nClick the button below to open the add contact form, or click 'Add Contact' in the dashboard."
        suggestions = ["Go to add contact", "Show dashboard", "Import contacts"]
    
    # Export/Download
    elif any(word in user_message for word in ['export', 'download', 'backup']):
        response = """💾 **Export Your Contacts**

You can export your contacts in multiple formats:

📄 **All Contacts (CSV)**
• Go to Dashboard
• Scroll to bottom
• Click "Export CSV"

📇 **Individual Contact**
• Click download button on any contact card
• Choose format: vCard, CSV, or PDF

The PDF format creates a beautiful business card! 🎨"""
        suggestions = ["Show dashboard", "How to import contacts"]
    
    # Categories
    elif any(word in user_message for word in ['category', 'group', 'family', 'friend', 'work']):
        categories = contacts.exclude(category='').values_list('category', flat=True).distinct()
        if categories:
            cat_list = [f"• {cat}" for cat in categories]
            response = f"📁 **Your Contact Categories:**\n\n" + "\n".join(cat_list)
            response += "\n\nYou can filter contacts by category from the dashboard!"
            suggestions = ["Show dashboard", "Add new contact"]
        else:
            response = "📁 You haven't organized your contacts into categories yet.\n\nCategories help you group contacts like Family, Friends, Work, etc."
            suggestions = ["Add new contact", "Show all contacts"]
    
    # Favorites
    elif any(word in user_message for word in ['favorite', 'starred', 'important']):
        favorites = contacts.filter(is_favorite=True)
        if favorites.exists():
            fav_list = []
            for c in favorites[:5]:
                fav_list.append(f"⭐ **{c.name}** - {c.phone}")
            
            response = f"⭐ **Your {favorites.count()} Favorite Contact(s):**\n\n" + "\n".join(fav_list)
            suggestions = ["Show all contacts", "Add new favorite"]
        else:
            response = "⭐ You haven't marked any contacts as favorites yet.\n\nClick the star icon on any contact to add them to favorites!"
            suggestions = ["Show dashboard", "Add new contact"]
    
    # Default response
    else:
        response = f"""🤔 I'm not sure about "{user_message}".

Try asking me:
• "Find [name]" - Search for a contact
• "How many contacts?" - See statistics
• "Show emergency contacts"
• "View my reminders"
• "Help" - See all commands

What would you like to know?"""
        suggestions = ["Help", "Show statistics", "Find a contact"]
    
    return JsonResponse({
        'response': response,
        'suggestions': suggestions,
        'timestamp': timezone.now().isoformat()
    })



@login_required
def stats_view(request):
    """Statistics dashboard showing contact insights."""
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta
    
    contacts = Contact.objects.filter(user=request.user)
    now = timezone.now()
    
    # Basic stats
    total = contacts.count()
    emergency = contacts.filter(is_emergency=True).count()
    favorites = contacts.filter(is_favorite=True).count()
    reminders = contacts.filter(has_reminder=True).count()
    
    # Detail stats
    with_email = contacts.exclude(email='').count()
    with_address = contacts.exclude(address='').count()
    with_photo = contacts.exclude(image='').count()
    with_notes = contacts.exclude(notes='').count()
    
    # Activity stats
    month_ago = now - timedelta(days=30)
    week_ago = now - timedelta(days=7)
    added_this_month = contacts.filter(created_at__gte=month_ago).count()
    updated_this_week = contacts.filter(updated_at__gte=week_ago).count()
    
    most_recent_contact = contacts.order_by('-created_at').first()
    most_recent = most_recent_contact.name if most_recent_contact else 'None'
    
    # Category breakdown
    categories = {}
    for contact in contacts.exclude(category=''):
        cat = contact.category
        categories[cat] = categories.get(cat, 0) + 1
    
    # Sort by count
    categories = dict(sorted(categories.items(), key=lambda x: x[1], reverse=True))
    
    return render(request, 'contacts/stats.html', {
        'stats': {
            'total': total,
            'emergency': emergency,
            'favorites': favorites,
            'reminders': reminders,
            'with_email': with_email,
            'with_address': with_address,
            'with_photo': with_photo,
            'with_notes': with_notes,
            'added_this_month': added_this_month,
            'updated_this_week': updated_this_week,
            'most_recent': most_recent,
            'categories': categories,
        }
    })
