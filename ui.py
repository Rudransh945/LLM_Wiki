import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="AI Second Brain",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 AI Second Brain")
st.caption("Personal cognitive operating system — Groq + LangGraph + LLM Wiki")


# ── Sidebar ───────────────────────────────────────────
with st.sidebar:
    st.header("Status")
    try:
        r = requests.get(f"{API_BASE}/status", timeout=3)
        if r.status_code == 200:
            st.success("Backend Online ✅")
        else:
            st.error("Backend Error")
    except Exception:
        st.error("Backend Offline ❌")
        st.info("Run: uvicorn main:app --reload")

    st.divider()

    st.header("Knowledge Base")
    try:
        r = requests.get(f"{API_BASE}/query/wiki/pages", timeout=3)
        if r.status_code == 200:
            pages = r.json().get("pages", [])
            st.write(f"**{len(pages)} wiki pages**")
            for p in pages[:20]:
                st.write(f"• {p}")
    except Exception:
        st.write("Could not load pages")


# ── Helper ────────────────────────────────────────────
def show_ingest_result(result: dict):
    status = result.get("status")
    if status == "success":
        st.success(
            f"✅ Wiki page: **{result.get('wiki_page_name')}** "
            f"({result.get('action')})"
        )
        if result.get("concepts"):
            st.write(
                "**Concepts extracted:**",
                ", ".join(result["concepts"])
            )
        if result.get("tags"):
            st.write(
                "**Tags:**",
                ", ".join(result["tags"])
            )
    elif status == "skipped":
        st.info("⏭️ Skipped — duplicate content already in knowledge base")
    elif status == "flagged":
        st.warning(
            f"⚠️ Contradiction detected: {result.get('contradictions')}"
        )
    else:
        st.error(f"❌ Failed: {result.get('error')}")


# ── Tabs ──────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["💬 Ask", "📥 Ingest", "📄 Wiki"])


# ── Tab 1: Ask ────────────────────────────────────────
with tab1:
    st.subheader("Ask your Second Brain")
    question = st.text_area(
        "Your question",
        placeholder="What do I know about transformers?",
        height=100
    )

    if st.button("Ask", type="primary"):
        if question.strip():
            with st.spinner("Thinking..."):
                try:
                    r = requests.post(
                        f"{API_BASE}/query/",
                        json={"question": question},
                        timeout=60
                    )
                    result = r.json()

                    st.markdown("### Answer")
                    st.markdown(result.get("answer", "No answer returned"))

                    col1, col2 = st.columns(2)
                    with col1:
                        if result.get("sources"):
                            st.markdown("**Sources used:**")
                            for s in result["sources"]:
                                st.write(f"• wiki/{s}")
                    with col2:
                        if result.get("intent"):
                            st.markdown("**Intent detected:**")
                            st.write(result["intent"])

                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a question")


# ── Tab 2: Ingest ─────────────────────────────────────
with tab2:
    st.subheader("Add Knowledge")

    ingest_type = st.radio(
        "What are you ingesting?",
        ["Quick Thought", "Web Page", "Raw Text"],
        horizontal=True
    )

    if ingest_type == "Quick Thought":
        title = st.text_input(
            "Title (optional)",
            placeholder="e.g. Startup idea about AI"
        )
        content = st.text_area(
            "Your thought",
            height=200,
            placeholder="Write your idea, insight, or observation..."
        )
        if st.button("Ingest Thought", type="primary"):
            if content.strip():
                with st.spinner("Processing..."):
                    r = requests.post(
                        f"{API_BASE}/ingest/thought",
                        json={"content": content, "title": title},
                        timeout=60
                    )
                    show_ingest_result(r.json())
            else:
                st.warning("Content cannot be empty")

    elif ingest_type == "Web Page":
        url = st.text_input("URL", placeholder="https://...")
        web_title = st.text_input("Title (optional)")
        content = st.text_area(
            "Paste page content here",
            height=300,
            placeholder="Paste the article text here..."
        )
        if st.button("Ingest Web Page", type="primary"):
            if content.strip() and url.strip():
                with st.spinner("Processing..."):
                    r = requests.post(
                        f"{API_BASE}/ingest/web",
                        json={
                            "content": content,
                            "url": url,
                            "title": web_title
                        },
                        timeout=60
                    )
                    show_ingest_result(r.json())
            else:
                st.warning("URL and content are both required")

    else:
        source_ref = st.text_input(
            "Source reference (optional)",
            placeholder="e.g. book name, doc title"
        )
        content = st.text_area(
            "Raw content",
            height=300,
            placeholder="Paste any raw text here..."
        )
        if st.button("Ingest Raw", type="primary"):
            if content.strip():
                with st.spinner("Processing..."):
                    r = requests.post(
                        f"{API_BASE}/ingest/raw",
                        json={
                            "content": content,
                            "source_type": "doc",
                            "source_ref": source_ref
                        },
                        timeout=60
                    )
                    show_ingest_result(r.json())
            else:
                st.warning("Content cannot be empty")


# ── Tab 3: Wiki ───────────────────────────────────────
with tab3:
    st.subheader("Browse Knowledge Base")
    try:
        r = requests.get(f"{API_BASE}/query/wiki/pages", timeout=3)
        if r.status_code == 200:
            pages = r.json().get("pages", [])
            if pages:
                selected = st.selectbox("Select a wiki page", pages)
                if selected:
                    r2 = requests.get(
                        f"{API_BASE}/query/wiki/page/{selected}",
                        timeout=5
                    )
                    if r2.status_code == 200:
                        st.markdown(r2.json().get("content", ""))
            else:
                st.info(
                    "No wiki pages yet. "
                    "Start by ingesting some content!"
                )
    except Exception as e:
        st.error(f"Could not load wiki: {e}")