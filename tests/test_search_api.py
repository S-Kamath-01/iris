def test_search_requires_authentication(client):
    response = client.get("/api/v1/search/", params={"q": "space shuttle", "top_k": 3})
    assert response.status_code == 401


def test_search_succeeds_with_valid_token(client, auth_token):
    response = client.get(
        "/api/v1/search/",
        params={"q": "space shuttle", "top_k": 3},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) <= 3


def test_search_with_explain_returns_contributions(client, auth_token):
    response = client.get(
        "/api/v1/search/",
        params={"q": "space shuttle", "top_k": 3, "explain": True},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["results"][0]["explanation"] is not None