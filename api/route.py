# api/route.py
from app.main import app
from mangum import Mangum

# This is the only thing Vercel needs
handler = Mangum(app)

print("🟩 FastAPI app loaded and wrapped with Mangum")