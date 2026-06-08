"""
Forms for user authentication and contact management.
Django forms handle validation and rendering automatically.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator
from .models import Contact


class SignupForm(UserCreationForm):
    """Extended signup form with email field."""
    email = forms.EmailField(
        required=True,
        validators=[EmailValidator(message='Enter a valid email address.')],
        error_messages={
            'required': 'Email address is required.',
            'invalid': 'Enter a valid email address.',
        }
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Clean up default help texts and placeholders
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            field.help_text = ''

        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['username'].required = True
        self.fields['username'].error_messages = {
            'required': 'Username is required.',
            'unique': 'This username is already taken.',
        }
        
        self.fields['email'].widget.attrs['placeholder'] = 'Your email address'
        self.fields['password1'].widget.attrs['placeholder'] = 'Create a password'
        self.fields['password1'].required = True
        self.fields['password1'].error_messages = {
            'required': 'Password is required.',
        }
        
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'
        self.fields['password2'].required = True
        self.fields['password2'].error_messages = {
            'required': 'Please confirm your password.',
        }

    def clean_email(self):
        """Validate that the email is unique."""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already registered.')
        return email


class LoginForm(forms.Form):
    """Simple login form with username and password."""
    username = forms.CharField(
        required=True,
        error_messages={
            'required': 'Username is required.',
        },
        widget=forms.TextInput(attrs={
            'placeholder': 'Your username',
            'class': 'form-input',
        })
    )
    password = forms.CharField(
        required=True,
        error_messages={
            'required': 'Password is required.',
        },
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Your password',
            'class': 'form-input',
        })
    )


class ContactForm(forms.ModelForm):
    """Form for creating and editing contacts."""
    
    # Ethiopian phone validator: accepts formats like +251912345678, 0912345678, 251912345678, 09-12-34-56-78
    phone_validator = RegexValidator(
        regex=r'^(\+?251|0)?[79]\d{8}$|^(\+?251|0)?[79]\d[\s\-]?\d{2}[\s\-]?\d{2}[\s\-]?\d{2}[\s\-]?\d{2}$',
        message='Enter a valid Ethiopian phone number (e.g., 0912345678, +251912345678)'
    )
    
    name = forms.CharField(
        required=True,
        max_length=100,
        error_messages={
            'required': 'Name is required.',
            'max_length': 'Name cannot exceed 100 characters.',
        },
        widget=forms.TextInput(attrs={'placeholder': 'Full name', 'class': 'form-input'})
    )
    
    phone = forms.CharField(
        required=True,
        max_length=20,
        validators=[phone_validator],
        error_messages={
            'required': 'Phone number is required.',
            'max_length': 'Phone number cannot exceed 20 characters.',
        },
        widget=forms.TextInput(attrs={'placeholder': 'Ethiopian phone (e.g., 0912345678)', 'class': 'form-input'})
    )
    
    email = forms.EmailField(
        required=False,
        validators=[EmailValidator(message='Enter a valid email address.')],
        error_messages={
            'invalid': 'Enter a valid email address.',
        },
        widget=forms.EmailInput(attrs={'placeholder': 'Email address (optional)', 'class': 'form-input'})
    )
    
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Street address, city... (optional)', 'class': 'form-input', 'rows': 3})
    )
    
    image = forms.ImageField(
        required=False,
        error_messages={
            'invalid_image': 'Upload a valid image file.',
        },
        widget=forms.FileInput(attrs={'class': 'form-file'})
    )
    
    category = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Family, Friend, Work... (optional)', 'class': 'form-input', 'list': 'categoryList'})
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Additional notes or information... (optional)', 'class': 'form-input', 'rows': 3})
    )
    
    is_emergency = forms.BooleanField(
        required=False,
        label='Mark as Emergency Contact',
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )
    
    has_reminder = forms.BooleanField(
        required=False,
        label='Set a reminder for this contact',
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox', 'id': 'id_has_reminder', 'onchange': 'toggleReminderFields()'})
    )
    
    reminder_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-input',
            'id': 'id_reminder_date'
        }),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    
    reminder_note = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., Birthday, Anniversary, Follow-up call...',
            'class': 'form-input',
            'id': 'id_reminder_note'
        })
    )
    
    class Meta:
        model = Contact
        fields = ['name', 'phone', 'email', 'address', 'category', 'notes', 'is_emergency', 'has_reminder', 'reminder_date', 'reminder_note', 'image']
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.instance_id = kwargs.get('instance').pk if kwargs.get('instance') else None
        super().__init__(*args, **kwargs)
    
    def clean_phone(self):
        """Additional validation for Ethiopian phone number."""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove spaces and dashes for validation
            cleaned = phone.replace(' ', '').replace('-', '')
            
            # Remove country code prefix if present
            if cleaned.startswith('+251'):
                cleaned = cleaned[4:]
            elif cleaned.startswith('251'):
                cleaned = cleaned[3:]
            elif cleaned.startswith('0'):
                cleaned = cleaned[1:]
            
            # Ethiopian mobile numbers start with 9 or 7 and have 8 more digits
            if not (cleaned.startswith(('9', '7')) and len(cleaned) == 9):
                raise forms.ValidationError('Ethiopian phone numbers must start with 09 or 07 and have 9 digits total.')
        
        return phone
    
    def clean_email(self):
        """Ensure email is properly formatted if provided."""
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip().lower()
        return email
    
    def clean(self):
        """Check for duplicate contacts."""
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        phone = cleaned_data.get('phone')
        email = cleaned_data.get('email')
        
        if not self.user:
            return cleaned_data
        
        # Build query to find similar contacts
        duplicates = Contact.objects.filter(user=self.user)
        
        # Exclude current instance when editing
        if self.instance_id:
            duplicates = duplicates.exclude(pk=self.instance_id)
        
        # Check for exact phone match
        if phone:
            phone_match = duplicates.filter(phone=phone)
            if phone_match.exists():
                contact = phone_match.first()
                raise forms.ValidationError(
                    f'Already existed contact: "{contact.name}" has this phone number. '
                    f'Please check if this is a duplicate.'
                )
        
        # Check for exact email match (if email provided)
        if email:
            email_match = duplicates.filter(email__iexact=email)
            if email_match.exists():
                contact = email_match.first()
                self.add_error('email', 
                    f'Already existed contact: "{contact.name}" has this email. '
                    f'Please check if this is a duplicate.'
                )
        
        # Check for similar name (case-insensitive)
        if name:
            name_match = duplicates.filter(name__iexact=name)
            if name_match.exists():
                contact = name_match.first()
                self.add_error('name',
                    f'Already existed contact: "{contact.name}" with phone {contact.phone}. '
                    f'Please check if this is a duplicate.'
                )
        
        return cleaned_data
