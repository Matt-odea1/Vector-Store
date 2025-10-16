# src/main/controller/ContextController.py
from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, Body, Depends, UploadFile, File, Form, HTTPException

from ..dtos.UploadRequest import UploadRequest
from ..dtos.DeleteRequest import DeleteRequest
from ..dtos.ListDocumentsRequest import ListDocumentsRequest
from src.main.service.ContextVectorService import ContextVectorService
from src.main.service.ChatService import ChatService, ChatServiceError
from src.main.dtos.ChatRequest import ChatRequest
from src.main.dtos.ChatResponse import ChatResponse
from src.main.service.FileToTextService import FileToTextService

# Add Deepgram Speech-to-Text import and tempfile/os
import tempfile
import os
from src.main.service.SpeechToTextService import DeepgramTranscribeService


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


# --- New endpoint: transcribe uploaded WAV and return transcript -----------------
@chat_router.post("/transcribe", status_code=200)
async def transcribe_uploaded_audio(
    DocumentTitle: str = Form(...),
    File: UploadFile = File(...),
):
    """
    Minimal endpoint that accepts a document title and an uploaded WAV file (.wav),
    streams the upload to a temporary file, calls the Deepgram transcription service,
    and returns the transcript.

    Returns JSON: {"documentTitle": str, "transcript": str}
    """
    # Save upload to a temporary file because DeepgramTranscribeService expects a file path
    contents = await File.read()
    # Require .wav files
    ext = os.path.splitext(File.filename)[1].lower()
    if ext != ".wav":
        raise HTTPException(status_code=400, detail="Only .wav files are accepted for this endpoint")

    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    try:
        tmp.write(contents)
        tmp.flush()
        tmp_path = tmp.name
    finally:
        tmp.close()

    try:
        svc = DeepgramTranscribeService()
        transcript = svc.transcribe(tmp_path)
        return {"documentTitle": DocumentTitle, "transcript": transcript}
    except Exception as e:
        return {"error": f"Transcription failed: {e}"}
    finally:
        # Clean up temp file
        try:
            os.remove(tmp_path)
        except Exception:
            pass


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
