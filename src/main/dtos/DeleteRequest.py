from pydantic import BaseModel

class DeleteRequest(BaseModel):
    document_id: str