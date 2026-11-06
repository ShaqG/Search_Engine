# Search Engine for ICS Websites

A Python search engine for a collection of previously crawled ICS web pages. It builds a positional inverted index from HTML and returns ranked URLs in the terminal.

## Try a local query

Run the commands from the repository root on Windows. The indexer expects a `DEV` directory containing JSON files with `url` and `content` fields.

If you don't have the original corpus, create `DEV/sample.json` with this single line:

```json
{"url":"https://example.com/retrieval","content":"<html><body><p>Information retrieval</p></body></html>"}
```

```shell
python -m pip install nltk beautifulsoup4 numpy floc_simhash
python indexer.py
python index_of_index.py
python search.py
```

Enter `retrieval` to look up the sample URL. Enter `_q` to exit. The Python installation needs Tkinter because `search.py` imports it.

## How it works

1. [`indexer.py`](indexer.py) parses HTML with BeautifulSoup, stems terms with the Porter stemmer, uses SimHash for near-duplicate detection, and writes positional postings and a URL map.
2. [`index_of_index.py`](index_of_index.py) records offsets into the index shards so queries can seek to the postings they need.
3. [`search.py`](search.py) looks up each query term in a separate thread and ranks URLs with TF-IDF-style weights and a boost for terms in prominent HTML elements.
