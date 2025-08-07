import pytest
from accounts.models import User
from accounts.tests.factories import UserFactory
from .factories import JobAdvertFactory, JobApplicationFactory,fake
from django.test.client import Client
from django.urls import reverse
from job_application.models import JobAdvert, JobApplication
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from job_application.enums import ApplicationStatus



pytestmark = pytest.mark.django_db

def test_list_adverts(client: Client, user_instance):
    """
    Test the list of job adverts.
    """
    JobAdvertFactory.create_batch(20, created_by=user_instance, deadline=fake.future_date())
    JobAdvertFactory.create_batch(5, created_by=user_instance, deadline=fake.past_date())
    url = reverse('home')
    response = client.get(url)
    assert response.status_code == 200
    assert "job_adverts" in response.context

    paginated_adverts = response.context['job_adverts']
    assert paginated_adverts.paginator.count == 20
    assert len(paginated_adverts.object_list) == 10  # Assuming default pagination of 10 per page


def test_create_advert(authenticate_user):
    """
    Test creating a job advert.
    """
    client, user = authenticate_user
    url = reverse('create_advert')

    request_data = {
        'title': "Title of the Job Advert",
        'company_name': "Company Name",
        'description': "Job Description",
        'deadline': "2025-12-31",
        'skills': 'Python, Django',
        'employment_type': 'full_time',
        'experience_level': 'mid_level',
        'job_type': 'remote',
        'location': "Remote Location"
    }
    response = client.post(url, request_data)
    assert response.status_code == 302  # Redirect after successful creation
    assert JobAdvert.objects.count() == 1
    assert JobAdvert.objects.filter(created_by=user).count() == 1

    message = list(get_messages(response.wsgi_request))
    assert len(message) == 1
    assert message[0].level_tag == 'success'
    assert "Job advert created successfully." in message[0].message

def test_delete_advert(authenticate_user):
    """
    Test deleting a job advert.
    """
    client, user = authenticate_user
    advert = JobAdvertFactory(created_by=user)
    url = reverse('delete_advert', kwargs={'advert_id': advert.id})

    response = client.post(url)
    assert response.status_code == 302  # Redirect after successful deletion
    assert response.url == reverse('my_jobs')
    assert JobAdvert.objects.count() == 0

    message = list(get_messages(response.wsgi_request))
    assert len(message) == 1
    assert message[0].level_tag == 'success'
    assert "Job advert deleted successfully." in message[0].message


def test_edit_advert(authenticate_user):
    """
    Test editing a job advert.
    """
    client, user = authenticate_user
    advert = JobAdvertFactory(created_by=user)
    url = reverse('update_advert', kwargs={'advert_id': advert.id})

    request_data = {
        'title': "Updated Job Advert Title",
        'company_name': "Updated Company Name",
        'description': "Updated Job Description",
        'deadline': "2025-12-31",
        'skills': 'Python, Django',
        'employment_type': 'part_time',
        'experience_level': 'senior_level',
        'job_type': 'on_site',
        'location': "On-site Location"
    }
    response = client.post(url, request_data)
    assert response.status_code == 302  # Redirect after successful update
    assert response.url == reverse('get_advert', kwargs={'advert_id': advert.id})
    advert.refresh_from_db()
    assert advert.title == "Updated Job Advert Title"
    assert advert.company_name == "Updated Company Name"

    message = list(get_messages(response.wsgi_request))
    assert len(message) == 1
    assert message[0].level_tag == 'success'
    assert "Job advert updated successfully." in message[0].message


def test_get_my_applications(authenticate_user):
    """
    Test getting the user's job applications.
    """
    client, user = authenticate_user
    JobApplicationFactory.create_batch(5, email=user.email, job_advert=JobAdvertFactory(created_by=UserFactory()))
    JobApplicationFactory.create_batch(3, email="otheruser@example.com", job_advert=JobAdvertFactory(created_by=UserFactory()))

    url = reverse('my_applications')
    response = client.get(url)
    assert response.status_code == 200
    assert "my_applications" in response.context
    assert len(response.context['my_applications'].object_list) == 5

def test_get_my_jobs(authenticate_user):
    """
    Test getting the user's job adverts.
    """
    client, user = authenticate_user
    JobAdvertFactory.create_batch(5, created_by=user)
    JobAdvertFactory.create_batch(3, created_by=UserFactory())

    url = reverse('my_jobs')
    response = client.get(url)
    assert response.status_code == 200
    assert "my_jobs" in response.context
    assert len(response.context['my_jobs'].object_list) == 5

def test_apply_for_job(client, user_instance):
    """
    Test applying for a job advert.
    """
    advert = JobAdvertFactory(created_by=user_instance)
    url = reverse('apply', kwargs={'advert_id': advert.id})

    resume_file = SimpleUploadedFile("resume.pdf", b"PDF content")

    request_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "portfolio_url": "",  # Assuming portfolio is optional
        "resume": resume_file,
    }
    response = client.post(url, request_data)
    assert response.status_code == 302  # Redirect after successful application
    assert response.url == reverse('get_advert', kwargs={'advert_id': advert.id})

    message = list(get_messages(response.wsgi_request))
    assert len(message) == 1
    assert message[0].level_tag == 'success'
    assert "Application submitted successfully." in message[0].message

    application = JobApplication.objects.filter(email=request_data['email']).first()
    assert application.name == request_data['name']

    application.resume.delete(save=False)  # Clean up the uploaded file after test


