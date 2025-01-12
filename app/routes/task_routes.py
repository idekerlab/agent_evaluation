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

router = APIRouter(prefix="/objects", tags=["tasks"])

@router.post("/{object_type}/{object_id}/execute")
async def execute_object(request: Request, object_type: str, object_id: str):
    db = request.app.state.db
    
    if object_type == "analysis_plan":
        analysis_plan = AnalysisPlan.load(db, object_id)
        
        try:
            analysis_run = analysis_plan.generate_analysis_run()
        except Exception as e:
            return {"error": f"{e}"}
        
        def execute_analysis_plan(analysis_run_id):
            uri = load_database_uri()
            db = SqliteDatabase(uri)
            runner = AnalysisRunner(db, analysis_run_id)
            result = runner.run()
            return result
        
        loop = asyncio.get_event_loop()
        runner_func = functools.partial(execute_analysis_plan, analysis_run.object_id)
        result = await loop.run_in_executor(None, runner_func)
        return {"url": f"/analysis_run/{analysis_run.object_id}"}
    
    elif object_type == "review_plan":
        review_plan = ReviewPlan.load(db, object_id)
        
        try:
            review_set = review_plan.generate_review_set()
        except Exception as e:
            return {"error": f"{e}"}
        
        def execute_review_plan(review_set_id):
            uri = load_database_uri()
            db = SqliteDatabase(uri)
            runner = ReviewRunner(db, review_set_id)
            result = runner.run()
            return result
        
        loop = asyncio.get_event_loop()
        runner_func = functools.partial(execute_review_plan, review_set.object_id)
        result = await loop.run_in_executor(None, runner_func)
        return {"url": f"/review_set/{review_set.object_id}"}
    
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Execution not supported for object type: {object_type}"
        )
