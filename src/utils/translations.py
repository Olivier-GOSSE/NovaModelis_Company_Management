"""
Module for handling translations in the application.
"""
import os
import json
import logging

# Default language
DEFAULT_LANGUAGE = "fr"  # French as default

# Available languages
AVAILABLE_LANGUAGES = ["fr", "en"]

# Translations dictionary
_translations = {
    "fr": {
        # Main window
        "app_title": "NovaModelis",
        "dashboard": "Tableau de bord",
        "printers": "Imprimantes",
        "customers": "Clients",
        "orders": "Commandes",
        "settings": "Paramètres",
        "logout": "Déconnexion",
        "logout_confirm": "Êtes-vous sûr de vouloir vous déconnecter ?",
        
        # Dashboard view
        "active_print_jobs": "Travaux d'impression actifs",
        "recent_orders": "Commandes récentes",
        "revenue_overview": "Aperçu des revenus",
        "printer_status": "État des imprimantes",
        "today": "Aujourd'hui",
        "this_week": "Cette semaine",
        "this_month": "Ce mois",
        "this_year": "Cette année",
        "view_all": "Voir tout",
        "no_active_jobs": "Aucun travail d'impression actif",
        "no_recent_orders": "Aucune commande récente",
        
        # Printers view
        "add_printer": "Ajouter une imprimante",
        "search_printers": "Rechercher des imprimantes...",
        "name": "Nom",
        "build_volume": "Volume d'impression",
        "status": "Statut",
        "ip_address": "Adresse IP",
        "operating_hours": "Heures de fonctionnement",
        "actions": "Actions",
        "edit_printer": "Modifier l'imprimante",
        "delete_printer": "Supprimer l'imprimante",
        "active_print_jobs": "Travaux d'impression actifs",
        "job_name": "Nom du travail",
        "printer": "Imprimante",
        "started": "Démarré",
        "progress": "Progression",
        "est_completion": "Fin estimée",
        "view_job": "Voir le travail",
        "pause_job": "Mettre en pause",
        "cancel_job": "Annuler",
        "add_edit_printer": "Ajouter/Modifier une imprimante",
        "edit": "Modifier",
        "add": "Ajouter",
        "model": "Modèle",
        "manufacturer": "Fabricant",
        "api_key": "Clé API",
        "notes": "Notes",
        "save": "Enregistrer",
        "cancel": "Annuler",
        "validation_error": "Erreur de validation",
        "name_required": "Le nom est requis.",
        "model_required": "Le modèle est requis.",
        "manufacturer_required": "Le fabricant est requis.",
        "error": "Erreur",
        "printer_not_found": "Imprimante non trouvée.",
        "error_occurred": "Une erreur est survenue : {0}",
        "cannot_delete": "Impossible de supprimer",
        "cannot_delete_printer": "Impossible de supprimer l'imprimante '{0}' car elle a des travaux d'impression actifs.",
        "confirm_deletion": "Confirmer la suppression",
        "confirm_delete_printer": "Êtes-vous sûr de vouloir supprimer l'imprimante '{0}' ?",
        
        # Customers view
        "add_customer": "Ajouter un client",
        "search_customers": "Rechercher des clients...",
        "email": "Email",
        "phone": "Téléphone",
        "address": "Adresse",
        "total_orders": "Total des commandes",
        "last_order": "Dernière commande",
        "edit_customer": "Modifier le client",
        "delete_customer": "Supprimer le client",
        "add_edit_customer": "Ajouter/Modifier un client",
        "first_name": "Prénom",
        "last_name": "Nom",
        "company": "Entreprise",
        "street": "Rue",
        "city": "Ville",
        "state": "État/Province",
        "zip": "Code postal",
        "country": "Pays",
        "first_name_required": "Le prénom est requis.",
        "last_name_required": "Le nom est requis.",
        "email_required": "L'email est requis.",
        "customer_not_found": "Client non trouvé.",
        "cannot_delete_customer": "Impossible de supprimer le client '{0}' car il a des commandes.",
        "confirm_delete_customer": "Êtes-vous sûr de vouloir supprimer le client '{0}' ?",
        
        # Orders view
        "add_order": "Ajouter une commande",
        "search_orders": "Rechercher des commandes...",
        "order_number": "Numéro de commande",
        "customer": "Client",
        "date": "Date",
        "total": "Total",
        "payment_status": "Statut de paiement",
        "order_status": "Statut de la commande",
        "edit_order": "Modifier la commande",
        "delete_order": "Supprimer la commande",
        "view_order": "Voir la commande",
        "add_edit_order": "Ajouter/Modifier une commande",
        "order_details": "Détails de la commande",
        "items": "Articles",
        "quantity": "Quantité",
        "price": "Prix",
        "subtotal": "Sous-total",
        "tax": "Taxe",
        "shipping": "Livraison",
        "discount": "Remise",
        "add_item": "Ajouter un article",
        "remove_item": "Supprimer l'article",
        "order_not_found": "Commande non trouvée.",
        "cannot_delete_order": "Impossible de supprimer la commande car elle a des travaux d'impression actifs.",
        "confirm_delete_order": "Êtes-vous sûr de vouloir supprimer la commande '{0}' ?",
        
        # Settings view
        "general_settings": "Paramètres généraux",
        "user_settings": "Paramètres utilisateur",
        "appearance": "Apparence",
        "language": "Langue",
        "theme": "Thème",
        "dark_mode": "Mode sombre",
        "light_mode": "Mode clair",
        "notifications": "Notifications",
        "enable_notifications": "Activer les notifications",
        "sound_notifications": "Notifications sonores",
        "email_notifications": "Notifications par email",
        "auto_refresh": "Actualisation automatique",
        "refresh_interval": "Intervalle d'actualisation (secondes)",
        "user_profile": "Profil utilisateur",
        "change_password": "Changer le mot de passe",
        "current_password": "Mot de passe actuel",
        "new_password": "Nouveau mot de passe",
        "confirm_password": "Confirmer le mot de passe",
        "update_profile": "Mettre à jour le profil",
        "save_settings": "Enregistrer les paramètres",
        "settings_saved": "Paramètres enregistrés",
        "settings_saved_message": "Vos paramètres ont été enregistrés avec succès.",
        "password_changed": "Mot de passe changé",
        "password_changed_message": "Votre mot de passe a été changé avec succès.",
        "password_error": "Erreur de mot de passe",
        "current_password_incorrect": "Le mot de passe actuel est incorrect.",
        "passwords_dont_match": "Les nouveaux mots de passe ne correspondent pas.",
        "theme_changed": "Thème modifié",
        "theme_changed_message": "Thème changé en mode {0}.",
        "dark": "Sombre",
        "light": "Clair",
        
        # Login window
        "login": "Connexion",
        "username": "Nom d'utilisateur",
        "password": "Mot de passe",
        "remember_me": "Se souvenir de moi",
        "login_button": "Se connecter",
        "login_error": "Erreur de connexion",
        "invalid_credentials": "Nom d'utilisateur ou mot de passe invalide.",
        
        # Status values
        "idle": "Inactif",
        "printing": "Impression en cours",
        "maintenance": "Maintenance",
        "error_status": "Erreur",
        "offline": "Hors ligne",
        "paused": "En pause",
        "completed": "Terminé",
        "cancelled": "Annulé",
        "failed": "Échoué",
        "queued": "En attente",
        "paid": "Payé",
        "unpaid": "Non payé",
        "partial": "Partiel",
        "refunded": "Remboursé",
        "pending": "En attente",
        "processing": "En traitement",
        "shipped": "Expédié",
        "delivered": "Livré",
        "returned": "Retourné",
        
        # Misc
        "yes": "Oui",
        "no": "Non",
        "ok": "OK",
        "close": "Fermer",
        "unknown": "Inconnu",
        "none": "Aucun",
        "all": "Tous",
        "search": "Rechercher",
        "filter": "Filtrer",
        "sort": "Trier",
        "refresh": "Actualiser",
        "loading": "Chargement...",
        "no_results": "Aucun résultat",
        "no_data": "Aucune donnée",
        "not_available": "Non disponible",
        "hours_short": "h",
    },
    "en": {
        # Main window
        "app_title": "NovaModelis",
        "dashboard": "Dashboard",
        "printers": "Printers",
        "customers": "Customers",
        "orders": "Orders",
        "settings": "Settings",
        "logout": "Logout",
        "logout_confirm": "Are you sure you want to log out?",
        
        # Dashboard view
        "active_print_jobs": "Active Print Jobs",
        "recent_orders": "Recent Orders",
        "revenue_overview": "Revenue Overview",
        "printer_status": "Printer Status",
        "today": "Today",
        "this_week": "This Week",
        "this_month": "This Month",
        "this_year": "This Year",
        "view_all": "View All",
        "no_active_jobs": "No active print jobs",
        "no_recent_orders": "No recent orders",
        
        # Printers view
        "add_printer": "Add Printer",
        "search_printers": "Search printers...",
        "name": "Name",
        "build_volume": "Build Volume",
        "status": "Status",
        "ip_address": "IP Address",
        "operating_hours": "Operating Hours",
        "actions": "Actions",
        "edit_printer": "Edit Printer",
        "delete_printer": "Delete Printer",
        "active_print_jobs": "Active Print Jobs",
        "job_name": "Job Name",
        "printer": "Printer",
        "started": "Started",
        "progress": "Progress",
        "est_completion": "Est. Completion",
        "view_job": "View Job",
        "pause_job": "Pause Job",
        "cancel_job": "Cancel Job",
        "add_edit_printer": "Add/Edit Printer",
        "edit": "Edit",
        "add": "Add",
        "model": "Model",
        "manufacturer": "Manufacturer",
        "api_key": "API Key",
        "notes": "Notes",
        "save": "Save",
        "cancel": "Cancel",
        "validation_error": "Validation Error",
        "name_required": "Name is required.",
        "model_required": "Model is required.",
        "manufacturer_required": "Manufacturer is required.",
        "error": "Error",
        "printer_not_found": "Printer not found.",
        "error_occurred": "An error occurred: {0}",
        "cannot_delete": "Cannot Delete",
        "cannot_delete_printer": "Cannot delete printer '{0}' because it has active print jobs.",
        "confirm_deletion": "Confirm Deletion",
        "confirm_delete_printer": "Are you sure you want to delete printer '{0}'?",
        
        # Customers view
        "add_customer": "Add Customer",
        "search_customers": "Search customers...",
        "email": "Email",
        "phone": "Phone",
        "address": "Address",
        "total_orders": "Total Orders",
        "last_order": "Last Order",
        "edit_customer": "Edit Customer",
        "delete_customer": "Delete Customer",
        "add_edit_customer": "Add/Edit Customer",
        "first_name": "First Name",
        "last_name": "Last Name",
        "company": "Company",
        "street": "Street",
        "city": "City",
        "state": "State/Province",
        "zip": "ZIP/Postal Code",
        "country": "Country",
        "first_name_required": "First name is required.",
        "last_name_required": "Last name is required.",
        "email_required": "Email is required.",
        "customer_not_found": "Customer not found.",
        "cannot_delete_customer": "Cannot delete customer '{0}' because they have orders.",
        "confirm_delete_customer": "Are you sure you want to delete customer '{0}'?",
        
        # Orders view
        "add_order": "Add Order",
        "search_orders": "Search orders...",
        "order_number": "Order Number",
        "customer": "Customer",
        "date": "Date",
        "total": "Total",
        "payment_status": "Payment Status",
        "order_status": "Order Status",
        "edit_order": "Edit Order",
        "delete_order": "Delete Order",
        "view_order": "View Order",
        "add_edit_order": "Add/Edit Order",
        "order_details": "Order Details",
        "items": "Items",
        "quantity": "Quantity",
        "price": "Price",
        "subtotal": "Subtotal",
        "tax": "Tax",
        "shipping": "Shipping",
        "discount": "Discount",
        "add_item": "Add Item",
        "remove_item": "Remove Item",
        "order_not_found": "Order not found.",
        "cannot_delete_order": "Cannot delete order because it has active print jobs.",
        "confirm_delete_order": "Are you sure you want to delete order '{0}'?",
        
        # Settings view
        "general_settings": "General Settings",
        "user_settings": "User Settings",
        "appearance": "Appearance",
        "language": "Language",
        "theme": "Theme",
        "dark_mode": "Dark Mode",
        "light_mode": "Light Mode",
        "notifications": "Notifications",
        "enable_notifications": "Enable Notifications",
        "sound_notifications": "Sound Notifications",
        "email_notifications": "Email Notifications",
        "auto_refresh": "Auto Refresh",
        "refresh_interval": "Refresh Interval (seconds)",
        "user_profile": "User Profile",
        "change_password": "Change Password",
        "current_password": "Current Password",
        "new_password": "New Password",
        "confirm_password": "Confirm Password",
        "update_profile": "Update Profile",
        "save_settings": "Save Settings",
        "settings_saved": "Settings Saved",
        "settings_saved_message": "Your settings have been saved successfully.",
        "password_changed": "Password Changed",
        "password_changed_message": "Your password has been changed successfully.",
        "password_error": "Password Error",
        "current_password_incorrect": "Current password is incorrect.",
        "passwords_dont_match": "New passwords don't match.",
        "theme_changed": "Theme Changed",
        "theme_changed_message": "Theme changed to {0} mode.",
        "dark": "Dark",
        "light": "Light",
        
        # Login window
        "login": "Login",
        "username": "Username",
        "password": "Password",
        "remember_me": "Remember Me",
        "login_button": "Login",
        "login_error": "Login Error",
        "invalid_credentials": "Invalid username or password.",
        
        # Status values
        "idle": "Idle",
        "printing": "Printing",
        "maintenance": "Maintenance",
        "error_status": "Error",
        "offline": "Offline",
        "paused": "Paused",
        "completed": "Completed",
        "cancelled": "Cancelled",
        "failed": "Failed",
        "queued": "Queued",
        "paid": "Paid",
        "unpaid": "Unpaid",
        "partial": "Partial",
        "refunded": "Refunded",
        "pending": "Pending",
        "processing": "Processing",
        "shipped": "Shipped",
        "delivered": "Delivered",
        "returned": "Returned",
        
        # Misc
        "yes": "Yes",
        "no": "No",
        "ok": "OK",
        "close": "Close",
        "unknown": "Unknown",
        "none": "None",
        "all": "All",
        "search": "Search",
        "filter": "Filter",
        "sort": "Sort",
        "refresh": "Refresh",
        "loading": "Loading...",
        "no_results": "No results",
        "no_data": "No data",
        "not_available": "Not available",
        "hours_short": "h",
    }
}

