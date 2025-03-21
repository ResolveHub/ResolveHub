from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from .models import Authority
import json

User = get_user_model()  # Get the User model dynamically

@csrf_exempt
def assign_authority(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")
            role = data.get("role")
            priority = int(data.get("priority", 0))  # Convert priority to int (default 0)

            user = User.objects.get(id=user_id)  # Fetch the user
            authority, created = Authority.objects.get_or_create(user=user)
            authority.role = role
            authority.priority = priority
            authority.save()
            print(f"Authority assigned: {user.username} -> {role}") 
            return JsonResponse({
                "message": "Authority assigned successfully",
                "user": user.email,
                "role": role,
                "priority": priority
            })

        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=400)
