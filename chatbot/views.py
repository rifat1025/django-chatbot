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



class ChatAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_message = serializer.validated_data['message']
        conv_id = serializer.validated_data.get('conversation_id')

        if conv_id:
            conversation = Conversation.objects.filter(id=conv_id, user=request.user).first()
            if not conversation:
                return Response({"error": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            conversation = Conversation.objects.create(
                user=request.user,
                title=user_message[:50]
            )

        Message.objects.create(conversation=conversation, role='user', content=user_message)

        result = answer_query(user_message, user_id=request.user.id)

        assistant_msg = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=result['answer'],
            sources=result['sources'],
        )

        return Response({
            "conversation_id": conversation.id,
            "answer": assistant_msg.content,
            "sources": assistant_msg.sources,
        }, status=status.HTTP_200_OK)
