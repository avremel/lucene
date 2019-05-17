# Basic Search Engine
### Lucene Vector Space Model (VSM)
## Links

- [Scoring Formula - Lucene API](https://lucene.apache.org/core/8_0_0/core/org/apache/lucene/search/similarities/TFIDFSimilarity.html)
- [Vector space model - Wikipedia](https://en.wikipedia.org/wiki/Vector_space_model)
- [td/idf - Wikipedia](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)

## Use cases
1. Search products (query -> docs)
2. Similiar products  on a product page (doc -> docs)
3. Personalized suggestions base on user history (docs -> docs)

## Tokenization
Search is a balance of precision and recall. Lucene is dumb by default; only exact words will be a match leading to great precision, but terrible recall (too many false negatives). To better search relevance, all terms go through a tokenization process (docs at index time, query at runtime). Tokenization associates different forms of a term so the recall will be greater.

Some tokenizations ([see here](https://lucene.apache.org/solr/guide/7_6/filter-descriptions.html)):
- Lower case
- Strip punctuation
- Split field by white space
- Remove possessives: "Man’s" -> "Man
- Stemming: "Jumping" -> "Jump"
- Phonetic: BMPM: "In its current implementation, BMPM' is primarily concerned with matching surnames of Ashkenazic Jews..." [website](https://stevemorse.org/phonetics/bmpm.htm)
- N-Gram: Each combination of n chars for a term. "hello" for 2-3 chars is ["he", "el", "ll", "lo", "hel", "ell", "llo"]
- Edge-N-Gram: Each combination of n chars for a term from start of word. "hello" for 3+ chars is ["hel", "hell", "hello"]. Very useful for autosuggest while user typing.
- Bigrams: Pairs of words

## Scoring Formula

### Terminology
| Term | Explanation  |
|---|---|
| Doc  | Record from CSV/JSON/HTML/PDF/DB, etc. |
| Term | Subset of field, could be letter, word, or any n-chars. |
| Weight | Value of term within a field of doc |
| TF | Term Frequency within a field |
| IDF  | Rarity of term within doc (Inverse Doc Frequency) 1/DF |
| fieldNorm | Shorter fields have more weight than longer ones |

### Intro
![alt text](https://www.intmath.com/vectors/img/235-3D-vector.png)

The vector model views both the query and the searchable documents as a vector on a mullti-dimensional graph.

Each axis of the graph represents a term and the value on the axis is the weight of the term within the doc or query.

The vectors will only have numbers >= 0. Doc vectors with axis's of 0 indicate that a particular term has no match in the query vector and can be safely ignored.

There are two components to understand:
1. How we procure the value of a particiular axis (the weight of a term). These calculations are done at index time.
2. How we calculate the similiarity between two vecors (query <-> docs) .

### TD*IDF

The weight of a matching term is scored by the frequency of the term within the given field (TF) multiplied by how rare the term is within the set of documents (IDF).

Practically, the a variation of the this formula is generally used:

| Name | Formula | Query | Document |
|---|---|---|---|
| TF  | sqrt(field.count(term)) | NO |YES|
| IDF | log( doc_count / num_docs_which_contain_term ) + 1 ) + 1 |YES|YES|
| fieldNorm | 1 / sqrt( num_chars_in_field) |NO|YES|

For a query, TF is irrelevant since query rarely contain duplicate words. fieldNorm is also not important; queries are usually concise.

Here is an example for a query of `gi joe ww2 documentary`. `fieldNorms` are set to `True` and `field_boosts` are `{'title': 1.1, 'genre': 1.5}`:

```python
# query vector
{'documentary': {'score': 5.015173140485178},
 'gi': {'score': 8.965719169172438},
 'joe': {'score': 5.642844374217615},
 'ww2': {'score': 0}}

# top result vector for doc 11838
{'gi': {'field_name': 'title',
        'field_text': 'The Story of G.I. Joe',
        'score': 1.956480321545204},
 'joe': {'field_name': 'title',
         'field_text': 'The Story of G.I. Joe',
         'score': 1.2313695942718068}}

# original record
{'cast': ['Burgess Meredith', 'Robert Mitchum'],
 'genres': ['War'],
 'title': 'The Story of G.I. Joe',
 'year': 1945}
 
# doc weights from index
{'cast': {'burgess': 1.2106351225005683,
          'meredith': 1.1461898093155403,
          'mitchum': 1.1096031454459072,
          'robert': 0.6646962483369104},
'genres': {'war': 1.8221135281634746},
'title': {'gi': 1.956480321545204,
           'joe': 1.2313695942718068,
           'of': 0.7117316180615629,
           'story': 1.3784931651895422,
           'the': 0.5162296287278824},
'year': {'1945': 2.625807684692801}}
```

### Compare Vectors

`query_vector = {'joe': 5.642844374217615, gi}

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
