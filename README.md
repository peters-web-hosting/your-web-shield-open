# Your Web Shield Open

Analyze web server logs and generate risk-focused output files.

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies.
3. Start the Flask UI.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:8501`, upload a log file, and click **Analyze uploaded file**.

## Community API configuration

Community sharing is optional and disabled by default.

1. Copy `.env.example` to `.env`.
2. Set:
   - `COMMUNITY_OPT_IN=true`
   - `COMMUNITY_API_URL=<your endpoint>`
   - `COMMUNITY_API_KEY=<optional; only if your API enforces one>`

## Docker image option

Build:

```bash
docker build -t your-web-shield-open .
```

Run:

```bash
docker run --rm -p 8501:8501 your-web-shield-open
```

Open `http://localhost:8501` and use the upload UI.
