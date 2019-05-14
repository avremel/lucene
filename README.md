# Lucene Vector Space Model (VSM) Basic Search Engine

## Links

- [Scoring Formula - Lucene API](https://lucene.apache.org/core/8_0_0/core/org/apache/lucene/search/similarities/TFIDFSimilarity.html)
- [Vector space model - Wikipedia](https://en.wikipedia.org/wiki/Vector_space_model)
- [td/idf - Wikipedia](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)

## Scoring Formula

**TermFrequency** sqrt(field.count(term))

**InverseDocFrequency** log( doc_count / num_docs_which_contain_term ) + 1 ) + 1

**fieldNorm** 1 / sqrt( num_chars_in_field)

Weight of term in document field = TF * IDF * fieldNorm

Weight of term in query = IDF * field_boost_exponent

## Instructions

Easiest way to get started, clone repo and run `python -i search_engine.py`.

```python
products = json.load( open('movies.json') )
search_engine = SearchEngine(docs=products, use_field_norms=False)
field_boosts = {'title': 1.1}
query = search_engine.query("gi joe ww2 documentary", field_boosts=field_boosts, num_results=10)
```

## Options

- **use_field_norms** (boolean): Factor in field length for TD-IDF scoring
- **num_results** (int): Total results to display
- **field_boosts** (dict[string, int]): Boost certain fields by an exponent
