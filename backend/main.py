from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from chatbot import router as chatbot_router
from auth import get_current_user
from auth_routes import router as auth_router

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Chat with Docs API"}

# Include authentication router
app.include_router(auth_router, prefix="/api/v1/auth")

# Include chatbot router with authentication
app.include_router(chatbot_router, prefix="/api/v1", dependencies=[Depends(get_current_user)])

# TODO: Add routes for document processing
# TODO: Add routes for chatbot interactions