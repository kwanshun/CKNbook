# Deployment Notes & Troubleshooting

## ⚠️ Critical Issue: Environment Variables Disappearing

### Problem Description
Environment variables (`API_KEY`, `SECRET_KEY`) disappeared after redeploying to Cloud Run, causing `SystemExit: 1` errors.

### Root Cause
- **Service updates with `--set-env-vars` REPLACE ALL existing environment variables**
- **Region changes create new services** that don't inherit environment variables
- **Partial updates** (setting only one variable) overwrite others

### What Happened
1. Original deployment had `API_KEY` set
2. Redeployed to `asia-southeast1` region (new service)
3. Only set `SECRET_KEY`, which overwrote existing `API_KEY`
4. Service crashed with "API_KEY not found" error

### Prevention Checklist ✅

#### Before Every Deployment:
- [ ] Check current environment variables: `gcloud run services describe tone-toner --region=asia-southeast1 --format="value(spec.template.spec.containers[0].env[].name)"`
- [ ] Document all required environment variables
- [ ] Use `--set-env-vars` with ALL variables at once

#### Required Environment Variables:
```bash
API_KEY="your-gemini-api-key"
SECRET_KEY="your-flask-secret-key"
```

#### Safe Deployment Command:
```bash
gcloud run services update tone-toner --region=asia-southeast1 \
  --set-env-vars API_KEY="your-key",SECRET_KEY="your-secret"
```

### Alternative Solutions

#### Option 1: Environment File
Create `.env.yaml`:
```yaml
API_KEY: "your-gemini-api-key"
SECRET_KEY: "your-flask-secret-key"
```

Deploy with:
```bash
gcloud run services update tone-toner --region=asia-southeast1 --env-vars-file .env.yaml
```

#### Option 2: Check and Preserve
```bash
# 1. Check current variables
gcloud run services describe tone-toner --region=asia-southeast1 --format="value(spec.template.spec.containers[0].env[].name,spec.template.spec.containers[0].env[].value)"

# 2. Set all variables together
gcloud run services update tone-toner --region=asia-southeast1 --set-env-vars API_KEY="key",SECRET_KEY="secret"
```

### Troubleshooting Commands

#### Check Service Status:
```bash
gcloud run services describe tone-toner --region=asia-southeast1 --format="value(status.conditions[0].status)"
```

#### Check Environment Variables:
```bash
gcloud run services describe tone-toner --region=asia-southeast1 --format="value(spec.template.spec.containers[0].env[].name,spec.template.spec.containers[0].env[].value)"
```

#### Check Logs:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=tone-toner" --limit=10 --format="value(timestamp,severity,textPayload)"
```

### Last Updated
2025-09-02 - Environment variable issue documented
