# Basic Search Engine
### Lucene Vector Space Model (VSM)
## Links

- [Scoring Formula - Lucene API](https://lucene.apache.org/core/8_0_0/core/org/apache/lucene/search/similarities/TFIDFSimilarity.html)
- [Vector space model - Wikipedia](https://en.wikipedia.org/wiki/Vector_space_model)
- [td/idf - Wikipedia](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)


## Tokenization
Search is a balance of precision and recall. Lucene is quite dumb and by default, only exact words will be a match leading to great precision, but terrible recall (too many false negatives). To better search relevance, all terms go through a tokenization process (docs at index time, query at runtime). Tokenization associates different forms of a term so the recall will be greater.

Some tokenizations ([see here](https://lucene.apache.org/solr/guide/7_6/filter-descriptions.html)):
- Lower case
- Strip punctuation
- Split field by white space
- Remove possessives: "Man’s" -> "Man
- Stemming: "Jumping" -> "Jump"
- Phonetic: BMPM is popular, "In its current implementation, BMPM' is primarily concerned with matching surnames of Ashkenazic Jews..." (from the paper)[https://stevemorse.org/phonetics/bmpm.htm]
- N-Gram: Each combination of n chars for a term. "hello" for 2-3 chars is ["he", "el", "ll", "lo", "hel", "ell", "llo"]
- Edge-N-Gram: Each combination of n chars for a term from start of word. "hello" for 3+ chars is ["hel", "hell", "hello"]. Very useful for autosuggest while user typing.

## Scoring Formula

**TermFrequency** sqrt(field.count(term))

**InverseDocFrequency** log( doc_count / num_docs_which_contain_term ) + 1 ) + 1

**fieldNorm** 1 / sqrt( num_chars_in_field)

Weight of term in document field = TF * IDF * fieldNorm

Weight of term in query = IDF * field_boost_exponent

1. Multiply each term_score in query with matching term_score of doc[n] to produce the dot_product of query_vectory <-> doc[n]_vector.
2. If term exists in more than one field within the same document, pick the field with highest scoring match ([see here](https://lucene.apache.org/solr/guide/7_0/the-dismax-query-parser.html#the-tie-tie-breaker-parameter)).
3. dot_product * ( matching_terms / num_terms_in_query ) which punishes match that is missing some query terms.
4. dot_product / norm( query_vector ) * norm( doc_vector )
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
