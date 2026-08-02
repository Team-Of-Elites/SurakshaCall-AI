from backend.app.orchestration.state import CallState
from backend.app.schemas.identity import CommunityMatch


async def check_community_patterns(state: CallState) -> CommunityMatch:
    from backend.app.orchestration.graph import match_community

    return await match_community(state)
