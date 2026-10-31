
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import route modules
from routes import schemes, profile, matching, gap_analysis, simulation, documents, comparison

app = FastAPI(
    title="BenefitBridge API",
    description="Intelligent Government Scheme Matching System Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# React + Vite frontend CORS configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(schemes.router)
app.include_router(profile.router)
app.include_router(matching.router)
app.include_router(gap_analysis.router)
app.include_router(simulation.router)
app.include_router(documents.router)
app.include_router(comparison.router)


@app.get("/", tags=["Health"])
def read_root():
    return {
        "success": True,
        "message": "Welcome to BenefitBridge API. Backend is running successfully!"
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "success": True,
        "status": "healthy"
    }
