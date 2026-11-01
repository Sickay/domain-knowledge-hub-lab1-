from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class Claim(BaseModel):
    id: str = Field(..., description="Унікальний ідентифікатор твердження, наприклад CLM-001")
    statement: str = Field(..., description="Зміст твердження або правила")
    kind: Literal["факт", "правило", "гіпотеза"] = Field(..., description="Тип твердження")
    sources: List[str] = Field(..., description="Список джерел або посилань (V1)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Рівень впевненості моделі від 0 до 1")
    scope: str = Field(..., description="Межі застосування (наприклад, верстати ЧПК, SCADA)")
    condition: Optional[str] = Field(None, description="Умова для правил")
    action: Optional[str] = Field(None, description="Дія для правил")


class ExpertAnswer(BaseModel):
    session_id: str
    model_name: str
    claims: List[Claim]
