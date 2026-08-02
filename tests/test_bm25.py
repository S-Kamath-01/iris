from app.search.bm25 import score_document, explain_document_score


def test_score_document_returns_zero_for_no_matching_terms():
    score = score_document(
        term_freqs={"absent": 0},
        doc_freqs={"absent": 0},
        doc_length=100,
        total_documents=1000,
        avg_doc_length=100,
        k1=1.2,
        b=0.75,
    )
    assert score == 0.0


def test_score_document_rewards_rarer_terms_more():
    common_term_score = score_document(
        term_freqs={"common": 2},
        doc_freqs={"common": 900},
        doc_length=100,
        total_documents=1000,
        avg_doc_length=100,
        k1=1.2,
        b=0.75,
    )
    rare_term_score = score_document(
        term_freqs={"rare": 2},
        doc_freqs={"rare": 10},
        doc_length=100,
        total_documents=1000,
        avg_doc_length=100,
        k1=1.2,
        b=0.75,
    )
    assert rare_term_score > common_term_score


def test_explain_document_score_sums_to_total_score():
    term_freqs = {"space": 12, "shuttl": 5}
    doc_freqs = {"space": 662, "shuttl": 130}
    kwargs = dict(doc_length=150, total_documents=18846, avg_doc_length=109.2, k1=1.2, b=0.75)

    total = score_document(term_freqs=term_freqs, doc_freqs=doc_freqs, **kwargs)
    contributions = explain_document_score(term_freqs=term_freqs, doc_freqs=doc_freqs, **kwargs)

    assert abs(sum(c.contribution for c in contributions) - total) < 1e-9