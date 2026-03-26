from .models import About, Project, Skill, ContactMessage

def about_context(request):
    """Add about object and other global data to all templates automatically"""
    return {
        'about': About.objects.first(),
        'total_projects': Project.objects.count(),
        'total_skills': Skill.objects.count(),
        'total_messages': ContactMessage.objects.count(),
        'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
    }
