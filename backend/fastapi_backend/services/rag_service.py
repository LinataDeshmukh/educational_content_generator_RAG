"""RAG service using LlamaIndex with Pinecone."""

import logging
from typing import Optional

from llama_index.core import VectorStoreIndex, PromptTemplate
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms import LLM
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

# Try to import ResponseSynthesizer (may vary by LlamaIndex version)
try:
    from llama_index.core.response_synthesizers import ResponseSynthesizer
    HAS_RESPONSE_SYNTHESIZER = True
except ImportError:
    HAS_RESPONSE_SYNTHESIZER = False

from fastapi_backend.config import settings
from fastapi_backend.models.document import DocumentChunk
from fastapi_backend.services.vector_store import VectorStoreService
from fastapi_backend.utils.errors import RAGServiceError

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG operations using LlamaIndex."""

    def __init__(
        self,
        vector_store_service: VectorStoreService,
        embedding_model: Optional[BaseEmbedding] = None,
        llm: Optional[LLM] = None,
    ):
        """
        Initialize the RAG service.

        Args:
            vector_store_service: Vector store service instance
            embedding_model: Optional embedding model (defaults to OpenAI)
            llm: Optional LLM (defaults to OpenAI)
        """
        self.vector_store_service = vector_store_service

        # Initialize embedding model
        if embedding_model:
            self.embedding_model = embedding_model
        else:
            self.embedding_model = OpenAIEmbedding(
                model=settings.embedding_model,
                api_key=settings.openai_api_key,
            )

        # Initialize LLM
        if llm:
            self.llm = llm
        else:
            self.llm = OpenAI(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                api_key=settings.openai_api_key,
            )

        self.index: Optional[VectorStoreIndex] = None
        self.query_engine: Optional[RetrieverQueryEngine] = None

    def index_documents(
        self, chunks: list[DocumentChunk], namespace: Optional[str] = None
    ) -> str:
        """
        Index document chunks in the vector store.

        Args:
            chunks: List of document chunks to index
            namespace: Optional namespace for document isolation

        Returns:
            Document ID or namespace identifier

        Raises:
            RAGServiceError: If indexing fails
        """
        try:
            # Convert DocumentChunks to LlamaIndex Documents
            from llama_index.core import Document as LlamaDocument
            
            llama_docs = []
            for idx, chunk in enumerate(chunks):
                metadata = {
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    **(chunk.metadata or {}),
                }
                if namespace:
                    metadata["namespace"] = namespace
                
                # Generate unique ID for each document
                doc_id = f"{namespace}_{idx}" if namespace else f"doc_{idx}"
                    
                llama_doc = LlamaDocument(
                    text=chunk.text,
                    metadata=metadata,
                    id_=doc_id,
                )
                llama_docs.append(llama_doc)

            # Get vector store
            vector_store = self.vector_store_service.get_vector_store()

            # Log document details before indexing
            logger.info("\n" + "=" * 80)
            logger.info("INDEXING PREPARATION")
            logger.info("=" * 80)
            logger.info(f"Total documents to index: {len(llama_docs)}")
            logger.info(f"Namespace: {namespace if namespace else 'default'}")
            logger.info("\nFirst 5 documents preview:")
            for i, doc in enumerate(llama_docs[:5], 1):
                logger.info(f"\n  Document #{i}:")
                logger.info(f"    ID: {doc.id_ if hasattr(doc, 'id_') and doc.id_ else 'N/A'}")
                logger.info(f"    Page: {doc.metadata.get('page_number', 'N/A')}")
                logger.info(f"    Text Length: {len(doc.text)} characters")
                preview = doc.text[:150].replace('\n', ' ').replace('\r', ' ')
                logger.info(f"    Preview: {preview}...")
                logger.info(f"    Metadata: {doc.metadata}")
            if len(llama_docs) > 5:
                logger.info(f"\n  ... and {len(llama_docs) - 5} more documents")
            logger.info("=" * 80)

            # Create index from documents (this generates embeddings and adds to Pinecone)
            logger.info("Creating VectorStoreIndex and generating embeddings...")
            logger.info(f"Using embedding model: {self.embedding_model}")
            logger.info(f"Vector store: {type(vector_store).__name__}")
            if namespace:
                logger.info(f"Using namespace: {namespace}")
            
            # IMPORTANT: Use from_vector_store first, then insert documents
            # This ensures we're working with the existing Pinecone index
            # from_documents() might not persist properly in some cases
            logger.info("Creating index from existing vector store...")
            temp_index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                embed_model=self.embedding_model,
            )
            
            # Convert documents to nodes (documents are already chunked, so this is just conversion)
            # Then insert them - this will generate embeddings and persist to Pinecone
            from llama_index.core.schema import TextNode
            
            logger.info("Converting documents to nodes...")
            # Since documents are already chunked, we'll create nodes directly
            nodes = []
            for doc in llama_docs:
                # Create a node from the document (documents are already chunked)
                node = TextNode(
                    text=doc.text,
                    metadata=doc.metadata,
                    id_=doc.id_ if hasattr(doc, 'id_') and doc.id_ else None,
                )
                nodes.append(node)
            
            logger.info(f"\nCreated {len(nodes)} nodes from {len(llama_docs)} documents")
            logger.info("\n" + "-" * 80)
            logger.info("NODE DETAILS (First 3):")
            logger.info("-" * 80)
            for i, node in enumerate(nodes[:3], 1):
                logger.info(f"\n  Node #{i}:")
                logger.info(f"    ID: {node.id_ if hasattr(node, 'id_') and node.id_ else 'N/A'}")
                logger.info(f"    Text Length: {len(node.text)} characters")
                preview = node.text[:150].replace('\n', ' ').replace('\r', ' ')
                logger.info(f"    Preview: {preview}...")
                logger.info(f"    Metadata: {node.metadata}")
            if len(nodes) > 3:
                logger.info(f"\n  ... and {len(nodes) - 3} more nodes")
            logger.info("-" * 80)
            logger.info("\nInserting nodes into index (generating embeddings and storing in Pinecone)...")
            logger.info("This may take a moment depending on the number of chunks...")
            
            # Insert nodes - this will generate embeddings and store in Pinecone
            # Use the already-initialized Pinecone index from vector_store_service
            try:
                # Get the Pinecone index from vector store service
                pinecone_index = self.vector_store_service.pinecone_index
                
                if not pinecone_index:
                    raise RAGServiceError("Pinecone index not initialized")
                
                # Generate embeddings and upsert
                vectors_to_upsert = []
                for node_idx, node in enumerate(nodes):
                    # Get embedding for the node text
                    embedding = self.embedding_model.get_text_embedding(node.text)
                    
                    # Prepare metadata
                    metadata = {
                        "text": node.text,  # Store text in metadata for retrieval
                        "page_number": node.metadata.get("page_number", 1),
                        "chunk_index": node.metadata.get("chunk_index", node_idx),
                    }
                    
                    # Add namespace to metadata if provided
                    if namespace:
                        metadata["namespace"] = namespace
                    
                    # Store filename from document metadata (first chunk usually has it)
                    if node.metadata.get("filename"):
                        metadata["filename"] = node.metadata.get("filename")
                    elif node.metadata.get("files"):
                        files_info = node.metadata.get("files")
                        if isinstance(files_info, list):
                            filenames = [f.get("filename", "") for f in files_info if isinstance(f, dict)]
                            if filenames:
                                metadata["filename"] = ", ".join(filter(None, filenames))
                    
                    vectors_to_upsert.append({
                        "id": node.id_ if hasattr(node, 'id_') and node.id_ else f"{namespace or 'doc'}_{node_idx}",
                        "values": embedding,
                        "metadata": metadata,
                    })
                
                # Upsert in batches
                batch_size = 100
                for i in range(0, len(vectors_to_upsert), batch_size):
                    batch = vectors_to_upsert[i:i + batch_size]
                    if namespace:
                        pinecone_index.upsert(vectors=batch, namespace=namespace)
                    else:
                        pinecone_index.upsert(vectors=batch)
                    logger.info(f"Upserted batch {i//batch_size + 1} ({len(batch)} vectors)")
                
                logger.info(f"Successfully inserted {len(nodes)} nodes into Pinecone")
            except Exception as insert_error:
                logger.error(f"Error inserting nodes: {insert_error}", exc_info=True)
                raise
            
            logger.info("Nodes inserted successfully. Verifying persistence...")
            
            # Store the index for querying later
            self.index = temp_index

            logger.info(
                f"Successfully indexed {len(chunks)} chunks to Pinecone"
                + (f" (namespace: {namespace})" if namespace else "")
            )
            
            # Verify by checking Pinecone
            try:
                from fastapi_backend.config import settings
                from pinecone import Pinecone
                pc = Pinecone(api_key=settings.pinecone_api_key)
                index = pc.Index(settings.pinecone_index_name)
                stats = index.describe_index_stats()
                total_vectors = stats.get('total_vector_count', 0)
                namespace_stats = stats.get('namespaces', {})
                logger.info(f"Pinecone verification: Total vectors in index: {total_vectors}")
                if namespace and namespace in namespace_stats:
                    ns_count = namespace_stats[namespace].get('vector_count', 0)
                    logger.info(f"  Vectors in namespace '{namespace}': {ns_count}")
                elif namespace_stats:
                    logger.info(f"  Available namespaces: {list(namespace_stats.keys())}")
                else:
                    logger.info("  No namespace stats available (might be in default namespace)")
            except Exception as e:
                logger.warning(f"Could not verify Pinecone count: {e}")

            return namespace or "default"

        except Exception as e:
            error_msg = f"Failed to index documents: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise RAGServiceError(error_msg) from e

    def create_query_engine(
        self, similarity_top_k: int = 5, namespace: Optional[str] = None
    ) -> RetrieverQueryEngine:
        """
        Create a query engine for RAG queries.

        Args:
            similarity_top_k: Number of similar chunks to retrieve
            namespace: Optional namespace to query

        Returns:
            RetrieverQueryEngine instance

        Raises:
            RAGServiceError: If query engine creation fails
        """
        try:
            if not self.index:
                # Create index from vector store if not exists
                vector_store = self.vector_store_service.get_vector_store()
                self.index = VectorStoreIndex.from_vector_store(
                    vector_store=vector_store,
                    embed_model=self.embedding_model,
                )

            # Create retriever
            retriever = VectorIndexRetriever(
                index=self.index,
                similarity_top_k=similarity_top_k,
            )

            # Create custom prompt template for better responses
            custom_prompt = PromptTemplate(
                """You are an expert educational assistant helping students understand material from uploaded documents.

