from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.security import require_roles
from app.database.session import get_db
from app.models.entities import Quote, User, UserRole
from app.schemas.domain import QuoteCreate, QuoteOut
from app.services.quote_service import create_quote, render_quote_pdf

router = APIRouter(prefix="/quotes", tags=["quotations"])
SalesUser = Annotated[User, Depends(require_roles(UserRole.SALES, UserRole.ADMIN))]


@router.post("", response_model=QuoteOut, status_code=201)
def post_quote(payload: QuoteCreate, _: SalesUser, db: Annotated[Session, Depends(get_db)]) -> QuoteOut:
    try:
        quote = create_quote(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return QuoteOut.model_validate(quote)


@router.get("", response_model=list[QuoteOut])
def list_quotes(_: SalesUser, db: Annotated[Session, Depends(get_db)]) -> list[QuoteOut]:
    return [QuoteOut.model_validate(item) for item in db.query(Quote).order_by(Quote.created_at.desc()).all()]


@router.get("/{quote_id}", response_model=QuoteOut)
def get_quote(quote_id: str, _: SalesUser, db: Annotated[Session, Depends(get_db)]) -> QuoteOut:
    quote = db.get(Quote, quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return QuoteOut.model_validate(quote)


@router.post("/{quote_id}/pdf")
def quote_pdf(quote_id: str, _: SalesUser, db: Annotated[Session, Depends(get_db)]) -> StreamingResponse:
    quote = db.get(Quote, quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
    payload = render_quote_pdf(quote)
    return StreamingResponse(BytesIO(payload), media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{quote.reference}.pdf"'})

