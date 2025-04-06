# from django import forms
# from .models import Complaint
# from django.core.exceptions import ValidationError


# class ComplaintForm(forms.ModelForm):
#     class Meta:
#         model = Complaint
#         fields = ['title', 'description', 'proof', 'complaint_type']

#     def clean_title(self):
#         title = self.cleaned_data.get('title')
#         if not title:
#             raise ValidationError("Title is required.")
#         return title

#     def clean_description(self):
#         description = self.cleaned_data.get('description')
#         if not description:
#             raise ValidationError("Description is required.")
#         return description

#     def clean_proof(self):
#         proof = self.cleaned_data.get('proof')
#         if proof and not proof.name.endswith('.pdf'):
#             raise ValidationError("Proof must be a PDF file.")
#         return proof