Context Information:
{context_str}

Instruction: Based on the provided context information above, answer the following question. 
If the context does not contain enough information to answer the question, please state that clearly.

Guidelines:
1. Provide a clear, comprehensive, and well-structured answer
2. Use the context information directly - quote or paraphrase relevant sections when helpful
3. If the question requires information not in the context, acknowledge this limitation
4. Structure your answer with:
   - A brief direct answer first
   - Then provide detailed explanation with examples from the context
   - Use bullet points or numbered lists when appropriate for clarity
5. Maintain an educational, helpful tone
6. If multiple concepts are mentioned, explain how they relate to each other
7. Cite specific details from the context to support your answer

Question: {query_str}

Answer:"""
            )

            # Create query engine with custom prompt
            if HAS_RESPONSE_SYNTHESIZER:
                try:
                    response_synthesizer = ResponseSynthesizer.from_args(
                        llm=self.llm,
                        text_qa_template=custom_prompt,
                    )

                    self.query_engine = RetrieverQueryEngine(
                        retriever=retriever,
                        response_synthesizer=response_synthesizer,
                    )
                except Exception as e:
                    logger.warning(f"Could not use custom prompt, using default: {e}")
                    self.query_engine = RetrieverQueryEngine.from_args(
                        retriever=retriever,
                        llm=self.llm,
                    )
            else:
                # Fallback to default if ResponseSynthesizer not available
                logger.warning("ResponseSynthesizer not available, using default query engine")
                self.query_engine = RetrieverQueryEngine.from_args(
                    retriever=retriever,
                    llm=self.llm,
                )

            logger.info("Created query engine for RAG queries")

            return self.query_engine

        except Exception as e:
            error_msg = f"Failed to create query engine: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise RAGServiceError(error_msg) from e

    def _detect_question_type(self, question: str) -> str:
        """
        Detect the type of question to adapt prompting strategy.

        Args:
            question: User question

        Returns:
            Question type: 'list', 'definition', 'comparison', 'how', 'why', 'what', 'general'
        """
        question_lower = question.lower()
        
        # List/pointers questions
        if any(word in question_lower for word in ['list', 'enumerate', 'give me', 'what are', 'name', 'mention', 'pointers', 'points']):
            return 'list'
        
        # Definition questions
        if any(word in question_lower for word in ['what is', 'define', 'definition', 'meaning of', 'explain what']):
            return 'definition'
        
        # Comparison questions
        if any(word in question_lower for word in ['compare', 'difference', 'versus', 'vs', 'between', 'contrast']):
            return 'comparison'
        
        # How-to questions
        if question_lower.startswith('how'):
            return 'how'
        
        # Why questions
        if question_lower.startswith('why'):
            return 'why'
        
        # What questions
        if question_lower.startswith('what'):
            return 'what'
        
        return 'general'

    def _create_dynamic_prompt(
        self, question: str, context: str, question_type: str
    ) -> str:
        """
        Create a dynamic prompt based on question type and context.

        Args:
            question: User question
            context: Retrieved context chunks
            question_type: Detected question type

        Returns:
            Formatted prompt string
        """
        # Base prompt structure
        base_prompt = f"""You are an expert educational assistant helping students understand material from uploaded documents.

