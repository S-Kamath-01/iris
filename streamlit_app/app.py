# streamlit_app/app.py

import os
import html
import re

import requests
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 10

st.set_page_config(page_title="IRIS Search", page_icon="🔍", layout="wide")

st.markdown(
    """
    <style>
    section.main > div.block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1180px;
    }
    .iris-title {
        font-size: 2rem;
        line-height: 1.1;
        margin: 0;
    }
    .iris-subtitle {
        color: inherit;
        opacity: 0.78;
        margin-top: 0.35rem;
    }
    .iris-pill {
        display: inline-block;
        padding: 0.28rem 0.6rem;
        border-radius: 999px;
        background: color-mix(in srgb, currentColor 12%, transparent);
        color: inherit;
        font-size: 0.76rem;
        font-weight: 700;
        margin-right: 0.4rem;
    }
    .iris-score-value {
        font-size: 1.18rem;
        font-weight: 750;
        line-height: 1.1;
        text-align: right;
    }
    .iris-score-label {
        color: inherit;
        opacity: 0.7;
        font-size: 0.78rem;
        margin-bottom: 0.15rem;
        text-align: right;
    }
    .iris-snippet {
        line-height: 1.6;
        white-space: pre-wrap;
        margin-top: 0.3rem;
    }
    .iris-snippet mark {
        background: color-mix(in srgb, currentColor 14%, transparent);
        color: inherit;
        padding: 0 0.15rem;
        border-radius: 0.2rem;
    }
    .iris-empty,
    .iris-loading {
        border: 1px dashed currentColor;
        opacity: 0.85;
        border-radius: 1rem;
        padding: 1.2rem 1rem;
        background: transparent;
    }
    .iris-login-kicker {
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.72rem;
        font-weight: 700;
        color: inherit;
        opacity: 0.65;
        margin-bottom: 0.35rem;
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
    return f'<span class="iris-pill">{html.escape(text)}</span>'


def _render_error(message: str) -> None:
    st.error(message)


def _render_empty_state() -> None:
    st.markdown(
        """
        <div class="iris-empty">
            <h4 style="margin: 0 0 0.35rem 0;">Search to see results</h4>
            <div>Try a query like <b>space shuttle</b>, <b>graphics card</b>, or <b>medical imaging</b>.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _highlight_snippet(snippet: str, query: str) -> str:
    escaped = html.escape(snippet)
    terms = [term for term in re.findall(r"[a-z0-9]+", query.lower()) if term]
    if not terms:
        return escaped

    pattern = re.compile(r"(" + "|".join(re.escape(term) for term in terms) + r")", re.IGNORECASE)
    return pattern.sub(lambda match: f"<mark>{match.group(0)}</mark>", escaped)


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
        column_config={
            "Contribution": st.column_config.NumberColumn(format="%.4f"),
            "TF": st.column_config.NumberColumn(width="small"),
            "DF": st.column_config.NumberColumn(width="small"),
        },
    )


def _render_result_card(result: dict[str, object], index: int) -> None:
    category = str(result.get("category", "unknown"))
    preview = str(result.get("preview", ""))
    score = float(result.get("score", 0.0))
    doc_id = result.get("doc_id", "?")
    query = str(st.session_state.get("last_query", ""))

    with st.container(border=True):
        top_left, top_right = st.columns([4, 1])
        with top_left:
            st.markdown(f"**Document {doc_id}**")
            st.markdown(_render_badge(category), unsafe_allow_html=True)
        with top_right:
            st.markdown('<div class="iris-score-label">BM25 Score</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="iris-score-value">{score:.4f}</div>', unsafe_allow_html=True)

        st.markdown(
            f'<div class="iris-snippet">{_highlight_snippet(preview, query)}</div>',
            unsafe_allow_html=True,
        )

        explanation = result.get("explanation")
        if explanation:
            with st.expander("BM25 explanation", expanded=False):
                _render_explanation_table(explanation)


def _render_search_header() -> None:
    st.markdown('<div class="iris-title">IRIS Search</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="iris-subtitle">Ranked retrieval over 20 Newsgroups with categories, snippets, and explainable BM25 scores.</div>',
        unsafe_allow_html=True,
    )


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
    st.markdown('<div class="iris-title">IRIS Search</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="iris-subtitle">Search the 20 Newsgroups corpus with BM25 ranking, snippets, and explainable scores.</div>',
        unsafe_allow_html=True,
    )

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
        st.markdown('### Account')
        st.markdown(f'**{html.escape(st.session_state.email)}**')
        if st.button('Log out', use_container_width=True):
            _sign_out()
            st.rerun()

    _render_search_header()

    with st.form("search_form", clear_on_submit=False):
        search_col, topk_col = st.columns([5, 1])
        with search_col:
            query = st.text_input("Search query", placeholder="Try: space shuttle, telescope, graphics card")
        with topk_col:
            top_k = st.slider("Top k", min_value=1, max_value=20, value=10)
            explain = st.checkbox("Explain scores", value=False)

        search_clicked = st.form_submit_button("Search", type="primary", use_container_width=True)

    clean_query = query.strip()
    last_results, last_query = _get_search_state()

    if search_clicked and not clean_query:
        st.warning("Enter a search query to begin.")
    elif search_clicked and clean_query:
        with st.spinner("Searching documents…"):
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
            st.info("No matches found. Try broader wording or fewer terms.")
        else:
            _set_search_state(results, clean_query)
            last_results, last_query = results, clean_query

    if last_results:
        results = last_results
        active_query = last_query or results.get("query", "")

        st.markdown(f"### Results for \"{active_query}\"")
        st.caption(
            f"Showing top {len(results['results'])} of {results['total_matches']} matching documents."
        )

        for i, result in enumerate(results["results"], start=1):
            _render_result_card(result, i)
    else:
        _render_empty_state()


if "token" not in st.session_state:
    show_login()
else:
    show_search()