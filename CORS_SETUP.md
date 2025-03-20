# CORS Configuration for MailoBot

## What is CORS?

Cross-Origin Resource Sharing (CORS) is a security feature implemented by browsers that restricts web pages from making requests to a different domain than the one that served the original page. This is a security measure to prevent malicious websites from accessing sensitive data on other sites.

## Why MailoBot Needs CORS

MailoBot's architecture consists of:
1. A Flask server serving the frontend (HTML, CSS, JS)
2. A Rasa server handling the conversation logic

Since these run on different ports (3000 and 5005 respectively), the browser considers them different origins, which triggers CORS protection.

## Properly Configuring Rasa for CORS

### Method 1: Using the Command Line

When starting Rasa, always include the CORS parameters:

```bash
rasa run --enable-api --cors "*"
```

### Method 2: Using the run.sh Script

Our provided `run.sh` script automatically includes the proper CORS settings when starting the Rasa server.

### Method 3: Using endpoints.yml

You can also configure CORS settings in your endpoints.yml file:

```yaml
cors:
  origin: ["*"]
  methods: ["GET", "POST", "PUT", "OPTIONS"]
  headers: ["Content-Type"]
```

## Troubleshooting CORS Issues

If you're experiencing CORS errors (visible in browser console):

1. Ensure Rasa is started with the `--cors "*"` parameter
2. Check that the `--enable-api` parameter is also included
3. Verify that your browser isn't blocking requests
4. Try disabling browser extensions that might interfere with CORS
5. Check for proper endpoint configuration in `frontend/js/rasa-service.js`

When CORS is properly configured, you'll be able to make API calls from the frontend to the Rasa backend without any cross-origin errors.
