# streamlit_app/app.py

import os

import requests
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 10

st.set_page_config(page_title="IRIS Search", page_icon="🔍", layout="wide")

st.markdown(
    """
    <style>
    .iris-shell { padding-top: 0.5rem; }
    .iris-hero {
        padding: 1.25rem 1.5rem;
        border: 1px solid rgba(49, 51, 63, 0.12);
        border-radius: 1rem;
        background: linear-gradient(135deg, rgba(19, 111, 99, 0.08), rgba(31, 119, 180, 0.05));
        margin-bottom: 1rem;
    }
    .iris-kicker {
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.74rem;
        font-weight: 700;
        color: rgba(49, 51, 63, 0.7);
        margin-bottom: 0.35rem;
    }
    .iris-title {
        font-size: 1.8rem;
        font-weight: 750;
        line-height: 1.1;
        margin: 0;
    }
    .iris-subtitle {
        margin-top: 0.45rem;
        color: rgba(49, 51, 63, 0.8);
        font-size: 0.98rem;
    }
    .iris-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        background: rgba(31, 119, 180, 0.12);
        color: rgb(31, 119, 180);
        font-size: 0.78rem;
        font-weight: 700;
        margin-right: 0.35rem;
        margin-bottom: 0.25rem;
    }
    .iris-muted {
        color: rgba(49, 51, 63, 0.7);
        font-size: 0.9rem;
    }
    .iris-preview {
        white-space: pre-wrap;
        line-height: 1.6;
        margin: 0.35rem 0 0;
    }
    .iris-empty {
        padding: 1.4rem 1.25rem;
        border: 1px dashed rgba(49, 51, 63, 0.22);
        border-radius: 1rem;
        background: rgba(255, 255, 255, 0.65);
    }
    .iris-empty h4 {
        margin: 0 0 0.35rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _extract_error_detail(response: requests.Response, fallback: str) -> str:
    try:
        detail = response.json().get("detail", fallback)
        return detail if isinstance(detail, str) else str(detail)
    except ValueError:
        return fallback


def _sign_out() -> None:
    st.session_state.pop("token", None)
    st.session_state.pop("email", None)
    st.session_state.pop("last_results", None)
    st.session_state.pop("last_query", None)


def _set_search_state(results: dict, query: str) -> None:
    st.session_state.last_results = results
    st.session_state.last_query = query


def _get_search_state() -> tuple[dict | None, str | None]:
    return st.session_state.get("last_results"), st.session_state.get("last_query")


def _render_badge(text: str) -> str:
    return f'<span class="iris-badge">{text}</span>'


def _render_error(message: str) -> None:
    st.error(f"{message}")


def _render_empty_state() -> None:
    st.markdown(
        """
        <div class="iris-empty">
            <h4>No search yet</h4>
            <div class="iris-muted">Try a query like <b>space shuttle</b> or <b>graphics card</b> to see ranked results, categories, snippets, and explainable BM25 scores.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_explanation_table(explanation: list[dict[str, object]]) -> None:
    st.dataframe(
        [
            {
                "Term": item["term"],
                "Contribution": round(float(item["contribution"]), 4),
                "TF": item["term_freq"],
                "DF": item["doc_freq"],
            }
            for item in explanation
        ],
        hide_index=True,
        use_container_width=True,
    )


def _render_result_card(result: dict[str, object], index: int) -> None:
    category = str(result.get("category", "unknown"))
    preview = str(result.get("preview", ""))
    score = float(result.get("score", 0.0))
    doc_id = result.get("doc_id", "?")

    with st.container(border=True):
        top_left, top_right = st.columns([3, 1])
        with top_left:
            st.markdown(f"**Result {index}**")
            st.markdown(_render_badge(category), unsafe_allow_html=True)
        with top_right:
            st.markdown("**BM25 Score**")
            st.markdown(f"{score:.4f}")

        doc_col, meta_col = st.columns([1, 4])
        with doc_col:
            st.markdown("**Document ID**")
            st.markdown(f"{doc_id}")
        with meta_col:
            st.markdown("**Preview**")
            st.markdown(f'<p class="iris-preview">{preview}</p>', unsafe_allow_html=True)

        explanation = result.get("explanation")
        if explanation:
            with st.expander("BM25 explanation"):
                _render_explanation_table(explanation)


def login(email: str, password: str) -> tuple[str | None, str | None]:
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/login",
            data={"username": email, "password": password},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException:
        return None, "Could not reach the server. Please try again shortly."

    if response.status_code == 200:
        return response.json()["access_token"], None
    return None, _extract_error_detail(response, "Login failed. Check your email and password.")


def register(email: str, password: str) -> tuple[bool, str]:
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/register",
            json={"email": email, "password": password},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException:
        return False, "Could not reach the server. Please try again shortly."

    if response.status_code == 201:
        return True, "Account created — you can log in now."
    return False, _extract_error_detail(response, "Registration failed. Please try a different email.")


def run_search(token: str, query: str, top_k: int, explain: bool):
    """Returns (results_dict, error_message, unauthorized). Exactly one of the
    first two is meaningful; unauthorized signals the caller should log out."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/search/",
            params={"q": query, "top_k": top_k, "explain": explain},
            headers={"Authorization": f"Bearer {token}"},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException:
        return None, "Could not reach the server. Please try again shortly.", False

    if response.status_code == 200:
        return response.json(), None, False
    if response.status_code == 401:
        return None, "Your session has expired. Please log in again.", True
    return None, _extract_error_detail(response, "Search failed. Please try again."), False


def show_login():
    left, right = st.columns([1.3, 1])

    with left:
        st.markdown(
            """
            <div class="iris-hero">
                <div class="iris-kicker">IRIS search engine</div>
                <div class="iris-title">Find documents across 20 Newsgroups with ranked search.</div>
                <div class="iris-subtitle">FastAPI backend, PostgreSQL persistence, BM25 ranking, and explainable results in a clean demo UI.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="iris-empty">
                <h4>What you can demo</h4>
                <div class="iris-muted">
                    Login, run a search, inspect category badges, review query-aware snippets, and expand BM25 contributions.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        tab_login, tab_register = st.tabs(["Log in", "Create account"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="Your password")
                submitted = st.form_submit_button("Log in", use_container_width=True)
                if submitted:
                    token, error = login(email, password)
                    if token:
                        st.session_state.token = token
                        st.session_state.email = email
                        st.session_state.pop("last_results", None)
                        st.session_state.pop("last_query", None)
                        st.rerun()
                    else:
                        _render_error(error)

        with tab_register:
            with st.form("register_form"):
                new_email = st.text_input("Email", key="reg_email", placeholder="you@example.com")
                new_password = st.text_input("Password", type="password", key="reg_password", placeholder="Choose a strong password")
                reg_submitted = st.form_submit_button("Create account", use_container_width=True)
                if reg_submitted:
                    success, message = register(new_email, new_password)
                    if success:
                        st.success(message)
                    else:
                        _render_error(message)


def show_search():
    with st.sidebar:
        st.markdown("### Signed in")
        st.markdown(st.session_state.email)
        st.caption("Search the indexed 20 Newsgroups corpus.")
        if st.button("Log out", use_container_width=True):
            _sign_out()
            st.rerun()

    st.markdown(
        """
        <div class="iris-hero iris-shell">
            <div class="iris-kicker">Search</div>
            <div class="iris-title">IRIS Search</div>
            <div class="iris-subtitle">Ranked retrieval with category labels, query-aware snippets, and optional explanations.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("search_form", clear_on_submit=False):
        query = st.text_input("Search query", placeholder="e.g. space shuttle")
        control_left, control_right = st.columns([3, 1])
        with control_left:
            top_k = st.slider("Number of results", min_value=1, max_value=20, value=10)
        with control_right:
            explain = st.checkbox("Explain scores", value=False)

        search_clicked = st.form_submit_button("Search", type="primary", use_container_width=True)

    clean_query = query.strip()
    last_results, last_query = _get_search_state()

    if search_clicked and not clean_query:
        st.warning("Type a query before searching.")
    elif search_clicked and clean_query:
        with st.spinner("Searching..."):
            results, error, unauthorized = run_search(
                st.session_state.token, clean_query, top_k, explain
            )

        if unauthorized:
            _sign_out()
            _render_error(error)
            st.rerun()
        elif error:
            _render_error(error)
        elif not results.get("results"):
            st.session_state.pop("last_results", None)
            st.session_state.pop("last_query", None)
            st.info("No matches found. Try fewer words or a broader topic.")
        else:
            _set_search_state(results, clean_query)
            last_results, last_query = results, clean_query

    if last_results:
        results = last_results
        active_query = last_query or results.get("query", "")

        summary_left, summary_right = st.columns([3, 1])
        with summary_left:
            st.markdown(f"### Results for \"{active_query}\"")
            st.caption(
                f"Showing top {len(results['results'])} of {results['total_matches']} matching documents."
            )
        with summary_right:
            st.markdown(
                f"<div class='iris-empty'><div class='iris-muted'>Top k</div><div style='font-size: 1.4rem; font-weight: 750;'>{len(results['results'])}</div></div>",
                unsafe_allow_html=True,
            )

        for i, result in enumerate(results["results"], start=1):
            _render_result_card(result, i)
    else:
        _render_empty_state()


if "token" not in st.session_state:
    show_login()
else:
    show_search()