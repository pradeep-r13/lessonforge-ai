# Trusted reference facts for the Introduction to RAG lesson

This small reference set is a fixed, reviewed baseline for the assessment topic. It is passed to both the generator and evaluator. It is not a live retrieval system and does not prove every generated sentence true; it makes the grounding criteria explicit and enables repeatable checks for known false claims.

- RAG stands for Retrieval-Augmented Generation.
- A RAG system retrieves relevant information from an external knowledge source before generating an answer.
- Retrieved text is supplied to a language model as context for its answer.
- RAG can make private or updated documents available at answer time without retraining the model for every document update.
- RAG does not guarantee correctness: results depend on source quality, retrieval quality, and how the model uses the retrieved context.
- Common stages include preparing/indexing documents, retrieving relevant passages for a query, and generating an answer grounded in those passages.

The reference facts and known-false-claim rules live in `lessonforge/reference_facts.py`. Changes should be reviewed and regression-tested; model output must never modify the rubric or reference facts automatically.
