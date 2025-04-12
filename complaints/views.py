
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count

from .models import Complaint, Upvote
from .serializers import ComplaintSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

# ==============================
# API VIEWS
# ==============================

class ComplaintListView(generics.ListAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get(self, request):
        complaints = Complaint.objects.all().annotate(upvote_count=Count('upvotes')).order_by('-upvote_count')
        user = request.user

        response_data = []
        for complaint in complaints:
            already_upvoted = Upvote.objects.filter(user=user, complaint=complaint).exists()
            data = ComplaintSerializer(complaint).data
            data["already_upvoted"] = already_upvoted
            response_data.append(data)

        return Response(response_data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upvote_complaint(request):
    user = request.user
    complaint_id = request.data.get("complaint_id")

    try:
        complaint = Complaint.objects.get(id=complaint_id)

        # Avoid duplicate upvotes
        if Upvote.objects.filter(user=user, complaint=complaint).exists():
            return Response({"message": "Already upvoted"}, status=200)

        # Save in the separate Upvote model
        Upvote.objects.create(user=user, complaint=complaint)

        # ✅ ALSO save in the ManyToManyField
        # complaint.upvotes.add(user)

        return Response({"message": "Upvoted successfully"}, status=201)

    except Complaint.DoesNotExist:
        return Response({"error": "Complaint not found"}, status=404)


# ==============================
# FUNCTION-BASED VIEWS
# ==============================

# @login_required
# def complaint_detail(request, pk):
#     complaint = get_object_or_404(Complaint, pk=pk)
#     return render(request, 'complaints/complaint_detail.html', {'complaint': complaint})

# @login_required
# def complaint_create(request):
#     if request.method == 'POST':
#         form = ComplaintForm(request.POST, request.FILES)
#         if form.is_valid():
#             complaint = form.save(commit=False)
#             complaint.user = request.user
#             complaint.save()
#             return HttpResponse("Complaint submitted successfully.")
#     else:
#         form = ComplaintForm()
#     return render(request, 'complaints/complaint_form.html', {'form': form})

# @login_required
# def complaint_update(request, pk):
#     complaint = get_object_or_404(Complaint, pk=pk)
#     if request.method == 'POST':
#         form = ComplaintForm(request.POST, request.FILES, instance=complaint)
#         if form.is_valid():
#             form.save()
#             return HttpResponse("Complaint updated successfully.")
#     else:
#         form = ComplaintForm(instance=complaint)
#     return render(request, 'complaints/complaint_form.html', {'form': form})

# @login_required
# def complaint_delete(request, pk):
#     complaint = get_object_or_404(Complaint, pk=pk)
#     if request.method == 'POST':
#         complaint.delete()
#         return HttpResponse("Complaint deleted successfully.")
#     return render(request, 'complaints/complaint_confirm_delete.html', {'complaint': complaint})

# @login_required
# def complaint_status(request, pk):
#     complaint = get_object_or_404(Complaint, pk=pk)
#     if request.method == 'POST':
#         status = request.POST.get('status')
#         complaint.status = status
#         complaint.save()
#         return HttpResponse("Complaint status updated successfully.")
#     return render(request, 'complaints/complaint_status.html', {'complaint': complaint})

# @login_required
# def complaint_search(request):
#     query = request.GET.get('q')
#     complaints = Complaint.objects.filter(title__icontains=query) if query else Complaint.objects.all()
#     return render(request, 'complaints/complaint_list.html', {'complaints': complaints})

# @login_required
# def complaint_filter(request):
#     status = request.GET.get('status')
#     complaints = Complaint.objects.filter(status=status) if status else Complaint.objects.all()
#     return render(request, 'complaints/complaint_list.html', {'complaints': complaints})

# @login_required
# def complaint_edit(request, pk):
#     complaint = get_object_or_404(Complaint, pk=pk)
#     if request.method == 'POST':
#         form = ComplaintForm(request.POST, request.FILES, instance=complaint)
#         if form.is_valid():
#             form.save()
#             return HttpResponse("Complaint updated successfully.")
#     else:
#         form = ComplaintForm(instance=complaint)
#     return render(request, 'complaints/complaint_form.html', {'form': form})

# @login_required
# def complaint_history(request):
#     complaints = Complaint.objects.filter(user=request.user)
#     return render(request, 'complaints/complaint_history.html', {'complaints': complaints})

# @login_required
# def complaint_view(request, pk):
#     complaint = get_object_or_404(Complaint, pk=pk)
#     return render(request, 'complaints/complaint_detail.html', {'complaint': complaint})

# @login_required
# def complaint_download(request, pk):
#     complaint = get_object_or_404(Complaint, pk=pk)
#     response = HttpResponse(complaint.proof, content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="{complaint.proof.name}"'
#     return response


from rest_framework import generics, permissions
from .models import Complaint
from .serializers import ComplaintSerializer

class ComplaintCreateView(generics.CreateAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Complaint
from .serializers import ComplaintSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_complaint(request):
    data = request.data.copy()
    data['created_by'] = request.user.id  # Set created_by to logged-in user

    serializer = ComplaintSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user) 
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from rest_framework.permissions import IsAuthenticated

class MyComplaintsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        complaints = Complaint.objects.filter(user=request.user)
        serializer = ComplaintSerializer(complaints, many=True)
        return Response(serializer.data)

class UpvotedComplaintsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        upvoted_complaint_ids = Upvote.objects.filter(user=request.user).values_list('complaint_id', flat=True)
        upvoted_complaints = Complaint.objects.filter(id__in=upvoted_complaint_ids)
        serializer = ComplaintSerializer(upvoted_complaints, many=True, context={'request': request})
        return Response(serializer.data)


class ComplaintUpdateView(generics.UpdateAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        complaint = super().get_object()
        if complaint.user != self.request.user:
            raise PermissionDenied("You can only edit your own complaint.")
        return complaint

class ComplaintDeleteView(generics.DestroyAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if obj.user != self.request.user:
            raise PermissionDenied("You can only delete your own complaint.")
        return obj

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .models import Complaint
from .serializers import ComplaintSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_complaints(request):
    query = request.GET.get('q', '')
    complaints = Complaint.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query),
        user=request.user  # optional: restrict to logged-in user's complaints
    )
    serializer = ComplaintSerializer(complaints, many=True)
    return Response(serializer.data)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Complaint

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_resolution(request):
    complaint_id = request.data.get("complaint_id")
    confirmation = request.data.get("confirmation")  # "Confirmed" or "Rejected"

    try:
        complaint = Complaint.objects.get(id=complaint_id, user=request.user)  # assuming each complaint is linked to a user
    except Complaint.DoesNotExist:
        return Response({"error": "Complaint not found"}, status=404)

    complaint.user_confirmation_status = confirmation
    complaint.save()

    return Response({"message": "Confirmation recorded successfully"}, status=200)
