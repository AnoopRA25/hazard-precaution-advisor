# Hazard Precaution Advisor

An AI-powered safety assistance system that analyzes images of indoor environments, identifies visible physical hazards, estimates risk levels, and recommends precautions.

## Features

- **AI-based scene analysis:** Uses Google Gemini Vision to identify visible hazards in uploaded images.
- **Risk assessment:** Classifies potential risk as Low, Medium, or High using hazard keywords and the selected person type.
- **Person-aware assessment:** Supports babies, children, adults, and elderly people.
- **Safety recommendations:** Matches detected hazards with precautions from a local safety guidelines dataset.
- **Multilingual reporting:** Supports English, Kannada, and Hindi reports.
- **Caregiver notifications:** Can send Telegram alerts for high-risk assessments when credentials are configured.
- **REST API:** Provides image-analysis, health-check, and homepage endpoints.
- **Image validation:** Accepts JPEG, PNG, and WebP images up to 10 MB.

## Technology Stack

- Python 3.11
- FastAPI and Uvicorn
- LangGraph
- Google Gemini API
- Pillow
- Pydantic
- Python Telegram integration
- Pytest

## Project Structure

```text
hazard-precaution-advisor/
├── app/
│   ├── agents/
│   │   ├── scene_analyst.py
│   │   ├── risk_predictor.py
│   │   ├── safety_advisor.py
│   │   ├── reporter.py
│   │   └── caregiver_alert.py
│   ├── state.py
│   ├── graph.py
│   ├── api.py
│   └── main.py
├── data/
│   ├── guidelines/
│   │   └── safety_guidelines.json
│   └── test_images/
├── tests/
├── evaluate_hazards.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Requirements

- Python 3.11
- A Google Gemini API key
- Telegram bot credentials if caregiver notifications are required
- Internet access for Gemini analysis and report translation

## Installation

### 1. Clone the repository

```powershell
git clone https://github.com/AnoopRA25/hazard-precaution-advisor.git
cd hazard-precaution-advisor
```

### 2. Create a virtual environment

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks virtual-environment activation, use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file using `.env.example` as a template.

Configure the following variables:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.8-flash

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

Replace the Gemini placeholder with your actual API key. Add Telegram credentials only if you want caregiver notifications.

**Never commit `.env` or publish API keys.**

## Run the Application

Start the FastAPI server from the project root:

```powershell
python -m uvicorn app.api:app --reload
```

Open the following URLs in your browser:

- Homepage: http://127.0.0.1:8000/
- Health check: http://127.0.0.1:8000/health
- Interactive API documentation: http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Returns application information and status |
| GET | `/health` | Returns the health-check response |
| POST | `/analyze` | Analyzes an uploaded image and returns a safety assessment |

### Analyze an Image

Open `/docs`, expand `POST /analyze`, and select **Try it out**.

Provide these multipart form fields:

| Field | Type | Allowed values |
|---|---|---|
| `image` | File | JPEG, PNG, or WebP |
| `person_type` | Text | `baby`, `child`, `elderly`, `adult` |
| `language` | Text | `English`, `Kannada`, `Hindi` |

The default person type is `adult`; the default language is `English`.

The response includes the scene setting, detected hazards, confidence, risk level, predicted risk, reason, precautions, guideline sources, report message, and caregiver-alert status.

## Workflow Architecture

1. **Scene Analyst:** Sends the uploaded image to Gemini Vision and obtains structured hazard observations.
2. **Confidence Routing:** Retries low-confidence analyses and produces a cautious report if the assessment remains unreliable.
3. **Risk Predictor:** Assigns a risk level based on detected hazard descriptions and the selected person type.
4. **Safety Advisor:** Matches hazards to categories in the local safety guidelines JSON file and retrieves relevant precautions.
5. **Reporter:** Creates a readable safety report and can translate dynamic report content into Kannada or Hindi using Gemini.
6. **Caregiver Alert:** Sends a Telegram message for high-risk assessments when valid Telegram credentials are configured.

The workflow is orchestrated using LangGraph.

## Testing

Run the automated test suite:

```powershell
python -m pytest -q
```

Run the image evaluation script:

```powershell
python evaluate_hazards.py
```

The image evaluation script saves its results to `hazard_evaluation.csv`.

Previously recorded results included **22 passing automated tests** and successful analysis of five evaluation images. Rerun the commands to verify results in your current environment.

## Limitations

- Hazard detection depends on image quality, visible evidence, and the AI model's output.
- Risk classification currently uses keyword-based rules; it is not a validated medical or engineering risk model.
- A low-risk result does not guarantee that an environment is safe.
- Multilingual translation and image analysis require access to the configured Gemini model.
- Telegram notifications require valid credentials and network connectivity.
- The application is a safety-assistance prototype, not a substitute for professional inspection or emergency services.

## Future Enhancements

- CCTV stream integration
- IoT sensor integration
- Improved risk classification
- A dedicated web dashboard
- Cloud deployment and monitoring

## License

Add a license before distributing the project publicly.
