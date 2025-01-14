import streamlit as st
import json
import os

# Load JSON files
# Load JSON files with proper encoding
def load_docs():
    docs = {}
    for file in os.listdir("docs"):
        if file.endswith(".json"):
            with open(os.path.join("docs", file), "r", encoding="utf-8") as f:
                docs[file.split(".")[0]] = json.load(f)
    return docs


# Search functionality
def search_docs(cdp, query, docs):
    if cdp in docs:
        for topic, content in docs[cdp].items():
            if query.lower() in topic.lower():
                return content
    return "Sorry, I couldn't find relevant information for your query."

# App interface
def main():
    st.title("Support Agent Chatbot for CDPs")

    st.sidebar.header("Select Options")
    cdp = st.sidebar.selectbox("Choose a CDP", ["Segment", "mParticle", "Lytics", "Zeotap"])
    query = st.text_input("Ask a 'how-to' question:", "")

    if st.button("Get Answer"):
        docs = load_docs()
        answer = search_docs(cdp.lower(), query, docs)
        st.write(f"**Answer:** {answer}")

    # Bonus Feature: Cross-CDP Comparison
    st.header("Bonus: Cross-CDP Comparison")
    compare_query = st.text_input("Ask about differences between CDPs:", "")
    if st.button("Compare"):
        st.write("Comparison feature is under development.")

if __name__ == "__main__":
    main()

