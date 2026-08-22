from sentence_transformers import SentenceTransformer
from parser import parse_policy


class PolicyRetriever:
    def __init__(self, policy_path):
        self.clauses = parse_policy(policy_path)

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        self.embeddings = self.model.encode(
            [clause["text"] for clause in self.clauses],
            normalize_embeddings=True
        )

    def search(self, query, top_k=5):
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        )[0]

        scores = self.embeddings @ query_embedding

        ranked_indices = scores.argsort()[::-1][:top_k]

        results = []

        for index in ranked_indices:
            results.append({
                "clause": self.clauses[index]["clause"],
                "text": self.clauses[index]["text"],
                "score": float(scores[index])
            })

        return results


if __name__ == "__main__":
    retriever = PolicyRetriever("data/policy-manual.md")

    query = input("Question: ")

    results = retriever.search(query)

    print("\nRelevant clauses:\n")

    for result in results:
        print(f"§{result['clause']}  |  Score: {result['score']:.3f}")
        print(result["text"])
        print("-" * 60)