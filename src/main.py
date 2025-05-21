from fastapi import FastAPI, status
from contextlib import asynccontextmanager
from database import init_db
from fastapi.middleware.cors import CORSMiddleware
from controllers.users_controller import auth_router
from controllers.roles_controller import roles_router
from controllers.role_permissions_controller import role_permissions_router
from controllers.ai_persona_controller import ai_persona_router
from middleware import register_middleware
from controllers.subscriptions_controller import subscriptions_router
from controllers.interaction_modes_controller import interaction_modes_router
from controllers.sessions_controller import sessions_router
from controllers.user_subscriptions_controller import user_subscriptions_router
from controllers.ai_persona_chat_controller import ai_persona_chat_router
from controllers.interaction_mode_ai_roles_controller import interaction_mode_ai_roles_router
from controllers.interaction_mode_manufacturing_models_controller import interaction_mode_manufacturing_models_router
from controllers.interaction_mode_plant_size_impacts_controller import interaction_mode_plant_size_impacts_router

import yaml
import os

@asynccontextmanager
async def life_span(app:FastAPI):
    print("server starting...")
    await init_db()
    yield
    print("server has been stopped")

app = FastAPI(
    title="Sales AI",
    description="REST API for Sales AI project",
    lifespan=life_span
)

version = "v1"

register_middleware(app)

app.include_router(auth_router, prefix="/api/{version}/auth")
app.include_router(roles_router, prefix="/api/{version}/roles")
app.include_router(ai_persona_router, prefix="/api/{version}/ai-personas")
app.include_router(role_permissions_router, prefix="/api/{version}/role-permissions")
app.include_router(subscriptions_router, prefix="/api/{version}/subscriptions")
app.include_router(interaction_modes_router, prefix="/api/{version}/interaction-modes")
app.include_router(sessions_router, prefix="/api/{version}/sessions")
app.include_router(user_subscriptions_router, prefix="/api/{version}/user-subscriptions")
app.include_router(ai_persona_chat_router, prefix="/api/{version}/ai-persona-chat")
app.include_router(interaction_mode_ai_roles_router, prefix="/api/{version}/interaction-mode-ai-roles")
app.include_router(interaction_mode_manufacturing_models_router, prefix="/api/{version}/interaction-mode-manufacturing-models")
app.include_router(interaction_mode_plant_size_impacts_router, prefix="/api/{version}/interaction-mode-plant-size-impacts")

# Load Swagger YAML - using correct file path
swagger_file_path = os.path.join(os.path.dirname(__file__), "swagger.yaml")
try:
    with open(swagger_file_path, "r") as file:
        swagger_yaml = yaml.safe_load(file)
        
    # Custom OpenAPI schema
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        app.openapi_schema = swagger_yaml
        return app.openapi_schema

    app.openapi = custom_openapi
    print(f"Swagger documentation loaded from {swagger_file_path}")
except Exception as e:
    print(f"Error loading Swagger YAML: {e}")