# Current language
_current_language = DEFAULT_LANGUAGE

def set_language(language_code):
    """
    Set the current language.
    
    Args:
        language_code (str): The language code to set.
    
    Returns:
        bool: True if the language was set successfully, False otherwise.
    """
    global _current_language
    
    if language_code in AVAILABLE_LANGUAGES:
        _current_language = language_code
        logging.info(f"Language set to {language_code}")
        return True
    else:
        logging.warning(f"Unsupported language: {language_code}")
        return False

def get_current_language():
    """
    Get the current language code.
    
    Returns:
        str: The current language code.
    """
    return _current_language

def get_text(key, *args):
    """
    Get the translated text for the given key.
    
    Args:
        key (str): The translation key.
        *args: Optional arguments for string formatting.
    
    Returns:
        str: The translated text.
    """
    # Get the translation for the current language
    translation = _translations.get(_current_language, {}).get(key)
    
    # If the translation is not found, try the default language
    if translation is None:
        translation = _translations.get(DEFAULT_LANGUAGE, {}).get(key)
    
    # If still not found, return the key itself
    if translation is None:
        logging.warning(f"Translation not found for key: {key}")
        return key
    
    # Format the translation if args are provided
    if args:
        try:
            return translation.format(*args)
        except Exception as e:
            logging.error(f"Error formatting translation for key {key}: {str(e)}")
            return translation
    
    return translation

# Shorthand function for get_text
def _(key, *args):
    """
    Shorthand function for get_text.
    
    Args:
        key (str): The translation key.
        *args: Optional arguments for string formatting.
    
    Returns:
        str: The translated text.
    """
    return get_text(key, *args)
