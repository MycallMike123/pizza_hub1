from django.forms import ModelForm
from job_application.models import JobAdvert, JobApplication
from django import forms


class JobAdvertForm(ModelForm):
    class Meta:
        model = JobAdvert
        fields = [
            'title',
            'company_name',
            'experience_level',
            'employment_type',
            'description',
            'job_type',
            'location',
            'is_published',
            'deadline',
            'skills'
        ]

        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "job title", "class": "form-control"}),
            "description": forms.Textarea(attrs={"placeholder": "job description", "class": "form-control"}),
            "company_name": forms.TextInput(attrs={"placeholder": "company name", "class": "form-control"}),
            "location": forms.TextInput(attrs={"placeholder": "job location", "class": "form-control"}),
            "employment_type": forms.Select(attrs={"class": "form-control"}),
            "experience_level": forms.Select(attrs={"class": "form-control"}),
            "job_type": forms.Select(attrs={"class": "form-control"}),
            "deadline": forms.DateInput(attrs={"placeholder": "date", "type": "date", "class": "form-control"}),
            "skills": forms.TextInput(attrs={"placeholder": "comma-separated skills", "class": "form-control"}),
        }

class JobApplicationForm(ModelForm):
    class Meta:
        model = JobApplication
        fields = [
            'name',
            'email',
            'portfolio_url',
            'resume'
            ]

        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your Name", "class": "form-control"}),
            "email": forms.EmailInput(attrs={"placeholder": "Your Email", "class": "form-control"}),
            "portfolio_url": forms.URLInput(attrs={"placeholder": "Portfolio URL (optional)", "class": "form-control"},),
            "resume": forms.FileInput(attrs={"placeholder": "Upload your resume", "class": "form-control", "accept": ".pdf,.doc,.docx"}),
        }
