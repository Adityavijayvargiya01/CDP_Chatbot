import streamlit as st
import json

# Load the JSON file
def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# Search logic
def search_docs(query, docs):
    results = []
    query_lower = query.lower()

    for entry in docs:
        if query_lower in entry['content'].lower():
            results.append({
                'title': entry['title'],
                'url': entry['url'],
                'excerpt': entry['content'][:300],
            })

    if results:
        return results
    else:
        return [{"message": "Sorry, I couldn't find relevant information for your query."}]

# Main Streamlit app
def main():
    st.title("Support Agent Chatbot for CDPs")

    # Load the data
    docs = load_json("docs/segment_docs.json")

    # Query input
    query = st.text_input("Ask a 'how-to' question:")

    # Search button
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

