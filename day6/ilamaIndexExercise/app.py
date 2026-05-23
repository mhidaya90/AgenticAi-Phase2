import streamlit as st
import pandas as pd
from llama_index.core import VectorStoreIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.response_synthesizers import get_response_synthesizer

# Import your helper functions from the backend file
from backend import build_or_load_index, retrieve_only, classic_rag

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="Indian History RAG", layout="wide")

st.title("📚 Indian History RAG Explorer")
st.markdown("Interact with your **PDF-based RAG pipeline** using Streamlit.")

# Sidebar controls
st.sidebar.header("⚙️ Settings")
top_k = st.sidebar.slider("Number of chunks (top_k)", 1, 10, 4)
mode = st.sidebar.radio("Query Mode", ["Retrieval Only", "Classic RAG"])
response_mode = None
if mode == "Classic RAG":
    response_mode = st.sidebar.selectbox(
        "Response Mode",
        ["compact", "tree_summarize", "refine", "simple_summarize", "accumulate", "structure_refine"],
        index=2  # default to "refine"
    )
# Query input
query = st.text_input("Enter your question:", "Describe the Indus Valley Civilisation and its features.")

if st.button("Run Query"):
    if mode == "Retrieval Only":
        st.subheader("🔎 Retrieved Chunks")
        df = retrieve_only(query, top_k=top_k)
        st.dataframe(df, use_container_width=True)

        # Show first chunk preview
        if not df.empty:
            st.markdown("**Retrieved chunk previews:**")
            for i, row in df.iterrows():
                with st.expander(f"Chunk {row['rank']} (score={row['score']})"):
                    st.json(row['metadata'])
                    st.write(row['response'][:300])  # show first 700 characters

    elif mode == "Classic RAG":
        st.subheader("🤖 Synthesized Answer")
        answer, sources = classic_rag(query, top_k=top_k, response_mode=response_mode)
        st.write(answer)

        st.subheader("📑 Sources")
        for src in sources:
            with st.expander(f"Source {src['rank']} (score={src['score']})"):
                st.json(src['metadata'])
                st.write(src['text'])
# Footer
st.sidebar.markdown("---")
st.sidebar.write("Built with 🦙 LlamaIndex + Streamlit")
