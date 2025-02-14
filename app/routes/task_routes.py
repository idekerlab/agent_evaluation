import logging
import asyncio
import functools
from typing import Dict

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.sqlite_database import SqliteDatabase
from app.config import load_database_uri
from models.analysis_plan import AnalysisPlan
from models.review_plan import ReviewPlan
from services.analysisrunner import AnalysisRunner
from services.reviewrunner import ReviewRunner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["tasks"])
