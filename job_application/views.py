from django.shortcuts import render
from accounts.models import User
from job_application.enums import ApplicationStatus
from job_application.forms import JobAdvertForm, JobApplicationForm
from django.http import HttpRequest, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from job_application.models import JobAdvert, JobApplication
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Q
from common.tasks import send_verification_email
from django.core.paginator import Paginator

# Create your views here.
@login_required
def create_advert(request: HttpRequest):
    form = JobAdvertForm(request.POST or None)

    if form.is_valid():
        instance: JobAdvert = form.save(commit=False)  # type: ignore
        instance.created_by = request.user
        instance.save()

        messages.success(request, "Job advert created successfully.")
        return redirect(instance.get_absolute_url())
    
    context = {
        "job_advert_form": form,
        "title": "Create Job Advert",
        "btn_text": "Create Advert",
    }
    return render(request, "create_advert.html", context)

def get_advert(request: HttpRequest, advert_id: int):
    form = JobApplicationForm()

    job_advert = get_object_or_404(JobAdvert, pk=advert_id)
    context = {
        "job_advert": job_advert,
        "application_form": form,
    }
    return render(request, "advert.html", context)


def list_adverts(request: HttpRequest):
    active_adverts = JobAdvert.objects.filter(is_published=True, deadline__gte=timezone.now().date())

    paginator = Paginator(active_adverts, 10)  # Show 10 adverts per page
    requested_page = request.GET.get('page')
    adverts = paginator.get_page(requested_page)
    print(adverts.next_page_number, adverts.previous_page_number, adverts.has_previous)

    context = {
        "job_adverts": adverts,
    }

    return render(request, "home.html", context)

@login_required
def update_advert(request: HttpRequest, advert_id: int):
    advert: JobAdvert = get_object_or_404(JobAdvert, pk=advert_id, created_by=request.user)
    if request.user != advert.created_by:
        messages.error(request, "You do not have permission to edit this advert.")
    # Create a form instance with the existing advert data
    form = JobAdvertForm(request.POST or None, instance=advert)

    if form.is_valid():
        instance: JobAdvert = form.save(commit=False)  # type: ignore
        instance.save()
        
        messages.success(request, "Job advert updated successfully.")
        return redirect(advert.get_absolute_url())

    context = {
        "job_advert_form": form,
        "btn_text": "Update Advert",
    }
    return render(request, "create_advert.html", context)

@login_required
def delete_advert(request: HttpRequest, advert_id: int):
    advert: JobAdvert = get_object_or_404(JobAdvert, pk=advert_id, created_by=request.user)
    if request.user != advert.created_by:
        messages.error(request, "You do not have permission to delete this advert.")
    # Handle the deletion
    advert.delete()
    messages.success(request, "Job advert deleted successfully.")
    return redirect('my_jobs')


def apply(request: HttpRequest, advert_id: int):
    job_advert = get_object_or_404(JobAdvert, pk=advert_id)

    if request.method == "POST":
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            if job_advert.applications.filter(email=email).exists():
                messages.error(request, "You have already applied for this job.")
                return redirect(job_advert.get_absolute_url())
            
            # Save new application
            application: JobApplication = form.save(commit=False)  # type: ignore
            application.job_advert = job_advert
            application.save()

            messages.success(request, "Application submitted successfully.")
            return redirect(job_advert.get_absolute_url())
    else:
        form = JobApplicationForm()

    context = {
        "job_advert": job_advert,
        "application_form": form,
    }
    return render(request, "advert.html", context)

@login_required
def my_application(request: HttpRequest):
    user: User = request.user
    applications = JobApplication.objects.filter(email=user.email)
    paginator = Paginator(applications, 10)  # Show 10 applications per page

    requested_page = request.GET.get('page')
    paginated_applications = paginator.get_page(requested_page)

    context = {
        "my_applications": paginated_applications,
    }
    return render(request, "my_applications.html", context)


@login_required
def my_jobs(request: HttpRequest):
    user: User = request.user
    job_adverts = JobAdvert.objects.filter(created_by=user)
    paginator = Paginator(job_adverts, 10)  # Show 10 adverts per page

    requested_page = request.GET.get('page')
    paginated_adverts = paginator.get_page(requested_page)

    context = {
        "my_jobs": paginated_adverts,
        "current_date": timezone.now().date(),
    }
    return render(request, "my_jobs.html", context)

@login_required
def advert_applications(request: HttpRequest, advert_id: int):
    Advert: JobAdvert = get_object_or_404(JobAdvert, pk=advert_id)
    if request.user != Advert.created_by:
        return HttpResponseForbidden("You do not have permission to view these applications.")

    applications = Advert.applications.all()
    # applications = JobApplication.objects.filter(job_advert=Advert.id)
    paginator = Paginator(applications, 10)  # Show 10 applications per page
    requested_page = request.GET.get('page')
    paginated_applications = paginator.get_page(requested_page)

    context = {
        "job_advert": Advert,
        "applications": paginated_applications,
    }
    return render(request, "advert_applications.html", context)

@login_required
def decide(request: HttpRequest, application_id: int):
    application: JobApplication = get_object_or_404(JobApplication, pk=application_id)
    if request.user != application.job_advert.created_by:
        return HttpResponseForbidden("You do not have permission to change the status of this application.")
    if request.method == "POST":
        status = request.POST.get("status")
        application.status = status
        application.save(update_fields=['status'])
        messages.success(request, f"Application status updated successfully to {status}.")

        # Send email notification
        if status == ApplicationStatus.REJECTED:
            context = {
                "applicant_name": application.name,
                "job_title": application.job_advert.title,
                "company_name": application.job_advert.company_name,
            }
            send_verification_email(
                f"Application outcome for {application.job_advert.title}",
                [application.email],
                "emails/job_application_update.html",
                context
            )
        return redirect('advert_applications', advert_id=application.job_advert.id)
    

def search(request: HttpRequest):
    keyword = request.GET.get("keyword")
    location = request.GET.get("location")

    query = Q()
    
    if keyword:
        query &= (
            Q(title__icontains=keyword)
             | Q(description__icontains=keyword)
             | Q(company_name__icontains=keyword)
             | Q(skills__icontains=keyword)
        )

    if location:
        query &= Q(location__icontains=location)

    active_adverts = JobAdvert.objects.filter(is_published=True, deadline__gte=timezone.now().date())

    result = active_adverts.filter(query)
    paginator = Paginator(result, 10)  # Show 10 adverts per page
    requested_page = request.GET.get('page')
    paginated_adverts = paginator.get_page(requested_page)

    context = {
        "job_adverts": paginated_adverts,
    }
    return render(request, "home.html", context)
