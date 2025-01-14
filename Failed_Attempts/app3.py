import streamlit as st
import json

# Load JSON data
def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

import logging
logging.basicConfig(level=logging.INFO)

def search_docs(query, docs):
    results = []
    query_lower = query.lower()
    logging.info(f"Searching for query: '{query_lower}'")

    for entry in docs:
        if query_lower in entry['content'].lower():
            logging.info(f"Match found in title: {entry['title']}")
            results.append({
                'title': entry['title'],
                'url': entry['url'],
                'excerpt': entry['content'][:300],
            })

    if not results:
        logging.info("No matches found.")

    return results


# Streamlit app
def main():
    st.title("Support Agent Chatbot for CDPs")

    # Load the JSON file
    docs = load_json("docs/lytics_docs.json")  # Adjust file path as needed

    # User input
    query = st.text_input("Ask a 'how-to' question:")

    if st.button("Search"):
        results = search_docs(query, docs)
        for result in results:
            if "message" in result:
                st.write(result["message"])
            else:
                st.subheader(result['title'])
                st.write(f"[Read more]({result['url']})")
                st.write(result['excerpt'])

if __name__ == "__main__":
    main()