Context Information from Document:
{context}

User Question: {question}

"""

        # Question-type specific instructions
        if question_type == 'list':
            prompt = base_prompt + """Instructions:
1. Identify all key points, items, or concepts related to the question
2. Present them as a clear, numbered or bulleted list with proper formatting
3. Use EXACT formatting with proper indentation:
   
   **Item 1 Name:**
   - Brief explanation (1-2 sentences)
   
   **Item 2 Name:**
   - Brief explanation (1-2 sentences)
   
   **Item 3 Name:**
   - Brief explanation (1-2 sentences)

4. CRITICAL FORMATTING REQUIREMENTS:
   - Each item must be on its own line with a blank line before it
   - Use **bold** for item names/headings
   - Use proper indentation with dashes or bullets for explanations
   - Add a blank line between each item for readability
   - Do NOT write as a continuous paragraph

5. If the context mentions specific examples, include them under each item
6. Ensure all items are directly from the context provided

Answer:"""
        
        elif question_type == 'definition':
            prompt = base_prompt + """Instructions:
1. Provide a clear, concise definition first (1-2 sentences) - put this on its own line
2. Then add a blank line and expand with detailed explanation
3. Use proper formatting with clear sections:
   
   **Definition:**
   [Your definition here - 1-2 sentences]
   
   **Key Characteristics:**
   - Characteristic 1: Explanation
   - Characteristic 2: Explanation
   - Characteristic 3: Explanation
   
   **How It Works:**
   [Explanation of how it works or what it does]
   
   **Examples:**
   - Example 1 from context
   - Example 2 from context

