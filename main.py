from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="GitHub Bounty API",
    description="API for searching and discovering GitHub bounty programs and issues",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Pydantic models
class BountyIssue(BaseModel):
    title: str
    url: str
    repo_name: str
    repo_url: str
    labels: List[str]
    state: str
    created_at: str
    updated_at: Optional[str] = None
    body: Optional[str] = None
    comments_count: Optional[int] = None

class BountyProgram(BaseModel):
    name: str
    url: str
    description: Optional[str] = None
    platform: str

class SearchResponse(BaseModel):
    total_count: int
    issues: List[BountyIssue]
    programs: List[BountyProgram]

# GitHub API configuration
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Common bounty labels
BOUNTY_LABELS = [
    "bounty",
    "bug-bounty",
    "good first issue",
    "hacktoberfest",
    "help wanted",
    "bounty-program",
    "reward",
    "$",
    "payment"
]

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "GitHub Bounty API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/api/search/issues", response_model=SearchResponse)
async def search_bounty_issues(
    query: Optional[str] = Query(None, description="Search query string"),
    labels: Optional[str] = Query(None, description="Comma-separated list of labels"),
    language: Optional[str] = Query(None, description="Programming language filter"),
    state: str = Query("open", description="Issue state (open/closed)"),
    per_page: int = Query(30, ge=1, le=100, description="Results per page"),
    page: int = Query(1, ge=1, description="Page number")
):
    """
    Search GitHub issues that might have bounties
    
    This endpoint searches GitHub issues with common bounty labels and keywords.
    """
    # Build search query
    search_terms = []
    
    if query:
        search_terms.append(query)
    else:
        # Default search for bounty-related terms
        bounty_keywords = " OR ".join([f'"{label}"' for label in BOUNTY_LABELS])
        search_terms.append(f"({bounty_keywords})")
    
    if labels:
        label_list = [label.strip() for label in labels.split(",")]
        search_terms.append(" ".join([f'label:"{label}"' for label in label_list]))
    
    if language:
        search_terms.append(f'language:{language}')
    
    search_terms.append(f'state:{state}')
    
    full_query = " ".join(search_terms)
    
    # Make request to GitHub API
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    params = {
        "q": full_query,
        "per_page": per_page,
        "page": page
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GITHUB_API_URL}/search/issues",
                headers=headers,
                params=params,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"GitHub API error: {response.text}"
                )
            
            data = response.json()
            
            # Transform issues to our model
            issues = []
            for item in data.get("items", []):
                repo_url = item.get("repository_url", "")
                repo_name = repo_url.split("/")[-1] if repo_url else ""
                
                issue = BountyIssue(
                    title=item.get("title", ""),
                    url=item.get("html_url", ""),
                    repo_name=repo_name,
                    repo_url=f"https://github.com/{repo_name}" if repo_name else "",
                    labels=[label.get("name", "") for label in item.get("labels", [])],
                    state=item.get("state", ""),
                    created_at=item.get("created_at", ""),
                    updated_at=item.get("updated_at"),
                    body=item.get("body"),
                    comments_count=item.get("comments")
                )
                issues.append(issue)
            
            return SearchResponse(
                total_count=data.get("total_count", 0),
                issues=issues,
                programs=[]  # We'll add program search later
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request to GitHub API timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/programs", response_model=List[BountyProgram])
async def get_bounty_programs():
    """
    Get known bounty programs
    
    This endpoint returns a list of known bug bounty programs and platforms.
    """
    programs = [
        BountyProgram(
            name="HackerOne",
            url="https://hackerone.com",
            description="Bug bounty and vulnerability disclosure platform",
            platform="hackerone"
        ),
        BountyProgram(
            name="Bugcrowd",
            url="https://bugcrowd.com",
            description="Crowdsourced security platform",
            platform="bugcrowd"
        ),
        BountyProgram(
            name="Open Bug Bounty",
            url="https://www.openbugbounty.org",
            description="Open and free bug bounty program",
            platform="openbugbounty"
        ),
        BountyProgram(
            name="Intigriti",
            url="https://www.intigriti.com",
            description="European bug bounty platform",
            platform="intigriti"
        ),
        BountyProgram(
            name="YesWeHack",
            url="https://www.yeswehack.com",
            description="Global bug bounty platform",
            platform="yeswehack"
        ),
        BountyProgram(
            name="GitHub Security Lab",
            url="https://securitylab.github.com",
            description="GitHub's security research initiative",
            platform="github"
        )
    ]
    
    return programs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
