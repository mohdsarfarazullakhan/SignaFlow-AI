from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.workflow import run_customer_journey
from app.core.security import CurrentUser
from app.database.session import get_db
from app.schemas.domain import CustomerRequirement, RecommendationRequest, RecommendationResponse, RequirementRequest, RequirementResponse, SolutionOut, SolutionRequest
from app.services.llm_service import llm_service
from app.services.recommendation_service import build_solution, recommend_products
from app.services.requirement_service import clarification_for, fallback_requirement_response

router = APIRouter(tags=["advisor"])


@router.post("/requirements/extract", response_model=RequirementResponse)
def extract_requirement(payload: RequirementRequest, _: CurrentUser) -> RequirementResponse:
    result = fallback_requirement_response(payload.message)
    live = llm_service.generate_structured(
        "You are the Requirement Agent. Extract only facts present in the customer message. Use null for missing information. Never fabricate budget, dimensions, quantities, or timeline.",
        payload.message,
        CustomerRequirement,
        model_kind="fast",
    )
    if live:
        question = clarification_for(live)
        return RequirementResponse(requirement=live, enough_information=question is None, clarification_question=question, extraction_mode="groq")
    return result


@router.post("/recommend", response_model=RecommendationResponse)
def recommend(payload: RecommendationRequest, _: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> RecommendationResponse:
    return recommend_products(db, payload.requirement, payload.limit)


@router.post("/solutions/build", response_model=SolutionOut)
def solution(payload: SolutionRequest, _: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> SolutionOut:
    return build_solution(db, payload.requirement, payload.recommendation_product_ids)


@router.post("/chat")
def connected_chat(payload: RequirementRequest, _: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    return run_customer_journey(db, payload.message)

