from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import path
from django.template.loader import render_to_string
from django.utils import timezone
from .models import Project, Skill, ContactMessage, About, Testimonial
from .forms import ReplyForm

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'technologies', 'created_date', 'is_featured')
    list_filter = ('technologies', 'created_date', 'is_featured')
    search_fields = ('title', 'description')
    list_editable = ('is_featured',)
    readonly_fields = ('created_date', 'updated_date')
    fieldsets = (
        ('Project Information', {
            'fields': ('title', 'description', 'technologies')
        }),
        ('Media', {
            'fields': ('image',),
            'classes': ('wide',)
        }),
        ('Links', {
            'fields': ('github_link', 'live_link'),
            'classes': ('wide',)
        }),
        ('Featured', {
            'fields': ('is_featured',),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': ('created_date', 'updated_date'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            messages.success(request, f'Project "{obj.title}" has been added successfully!')
        else:
            messages.success(request, f'Project "{obj.title}" has been updated successfully!')
        super().save_model(request, obj, form, change)

class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'proficiency', 'display_proficiency_bar')
    list_filter = ('category', 'proficiency')
    search_fields = ('name',)
    list_editable = ('proficiency', 'category')
    
    def display_proficiency_bar(self, obj):
        return f'<div style="background: #f0f0f0; border-radius: 10px; overflow: hidden;"><div style="background: #28a745; width: {obj.proficiency}%; height: 20px; text-align: center; color: white; font-size: 12px; line-height: 20px;">{obj.proficiency}%</div></div>'
    
    display_proficiency_bar.allow_tags = True
    display_proficiency_bar.short_description = 'Proficiency'
    
    def save_model(self, request, obj, form, change):
        if not change:
            messages.success(request, f'Skill "{obj.name}" has been added successfully!')
        else:
            messages.success(request, f'Skill "{obj.name}" has been updated successfully!')
        super().save_model(request, obj, form, change)

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_date', 'is_read', 'is_replied', 'message_preview')
    list_filter = ('created_date', 'is_read', 'is_replied')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_date', 'reply_sent_date')
    list_editable = ('is_read',)
    list_per_page = 25
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'
    
    def has_add_permission(self, request):
        return False
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:message_id>/reply/', self.admin_site.admin_view(self.reply_view), name='reply_message'),
        ]
        return custom_urls + urls
    
    def reply_view(self, request, message_id):
        """Custom view for replying to messages"""
        message = ContactMessage.objects.get(id=message_id)
        
        if request.method == 'POST':
            form = ReplyForm(request.POST, original_subject=message.subject)
            if form.is_valid():
                subject = form.cleaned_data['subject']
                reply_text = form.cleaned_data['message']
                
                # Save reply to database
                message.reply_subject = subject
                message.reply_message = reply_text
                message.reply_sent_date = timezone.now()
                message.is_replied = True
                message.save()
                
                # Send email
                try:
                    # Create email content
                    html_message = render_to_string('portfolio/reply_email.html', {
                        'message': message,
                        'reply_subject': subject,
                        'reply_message': reply_text,
                        'reply_date': timezone.now()
                    })
                    
                    plain_message = f"""
                    Hello {message.name},
                    
                    Thank you for contacting me. Here's my response:
                    
                    {reply_text}
                    
                    Original Message:
                    Subject: {message.subject}
                    Message: {message.message}
                    
                    Best regards,
                    {settings.FROM_NAME}
                    """
                    
                    send_mail(
                        subject,
                        plain_message,
                        settings.DEFAULT_FROM_EMAIL,
                        [message.email],
                        fail_silently=False,
                        html_message=html_message
                    )
                    
                    messages.success(request, f'Reply sent successfully to {message.email}!')
                    return redirect('admin:portfolio_contactmessage_changelist')
                    
                except Exception as e:
                    messages.error(request, f'Error sending email: {str(e)}')
                    return redirect('admin:portfolio_contactmessage_changelist')
        else:
            form = ReplyForm(original_subject=message.subject)
        
        context = {
            'message': message,
            'form': form,
            'opts': self.model._meta,
            'title': f'Reply to {message.name}',
        }
        return render(request, 'admin/reply_message.html', context)
    
    # Define custom actions
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} message(s) marked as read.')
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} message(s) marked as unread.')
    mark_as_unread.short_description = "Mark selected messages as unread"
    
    actions = [mark_as_read, mark_as_unread]
class AboutAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'email', 'updated_date')
    
    def has_add_permission(self, request):
        # Allow adding only if no About objects exist
        if self.model.objects.count() == 0:
            return True
        return False

class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'created_date', 'is_approved')
    list_filter = ('is_approved', 'created_date')
    search_fields = ('name', 'company', 'testimonial')
    list_editable = ('is_approved',)
    
    def save_model(self, request, obj, form, change):
        if not change:
            messages.success(request, f'Testimonial from "{obj.name}" has been added!')
        super().save_model(request, obj, form, change)

admin.site.register(Project, ProjectAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(About, AboutAdmin)
admin.site.register(Testimonial, TestimonialAdmin)

admin.site.site_header = "Portfolio Admin Panel"
admin.site.site_title = "Portfolio Admin"
admin.site.index_title = "Welcome to Portfolio Administration"