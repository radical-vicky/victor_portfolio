from .models import About

def about_context(request):
    """Add about object to all templates automatically"""
    return {
        'about': About.objects.first()
    }