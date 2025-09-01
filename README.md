# Tone-Toner

A Flask-based web application that uses Google's Gemini AI to rewrite text in different tones and languages.

## Features

- Rewrite text in multiple tones (輕鬆, 溫暖, 專業, 謙虛, 幽默)
- Support for multiple languages (廣東話, 普通話, 英文, 西班牙文)
- Generate three different text variations
- Copy-to-clipboard functionality

## Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export API_KEY="your-gemini-api-key"
export SECRET_KEY="your-flask-secret-key"

# Run locally
python main.py
```

### Cloud Run Deployment

#### ⚠️ CRITICAL: Environment Variables
**Always set ALL environment variables together to avoid service crashes:**

```bash
# ✅ CORRECT - Set all variables at once
gcloud run services update tone-toner --region=asia-southeast1 \
  --set-env-vars API_KEY="your-key",SECRET_KEY="your-secret"

# ❌ WRONG - This will overwrite existing variables
gcloud run services update tone-toner --region=asia-southeast1 \
  --set-env-vars API_KEY="your-key"
```

#### Deployment Commands
```bash
# Deploy to Cloud Run
./deploy-gcp.sh

# Or deploy manually
gcloud run deploy tone-toner --source . --region asia-southeast1 --allow-unauthenticated
```

## Troubleshooting

### Common Issues

#### 1. "SystemExit: 1" Error
- **Cause**: Missing environment variables (`API_KEY` or `SECRET_KEY`)
- **Solution**: Set all environment variables together

#### 2. Environment Variables Disappearing
- **Cause**: Partial updates overwrite existing variables
- **Prevention**: Always use `--set-env-vars` with ALL variables

#### 3. Service Not Responding
- **Check**: `gcloud run services describe tone-toner --region=asia-southeast1`
- **Verify**: Environment variables are set correctly

### Useful Commands

```bash
# Check service status
gcloud run services describe tone-toner --region=asia-southeast1

# Check environment variables
gcloud run services describe tone-toner --region=asia-southeast1 \
  --format="value(spec.template.spec.containers[0].env[].name,spec.template.spec.containers[0].env[].value)"

# Check logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=tone-toner" --limit=10
```

## Project Structure

```
tone-toner/
├── main.py                 # Development server
├── main_production.py      # Production server with rate limiting
├── deploy-gcp.sh          # Deployment script
├── cloudbuild.yaml        # Cloud Build configuration
├── DEPLOYMENT_NOTES.md    # Detailed deployment troubleshooting
├── prompts/
│   └── system_prompt.txt  # AI system prompt
├── static/                # CSS and JavaScript
└── templates/             # HTML templates
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_KEY` | Yes | Google Gemini API key |
| `SECRET_KEY` | Yes | Flask secret key (64+ characters) |

## Contributing

1. Make changes to `main.py` for development
2. Test locally
3. Update `main_production.py` if needed
4. Deploy using `./deploy-gcp.sh`
5. **Always verify environment variables are set correctly**

## Support

For deployment issues, see [DEPLOYMENT_NOTES.md](./DEPLOYMENT_NOTES.md)