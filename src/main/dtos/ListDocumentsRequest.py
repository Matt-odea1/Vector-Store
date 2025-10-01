from pydantic import BaseModel, Field

class ListDocumentsRequest(BaseModel):
    Offset: int = Field(0, ge=0, description="Number of documents to skip (pagination)")
    Limit: int = Field(10, gt=0, description="Maximum number of documents to return")
    Scope: str = Field(..., min_length=1, description="Scope to filter documents")
