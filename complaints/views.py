
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


from django.http import JsonResponse
from django.utils import timezone
from .models import Complaint
from auth_app.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model

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

    if not complaint_id:
        return Response({"error": "Complaint ID is required"}, status=400)

    try:
        complaint = Complaint.objects.get(id=complaint_id)

        # Avoid duplicate upvotes
        if Upvote.objects.filter(user=user, complaint=complaint).exists():
            return Response({"message": "Already upvoted"}, status=200)

        # Save in the Upvote model
        Upvote.objects.create(user=user, complaint=complaint)

        # ✅ Also update the ManyToManyField
        complaint.upvotes.add(user)

        return Response({"message": "Upvoted successfully"}, status=201)

    except Complaint.DoesNotExist:
        return Response({"error": "Complaint not found"}, status=404)


from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import authentication_classes
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from complaints.models import Complaint  # Update if your model is in another app


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def complaint_type_choices(request):
    return Response(dict(Complaint.COMPLAINT_TYPE_CHOICES))

@csrf_exempt
@require_GET
def assigned_complaints_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    user = request.user

    if not getattr(user, 'is_authority', False):
        return JsonResponse({"error": "Not an authority"}, status=403)

    # Escalation logic: escalate unresolved complaints based on authority level and time
    unresolved = Complaint.objects.filter(status="unresolved")

    for complaint in unresolved:
        hours_passed = (timezone.now() - complaint.created_at).total_seconds() / 3600

        if complaint.assigned_authority:
            level = getattr(complaint.assigned_authority, 'authority_level', 1)
            if level < 3 and hours_passed > level * 24:
                next_auth = get_user_model().objects.filter(
                    is_authority=True,
                    authority_level=level + 1
                ).first()
                if next_auth:
                    complaint.assigned_authority = next_auth
                    complaint.save()

    # Get complaints assigned to this authority
    assigned = Complaint.objects.filter(assigned_authority=user)

    complaints_data = []
    for c in assigned:
        complaints_data.append({
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "status": c.status,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "user": c.user.username
        })

    return JsonResponse({"complaints": complaints_data})

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
        # Preserve the current user (creator)
        complaint = serializer.save(user=self.request.user)

        # ✅ If no authority was assigned manually, assign to authority_level=1 by default
        if not complaint.assigned_authority:
            default_authority = User.objects.filter(is_authority=True, authority_level=1).first()
            if default_authority:
                complaint.assigned_authority = default_authority
                complaint.save()


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




from rest_framework.permissions import IsAuthenticated
from .models import Complaint
from .serializers import ComplaintSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_assigned_complaints(request):
    user = request.user
    if hasattr(user, 'authority'):
        complaints = Complaint.objects.filter(current_authority=user)
        serializer = ComplaintSerializer(complaints, many=True)
        return Response(serializer.data)
    return Response({"message": "User is not an authority"})

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Complaint
from .serializers import ComplaintSerializer
from django.db.models import Q

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_complaints(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return Response({"detail": "Search query missing."}, status=status.HTTP_400_BAD_REQUEST)

    # Search in title or description using case-insensitive partial match
    complaints = Complaint.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query),
        # user=request.user  # optional: only search complaints belonging to the current user
    )

    serializer = ComplaintSerializer(complaints, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
