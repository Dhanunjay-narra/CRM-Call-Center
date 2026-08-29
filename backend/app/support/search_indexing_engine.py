"""
BM25 Information Retrieval & Knowledge Base Search Indexer
Ranks knowledge articles, SOPs, and call scripts using the Okapi BM25 probabilistic algorithm
with term frequency, inverse document frequency, and document length normalization.
"""

import math
import re
from typing import List, Dict, Any, Tuple


class BM25SearchEngine:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_lengths: List[int] = []
        self.avg_doc_length: float = 0.0
        self.doc_term_freqs: List[Dict[str, int]] = []
        self.idf_cache: Dict[str, float] = {}
        self.corpus_size: int = 0
        self.doc_ids: List[str] = []

    def tokenize(self, text: str) -> List[str]:
        clean = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
        return [t for t in clean.split() if len(t) > 1]

    def index_documents(self, documents: List[Dict[str, Any]]) -> None:
        self.corpus_size = len(documents)
        self.doc_ids = []
        self.doc_lengths = []
        self.doc_term_freqs = []
        doc_freq: Dict[str, int] = {}

        for doc in documents:
            doc_id = doc.get("id", "")
            content = f"{doc.get('title', '')} {doc.get('content_markdown', '')} {' '.join(doc.get('tags', []))}"
            tokens = self.tokenize(content)

            self.doc_ids.append(doc_id)
            self.doc_lengths.append(len(tokens))

            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            self.doc_term_freqs.append(tf)

            for unique_token in set(tokens):
                doc_freq[unique_token] = doc_freq.get(unique_token, 0) + 1

        self.avg_doc_length = sum(self.doc_lengths) / float(self.corpus_size) if self.corpus_size > 0 else 1.0

        # Calculate IDF
        self.idf_cache = {}
        for term, df in doc_freq.items():
            # Robertson-Spärck Jones IDF
            idf = math.log((self.corpus_size - df + 0.5) / (df + 0.5) + 1.0)
            self.idf_cache[term] = max(0.0, idf)

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        query_tokens = self.tokenize(query)
        scores: List[float] = [0.0] * self.corpus_size

        for i in range(self.corpus_size):
            doc_len = self.doc_lengths[i]
            tf_dict = self.doc_term_freqs[i]

            for term in query_tokens:
                if term not in tf_dict:
                    continue
                tf = tf_dict[term]
                idf = self.idf_cache.get(term, 0.0)

                # BM25 formula
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_length))
                scores[i] += idf * (numerator / denominator)

        # Sort top-k
        indexed_scores = [(self.doc_ids[i], scores[i]) for i in range(self.corpus_size) if scores[i] > 0.0]
        indexed_scores.sort(key=lambda x: x[1], reverse=True)
        return indexed_scores[:top_k]
