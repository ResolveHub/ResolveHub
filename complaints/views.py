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

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Complaint, Upvote

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upvote_complaint(request):
    user = request.user
    complaint_id = request.data.get("complaint_id")

    if not complaint_id:
        return Response({"error": "Complaint ID is required"}, status=400)

    try:
        complaint = Complaint.objects.get(id=complaint_id)
        if Upvote.objects.filter(user=user, complaint=complaint).exists():
            return Response({"message": "Already upvoted"}, status=200)

        Upvote.objects.create(user=user, complaint=complaint)
        return Response({"message": "Upvoted successfully"}, status=201)
    except Complaint.DoesNotExist:
        return Response({"error": "Complaint not found"}, status=404)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_upvote(request):
    user = request.user
    complaint_id = request.data.get("complaint_id")

    if not complaint_id:
        return Response({"error": "Complaint ID is required"}, status=400)

    try:
        complaint = Complaint.objects.get(id=complaint_id)
        upvote = Upvote.objects.filter(user=user, complaint=complaint).first()
        if upvote:
            upvote.delete()
            return Response({"message": "Upvote removed successfully"}, status=200)
        else:
            return Response({"error": "You have not upvoted this complaint"}, status=400)
    except Complaint.DoesNotExist:
        return Response({"error": "Complaint not found"}, status=404)    

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
        serializer = ComplaintSerializer(upvoted_complaints, many=True)
        return Response(serializer.data)

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

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Complaint
from .serializers import ComplaintSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def complaints_under_you(request):
    user = request.user

    # Check if user is authority
    if hasattr(user, 'authority'):
        complaints = Complaint.objects.filter(assigned_authority=user).order_by('-created_at')
        serializer = ComplaintSerializer(complaints, many=True, context={'request': request})
        return Response(serializer.data)

    return Response({"message": "You are not an authority"}, status=403)


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


class ComplaintDetailView(generics.RetrieveAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Complaint.objects.filter(
            created_by=self.request.user
        )


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

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.http import HttpResponse
from .models import Complaint

def generate_complaint_report(request, pk=None):
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF object using the buffer as its "file"
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    normal_style = styles['Normal']
    
    # Add the title
    if pk:
        try:
            complaint = Complaint.objects.get(pk=pk)
            elements.append(Paragraph(f"Complaint Report - #{complaint.id}", title_style))
            
            # Add complaint details
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"Title: {complaint.title}", normal_style))
            elements.append(Paragraph(f"Status: {complaint.status}", normal_style))
            elements.append(Paragraph(f"Created: {complaint.created_at.strftime('%Y-%m-%d %H:%M')}", normal_style))
            elements.append(Paragraph(f"Description: {complaint.description}", normal_style))
            
        except Complaint.DoesNotExist:
            return HttpResponse("Complaint not found", status=404)
    else:
        # Generate report for all complaints
        elements.append(Paragraph("All Complaints Report", title_style))
        complaints = Complaint.objects.all()
        
        # Create table data
        data = [['ID', 'Title', 'Status', 'Created']]
        for c in complaints:
            data.append([
                str(c.id),
                c.title,
                c.status,
                c.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        # Create table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    
    # Build the PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the HTTP response
    response = HttpResponse(content_type='application/pdf')
    filename = f"complaint_{'single' if pk else 'all'}_report.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(pdf)
    
    return response