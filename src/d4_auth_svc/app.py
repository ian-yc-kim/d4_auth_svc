from fastapi import FastAPI

from d4_auth_svc.routers import user_registration, user_login

app = FastAPI(debug=True)

# Mount the user registration router under /auth
app.include_router(user_registration.router, prefix="/auth")
# Mount the user login router under /auth
app.include_router(user_login.router, prefix="/auth")
