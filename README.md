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
- Phonetic: BMPM is popular, "In its current implementation, BMPM' is primarily concerned with matching surnames of Ashkenazic Jews..." [from the paper](https://stevemorse.org/phonetics/bmpm.htm)
- N-Gram: Each combination of n chars for a term. "hello" for 2-3 chars is ["he", "el", "ll", "lo", "hel", "ell", "llo"]
- Edge-N-Gram: Each combination of n chars for a term from start of word. "hello" for 3+ chars is ["hel", "hell", "hello"]. Very useful for autosuggest while user typing.

## Scoring Formula

### Vectors
TODO

### TD*IDF
Terminology

*Doc*: Doc DB row, JSON object, CSV row, etc. which contains fields
*TF*: Term Frequency
*IDF*: Inverse Doc Frequency
*Weight*: Vaulue of term within a field of doc

The weight of a matching term is scored by the frequency of the term within the given field (TF) multiplied by how rare the term is within the set of documents (IDF).

Practically, the following formula is generally used:

*TF* = sqrt(field.count(term))

*IDF* = log( doc_count / num_docs_which_contain_term ) + 1 ) + 1

*fieldNorm* = 1 / sqrt( num_chars_in_field)

Weight of term in field = TF * IDF * fieldNorm

Weight of term in query = IDF * field_boost_exponent
(TF is irrelevant, users usually don't duplicate terms in query. Same with fieldNorm, searches are usually short)

### Summary of Calculation

1. Multiply each term_score in query with matching term_score of doc[n] to produce the dot_product of query_vectory <-> doc[n]_vector.
2. If term exists in more than one field within the same document, pick the field with highest scoring match ([see here](https://lucene.apache.org/solr/guide/7_0/the-dismax-query-parser.html#the-tie-tie-breaker-parameter)).
3. dot_product * ( matching_terms / num_terms_in_query ) which punishes match that is missing some query terms.
4. dot_product / norm( query_vector ) * norm( doc_vector )
## Instructions

Clone repo and run `python -i search_engine.py`.

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