4. CRITICAL: Use proper line breaks, blank lines between sections, and indentation
5. Do NOT write as one continuous paragraph
6. Use the context information directly to support your definition

Answer:"""
        
        elif question_type == 'comparison':
            prompt = base_prompt + """Instructions:
1. Identify the items/concepts being compared
2. Present similarities and differences with proper formatting:
   
   **Similarities:**
   - Similarity 1: Explanation
   - Similarity 2: Explanation
   
   **Differences:**
   - Difference 1: Explanation
   - Difference 2: Explanation

3. CRITICAL: Use blank lines between sections, proper indentation, and clear headings
4. Reference specific details from the context
5. Do NOT write as a continuous paragraph - use proper line breaks

Answer:"""
        
        elif question_type == 'how':
            prompt = base_prompt + """Instructions:
1. Provide a step-by-step explanation with proper formatting:
   
   **Step 1:**
   [Explanation of step 1]
   
   **Step 2:**
   [Explanation of step 2]
   
   **Step 3:**
   [Explanation of step 3]

2. CRITICAL: Each step must be on separate lines with blank lines between them
3. Use bold headings for each step number
4. Include specific details from the context
5. Explain each step clearly with proper indentation
6. If the context provides examples, reference them under relevant steps
7. Do NOT write as a continuous paragraph

