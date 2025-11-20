"""Embedding generation and similarity search service."""
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.db.crud import EmbeddingRepository


class EmbeddingService:
    """Service for generating and managing embeddings."""
    
    def __init__(self):
        self.embeddings_model = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.openai_api_key
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks for embedding."""
        chunks = self.text_splitter.split_text(text)
        return chunks
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector for text."""
        embedding = await self.embeddings_model.aembed_query(text)
        return embedding
    
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents."""
        embeddings = await self.embeddings_model.aembed_documents(texts)
        return embeddings
    
    async def generate_and_store_embeddings(
        self,
        session: AsyncSession,
        blog_post_id: int,
        content: str
    ) -> int:
        """
        Generate embeddings for blog content and store in database.
        
        Args:
            session: Database session
            blog_post_id: ID of the blog post
            content: Full blog content text
            
        Returns:
            Number of embeddings created
        """
        # Split content into chunks
        chunks = self.split_text(content)
        
        # Generate embeddings for all chunks
        embeddings = await self.embed_documents(chunks)
        
        # Store in database
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            await EmbeddingRepository.create(
                session,
                blog_post_id=blog_post_id,
                chunk_text=chunk,
                embedding_vector=embedding,
                chunk_index=idx
            )
        
        await session.commit()
        return len(chunks)
    
    async def similarity_search(
        self,
        session: AsyncSession,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search across all embeddings.
        
        Args:
            session: Database session
            query: Search query text
            limit: Maximum number of results
            
        Returns:
            List of similar chunks with metadata
        """
        # Generate query embedding
        query_embedding = await self.embed_text(query)
        
        # Perform vector similarity search (pgvector)
        from sqlalchemy import select, func
        from app.models.database import Embedding, BlogPost
        
        # Use pgvector cosine distance operator
        stmt = (
            select(
                Embedding.chunk_text,
                Embedding.chunk_index,
                BlogPost.title,
                BlogPost.id.label('blog_post_id'),
                func.cosine_distance(Embedding.embedding, query_embedding).label('distance')
            )
            .join(BlogPost, Embedding.blog_post_id == BlogPost.id)
            .order_by('distance')
            .limit(limit)
        )
        
        result = await session.execute(stmt)
        rows = result.all()
        
        return [
            {
                'chunk_text': row.chunk_text,
                'chunk_index': row.chunk_index,
                'blog_title': row.title,
                'blog_post_id': row.blog_post_id,
                'similarity_score': 1 - row.distance  # Convert distance to similarity
            }
            for row in rows
        ]
