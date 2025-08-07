from django.db import models


# File: job_application/enums.py
# This file contains enumerations for various fields used in the job application models.
EmploymentType = (
    ('full_time', 'Full Time'),
    ('part_time', 'Part Time'),
    ('contract', 'Contract'),
)

ExperienceLevel = (
    ('entry_level', 'Entry Level'),
    ('mid_level', 'Mid Level'),
    ('senior_level', 'Senior Level'),
    ('executive', 'Executive'),
)


LocationType = (
    ('remote', 'Remote'),
    ('on_site', 'On Site'),
    ('hybrid', 'Hybrid'),
)

class ApplicationStatus(models.TextChoices):
    APPLIED = ("APPLIED", "APPLIED")
    INTERVIEW_SCHEDULED = ("INTERVIEW_SCHEDULED", "INTERVIEW_SCHEDULED")
    REJECTED = ("REJECTED", "REJECTED")
