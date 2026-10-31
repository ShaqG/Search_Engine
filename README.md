# Search Engine for ICS Websites

A search engine written from scratch: crawl and parse pages from the ICS
websites, build a positional inverted index, and answer ranked queries from a
Tkinter GUI.

The point of the project was to build the whole retrieval pipeline by hand —
parsing, stemming, duplicate removal, index layout, and ranking — instead of
calling a search library.

## Pipeline

1. **`indexer.py`** — parses crawled HTML with BeautifulSoup, normalises tokens
   with a Porter stemmer, drops near-duplicate pages with SimHash, and writes the
   inverted index (`dict1.txt` … `dict3.txt`) together with the doc id → URL map.
2. **`index_of_index.py`** — builds an index *of* the index: for every stem it
   records `(index file, start offset, end offset)`, so a query only `seek()`s to
   the posting lists it needs instead of loading the whole index into memory.
3. **`search.py`** — term-at-a-time retrieval. Each query term is looked up in a
   thread, scored with a TF-IDF style weight
   (`1 + log10(tf) * log10(N / df) + importance / tf`), summed per URL, and the
   ranked list is shown in a Tkinter window.

## Run

```bash
pip install nltk beautifulsoup4 numpy floc_simhash
python indexer.py           # build the index
python index_of_index.py    # build the index of the index
python search.py            # then follow the prompt
```

`search.py` expects the index files and the URL map produced by the two scripts
above to be in the working directory.
