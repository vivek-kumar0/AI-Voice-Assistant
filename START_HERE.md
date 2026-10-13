# Nova AI Voice Assistant — Start Here

## 1. Backend

Open a terminal in the `backend` folder:

```bat
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
```

Create `backend/.env` by copying `backend/.env.example`.

At minimum set:

```env
JWT_SECRET=replace-with-your-own-long-random-secret
OPENAI_API_KEY=your_real_openai_api_key
OPENAI_MODEL=gpt-4.1-mini
```

**Never put the OpenAI key in the React frontend.** It belongs only in `backend/.env`.

Start FastAPI:

```bat
uvicorn app.main:app --reload --port 8000
```

Keep this terminal open.

## 2. Frontend

Open a second terminal in the `frontend` folder:

```bat
npm install
npm run dev
```

Open:

`http://localhost:5173`

## 3. If you see "Invalid or expired token"

The browser may still have an old login token from an earlier project version. The updated app automatically clears invalid tokens and sends you to Login.

Log in again. If necessary, open Chrome DevTools → Application → Local Storage → `http://localhost:5173` and delete `voice_token` and `voice_user`, then log in again.

## 4. PDF question answering

1. Log in.
2. Open **Documents**.
3. Click **Upload PDF**.
4. Choose a text-based PDF (maximum 15 MB).
5. Wait for the PDF to appear in the list.
6. Open **AI Chat**.
7. Select the uploaded PDF from the dropdown instead of **General assistant**.
8. Ask a question about the PDF.

The backend extracts the PDF text and retrieves relevant sections for the AI. If the answer is not found in the selected PDF, Nova will say that it could not find the answer instead of inventing a document answer.

Scanned/image-only PDFs are rejected because they require OCR; text-based PDFs are supported.

## 5. Notes and Reminders

Notes, Reminders and Documents now load their data inside a normal `useEffect` wrapper. This avoids the React cleanup crash that previously produced the **Something went wrong** page when navigating away from those screens.
