"""
Deduplication configuration settings.
"""

# Content similarity deduplication settings
ENABLE_CONTENT_DEDUPLICATION = True
SIMILARITY_THRESHOLD = 0.85  # 0.0-1.0, higher = more strict (0.85 = 85% similarity required)

# Performance settings
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'  # Fast, lightweight model (384 dimensions)
# Alternative models:
# - 'all-mpnet-base-v2': Better quality but slower (768 dimensions)
# - 'paraphrase-MiniLM-L6-v2': Good for paraphrasing detection (384 dimensions)

# Similarity threshold guide:
# 0.90-1.0 : Very strict - only near-identical articles
# 0.85-0.89: Strict - same story, different wording
# 0.80-0.84: Moderate - similar topics, different angles (may remove too much)
# <0.80    : Loose - risk keeping too many similar articles
