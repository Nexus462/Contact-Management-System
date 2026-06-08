"""
Script to create test data for ContactVault application.
Run this with: python manage.py shell < create_test_data.py
"""

from django.contrib.auth.models import User
from contacts.models import Contact

# Create test users
print("Creating test users...")

# User 1: testuser
user1, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
)
if created:
    user1.set_password('Test@123')
    user1.save()
    print(f"✓ Created user: testuser (password: Test@123)")
else:
    print(f"✓ User already exists: testuser")

# User 2: demo
user2, created = User.objects.get_or_create(
    username='demo',
    defaults={
        'email': 'demo@example.com',
        'first_name': 'Demo',
        'last_name': 'Account'
    }
)
if created:
    user2.set_password('Demo@123')
    user2.save()
    print(f"✓ Created user: demo (password: Demo@123)")
else:
    print(f"✓ User already exists: demo")

# Create test contacts for testuser
print("\nCreating test contacts for testuser...")

test_contacts = [
    {
        'name': 'John Smith',
        'phone': '+1-555-0101',
        'email': 'john.smith@email.com',
        'address': '123 Main St, New York, NY 10001',
        'is_favorite': True
    },
    {
        'name': 'Sarah Johnson',
        'phone': '+1-555-0102',
        'email': 'sarah.j@email.com',
        'address': '456 Oak Ave, Los Angeles, CA 90001',
        'is_favorite': True
    },
    {
        'name': 'Michael Brown',
        'phone': '+1-555-0103',
        'email': 'mbrown@email.com',
        'address': '789 Pine Rd, Chicago, IL 60601',
        'is_favorite': False
    },
    {
        'name': 'Emily Davis',
        'phone': '+1-555-0104',
        'email': 'emily.davis@email.com',
        'address': '321 Elm St, Houston, TX 77001',
        'is_favorite': False
    },
    {
        'name': 'David Wilson',
        'phone': '+1-555-0105',
        'email': 'dwilson@email.com',
        'address': '654 Maple Dr, Phoenix, AZ 85001',
        'is_favorite': True
    },
    {
        'name': 'Jessica Martinez',
        'phone': '+1-555-0106',
        'email': 'jmartinez@email.com',
        'address': '987 Cedar Ln, Philadelphia, PA 19101',
        'is_favorite': False
    },
    {
        'name': 'James Anderson',
        'phone': '+1-555-0107',
        'email': 'james.a@email.com',
        'address': '147 Birch Blvd, San Antonio, TX 78201',
        'is_favorite': False
    },
    {
        'name': 'Lisa Taylor',
        'phone': '+1-555-0108',
        'email': 'lisa.taylor@email.com',
        'address': '258 Spruce Way, San Diego, CA 92101',
        'is_favorite': False
    },
    {
        'name': 'Robert Thomas',
        'phone': '+1-555-0109',
        'email': 'rthomas@email.com',
        'address': '369 Willow Ct, Dallas, TX 75201',
        'is_favorite': True
    },
    {
        'name': 'Jennifer White',
        'phone': '+1-555-0110',
        'email': 'jwhite@email.com',
        'address': '741 Ash St, San Jose, CA 95101',
        'is_favorite': False
    },
]

for contact_data in test_contacts:
    contact, created = Contact.objects.get_or_create(
        user=user1,
        phone=contact_data['phone'],
        defaults=contact_data
    )
    if created:
        print(f"✓ Created contact: {contact.name}")
    else:
        print(f"✓ Contact already exists: {contact.name}")

print(f"\n✅ Test data creation complete!")
print(f"\nTest Accounts:")
print(f"  Username: testuser | Password: Test@123")
print(f"  Username: demo     | Password: Demo@123")
print(f"\nTotal contacts for testuser: {Contact.objects.filter(user=user1).count()}")
print(f"Favorites: {Contact.objects.filter(user=user1, is_favorite=True).count()}")
