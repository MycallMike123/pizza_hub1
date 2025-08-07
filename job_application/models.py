from time import timezone
from django.db import models
from django.utils import timezone
from common.models import BaseModel
from accounts.models import User
from job_application.enums import EmploymentType, ExperienceLevel, LocationType, ApplicationStatus
from django.urls import reverse

# Create your models here.
class JobAdvert(BaseModel):
    title = models.CharField(max_length=150)
    company_name = models.CharField(max_length=150)
    experience_level = models.CharField(max_length=50, choices=ExperienceLevel)
    employment_type = models.CharField(max_length=50, choices=EmploymentType)
    description = models.TextField()
    job_type = models.CharField(max_length=50, choices=LocationType)
    location = models.CharField(max_length=255, blank=True, null=True)
    is_published = models.BooleanField(default=True)
    deadline = models.DateTimeField()
    skills = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)


    class Meta:
        ordering = ('-created_at',)

    def publish_advert(self):
        self.is_published = True
        self.save(update_fields=['is_published'])

    @property
    def total_applicants(self):
        return self.applications.count()
    
    def get_absolute_url(self):
        return reverse('get_advert', kwargs={'advert_id': self.id})


class JobApplication(BaseModel):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    portfolio_url = models.URLField(blank=True, null=True)
    resume = models.FileField()
    status = models.CharField(max_length=50, choices=ApplicationStatus.choices, default=ApplicationStatus.APPLIED)
    job_advert = models.ForeignKey(JobAdvert, on_delete=models.CASCADE, related_name='applications')

