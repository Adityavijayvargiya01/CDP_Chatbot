import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import os
import concurrent.futures
import re
from typing import Dict, List, Set

class DocExtractor:
    def __init__(self):
        self.base_urls = {
            'segment': 'https://segment.com/docs/',
            'mparticle': 'https://docs.mparticle.com/',
            'lytics': 'https://docs.lytics.com/',
            'zeotap': 'https://docs.zeotap.com/home/en-us/'
        }
        self.visited_urls: Set[str] = set()
        self.doc_data: Dict[str, List[Dict]] = {
            'segment': [],
            'mparticle': [],
            'lytics': [],
            'zeotap': []
        }

    def fetch_page(self, url: str) -> str:
        """Fetch page content with proper headers and error handling"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return ""

    def extract_content(self, html: str, url: str) -> Dict:
        """Extract relevant content from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style']):
            element.decompose()

        # Extract title
        title = soup.title.string if soup.title else ""
        
        # Extract main content (customize selectors based on each CDP's documentation structure)
        content_selectors = [
            'article',
            '.content',
            '.documentation-content',
            'main',
            '.main-content'
        ]
        
        content = ""
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                content = content_element.get_text(strip=True, separator=' ')
                break

        # Extract headings for structure
        headings = []
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            headings.append({
                'level': int(heading.name[1]),
                'text': heading.get_text(strip=True)
            })

        return {
            'url': url,
            'title': title,
            'content': content,
            'headings': headings
        }

    def get_links(self, html: str, base_url: str) -> List[str]:
        """Extract relevant documentation links"""
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(base_url, href)
            
            # Only include links from the same documentation domain
            if base_url in full_url and full_url not in self.visited_urls:
                links.add(full_url)
        
        return list(links)

    def process_page(self, url: str, cdp: str):
        """Process a single documentation page"""
        if url in self.visited_urls:
            return

        self.visited_urls.add(url)
        html = self.fetch_page(url)
        if not html:
            return

        # Extract content
        content = self.extract_content(html, url)
        self.doc_data[cdp].append(content)

        # Get links for further processing
        links = self.get_links(html, self.base_urls[cdp])
        return links

    def crawl_documentation(self, max_pages: int = 100):
        """Crawl documentation for all CDPs"""
        for cdp, base_url in self.base_urls.items():
            print(f"Crawling {cdp} documentation...")
            
            urls_to_process = [base_url]
            processed_count = 0

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                while urls_to_process and processed_count < max_pages:
                    future_to_url = {
                        executor.submit(self.process_page, url, cdp): url 
                        for url in urls_to_process[:5]  # Process 5 pages at a time
                    }
                    urls_to_process = urls_to_process[5:]

                    for future in concurrent.futures.as_completed(future_to_url):
                        new_links = future.result()
                        if new_links:
                            urls_to_process.extend(
                                [url for url in new_links if url not in self.visited_urls]
                            )
                        processed_count += 1

            print(f"Processed {processed_count} pages for {cdp}")

    def save_documentation(self, output_dir: str):
        """Save extracted documentation to JSON files"""
        os.makedirs(output_dir, exist_ok=True)
        
        for cdp, data in self.doc_data.items():
            output_file = os.path.join(output_dir, f"{cdp}_docs.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def process_documentation(self, output_dir: str = 'cdp_docs'):
        """Main method to process all documentation"""
        self.crawl_documentation()
        self.save_documentation(output_dir)

# Example usage
if __name__ == "__main__":
    extractor = DocExtractor()
    extractor.process_documentation()
