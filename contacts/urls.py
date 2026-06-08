"""
URL patterns for the contacts app.
Maps URLs to view functions.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Home route
    path('',          views.home_view,     name='home'),
    
    # Auth routes
    path('dashboard/', views.dashboard,     name='dashboard'),
    path('signup/',   views.signup_view,   name='signup'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),

    # Contact CRUD routes
    path('add/',                    views.add_contact,      name='add_contact'),
    path('edit/<int:pk>/',          views.edit_contact,     name='edit_contact'),
    path('delete/<int:pk>/',        views.delete_contact,   name='delete_contact'),
    path('favorite/<int:pk>/',      views.toggle_favorite,  name='toggle_favorite'),
    
    # Reminders route
    path('reminders/',              views.reminders_view,   name='reminders'),
    path('api/check-reminders/',    views.check_reminders_api, name='check_reminders_api'),
    
    # Export single contact routes
    path('export/<int:pk>/vcard/',  views.export_single_contact, name='export_single_vcard'),
    path('export/<int:pk>/csv/',    views.export_single_contact_csv, name='export_single_csv'),
    # path('export/<int:pk>/pdf/',    views.export_single_contact_pdf, name='export_single_pdf'),  # Coming soon!
    
    # Chatbot route
    path('chatbot/',                views.chatbot_view, name='chatbot'),
    path('api/chatbot/',            views.chatbot_api, name='chatbot_api'),
    
    # Statistics route
    path('stats/',                  views.stats_view, name='stats'),
    
    # Settings routes
    path('settings/',               views.settings_view, name='settings'),
    path('settings/profile/',       views.update_profile, name='update_profile'),
    path('settings/password/',      views.change_password, name='change_password'),
    path('settings/delete/',        views.delete_account, name='delete_account'),
    
    # Import/Export routes
    path('export/',                 views.export_contacts,  name='export_contacts'),
    path('import/',                 views.import_contacts,  name='import_contacts'),
    path('delete-all/',             views.delete_all_contacts, name='delete_all_contacts'),
]
