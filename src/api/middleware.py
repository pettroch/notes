from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from time import time


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, max_requests: int, period: int):
        super().__init__(app)
        self.max_requests = max_requests
        self.period = period
        self.requests = {}


    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time()
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Удалять запросы за пределами указанного периода
        self.requests[client_ip] = [req for req in self.requests[client_ip] if current_time - req < self.period]
        
        if len(self.requests[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Превышен запрос. Попробуйте позже"}
            )
        
        # Запиcm запрос
        self.requests[client_ip].append(current_time)
        response = await call_next(request)
        return response