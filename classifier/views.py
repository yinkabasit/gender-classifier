import requests
from datetime import datetime, timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_http_methods(["GET"])
def classify(request):

    # -----------------------------------------------
    # STEP 1: Read the name from the URL
    # -----------------------------------------------
    name = request.GET.get('name', None)

    # -----------------------------------------------
    # STEP 2: Validate — Missing or empty name → 400
    # -----------------------------------------------
    if name is None or str(name).strip() == '':
        return JsonResponse(
            {
                "status": "error",
                "message": "Missing or empty name parameter"
            },
            status=400
        )

    # -----------------------------------------------
    # STEP 3: Validate — Non-string name → 422
    # -----------------------------------------------
    if not isinstance(name, str):
        return JsonResponse(
            {
                "status": "error",
                "message": "Name must be a string"
            },
            status=422
        )

    # -----------------------------------------------
    # STEP 4: Call the Genderize API
    # -----------------------------------------------
    try:
        genderize_response = requests.get(
            f"https://api.genderize.io/?name={name}",
            timeout=5
        )
        genderize_data = genderize_response.json()

    except requests.exceptions.Timeout:
        return JsonResponse(
            {
                "status": "error",
                "message": "Genderize API timed out"
            },
            status=502
        )

    except requests.exceptions.RequestException:
        return JsonResponse(
            {
                "status": "error",
                "message": "Failed to reach Genderize API"
            },
            status=502
        )

    # -----------------------------------------------
    # STEP 5: Handle edge cases — null gender or 0 count
    # -----------------------------------------------
    if genderize_data.get('gender') is None or genderize_data.get('count', 0) == 0:
        return JsonResponse(
            {
                "status": "error",
                "message": "No prediction available for the provided name"
            },
            status=200
        )

    # -----------------------------------------------
    # STEP 6: Extract and process the data
    # -----------------------------------------------
    gender      = genderize_data['gender']
    probability = float(genderize_data['probability'])
    sample_size = int(genderize_data['count'])

    # Both conditions must be true
    is_confident = (probability >= 0.7) and (sample_size >= 100)

    # Current UTC time in ISO 8601
    processed_at = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    # -----------------------------------------------
    # STEP 7: Return final response
    # -----------------------------------------------
    response = JsonResponse({
        "status": "success",
        "data": {
            "name": name,
            "gender": gender,
            "probability": probability,
            "sample_size": sample_size,
            "is_confident": is_confident,
            "processed_at": processed_at
        }
    }, status=200)

    # Manually set CORS header to be absolutely sure
    response["Access-Control-Allow-Origin"] = "*"

    return response