Answer:"""
        
        elif question_type == 'why':
            prompt = base_prompt + """Instructions:
1. Identify the reasons or explanations from the context
2. Present them with proper formatting:
   
   **Reason 1:**
   [Explanation - most important first]
   
   **Reason 2:**
   [Explanation]
   
   **Reason 3:**
   [Explanation]

3. CRITICAL: Use blank lines between each reason, proper indentation, and bold headings
4. Present in logical order (most important first)
5. Explain the cause-effect relationships clearly
6. Reference specific information from the context
7. Do NOT write as a continuous paragraph

Answer:"""
        
        else:  # general or what
            prompt = base_prompt + """Instructions:
1. Provide a comprehensive answer with proper formatting:
   
   **Brief Answer:**
   [Direct answer - 1-2 sentences]
   
   **Detailed Explanation:**
   [Main explanation paragraph]
   
   **Key Points:**
   - Point 1: Explanation
   - Point 2: Explanation
   - Point 3: Explanation
   
   **Examples:**
   - Example 1 from context
   - Example 2 from context

2. CRITICAL FORMATTING:
   - Use blank lines between each section
   - Use bold headings for sections (**Section Name:**)
   - Use proper indentation for bullet points
   - Each section should be clearly separated
   - Do NOT write as one continuous paragraph

3. Ensure all information comes from the provided context
4. Maintain clarity and educational tone
5. Use bullet points or numbered lists for multiple concepts

Answer:"""

        return prompt

    def query(
        self,
        question: str,
        similarity_top_k: int = 5,
        namespace: Optional[str] = None,
    ) -> dict:
        """
        Query the RAG system with a question.

        Args:
            question: User question
            similarity_top_k: Number of similar chunks to retrieve
            namespace: Optional namespace to query

        Returns:
            Dictionary with answer, source information, and whether answer is from document

        Raises:
            RAGServiceError: If query fails
        """
        try:
            # First, retrieve context to check if we have relevant information
            context_chunks = self.retrieve_context(
                query=question,
                top_k=similarity_top_k,
                namespace=namespace,
            )
            
            # Manage context window to avoid token limits
            context_chunks = self._manage_context_window(context_chunks, max_tokens=4000)

            # Check if we have relevant context
            # For now, we'll use all chunks that have meaningful text
            # The similarity scores from LlamaIndex/Pinecone may vary in format
            has_relevant_context = False
            relevant_chunks = []
            
            if context_chunks:
                # Filter chunks with meaningful content
                for chunk in context_chunks:
                    text = chunk.get("text", "").strip()
                    score = chunk.get("score")
                    
                    # Check if chunk has meaningful text (at least 50 characters)
                    if text and len(text) >= 50:
                        relevant_chunks.append(chunk)
                        logger.debug(f"Including chunk with score: {score}, length: {len(text)}")
                
                has_relevant_context = len(relevant_chunks) > 0
                logger.info(f"Found {len(relevant_chunks)} relevant chunks out of {len(context_chunks)} retrieved")

            # Use relevant_chunks if available, otherwise use all context_chunks
            chunks_to_use = relevant_chunks if relevant_chunks else context_chunks

            # If no relevant context, use fallback to general knowledge
            if not has_relevant_context or not chunks_to_use:
                logger.info(
                    f"No relevant context found for query: {question[:50]}... "
                    "Using general knowledge fallback."
                )

                # Use LLM directly with a prompt indicating information is not in the document
                fallback_prompt = f"""The user asked: "{question}"

