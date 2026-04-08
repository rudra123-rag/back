from fastapi import FastAPI,HTTPException,File,UploadFile,Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
import shutil
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime



app= FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLAlchemy Database Configuration
DATABASE_URL = "sqlite:///./contacts.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Model for Contact
class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    message = Column(String(1000), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create database tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# Load environment variables
load_dotenv()



# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-pro')

# Portfolio Data
PROFILE = {
    "name": "Ashutosh Kumar Dwivedi",
    "role": "Full Stack Developer & AI Engineer",
    "bio": "Innovative Full Stack Developer with a background in mechanical engineering and expertise in Python backend development and modern JavaScript frontends. Specialized in building high-performance RESTful APIs with FastAPI and Flask, and deeply focused on integrating cutting-edge AI workflows like RAG and autonomous agent pipelines (AutoGen).",
    "location": "Raebareli, UP, India",
    "social": {
        "github": "https://github.com/rudra123-rag",
        "linkedin": "https://linkedin.com/in/ashutosh-kumar-dwivedi",
        "email": "eagiv302@gmail.com",
        "phone": "+91 7081878467"
    }
}

SKILLS = [
    {"name": "Python (FastAPI/Flask)", "level": 95, "category": "Backend"},
    {"name": "React & JavaScript", "level": 88, "category": "Frontend"},
    {"name": "PostgreSQL & MySQL", "level": 90, "category": "Database"},
    {"name": "AutoGen, LangChain, CrewAi (Agentic AI)", "level": 92, "category": "AI/ML"},
    {"name": "RAG Pipelines", "level": 90, "category": "AI/ML"},
    {"name": "Prompt Engineering", "level": 95, "category": "AI/ML"},
    {"name": "Docker & GCP", "level": 85, "category": "DevOps"},
    {"name": "Data Analysis & Machine Learning", "level": 88, "category": "Data Science"}
]

EXPERIENCE = [
    {
        "role": "Full Stack & AI Developer",
        "company": "Self-directed & Freelance",
        "period": "2021 - Present",
        "description": [
            "Specialized in building high-performance RESTful APIs with FastAPI and Flask.",
            "Developing responsive user interfaces using React and Streamlit.",
            "Integrating cutting-edge AI workflows, including Retrieval-Augmented Generation (RAG) and autonomous agent pipelines (AutoGen).",
            "Containerizing applications using Docker and implementing scalable deployment via Google Cloud Run."
        ]
    }
]

EDUCATION = [
    {
        "degree": "B.Tech (Mechanical Engineering)",
        "school": "Gurukul Kangri - Vishwavidyalaya, Haridwar",
        "year": "2017 - 2021",
        "details": "Focus on engineering fundamentals and computational methods."
    }
]

PROJECTS = [
    {
        "id": "1",
        "title": "Autonomous Multi-Agent Stock Analysis System",
        "description": "An autonomous multi-agent system acting as a financial analysis team. Orchestrated multiple LLM agents to scrape, analyze, and summarize 6 months of financial news to generate future stock outlook reports.",
        "techStack": ["Python", "Microsoft AutoGen", "Streamlit", "Docker", "Google Cloud Run"],
        "image": "https://static3.bigstockphoto.com/3/8/3/large1500/383884268.jpg",
        "category": "AI/ML",
        "link": "https://stock-analysis-671219630940.us-east1.run.app/"
    },
    {
        "id": "2",
        "title": "Fully function RAG on Unstructured Data",
        "description": "A Rag system built in langchain can handle any type of unstructured data like pdf pdf,excel epub",
        "techStack": ["Python", "LangChain", "FAISS", "OpenAi"],
        "image": "https://www.techtarget.com/rms/onlineImages/business_analytics-unstructured_data.png",
        "category": "AI/ML"
    },
    {
        "id": "3",
        "title": "Digital Waiter",
        "description": "A digital waiter powered by LangChain and LangGraph with FAISS vector storage that intelligently takes customer orders, provides menu recommendations, through natural language conversations while maintaining context and personalization.",
        "techStack": ["Python", "Openai", "FAISS ", "Langchain", "Langraph"],
        "image": "https://img.freepik.com/premium-photo/futuristic-waiter-robot-serves-food-restaurant-showcasing-future-hospitality-with-ai-technology_856795-89935.jpg?semt=ais_hybrid&w=740&q=80",
        "category": "AI/Agentic"
    },
    {
        "id":"4",
        "title":"Wearhouse Microservice",
        "description":"Build microservice on FastApi backend with React frontend for managing product and order",
        "techStack":["Python","FastApi","Redis Om","React"],
        "image":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTbHX8ZJJ1tR8WJU4JOVcoKArM6K_s8OYjhxA&s",
        "category":"SAS"
    }
]

SYSTEM_INSTRUCTION = f"""
You are 'PortfolioBot', an AI assistant for Ashutosh Kumar Dwivedi's portfolio website.
Your goal is to answer visitor questions about Ashutosh's skills, experience, and projects professionally and concisely.

Context about Ashutosh:
- Role: {PROFILE['role']}
- Bio: {PROFILE['bio']}
- Key Skills: {', '.join([skill['name'] for skill in SKILLS])}.
- Experience: {str(EXPERIENCE)}
- Education: {str(EDUCATION)}
- Projects: {str([{'title': p['title'], 'desc': p['description'], 'tech': p['techStack']} for p in PROJECTS])}

Guidelines:
- If asked about "AutoGen" or "Multi-Agent Systems", explain his experience with Microsoft AutoGen and building financial analysis teams.
- If asked about "RAG", explain his focus on integrating cutting-edge AI workflows.
- Mention his background in Mechanical Engineering which gives him a unique problem-solving perspective.
- Be friendly, concise, and encourage the user to hire Ashutosh.
- If the user asks for contact info, provide the email: {PROFILE['social']['email']} and phone: {PROFILE['social']['phone']}.
- Do not make up facts not in the context.
"""

class ChatRequest(BaseModel):
    message: str

class ContactRequest(BaseModel):
    name: str
    email: str
    message: str

class ContactResponse(BaseModel):
    id: int
    name: str
    email: str
    message: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@app.get("/")
def read_root():
    return {"message": "Welcome to PortfolioBot! Send POST /chat with your query."}

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        prompt = f"{SYSTEM_INSTRUCTION}\n\nUser: {request.message}\nAssistant:"
        response = model.generate_content(prompt)
        return {"reply": response.text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profile")
def get_profile():
    return {
        "profile": PROFILE,
        "skills": SKILLS,
        "experience": EXPERIENCE,
        "education": EDUCATION,
        "projects": PROJECTS
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/contact", response_model=ContactResponse)
def submit_contact(request: ContactRequest, db: Session = Depends(get_db)):
    """Submit a contact form with name, email, and message"""
    try:
        # Create new contact record
        contact = Contact(
            name=request.name,
            email=request.email,
            message=request.message
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
def upload_file(file:UploadFile=File(...)):
    path =f"images/{file.filename}"
    with open(path,"wb") as f:
        shutil.copyfileobj(file.file,f)
    return {"message":"File uploaded sucessfully"}
@app.get('/download/{name}', response_class=FileResponse)
def get_file(name: str):
    path = f'images/{name}'
    return path

app.mount('/images', StaticFiles(directory="images"), name='files')
