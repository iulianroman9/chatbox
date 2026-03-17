import voyageai
from utils.config import settings

voyage_client = voyageai.Client(api_key=settings.voyage_api_key)


def get_embeddings(chunks: list[str]) -> list[list[float]]:
    if not chunks:
        return []

    response = voyage_client.embed(
        chunks, model="voyage-4", input_type="document", output_dimension=2048
    )

    return response.embeddings
