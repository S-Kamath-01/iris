# app/indexing/tokenizer.py

import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

TOKEN_PATTERN = re.compile(r"[a-zA-Z]+")
STOPWORDS = set(stopwords.words("english"))
_stemmer = PorterStemmer()


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_PATTERN.findall(text)]


def remove_stopwords(tokens: list[str]) -> list[str]:
    return [token for token in tokens if token not in STOPWORDS]


def stem_tokens(tokens: list[str]) -> list[str]:
    return [_stemmer.stem(token) for token in tokens]


def preprocess_text(text: str) -> list[str]:
    tokens = tokenize(text)
    tokens = remove_stopwords(tokens)
    tokens = stem_tokens(tokens)
    return tokens