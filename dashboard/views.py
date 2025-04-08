from django.shortcuts import render, redirect, get_object_or_404
from complaints.models import Complaint
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    complaints = Complaint.objects.all().order_by('-created_at')
    query = request.GET.get("search")
    if query:
        complaints = complaints.filter(title__icontains=query)
    return render(request, "dashboard/dashboard.html", {"complaints": complaints})

# @login_required
# def upvote_complaint(request, complaint_id):
#     complaint = get_object_or_404(Complaint, id=complaint_id)
#     if request.user in complaint.upvotes.all():
#         complaint.upvotes.remove(request.user)
#     else:
#         complaint.upvotes.add(request.user)
#     return redirect("dashboard")

# # Add Create/Edit/Delete Views after this
