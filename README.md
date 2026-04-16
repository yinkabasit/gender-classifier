# Gender Classifier API

A Django REST API that classifies gender from a name using the Genderize API.

## Setup Instructions

### 1. Clone the repository

git clone <your-repo-url>
cd gender_classifier

### 2. Create virtual environment

python -m venv venv
source venv/bin/activate # Mac/Linux
venv\Scripts\activate # Windows

### 3. Install dependencies

pip install -r requirements.txt

### 4. Run the server

python manage.py migrate
python manage.py runserver

## API Usage

### Endpoint

GET /api/classify?name={name}

### Example Request

GET /api/classify?name=James

### Success Response

{
"status": "success",
"data": {
"name": "James",
"gender": "male",
"probability": 0.99,
"sample_size": 12345,
"is_confident": true,
"processed_at": "2026-04-16T10:30:00Z"
}
}

### Error Responses

Missing name (400):
{ "status": "error", "message": "Missing or empty name parameter" }

Invalid type (422):
{ "status": "error", "message": "Name must be a string" }

No prediction available (200):
{ "status": "error", "message": "No prediction available for the provided name" }
