# SHS Class Scheduler — Web App

A Streamlit web app for Senior High School class scheduling.

---

## Run locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the app
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

---

## Deploy FREE to Streamlit Cloud (recommended)

1. Create a free account at https://streamlit.io/cloud
2. Push your files to a GitHub repository:
   - app.py
   - requirements.txt
3. In Streamlit Cloud → "New app" → connect your GitHub repo
4. Set "Main file path" to `app.py`
5. Click **Deploy** — done! You get a public URL like:
   `https://your-app-name.streamlit.app`

Anyone with the link can open it in their browser — no installs needed.

---

## Other free hosting options

### Render.com
```
Start command: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

### Railway.app
```
railway init
railway up
```

---

## Files
| File | Purpose |
|---|---|
| app.py | Main Streamlit application |
| requirements.txt | Python dependencies |
| shs_schedule_data.json | Auto-created when you save data |
