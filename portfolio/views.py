from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Project, Skill, ContactMessage, About, Testimonial
from .forms import ContactForm, TestimonialForm
from django.contrib.admin.views.decorators import staff_member_required

def home(request):
    """Home page view - dynamically loads from database"""
    # Get featured projects
    featured_projects = Project.objects.filter(is_featured=True)[:3]
    
    # Get recent projects
    recent_projects = Project.objects.all().order_by('-created_date')[:6]
    
    # Get all skills
    skills = Skill.objects.all()
    
    # Get approved testimonials
    testimonials = Testimonial.objects.filter(is_approved=True)[:5]
    
    # Get about information
    about = About.objects.first()
    
    # Get counts for stats
    total_projects = Project.objects.count()
    total_skills = Skill.objects.count()
    total_testimonials = Testimonial.objects.filter(is_approved=True).count()
    
    context = {
        'featured_projects': featured_projects,
        'recent_projects': recent_projects,
        'skills': skills,
        'testimonials': testimonials,
        'about': about,
        'total_projects': total_projects,
        'total_skills': total_skills,
        'total_testimonials': total_testimonials,
    }
    return render(request, 'portfolio/home.html', context)
def projects(request):
    """Projects listing page"""
    all_projects = Project.objects.all().order_by('-created_date')
    
    # Get about information for sidebar
    about = About.objects.first()
    
    # Pagination
    paginator = Paginator(all_projects, 9)
    page_number = request.GET.get('page')
    projects_list = paginator.get_page(page_number)
    
    context = {
        'projects': projects_list,
        'total_projects': all_projects.count(),
        'about': about,  # Add this line
    }
    return render(request, 'portfolio/projects.html', context)

def project_detail(request, project_id):
    """Single project detail page"""
    project = get_object_or_404(Project, id=project_id)
    
    # Get related projects (same technologies)
    tech_words = project.technologies.split(',')
    related_projects = Project.objects.filter(
        technologies__icontains=tech_words[0].strip() if tech_words else ''
    ).exclude(id=project.id)[:3]
    
    context = {
        'project': project,
        'related_projects': related_projects,
    }
    return render(request, 'portfolio/project_detail.html', context)

def about(request):
    """About page"""
    about_info = About.objects.first()
    skills = Skill.objects.all()
    testimonials = Testimonial.objects.filter(is_approved=True)
    
    context = {
        'about': about_info,
        'skills': skills,
        'testimonials': testimonials,
    }
    return render(request, 'portfolio/about.html', context)

def contact(request):
    """Contact form view"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save to database
            contact = form.save()
            
            # Send email notification to admin
            try:
                contact_email = getattr(settings, 'CONTACT_EMAIL', None)
                if contact_email:
                    send_mail(
                        f"New Contact: {form.cleaned_data['subject']}",
                        f"From: {form.cleaned_data['name']}\nEmail: {form.cleaned_data['email']}\n\nMessage:\n{form.cleaned_data['message']}",
                        settings.DEFAULT_FROM_EMAIL,
                        [contact_email],
                        fail_silently=False,
                    )
                    
                    # Send confirmation to user
                    send_mail(
                        f"Thank you for contacting me - {form.cleaned_data['subject']}",
                        f"Hello {form.cleaned_data['name']},\n\nThank you for reaching out! I've received your message and will get back to you within 24-48 hours.\n\nBest regards,\n{about.name if about else 'Portfolio Owner'}",
                        settings.DEFAULT_FROM_EMAIL,
                        [form.cleaned_data['email']],
                        fail_silently=True,
                    )
                    
                    messages.success(request, 'Your message has been sent successfully! A confirmation email has been sent to your inbox.')
                else:
                    messages.success(request, 'Your message has been saved. Thank you for contacting me!')
            except Exception as e:
                messages.success(request, 'Your message has been saved. Thank you for contacting me!')
                print(f"Email error: {e}")
            
            return redirect('contact_success')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    
    return render(request, 'portfolio/contact.html', {'form': form})

def contact_success(request):
    """Contact success page"""
    about = About.objects.first()  # Get about information for sidebar
    return render(request, 'portfolio/contact_success.html', {'about': about})

@staff_member_required
def dashboard(request):
    """Admin dashboard - only accessible by staff users"""
    all_messages = ContactMessage.objects.all().order_by('-created_date')
    unread_messages = all_messages.filter(is_read=False).count()
    read_messages = all_messages.filter(is_read=True).count()
    replied_messages = all_messages.filter(is_replied=True).count()
    
    # Get about information for sidebar
    about = About.objects.first()
    
    context = {
        'total_messages': all_messages.count(),
        'unread_messages': unread_messages,
        'read_messages': read_messages,
        'replied_messages': replied_messages,
        'messages_list': all_messages[:50],
        'total_projects': Project.objects.count(),
        'total_skills': Skill.objects.count(),
        'about': about,
    }
    return render(request, 'portfolio/dashboard.html', context)

@staff_member_required
def mark_message_read(request, message_id):
    """Mark a message as read"""
    message = get_object_or_404(ContactMessage, id=message_id)
    message.is_read = True
    message.save()
    messages.success(request, 'Message marked as read.')
    return redirect('dashboard')

@staff_member_required
def check_new_messages(request):
    """API endpoint for checking new messages"""
    unread_count = ContactMessage.objects.filter(is_read=False).count()
    return JsonResponse({'new_messages': unread_count})


def testimonials(request):
    """Testimonials page"""
    about = About.objects.first()
    testimonials_list = Testimonial.objects.filter(is_approved=True).order_by('-created_date')
    
    context = {
        'about': about,
        'testimonials': testimonials_list,
    }
    return render(request, 'portfolio/testimonials.html', context)

def submit_testimonial(request):
    """Allow users to submit testimonials"""
    about = About.objects.first()
    
    if request.method == 'POST':
        form = TestimonialForm(request.POST)
        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.is_approved = False  # Requires admin approval
            testimonial.save()
            messages.success(request, 'Thank you! Your testimonial has been submitted and will appear after review.')
            return redirect('testimonials')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TestimonialForm()
    
    context = {
        'form': form,
        'about': about,
    }
    return render(request, 'portfolio/submit_testimonial.html', context)