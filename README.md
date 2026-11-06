# Search Engine for ICS Websites

A Python search engine for a collection of previously crawled ICS web pages. It builds a positional inverted index from HTML and returns ranked URLs in the terminal.

## Try the three-page example

Install the dependencies from the repository root, then switch to the example
directory. Its [`DEV` corpus](examples/three-pages/DEV) contains three JSON
documents with `url` and `content` fields.

```shell
python -m pip install nltk beautifulsoup4 numpy scikit-learn
python -m pip install --no-deps floc_simhash==0.1.0
cd examples/three-pages
python ../../indexer.py
python ../../index_of_index.py
python ../../search.py --query retrieval
```

The same term appears in all three index shards. The command prints:

```text
3 results
1. https://example.com/retrieval-guide
2. https://example.com/retrieval-notes
3. https://example.com/glossary
```

The guide matches in its title and heading, the notes match in a heading and
body text, and the glossary matches only in body text.

Run `python ../../search.py` to try more queries interactively. Results are
shown ten at a time. Enter `_q` at the search prompt to exit.

`floc_simhash` 0.1.0 declares an older scikit-learn version. The two install
commands above use a current scikit-learn build and skip that legacy pin.

## How it works

1. [`indexer.py`](indexer.py) parses HTML with BeautifulSoup, stems terms with the Porter stemmer, uses SimHash for near-duplicate detection, and writes positional postings and a URL map.
2. [`index_of_index.py`](index_of_index.py) records offsets into the index shards so queries can seek to the postings they need.
3. [`search.py`](search.py) looks up each query term in a separate thread and ranks URLs with TF-IDF-style weights and a boost for terms in prominent HTML elements.