IMPORTANT: The information requested is NOT available in the uploaded document/material. 
Please answer the question using your general knowledge, but clearly state at the beginning 
that this information is not found in the provided materials.

Format your response as:
"This information is not available in the provided materials. However, based on general knowledge: [your answer]"

Answer:"""

                llm_response = self.llm.complete(fallback_prompt)
                answer = str(llm_response).strip()

                return {
                    "answer": answer,
                    "sources": [],
                    "from_document": False,
                    "message": "Information not found in provided materials. Answer based on general knowledge.",
                }

            # Detect question type for dynamic prompting
            question_type = self._detect_question_type(question)
            logger.info(f"Detected question type: {question_type} for query: {question[:50]}...")

            # Format context chunks into a single context string with better structure
            context_text = "\n\n---\n\n".join(
                [
                    f"[Source {i+1} - Page {chunk.get('metadata', {}).get('page_number', 'N/A')}]\n{chunk.get('text', '')}"
                    for i, chunk in enumerate(chunks_to_use)
                ]
            )

            # Create dynamic prompt based on question type
            dynamic_prompt = self._create_dynamic_prompt(
                question=question,
                context=context_text,
                question_type=question_type,
            )

            # Use LLM directly with custom prompt for better control
            logger.info("Generating answer with dynamic prompt...")
            llm_response = self.llm.complete(dynamic_prompt)
            answer_text = str(llm_response).strip()

            # Post-process answer for better quality
            answer_text = self._post_process_answer(answer_text)

            # Check if the RAG response indicates no information was found
            # Look for phrases that suggest the answer is not from the document
            no_info_phrases = [
                "provided context information does not include",
                "not available in the provided",
                "not found in the provided",
                "not mentioned in the",
                "not in the provided",
                "does not contain",
                "no information about",
                "no details about",
                "i'm sorry, but",
                "i cannot find",
                "unable to find",
                "the context does not contain",
            ]
            
            answer_lower = answer_text.lower()
            indicates_no_info = any(phrase in answer_lower for phrase in no_info_phrases)

            # Extract source nodes from context chunks (since we're using direct LLM call)
            source_nodes = []
            for chunk in chunks_to_use:
                text = chunk.get("text", "").strip()
                if len(text) < 50:  # Skip very short sources
                    continue
                source_info = {
                    "text": text[:300] + "..." if len(text) > 300 else text,
                    "score": chunk.get("score"),
                    "metadata": chunk.get("metadata", {}),
                }
                source_nodes.append(source_info)

            # Check if answer indicates no information (for fallback detection)
            answer_lower = answer_text.lower()
            no_info_phrases = [
                "provided context information does not include",
                "not available in the provided",
                "not found in the provided",
                "not mentioned in the",
                "not in the provided",
                "does not contain",
                "no information about",
                "no details about",
                "i'm sorry, but",
                "i cannot find",
                "unable to find",
                "the context does not contain",
            ]
            indicates_no_info = any(phrase in answer_lower for phrase in no_info_phrases)

            # If answer indicates no info or no sources, use fallback
            if indicates_no_info or len(source_nodes) == 0:
                logger.info(
                    f"RAG response indicates no information found for: {question[:50]}... "
                    "Using general knowledge fallback."
                )

                # Use LLM directly with a prompt indicating information is not in the document
                fallback_prompt = f"""The user asked: "{question}"

IMPORTANT: The information requested is NOT available in the uploaded document/material. 
Please answer the question using your general knowledge, but clearly state at the beginning 
that this information is not found in the provided materials.

Format your response as:
"This information is not available in the provided materials. However, based on general knowledge: [your answer]"

