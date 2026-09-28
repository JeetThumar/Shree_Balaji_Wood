"""
Shree Balaji Wood — Backend Application

Minimal FastAPI application for Phase 2 foundation.
Business logic, database, and authentication will be added in later phases.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Shree Balaji Wood API",
    description="Backend API for the Shree Balaji Wood product showcase and enquiry website.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """Health check endpoint to verify the backend is running."""
    return {"status": "ok"}
