from rest_framework import serializers
from .models import Complaint

class ComplaintSerializer(serializers.ModelSerializer):
    total_upvotes = serializers.SerializerMethodField()
    already_upvoted = serializers.SerializerMethodField()
    complaint_type_display = serializers.SerializerMethodField()

    class Meta:
        model = Complaint
        fields = '__all__'  # includes complaint_type_display
        read_only_fields = ['user', 'total_upvotes', 'already_upvoted']

    def get_total_upvotes(self, obj):
        return obj.upvotes.count()

    def get_already_upvoted(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.upvotes.filter(id=request.user.id).exists()
        return False

    def get_complaint_type_display(self, obj):
        return obj.get_complaint_type_display()
