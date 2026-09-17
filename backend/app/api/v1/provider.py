from fastapi import APIRouter, Depends
from backend.app.core.config import validate_provider_keys
from backend.app.schemas.observability import ProviderStatusOut
from backend.app.auth.dependencies import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/provider", tags=["LLM Provider Status"])

@router.get("/status", response_model=ProviderStatusOut)
def get_provider_status(current_user: User = Depends(get_current_user)):
    """Return safe LLM provider status without exposing secrets."""
    status_info = validate_provider_keys()
    return ProviderStatusOut(
        provider=status_info["provider"],
        configured=status_info["configured"],
        model=status_info.get("model", ""),
        error=status_info.get("error")
    )
