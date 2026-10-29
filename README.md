# LifePattern AI V1

A small Streamlit web app for logging goals, viewing descriptive patterns, and recording feedback about suggestions.

## Files
- `app.py` — application source code
- `requirements.txt` — Python dependencies

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Run:
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```
4. Open the local URL printed in the terminal.

## Deploy online with Streamlit Community Cloud
1. Create/sign in to GitHub and create a repository.
2. Upload `app.py` and `requirements.txt` to the repository root.
3. Open https://share.streamlit.io/ and sign in using GitHub.
4. Select **Create app**, choose your repository, branch (usually `main`), and main file path `app.py`.
5. Click **Deploy**. After it starts, Streamlit gives you a public `*.streamlit.app` URL.

## Data and privacy
This V1 stores data in Streamlit session state, not a permanent database. Data may disappear when the session resets or the app restarts. Use the JSON backup download to keep your own copy and restore it later. Do not enter sensitive personal data. This version has no login, no per-user cloud database, and no external AI API. Do not present it as a secure production service.

## What the prototype does
- Stores daily logs in the current session
- Calculates completion metrics and charts
- Shows simple observations based on entered data
- Lets users record whether suggestions helped
- Exports/imports a JSON backup and exports records to CSV

The insights are basic rule-based analysis, not a trained AI model. A later version can add authentication, persistent per-user storage, privacy controls, and an AI model.
