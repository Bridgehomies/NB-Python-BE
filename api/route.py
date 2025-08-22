# api/route.py
from app.main import app
from mangum import Mangum

# Create the handler for Vercel serverless
handler = Mangum(app)

# Optional: for debugging in Vercel
def handler_wrapper(event, context):
    print("Event:", event)
    return handler(event, context)

# If deploying to Vercel, export handler
__name__ = "__main__"  # trick to help some tools