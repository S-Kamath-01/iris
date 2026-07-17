# app/indexing/inverted_index.py

from collections import defaultdict

from app.indexing.posting_list import Posting
from app.indexing.tokenizer import preprocess_text


class InvertedIndex:
    def __init__(self):
        self.index: dict[str, list[Posting]] = defaultdict(list)
        self.doc_count: int = 0

    def add_document(self, doc_id: int, text: str) -> None:
        tokens = preprocess_text(text)
        term_freqs: dict[str, int] = defaultdict(int)

        for token in tokens:
            term_freqs[token] += 1

        for term, freq in term_freqs.items():
            self.index[term].append(Posting(doc_id=doc_id, term_freq=freq))

        self.doc_count += 1

    def get_postings(self, term: str) -> list[Posting]:
        return self.index.get(term, [])

    def vocabulary_size(self) -> int:
        return len(self.index)