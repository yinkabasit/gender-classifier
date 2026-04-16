import requests
from datetime import datetime, timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def classify(request):

    # -----------------------------------------------
    # STEP 1: Read the name from the URL
    # -----------------------------------------------
    name = request.GET.get('name', None)

    # -----------------------------------------------
    # STEP 2: Validate the input
    # -----------------------------------------------
    if name is None or name.strip() == '':
        return Response(
            {
                "status": "error",
                "message": "Missing or empty name parameter"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if not isinstance(name, str):
        return Response(
            {
                "status": "error",
                "message": "Name must be a string"
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    # -----------------------------------------------
    # STEP 3: Call the Genderize API
    # -----------------------------------------------
    try:
        genderize_response = requests.get(
            f"https://api.genderize.io/?name={name}",
            timeout=5
        )
        genderize_data = genderize_response.json()

    except requests.exceptions.Timeout:
        return Response(
            {
                "status": "error",
                "message": "Genderize API timed out"
            },
            status=status.HTTP_502_BAD_GATEWAY
        )

    except requests.exceptions.RequestException:
        return Response(
            {
                "status": "error",
                "message": "Failed to reach Genderize API"
            },
            status=status.HTTP_502_BAD_GATEWAY
        )

    # -----------------------------------------------
    # STEP 4: Handle Genderize edge cases
    # -----------------------------------------------
    if genderize_data.get('gender') is None or genderize_data.get('count', 0) == 0:
        return Response(
            {
                "status": "error",
                "message": "No prediction available for the provided name"
            },
            status=status.HTTP_200_OK
        )

    # -----------------------------------------------
    # STEP 5: Extract and PROCESS the data 🆕
    # -----------------------------------------------

    # Extract raw values from Genderize response
    gender      = genderize_data['gender']
    probability = genderize_data['probability']
    sample_size = genderize_data['count']       # renamed from 'count'

    # Compute is_confident — BOTH conditions must be true
    is_confident = (probability >= 0.7) and (sample_size >= 100)

    # Generate processed_at — current UTC time, auto-generated
    processed_at = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    # -----------------------------------------------
    # STEP 6: Return the final formatted response 🆕
    # -----------------------------------------------
    return Response({
        "status": "success",
        "data": {
            "name": name,
            "gender": gender,
            "probability": probability,
            "sample_size": sample_size,
            "is_confident": is_confident,
            "processed_at": processed_at
        }
    }, status=status.HTTP_200_OK)