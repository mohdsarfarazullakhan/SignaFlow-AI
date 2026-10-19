from __future__ import annotations

import logging
from typing import Any, TypedDict

from sqlalchemy.orm import Session

from app.schemas.domain import CustomerRequirement
from app.services.recommendation_service import build_solution, recommend_products
from app.services.requirement_service import fallback_requirement_response

logger = logging.getLogger(__name__)


class JourneyState(TypedDict, total=False):
    message: str
    requirement: dict[str, Any]
    clarification_question: str | None
    recommendations: list[dict[str, Any]]
    solution: dict[str, Any]
    mode: str


def run_customer_journey(db: Session, message: str) -> JourneyState:
    """Run the connected advisory graph; no node receives mutation permissions beyond its role."""

    def requirement_node(state: JourneyState) -> JourneyState:
        result = fallback_requirement_response(state["message"])
        return {**state, "requirement": result.requirement.model_dump(mode="json"), "clarification_question": result.clarification_question, "mode": "langgraph + fallback"}

    def recommendation_node(state: JourneyState) -> JourneyState:
        requirement = CustomerRequirement.model_validate(state["requirement"])
        result = recommend_products(db, requirement, 3)
        return {**state, "recommendations": [item.model_dump(mode="json") for item in result.recommendations]}

    def solution_node(state: JourneyState) -> JourneyState:
        requirement = CustomerRequirement.model_validate(state["requirement"])
        ids = [item["product"]["id"] for item in state.get("recommendations", [])]
        solution = build_solution(db, requirement, ids)
        return {**state, "solution": solution.model_dump(mode="json")}

    try:
        from langgraph.graph import END, START, StateGraph

        graph = StateGraph(JourneyState)
        graph.add_node("requirement_agent", requirement_node)
        graph.add_node("product_advisor", recommendation_node)
        graph.add_node("solution_architect", solution_node)
        graph.add_edge(START, "requirement_agent")
        graph.add_conditional_edges("requirement_agent", lambda state: "clarify" if state.get("clarification_question") else "recommend", {"clarify": END, "recommend": "product_advisor"})
        graph.add_edge("product_advisor", "solution_architect")
        graph.add_edge("solution_architect", END)
        return graph.compile().invoke({"message": message})
    except ImportError:
        state = requirement_node({"message": message})
        if state.get("clarification_question"):
            return state
        return solution_node(recommendation_node(state))

