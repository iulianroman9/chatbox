def compute_rrf(vector_results, fts_results, k=60):
    rrf_scores = {}
    chunk_map = {}

    for rank, chunk in enumerate(vector_results):
        rrf_scores[chunk.id] = rrf_scores.get(chunk.id, 0) + (1.0 / (k + rank + 1))
        chunk_map[chunk.id] = chunk

    for rank, chunk in enumerate(fts_results):
        rrf_scores[chunk.id] = rrf_scores.get(chunk.id, 0) + (1.0 / (k + rank + 1))
        chunk_map[chunk.id] = chunk

    sorted_chunk_ids = sorted(rrf_scores, key=rrf_scores.get, reverse=True)
    return [
        (chunk_map[chunk_id], rrf_scores[chunk_id]) for chunk_id in sorted_chunk_ids
    ]
