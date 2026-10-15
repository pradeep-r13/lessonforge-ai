"""Small trusted reference set for the assignment topic, Introduction to RAG.
Keep these facts reviewed and version-controlled; do not let model output edit them.
"""

RAG_REFERENCE_FACTS = [
    "RAG stands for Retrieval-Augmented Generation.",
    "A RAG system retrieves relevant information from an external knowledge source before generating an answer.",
    "The retrieved text is supplied to a language model as context for its answer.",
    "RAG can make private or updated documents available to a model at answer time without retraining the model for every document update.",
    "RAG does not guarantee correctness: results depend on source quality, retrieval quality, and how the model uses the retrieved context.",
    "Common RAG stages include preparing/indexing documents, retrieving relevant passages for a query, and generating an answer grounded in those passages.",
]

RAG_KNOWN_FALSE_CLAIMS = [
    "rag stands for random answer generation",
    "rag always guarantees correct answers",
    "rag retrains the model every time a document changes",
]

RUBRIC_CHECKS = (
    "accuracy",
    "beginner_language",
    "real_example",
    "jargon_explained",
    "key_coverage",
    "teaching_flow",
)
