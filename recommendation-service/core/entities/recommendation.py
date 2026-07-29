"""
Recommendation Entity

Represents the final recommendation generated for a user's agricultural or
water management problem.

This entity encapsulates the original problem description along with one or
more recommendation items produced from the retrieved knowledge base.

The Recommendation entity is part of the domain layer and contains only
business data. It is independent of infrastructure concerns such as RabbitMQ,
Qdrant, MinIO, FastAPI, or the underlying LLM implementation.
"""