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

