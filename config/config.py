import os

# API Configuration
API_NAME = os.environ.get('API_NAME', 'api-storage')
API_TAG_NAME = os.environ.get('API_TAG_NAME', 'storage')

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

URL_API_GATEWAY = os.environ.get('URL_API_GATEWAY', 'http://localhost:8000')

# Keycloak Configuration
KEYCLOAK_HOST = os.environ.get('KEYCLOAK_HOST', 'http://localhost:8080')
KEYCLOAK_REALM = os.environ.get('KEYCLOAK_REALM', 'master')
KEYCLOAK_CLIENT_ID = os.environ.get('KEYCLOAK_CLIENT_ID', 'test-client')
KEYCLOAK_CLIENT_SECRET = os.environ.get('KEYCLOAK_CLIENT_SECRET', 'test-secret')

# Redis Configuration
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))
REDIS_DB = int(os.environ.get('REDIS_DB', '0'))
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', 'test-password')

UNPROTECTED_PATHS = ['/favicon.ico', '/docs', '/storage/openapi.json']
UNLICENSED_PATHS = []
