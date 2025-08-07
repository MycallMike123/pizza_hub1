import factory
from faker import Faker
from job_application.models import JobAdvert, JobApplication


fake = Faker()


class JobAdvertFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = JobAdvert

    title = fake.job()
    company_name = fake.company()
    description = fake.sentence()
    deadline = fake.date()
    skills = "Python, Django"


class JobApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = JobApplication

    name = fake.name()
    portfolio_url = fake.url()
    resume = fake.file_path()

