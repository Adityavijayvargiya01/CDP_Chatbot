import streamlit as st
import json
from fuzzywuzzy import fuzz
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import nltk
import os

nltk.download('punkt')
nltk.download('stopwords')

# Preprocessing function
def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    tokens = word_tokenize(text.lower())
    return [stemmer.stem(word) for word in tokens if word not in stop_words]

# Search function
def search_docs(query, docs):
    results = []
    query_lower = query.lower()
    query_tokens = set(preprocess_text(query))

    for entry in docs:
        content_tokens = set(preprocess_text(entry['content']))

        # Exact match in content
        if query_lower in entry['content'].lower():
            results.append({
                'title': entry['title'],
                'url': entry['url'],
                'excerpt': entry['content'][:300],
                'match_type': 'Exact Match'
            })

        # Tokenized match in content
        if query_tokens & content_tokens:
            results.append({
                'title': entry['title'],
                'url': entry['url'],
                'excerpt': entry['content'][:300],
                'match_type': 'Tokenized Match'
            })

        # Heading match
        for heading in entry['headings']:
            if query_lower in heading['text'].lower():
                results.append({
                    'title': entry['title'],
                    'url': entry['url'],
                    'excerpt': f"Heading Match: {heading['text']}",
                    'match_type': 'Heading Match'
                })

        # Fuzzy match in content
        score = fuzz.partial_ratio(query_lower, entry['content'].lower())
        if score >= 70:  # Adjust threshold as needed
            results.append({
                'title': entry['title'],
                'url': entry['url'],
                'excerpt': entry['content'][:300],
                'match_type': f'Fuzzy Match (Score: {score})'
            })

    # Return results or default message
    if results:
        return results
    else:
        return [{"message": "Sorry, I couldn't find relevant information for your query."}]

# Load JSON data
def load_json(filepath):
    if not os.path.exists(filepath):
        st.error(f"File not found: {filepath}")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# Streamlit app
def main():
    st.title("Support Agent Chatbot for CDPs")

    # Load JSON file
    docs = load_json("docs/segment_docs.json")  # Replace with your JSON file path

    # Query input
    query = st.text_input("Ask a 'how-to' question:")

    if st.button("Search"):
        if not query.strip():
            st.warning("Please enter a query!")
        else:
            results = search_docs(query, docs)
            for result in results:
                if "message" in result:
                    st.write(result["message"])
                else:
                    st.subheader(result['title'])
                    st.write(f"[Read more]({result['url']})")
                    st.write(result['excerpt'])
                    st.write(f"**Match Type:** {result['match_type']}")

if __name__ == "__main__":
    main()

