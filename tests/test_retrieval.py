from app.retrieval.retriever import SupportRetriever, classify_source


def test_source_authority_classification():
    assert classify_source('Northstar_Customer_Agreement.pdf')[0] == 'signed_agreement'
    assert classify_source('Support_Policy_v3_Current.pdf')[0] == 'current_policy'
    assert classify_source('deprecated_policy_v2.pdf')[0] == 'deprecated'


def test_retrieval_excludes_deprecated_by_default():
    docs = [
        {'filename': 'deprecated_policy_v2.pdf', 'pages': [{'page': 1, 'text': 'refund policy'}]},
        {'filename': 'Support_Policy_v3_Current.pdf', 'pages': [{'page': 1, 'text': 'refund policy current'}]},
    ]
    retriever = SupportRetriever(documents=docs)
    hits = retriever.search_documents('refund policy')
    assert hits
    assert all(hit['authority'] != 'deprecated' for hit in hits)
