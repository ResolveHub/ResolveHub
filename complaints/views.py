from django.shortcuts import render
from django.http import HttpResponse
from .models import Complaint
from .forms import ComplaintForm
from django.contrib.auth.decorators import login_required

@login_required
def complaint_list(request):
    complaints = Complaint.objects.all()
    return render(request, 'complaints/complaint_list.html', {'complaints': complaints})

@login_required
def complaint_detail(request, pk):
    complaint = Complaint.objects.get(pk=pk)
    return render(request, 'complaints/complaint_detail.html', {'complaint': complaint})

@login_required
def complaint_create(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user  # Assuming you have user authentication
            complaint.save()
            return HttpResponse("Complaint submitted successfully.")
    else:
        form = ComplaintForm()
    return render(request, 'complaints/complaint_form.html', {'form': form})

@login_required
def complaint_update(request, pk):
    complaint = Complaint.objects.get(pk=pk)
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES, instance=complaint)
        if form.is_valid():
            form.save()
            return HttpResponse("Complaint updated successfully.")
    else:
        form = ComplaintForm(instance=complaint)
    return render(request, 'complaints/complaint_form.html', {'form': form})

@login_required
def complaint_delete(request, pk):
    complaint = Complaint.objects.get(pk=pk)
    if request.method == 'POST':
        complaint.delete()
        return HttpResponse("Complaint deleted successfully.")
    return render(request, 'complaints/complaint_confirm_delete.html', {'complaint': complaint})

@login_required
def complaint_status(request, pk):
    complaint = Complaint.objects.get(pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        complaint.status = status
        complaint.save()
        return HttpResponse("Complaint status updated successfully.")
    return render(request, 'complaints/complaint_status.html', {'complaint': complaint})

@login_required
def complaint_search(request):
    query = request.GET.get('q')
    complaints = Complaint.objects.filter(title__icontains=query) if query else Complaint.objects.all()
    return render(request, 'complaints/complaint_list.html', {'complaints': complaints})

@login_required
def complaint_filter(request):
    status = request.GET.get('status')
    complaints = Complaint.objects.filter(status=status) if status else Complaint.objects.all()
    return render(request, 'complaints/complaint_list.html', {'complaints': complaints})

@login_required
def complaint_edit(request, pk):
    complaint = Complaint.objects.get(pk=pk)
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES, instance=complaint)
        if form.is_valid():
            form.save()
            return HttpResponse("Complaint updated successfully.")
    else:
        form = ComplaintForm(instance=complaint)
    return render(request, 'complaints/complaint_form.html', {'form': form})

@login_required
def complaint_history(request):
    complaints = Complaint.objects.filter(user=request.user)
    return render(request, 'complaints/complaint_history.html', {'complaints': complaints})

@login_required
def complaint_view(request, pk):
    complaint = Complaint.objects.get(pk=pk)
    return render(request, 'complaints/complaint_detail.html', {'complaint': complaint})

@login_required
def complaint_download(request, pk):
    complaint = Complaint.objects.get(pk=pk)
    response = HttpResponse(complaint.proof, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{complaint.proof.name}"'
    return response


# Create your views here.
