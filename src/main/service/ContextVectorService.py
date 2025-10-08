# src/main/service/ContextVectorService.py
from __future__ import annotations

import os
import json
import uuid
from typing import List, Optional, Dict, Any

from neo4j import GraphDatabase, Driver

from src.main.utils.SplitByMd import split_by_markdown_heading
from src.main.service.TextPreprocessingService import TextPreprocessingService
from src.main.llm.AgentCoreProvider import AgentCoreProvider


class ContextVectorService:
    def __init__(
        self,
        neo4j_uri: str | None = None,
        neo4j_user: str | None = None,
        neo4j_password: str | None = None,
        aws_region: str | None = None,
        embed_model_id: str | None = None,
        expected_embed_dim: Optional[int] = None,   # defaults to 1024 if None
    ) -> None:
        self.neo4j_uri = neo4j_uri or os.getenv("NEO4J_URI")
        self.neo4j_user = neo4j_user or os.getenv("NEO4J_USERNAME")
        self.neo4j_password = neo4j_password or os.getenv("NEO4J_PASSWORD")

        # AWS Bedrock (Cohere)
        self.aws_region = aws_region or os.getenv("AWS_REGION", "ap-southeast-2")
        self.embed_model_id = embed_model_id or os.getenv("EMBED_MODEL", "cohere.embed-english-v3")
        self.expected_embed_dim = expected_embed_dim or 1024

        # Neo4j driver
        self.driver: Driver = GraphDatabase.driver(self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password))
        self.preprocessor = TextPreprocessingService()
        self.llm = AgentCoreProvider()

    # ------------------------ core ops ------------------------

    def embed(self, text: str) -> List[float]:
        # Use AgentCoreProvider for embeddings
        vectors = self.llm.embed([text])
        if len(vectors[0]) != self.expected_embed_dim:
            raise ValueError(f"Embedding dim mismatch: expected {self.expected_embed_dim}, got {len(vectors[0])}")
        return vectors[0]

    # ------------------------ public API for controller ------------------------

    def upload_document(self, document_name: str, description: str, text: str, scope: str) -> Dict[str, Any]:
        """
        Uploads a document, splitting into chunks. All chunks share the same document_id.
        """
        edited_text = self.preprocessor.preprocess_to_markdown(text)
        print("edited text:", edited_text[:200])
        chunks = split_by_markdown_heading(edited_text) or [edited_text]
        document_id = uuid.uuid4().hex

        inserted = []
        with self.driver.session() as s:
            for i, ch in enumerate(chunks):
                embedding = self.embed(ch)
                s.run(
                    """
                    MERGE (d:Document {id: $id, chunk_idx: $idx})
                    SET d.title = $title,
                        d.description = $description,
                        d.text = $text,
                        d.embedding = $embedding,
                        d.scope = $scope,
                        d.createdAt = datetime()
                    """,
                    id=document_id,
                    title=document_name,
                    description=description,
                    text=ch,
                    embedding=embedding,
                    idx=i,
                    scope=scope,
                )
                inserted.append({
                    "id": document_id,
                    "title": document_name,
                    "description": description,
                    "chunk_idx": i,
                    "scope": scope,
                })

        return {
            "document_id": document_id,
            "title": description,
            "chunks": inserted,
            "embed_dim": self.expected_embed_dim,
            "embed_model": self.embed_model_id,
        }

    def delete_document(self, document_id: str) -> Dict[str, int]:
        """
        Delete all Document nodes with the given id (document_id).
        Returns {'documents_deleted': <n>}
        """
        with self.driver.session() as s:
            rec = s.run(
                """
                MATCH (d:Document {id: $document_id})
                WITH collect(d) AS docs, count(d) AS doc_count
                FOREACH (x IN docs | DETACH DELETE x)
                RETURN doc_count AS documents_deleted
                """,
                document_id=document_id,
            ).single()

            if rec:
                return {"documents_deleted": rec["documents_deleted"]}
            else:
                return {"documents_deleted": 0}

    def list_documents(self, offset: int, limit: int, scope: str):
        query = (
            "MATCH (d:Document) "
            "WHERE d.Scope = $scope "
            "WITH d ORDER BY d.createdAt DESC "
            "SKIP $offset LIMIT $limit "
            "RETURN d.id AS document_id, d.title AS title, d.description AS description, d.scope AS scope, d.createdAt AS created_at "
        )
        with self.driver.session() as s:
            result = s.run(query, scope=scope, offset=offset, limit=limit)
            docs = []
            for record in result:
                docs.append({
                    "document_id": record["document_id"],
                    "title": record["title"],
                    "description": record["description"],
                    "scope": record["scope"],
                    "created_at": record["created_at"],
                })
            return docs

    def close(self) -> None:
        self.driver.close()
