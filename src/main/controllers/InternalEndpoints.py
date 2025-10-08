# src/main/controller/ContextController.py
from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, Body, Depends, UploadFile, File, Form

from ..dtos.UploadFileRequest import UploadFileRequest
from ..dtos.UploadRequest import UploadRequest
from ..dtos.DeleteRequest import DeleteRequest
from ..dtos.ListDocumentsRequest import ListDocumentsRequest
from src.main.service.ContextVectorService import ContextVectorService
from src.main.service.ChatService import ChatService, ChatServiceError
from src.main.dtos.ChatRequest import ChatRequest
from src.main.dtos.ChatResponse import ChatResponse
from src.main.service.FileToTextService import FileToTextService


# --- Dependency injection ------------------------------------------------------

@lru_cache(maxsize=1)
def _service_singleton() -> ContextVectorService:
    # Build once from env and reuse (keeps a single Neo4j driver instance)
    return ContextVectorService()

def get_context_service() -> ContextVectorService:
    return _service_singleton()


# --- ChatService DI -----------------------------------------------------------
from src.main.llm.AgentCoreProvider import AgentCoreProvider

def _chat_service_singleton() -> ChatService:
    vector_service = _service_singleton()
    agent_client = AgentCoreProvider()  # Wrap as needed
    return ChatService(vector_service, agent_client)

def get_chat_service() -> ChatService:
    return _chat_service_singleton()


router = APIRouter(prefix="/internal/context", tags=["context"])
chat_router = APIRouter(prefix="/internal/chat", tags=["chat"])


# --- Endpoints -----------------------------------------------------------------

@router.post("/upload", status_code=201)
def upload_context(dto: UploadRequest = Body(...), svc: ContextVectorService = Depends(get_context_service)):
    result = svc.upload_document(
        document_name=dto.DocumentName,
        description=dto.Description,
        text=dto.Text,
        scope=dto.Scope
    )
    return {"ok": True, **result}

@router.delete("/delete")
def delete_context(dto: DeleteRequest = Body(...), svc: ContextVectorService = Depends(get_context_service)):
    result = svc.delete_document(document_id=dto.document_id)
    return {"ok": True, **result}

@router.post("/list")
def list_documents(
    body: ListDocumentsRequest = Body(...),
    svc: ContextVectorService = Depends(get_context_service)
):
    docs = svc.list_documents(
        offset=body.Offset,
        limit=body.Limit,
        scope=body.Scope
    )
    return {"documents": docs}

@router.post("/uploadFile", status_code=201)
def upload_file_context(
    File: UploadFile = File(...),
    DocumentName: str = Form(...),
    Description: str = Form(""),
    Scope: str = Form("default"),
    svc: ContextVectorService = Depends(get_context_service)
):
    """
    Upload a PDF file, extract its text using FileToTextService, and process as a document upload.
    """
    text = FileToTextService().extract_text_from_uploadfile(File)
    upload_dto = UploadRequest(
        DocumentName=DocumentName,
        Description=Description,
        Text=text,
        Scope=Scope
    )
    result = svc.upload_document(
        document_name=upload_dto.DocumentName,
        description=upload_dto.Description,
        text=upload_dto.Text,
        scope=upload_dto.Scope
    )
    return {"ok": True, **result}


# --- Chat API models ----------------------------------------------------------
# (ChatRequest and ChatResponse now imported from DTOs)

@chat_router.post("", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest = Body(...), svc: ChatService = Depends(get_chat_service)):
    try:
        result = svc.chat(query=request.query, top_k=request.top_k or 5, session_id=request.session_id)
        return ChatResponse(**result)
    except ChatServiceError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}
