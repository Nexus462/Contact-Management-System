"""
Custom validators for password strength and other validations.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PasswordStrengthValidator:
    """
    Validates that the password meets strength requirements:
    - At least 8 characters
    - At least 1 uppercase letter
    - At least 1 number
    - At least 1 special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
    """
    
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(
                _("Password must be at least 8 characters long."),
                code='password_too_short',
            )
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Password must contain at least 1 uppercase letter."),
                code='password_no_upper',
            )
        
        if not re.search(r'\d', password):
            raise ValidationError(
                _("Password must contain at least 1 number."),
                code='password_no_number',
            )
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            raise ValidationError(
                _("Password must contain at least 1 special character (!@#$%^&*()_+-=[]{}|;:,.<>?)."),
                code='password_no_special',
            )
    
    def get_help_text(self):
        return _(
            "Your password must contain at least 8 characters, including 1 uppercase letter, "
            "1 number, and 1 special character (!@#$%^&*()_+-=[]{}|;:,.<>?)."
        )
