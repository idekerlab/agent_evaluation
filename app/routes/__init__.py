from app.routes.agent_routes import router as agent_routes
from app.routes.object_routes import router as object_routes
from app.routes.task_routes import router as task_routes

__all__ = ['agent_routes', 'object_routes', 'task_routes']
