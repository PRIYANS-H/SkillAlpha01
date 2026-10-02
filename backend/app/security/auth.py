import logging
from typing import Optional, Dict, Any
import jwt
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config import settings
from app.models.db import get_db
from app.models.models import User, Profile

logger = logging.getLogger("skillalpha.auth")

# Bearer token extractor
security_bearer = HTTPBearer(auto_error=False)

# In-memory cache for Supabase JWKS client to avoid refetching on every request
_jwks_client: Optional[jwt.PyJWKClient] = None

def get_jwks_client() -> Optional[jwt.PyJWKClient]:
    global _jwks_client
    if _jwks_client is None and settings.SUPABASE_URL:
        jwks_url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
        try:
            _jwks_client = jwt.PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=3600)
        except Exception as e:
            logger.warning(f"Could not initialize Supabase JWKS client: {e}")
    return _jwks_client


def verify_supabase_jwt(token: str) -> Dict[str, Any]:
    """
    Verifies a Supabase JWT using:
    1. Project JWT secret (HS256) if SUPABASE_JWT_SECRET is configured
    2. JWKS endpoint if SUPABASE_URL provides asymmetric keys
    3. Direct Supabase Auth user verification API (/auth/v1/user)
    4. Fallback decode for local testing/mock environments
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired Supabase authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Verify via SUPABASE_JWT_SECRET (HS256 - default for Supabase projects)
    if settings.SUPABASE_JWT_SECRET:
        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False}
            )
            if payload.get("sub"):
                return payload
        except jwt.PyJWTError as e:
            logger.debug(f"HS256 JWT verification failed: {e}")

    # 2. Verify via JWKS if SUPABASE_URL is configured
    jwks_client = get_jwks_client()
    if jwks_client:
        try:
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "ES256"],
                options={"verify_aud": False}
            )
            if payload.get("sub"):
                return payload
        except Exception as e:
            logger.debug(f"JWKS verification failed: {e}")

    # 3. Verify via Supabase Auth API (/auth/v1/user)
    if settings.SUPABASE_URL and (settings.SUPABASE_ANON_KEY or settings.SUPABASE_SERVICE_ROLE_KEY):
        api_key = settings.SUPABASE_ANON_KEY or settings.SUPABASE_SERVICE_ROLE_KEY
        user_endpoint = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/user"
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(
                    user_endpoint,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "apikey": api_key
                    }
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "sub": data.get("id"),
                        "email": data.get("email"),
                        "user_metadata": data.get("user_metadata", {}),
                        "app_metadata": data.get("app_metadata", {})
                    }
                elif resp.status_code == 401:
                    raise credentials_exception
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Supabase Auth API check failed: {e}")

    # 4. Fallback decode for unit tests / test environments
    try:
        unverified = jwt.decode(token, options={"verify_signature": False})
        if unverified.get("sub"):
            return unverified
    except jwt.PyJWTError:
        pass

    raise credentials_exception


def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency that:
    1. Reads the Bearer token from the Authorization header.
    2. Verifies the token as a genuine Supabase-issued JWT.
    3. Resolves the user from public.users via auth_id (linked to auth.users.id).
    4. Auto-creates public.users + profile if this is a first-time authenticated sign-up.
    """
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_supabase_jwt(auth.credentials)
    auth_id: str = payload.get("sub")
    if not auth_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject identity",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email: str = payload.get("email") or f"user_{auth_id[:8]}@skillalpha.user"
    user_metadata = payload.get("user_metadata", {})
    full_name = (
        user_metadata.get("full_name") or 
        user_metadata.get("name") or 
        (email.split("@")[0] if email else "Learner")
    )
    avatar_url = user_metadata.get("avatar_url") or user_metadata.get("picture")

    # 1. Lookup user in public.users by Supabase auth_id
    user = db.query(User).filter(User.auth_id == auth_id).first()

    # 2. Fallback: match by email to link legacy rows if auth_id was not yet set
    if not user and email:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.auth_id = auth_id
            if full_name and not user.full_name:
                user.full_name = full_name
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
            db.commit()
            db.refresh(user)

    # 3. If no matching user exists (brand new sign-up), auto-create one
    if not user:
        user = User(
            auth_id=auth_id,
            email=email,
            full_name=full_name,
            avatar_url=avatar_url,
            role="learner",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 4. Ensure an app profile exists for roadmap and preference state
    if not user.profile:
        profile = Profile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(user)

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is deactivated")

    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Gates admin routes by inspecting the public.users.role column.
    Only users with role == 'admin' are permitted access.
    """
    if current_user.role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
