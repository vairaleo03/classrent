import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("classrent")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log della richiesta
        logger.info(f"Request: {request.method} {request.url}")
        
        # Processa la richiesta
        response = await call_next(request)
        
        # Calcola tempo di risposta
        process_time = time.time() - start_time
        
        # Log della risposta
        logger.info(
            f"Response: {response.status_code} - "
            f"Process time: {process_time:.3f}s - "
            f"URL: {request.url}"
        )
        
        # Aggiungi header del tempo di processo
        response.headers["X-Process-Time"] = str(process_time)
        
        return response