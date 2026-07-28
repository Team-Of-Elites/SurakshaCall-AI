from backend.app.orchestration.state import CallState
from backend.app.schemas.identity import VerificationResult


async def verify_caller_identity(state: CallState) -> VerificationResult:
    from backend.app.orchestration.graph import verify_identity

    return await verify_identity(state)
