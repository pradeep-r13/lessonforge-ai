# Introduction to RAG

**Who this lesson is for:** A beginner who is new to Artificial Intelligence (AI).

## What is it?

RAG stands for **Retrieval-Augmented Generation**. It is a way for an AI system to look up useful information from documents before it writes an answer.

Think of it like an open-book exam. Instead of answering only from memory, the system first finds helpful pages and then uses them to answer the question.

## Why do we need it?

An AI model may not know the latest rules of a college or the private documents of a company. RAG can search those documents and give the useful parts to the model as context.

RAG does not guarantee a correct answer. If the documents are wrong or the system finds the wrong passage, the answer can still be wrong.

## How does it work?

1. **Prepare documents:** Split documents into smaller passages and store them in a searchable system.
2. **Receive a question:** A learner asks something in normal language.
3. **Retrieve information:** The system searches for passages related to the question.
4. **Generate an answer:** A language model reads the question and the retrieved passages, then writes an answer using that context.
5. **Check the answer:** A well-designed system can verify that the answer is supported by the retrieved information.

## Practical example

Imagine a college has a document explaining its attendance rules.

**Student asks:** “How much attendance do I need?”

**RAG system:** It searches the college document, finds the attendance section, and gives that passage to the language model.

**Answer:** The model explains the requirement using the information found in the college document. The exact percentage must come from the real college policy; the system should not guess it.

## Important terms

- **Document:** A file containing information, such as a PDF or a rulebook.
- **Chunk:** A smaller piece of a longer document.
- **Retrieval:** Finding the pieces of information that best match a question.
- **Embedding:** A list of numbers that represents the meaning of text so that similar text can be found.
- **Language model (LLM):** An AI model that can understand and generate text.
- **Context:** Information provided to the model to help it answer the current question.

## Benefits and limitations

**Benefits**
- It can use information from updated or private documents available to the system.
- It can show which passages support an answer, if citations are implemented.
- Updating a document collection does not normally require retraining the language model for every document change.

**Limitations**
- The system may retrieve irrelevant or incomplete passages.
- Source documents may contain mistakes or outdated information.
- The model may misunderstand the retrieved information or make unsupported claims.
- Access controls are needed so users cannot retrieve documents they are not allowed to see.

## Summary

RAG means Retrieval-Augmented Generation. It finds relevant information first and then gives that information to a language model to help create an answer. Its quality depends on the documents, retrieval process, and generated answer. RAG can reduce some knowledge gaps, but it does not guarantee correctness.

## Quick quiz

1. What does RAG stand for?
2. Why does a RAG system retrieve information before generating an answer?
3. Name one reason a RAG answer might still be wrong.
