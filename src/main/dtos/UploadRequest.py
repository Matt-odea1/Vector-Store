from pydantic import BaseModel, Field, ConfigDict, AliasChoices

class UploadRequest(BaseModel):
    """
    Body for /internal/context/upload
    """
    DocumentName: str = Field(..., min_length=1, description="Stable identifier for the document (e.g. slug)")
    Description: str = Field(..., min_length=1, description="Human-readable title")
    Text: str = Field(..., min_length=1, description="Raw text/content to ingest")
    Scope: str = Field(..., min_length=1, description="Scope or context for the document")
