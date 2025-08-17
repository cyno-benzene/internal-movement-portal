import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging_config import get_api_logger, get_error_logger

api_logger = get_api_logger()
error_logger = get_error_logger()

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request details
        api_logger.info(f"Request: {request.method} {request.url.path} - From: {request.client.host}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response details
            api_logger.info(f"Response: {request.method} {request.url.path} - Status: {response.status_code} - Took: {process_time:.4f}s")
            
            return response
        
        except Exception as e:
            process_time = time.time() - start_time
            error_logger.error(
                f"Unhandled error in request {request.method} {request.url.path} - Took: {process_time:.4f}s",
                exc_info=True
            )
            # Re-raise the exception to be handled by FastAPI's exception handlers
            raise e
