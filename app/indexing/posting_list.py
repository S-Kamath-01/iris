# app/indexing/posting_list.py

from dataclasses import dataclass


@dataclass
class Posting:
    doc_id: int
    term_freq: int