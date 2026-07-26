# Agent-Based Content Pipeline

## Run backend
```bash
cd backend
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
uvicorn main:app --reload --port 8000
```

## Run frontend
Just open `frontend/index.html` in a browser (no build step — React via CDN).
It calls `http://localhost:8000/generate`.

## Flow
1. Enter grade + topic → click Generate
2. `GeneratorAgent` drafts explanation + 3 MCQs
3. `ReviewerAgent` checks it → pass/fail + feedback
4. If fail → Generator re-runs once with feedback embedded → Reviewer re-checks
5. UI shows every stage: draft, feedback, refined output
