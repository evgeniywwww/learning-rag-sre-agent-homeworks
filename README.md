# Learning RAG SRE Agent

Learning project for building a RAG-based knowledge retrieval layer for an AI SRE Assistant.

## Project goal

The goal of this project is to build a knowledge layer for an AI SRE Assistant that helps SRE engineers retrieve operational information, incident procedures and troubleshooting guidance.

Current knowledge base contains:

- SRE operational policies
- Incident response procedures
- Service tier definitions
- Kubernetes troubleshooting runbooks
- Reliability improvement strategies


## RAG pipeline

Current implementation:

Raw documents  
↓  
Document normalization  
↓  
Chunk generation  
↓  
Embeddings creation  
↓  
FAISS vector index  
↓  
Semantic retrieval


## Implemented components

### Knowledge preparation

Implemented:

- Markdown document loading
- Document normalization
- Chunk generation
- Metadata preservation

Output:

data/processed/chunks.jsonl


### Embeddings and vector index

Implemented:

- Sentence Transformers embeddings
- Vector normalization
- FAISS IndexFlatIP similarity search

Embedding model:

sentence-transformers/all-MiniLM-L6-v2

Embedding dimension:

384

Generated artifacts:

data/processed/embeddings.npy

index/faiss.index


### Semantic retrieval

Implemented:

- Query embedding generation
- Top-k semantic search
- Retrieval of chunk text and metadata

Example retrieval results:

outputs/retrieval_examples.md


## Current limitations

Current implementation uses baseline semantic similarity search.

Possible improvements:

- Better chunking strategy based on document structure
- Metadata filtering
- Hybrid search
- Reranking models
- Integration with LLM generation layer


## Future direction

The project will be extended towards an AI SRE Assistant capable of:

- Incident investigation assistance
- Runbook retrieval
- Operational recommendations
- Integration with infrastructure tools such as Kubernetes, monitoring systems and CI/CD platforms