def test_apply_for_job_using_duplicate_email(client, user_instance):
    """
    Test applying for a job advert with an email that has already applied.
    """
    advert = JobAdvertFactory(created_by=user_instance)
    url = reverse('apply', kwargs={'advert_id': advert.id})

    resume_file = SimpleUploadedFile("resume.pdf", b"PDF content")

    # First application
    request_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "portfolio_url": "",  # Assuming portfolio is optional
        "resume": resume_file,
    }
    response = client.post(url, request_data)
    assert response.status_code == 302  # Redirect after successful application
    assert response.url == reverse('get_advert', kwargs={'advert_id': advert.id})

    message = list(get_messages(response.wsgi_request))
    assert len(message) == 1
    assert message[0].level_tag == 'success'
    assert "Application submitted successfully." in message[0].message

    application = JobApplication.objects.filter(email=request_data['email']).first()
    assert application.name == request_data['name']

    application.resume.delete(save=False)  # Clean up the uploaded file after test


def test_apply_for_job_using_duplicate_email(client, user_instance):
    """
    Test applying for a job advert with an email that has already applied.
    """
    advert = JobAdvertFactory(created_by=user_instance)
    application = JobApplicationFactory(job_advert=advert, email="john.doe@example.com")
    url = reverse('apply', kwargs={'advert_id': advert.id})

    resume_file = SimpleUploadedFile("resume.pdf", b"PDF content")

    # First application
    request_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "portfolio_url": "",  # Assuming portfolio is optional
        "resume": resume_file,
    }

    response = client.post(url, request_data)
    assert response.status_code == 302  # Redirect after unsuccessful application
    assert response.url == reverse('get_advert', kwargs={'advert_id': advert.id})

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == 'error'
    assert "You have already applied for this job." in messages[0].message

    assert JobApplication.objects.filter(email=application.email).count() == 1


def test_retrieve_job_advert(client: Client, user_instance):
    """
    Test retrieving a specific job advert.
    """
    advert = JobAdvertFactory(created_by=user_instance)
    url = reverse('get_advert', kwargs={'advert_id': advert.id})

    response = client.get(url)
    assert response.status_code == 200
    assert "job_advert" in response.context
    assert response.context['job_advert'] == advert

    # Check if the advert details are displayed correctly
    assert advert.title in response.content.decode()
    assert advert.company_name in response.content.decode()
    assert advert.description in response.content.decode()

def test_decide_applications_authorized_user(authenticate_user):
    """
    Test the view for deciding on job applications.
    """
    client, user = authenticate_user
    advert = JobAdvertFactory(created_by=user)
    application = JobApplicationFactory(job_advert=advert, email="john.doe@example.com",
                                        status=ApplicationStatus.APPLIED)  
    url = reverse('decide', kwargs={'application_id': application.id})
    request_data = {
        "status": "INTERVIEW",  # Assuming INTERVIEW is a valid status in ApplicationStatus
    }

    response = client.post(url, request_data)
    assert response.status_code == 302  # Redirect after successful decision
    assert response.url == reverse('advert_applications', kwargs={'advert_id': advert.id})
    application.refresh_from_db()
    assert application.status == request_data['status']

    message = list(get_messages(response.wsgi_request))
    assert len(message) == 1
    assert message[0].level_tag == 'success'
    assert "Application status updated successfully to INTERVIEW." in message[0].message


def test_decide_applications_unauthorized_user(authenticate_user):
    """
    Test the view for deciding on job applications by an unauthorized user.
    """
    client, user = authenticate_user
    advert = JobAdvertFactory(created_by=UserFactory())
    application = JobApplicationFactory(job_advert=advert, email="john.doe@example.com",
                                        status=ApplicationStatus.APPLIED)
    url = reverse('decide', kwargs={'application_id': application.id})
    request_data = {
        "status": "INTERVIEW",  # Assuming INTERVIEW is a valid status in ApplicationStatus
    }
    response = client.post(url, request_data)
    assert response.status_code == 403  # Forbidden for unauthorized user
    application.refresh_from_db()
    assert application.status == ApplicationStatus.APPLIED  # Status should not change

def test_get_applicants_for_an_advert(authenticate_user):
    """
    Test retrieving applications for a specific job advert.
    """
    client, user = authenticate_user
    advert1 = JobAdvertFactory(created_by=user)
    JobApplicationFactory.create_batch(5, job_advert=advert1, email="john.doe@example.com")
    advert2 = JobAdvertFactory(created_by=user)
    JobApplicationFactory.create_batch(3, job_advert=advert2, email="jane.doe@example.com")
    url = reverse('advert_applications', kwargs={'advert_id': advert2.id})

    response = client.get(url)
    assert response.status_code == 200
    assert "applications" in response.context
    assert len(response.context['applications'].object_list) == 3