Answer:"""

                llm_response = self.llm.complete(fallback_prompt)
                answer = str(llm_response).strip()

                return {
                    "answer": answer,
                    "sources": [],
                    "from_document": False,
                    "message": "Information not found in provided materials. Answer based on general knowledge.",
                }

            result = {
                "answer": answer_text,
                "sources": source_nodes,
                "from_document": True,
                "message": "Answer based on provided materials.",
            }

            logger.info(
                f"Processed RAG query: {question[:50]}... (found {len(source_nodes)} sources)"
            )

            return result

        except Exception as e:
            error_msg = f"Failed to process RAG query: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise RAGServiceError(error_msg) from e

    def retrieve_context(
        self, query: str, top_k: int = 5, namespace: Optional[str] = None
    ) -> list[dict]:
        """
        Retrieve relevant context chunks for a query with improved filtering.

        Args:
            query: Query string
            top_k: Number of chunks to retrieve
            namespace: Optional namespace to query (CRITICAL for document isolation)

        Returns:
            List of relevant chunks with metadata, sorted by relevance

        Raises:
            RAGServiceError: If retrieval fails
        """
        try:
            logger.info(
                f"Retrieving context for query: '{query[:50]}...' "
                f"(top_k={top_k}, namespace={namespace if namespace else 'ALL'})"
            )

            # Use Pinecone directly for namespace filtering if namespace is provided
            if namespace:
                # Get the Pinecone index from vector store service (already initialized)
                pinecone_index = self.vector_store_service.pinecone_index
                
                if not pinecone_index:
                    raise RAGServiceError("Pinecone index not initialized")

                # Get embedding for the query
                query_embedding = self.embedding_model.get_query_embedding(query)

                # Query with namespace filter
                query_response = pinecone_index.query(
                    vector=query_embedding,
                    top_k=min(top_k * 2, 20),  # Retrieve more for filtering
                    namespace=namespace,
                    include_metadata=True,
                )

                results = []
                for match in query_response.get("matches", []):
                    # Pinecone returns matches as dicts, not objects
                    metadata = match.get("metadata", {}) if isinstance(match, dict) else (match.metadata or {})
                    score = match.get("score") if isinstance(match, dict) else match.score
                    
                    # Get text from metadata (we store it as "text" when indexing)
                    text = metadata.get("text", "").strip() if metadata else ""
                    
                    # Skip if no text or too short
                    if not text or len(text) < 50:
                        logger.debug(f"Skipping match with insufficient text (length: {len(text)})")
                        continue

                    # Verify namespace matches (double-check)
                    chunk_namespace = metadata.get("namespace")
                    if chunk_namespace and chunk_namespace != namespace:
                        logger.warning(
                            f"Namespace mismatch: expected {namespace}, got {chunk_namespace}. Skipping."
                        )
                        continue

                    results.append(
                        {
                            "text": text,
                            "score": score,
                            "metadata": metadata,
                        }
                    )

                # Sort by score (higher is better for cosine similarity)
                results.sort(key=lambda x: x.get("score", 0), reverse=True)
                
                # Take top_k most relevant
                results = results[:top_k]

                logger.info(
                    f"Retrieved {len(results)} relevant chunks from namespace '{namespace}' "
                    f"(queried {len(query_response.get('matches', []))} total matches)"
                )

                return results

            else:
                # Fallback: Use LlamaIndex retriever (no namespace filtering)
                logger.warning(
                    "No namespace provided - querying ALL namespaces. "
                    "This may return results from multiple documents."
                )

                if not self.index:
                    vector_store = self.vector_store_service.get_vector_store()
                    self.index = VectorStoreIndex.from_vector_store(
                        vector_store=vector_store,
                        embed_model=self.embedding_model,
                    )

                # Retrieve more chunks initially for better filtering
                retriever = VectorIndexRetriever(
                    index=self.index,
                    similarity_top_k=min(top_k * 2, 10),  # Retrieve more for filtering
                )

                nodes = retriever.retrieve(query)

                results = []
                for node in nodes:
                    score = node.score if hasattr(node, "score") else None
                    text = node.text.strip()
                    
                    # Filter out very short or empty chunks
                    if len(text) < 50:
                        continue
                    
                    results.append(
                        {
                            "text": text,
                            "score": score,
                            "metadata": node.metadata or {},
                        }
                    )

                # Sort by score (higher is better for similarity, lower is better for distance)
                # Assuming cosine similarity where higher is better
                results.sort(key=lambda x: x.get("score", 0), reverse=True)
                
                # Take top_k most relevant
                results = results[:top_k]

                logger.info(f"Retrieved {len(results)} relevant chunks for query (no namespace filter)")

                return results

        except Exception as e:
            error_msg = f"Failed to retrieve context: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise RAGServiceError(error_msg) from e

    def _post_process_answer(self, answer: str) -> str:
        """
        Post-process answer to improve quality and formatting.

        Args:
            answer: Raw answer from LLM

        Returns:
            Processed answer with improved formatting
        """
        # Remove redundant phrases
        redundant_phrases = [
            "Based on the provided context information,",
            "According to the context information,",
            "Based on the context,",
            "According to the context,",
            "Based on the provided context,",
        ]
        
        processed = answer
        for phrase in redundant_phrases:
            if processed.lower().startswith(phrase.lower()):
                processed = processed[len(phrase):].strip()
                # Capitalize first letter
                if processed:
                    processed = processed[0].upper() + processed[1:]
        
        # Preserve markdown formatting - don't collapse whitespace in structured content
        # Check if answer has markdown structure (headers, lists, etc.)
        has_markdown = (
            "**" in processed or 
            "#" in processed or 
            ("-" in processed and "\n" in processed) or 
            ("*" in processed and "\n" in processed) or
            "\n\n" in processed
        )
        
        if has_markdown:
            # Remove markdown bold syntax (**text**) and convert to plain text with structure
            # Replace **text** with just text (removing the **)
            import re
            processed = re.sub(r'\*\*(.+?)\*\*', r'\1', processed)
            
            # Preserve structure - only clean up excessive newlines
            while "\n\n\n" in processed:
                processed = processed.replace("\n\n\n", "\n\n")
            
            # Ensure list items are properly formatted
            lines = processed.split("\n")
            formatted_lines = []
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped:
                    formatted_lines.append(stripped)
                else:
                    # Preserve blank lines for structure (but limit to one)
                    if formatted_lines and formatted_lines[-1]:
                        formatted_lines.append("")
            
            processed = "\n".join(formatted_lines)
        else:
            # For non-markdown content, ensure proper spacing
            processed = " ".join(processed.split())
        
        # Final cleanup - ensure no more than 2 consecutive newlines
        while "\n\n\n" in processed:
            processed = processed.replace("\n\n\n", "\n\n")
        
        return processed.strip()

    def _manage_context_window(
        self, chunks: list[dict], max_tokens: int = 4000
    ) -> list[dict]:
        """
        Manage context window by selecting most relevant chunks and truncating if needed.

        Args:
            chunks: List of context chunks
            max_tokens: Maximum tokens for context (rough estimate: 1 token ≈ 4 characters)

        Returns:
            Filtered and optimized list of chunks
        """
        if not chunks:
            return []

        # Estimate tokens (rough: 1 token ≈ 4 characters)
        total_chars = sum(len(chunk.get("text", "")) for chunk in chunks)
        estimated_tokens = total_chars / 4

        if estimated_tokens <= max_tokens:
            return chunks

        # If too large, prioritize by score and length
        # Sort by score (higher is better)
        sorted_chunks = sorted(
            chunks,
            key=lambda x: (x.get("score", 0), len(x.get("text", ""))),
            reverse=True,
        )

        # Select chunks until we're under the limit
        selected = []
        current_tokens = 0

        for chunk in sorted_chunks:
            chunk_text = chunk.get("text", "")
            chunk_tokens = len(chunk_text) / 4

            if current_tokens + chunk_tokens <= max_tokens:
                selected.append(chunk)
                current_tokens += chunk_tokens
            else:
                # Truncate this chunk if it's very relevant
                remaining = max_tokens - current_tokens
                if remaining > 200:  # Only if we have meaningful space
                    truncated_text = chunk_text[: int(remaining * 4)]
                    truncated_chunk = chunk.copy()
                    truncated_chunk["text"] = truncated_text + "..."
                    selected.append(truncated_chunk)
                break

        return selected

