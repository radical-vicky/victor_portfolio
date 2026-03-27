from .models import About, Project, Skill, ContactMessage, Testimonial

def about_context(request):
    """Add about object and stats to all templates"""
    return {
        'about': About.objects.first(),
        'total_projects': Project.objects.count(),
        'total_skills': Skill.objects.count(),
        'total_messages': ContactMessage.objects.count(),
        'total_testimonials': Testimonial.objects.filter(is_approved=True).count(),
        'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
    }