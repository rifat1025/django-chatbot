import os
from django.conf import settings
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import KnowledgeDocument, Conversation, Message
from .serializers import (
    KnowledgeDocumentSerializer, ConversationSerializer, ChatRequestSerializer
)
from .rag_engine import ingest_text, ingest_pdf, answer_query


class DocumentUploadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = KnowledgeDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doc = serializer.save(uploaded_by=request.user)

        metadata = {"title": doc.title, "user_id": request.user.id, "doc_id": doc.id}

        if doc.file:
            chunk_count = ingest_pdf(doc.file.path, metadata)
        elif doc.raw_text:
            chunk_count = ingest_text(doc.raw_text, metadata)
        else:
            return Response({"error": "Provide either a file or raw_text."}, status=status.HTTP_400_BAD_REQUEST)

        doc.chunk_count = chunk_count
        doc.save()

        return Response(KnowledgeDocumentSerializer(doc).data, status=status.HTTP_201_CREATED)

    def get(self, request):
        docs = KnowledgeDocument.objects.filter(uploaded_by=request.user).order_by('-created_at')
        return Response(KnowledgeDocumentSerializer(docs, many=True).data)
