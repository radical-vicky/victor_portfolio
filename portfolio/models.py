from django.db import models
from django.urls import reverse

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    technologies = models.CharField(max_length=200, help_text="Comma-separated technologies used")
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    github_link = models.URLField(blank=True, help_text="GitHub repository URL")
    live_link = models.URLField(blank=True, help_text="Live demo URL")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False, help_text="Show on homepage featured section")
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_date']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

class Skill(models.Model):
    name = models.CharField(max_length=100)
    proficiency = models.IntegerField(help_text='Percentage (0-100)')
    icon = models.CharField(max_length=50, blank=True, help_text='FontAwesome icon class (e.g., fab fa-python)')
    category = models.CharField(max_length=50, choices=[
        ('frontend', 'Frontend'),
        ('backend', 'Backend'),
        ('database', 'Database'),
        ('devops', 'DevOps'),
        ('other', 'Other')
    ], default='other')
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'

class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    # Reply fields
    reply_subject = models.CharField(max_length=200, blank=True, null=True)
    reply_message = models.TextField(blank=True, null=True)
    reply_sent_date = models.DateTimeField(blank=True, null=True)
    is_replied = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message from {self.name} - {self.subject}"
    
    class Meta:
        ordering = ['-created_date']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
class About(models.Model):
    name = models.CharField(max_length=100, default="My Name")
    title = models.CharField(max_length=200, help_text="Your professional title")
    bio = models.TextField(help_text="Tell visitors about yourself")
    profile_image = models.ImageField(upload_to='profile/', blank=True, null=True)
    hero_background = models.ImageField(upload_to='hero/', blank=True, null=True, help_text="Background image for hero section")
    resume_file = models.FileField(upload_to='resume/', blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200, blank=True)
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'About'
        verbose_name_plural = 'About'

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    testimonial = models.TextField()
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Testimonial from {self.name}"
    
    class Meta:
        ordering = ['-created_date']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'