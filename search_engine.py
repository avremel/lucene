import json
import string
from math import log, sqrt
from collections import defaultdict

def tokenize_field(field):
	string_field = str(field).lower()
	no_punctuation_field = string_field.translate(str.maketrans('', '', string.punctuation))
	return list(filter(None, no_punctuation_field.split()))

def inverse_doc_freq(doc_count, inverted_index, term):
	# query term might not exist in corpus
	if inverted_index.get(term):
		return log( doc_count / len( inverted_index[term] ) + 1 ) + 1
	else:
		return 0

def get_inverted_index(docs):
	inverted_index = defaultdict(set)

	for idx, doc in enumerate(docs):
		for field_name, field in doc.items():
			for term in set(tokenize_field(field)):
				inverted_index[term].add(idx)

	return inverted_index

def get_vector_norm(vector):
	return sqrt(sum(value['score']**2 for value in vector.values()))

def get_query_vector(doc_count, inverted_index, tokenized_query):
	return 	{
			term: {'score': inverse_doc_freq(doc_count, inverted_index, term)}
			for term in tokenized_query
		}

def get_doc_with_weights(doc, doc_count, inverted_index, use_field_norms):
	term_weights_in_docs = dict()
	for field_name, field in doc.items():
		term_weights_in_docs[field_name] = {}
		field_length = len(str(field))
		terms = tokenize_field(field)
		for term in set(terms):
			tf = sqrt(terms.count(term))
			idf = inverse_doc_freq(doc_count, inverted_index, term)
			weight = tf * idf * ( 1/sqrt(field_length) if use_field_norms else 1)
			term_weights_in_docs[field_name][term] = weight
	return term_weights_in_docs

def get_doc_vectors(docs, doc_count, inverted_index, tokenized_query):
	#TODO https://lucene.apache.org/solr/guide/7_0/the-dismax-query-parser.html#the-tie-tie-breaker-parameter
	doc_vectors = dict()
	for doc_idx, doc in docs.items():
		doc_term_scores = dict()
		for field_name, terms in doc['weights'].items():
			for term, score in terms.items():
				if term in tokenized_query and score > doc_term_scores.get(term, {}).get('score', 0):
					field_text = doc['doc'][field_name]
					term_score = {'field_name': field_name, 'field_text': field_text,'score': score}
					doc_term_scores[term] = term_score
		if doc_term_scores:
			doc_vectors[doc_idx] = doc_term_scores
	return doc_vectors

def get_ranking_list(docs, num_terms_in_query, query_vector, doc_vectors, num_results, field_boosts):
	ranking_list = []
	query_vector_norm = get_vector_norm(query_vector)
	for doc_idx, doc_vector in doc_vectors.items():
		dot_product = matching_terms = 0
		for query_term, query_score in query_vector.items():
			if query_term in doc_vector:
				field_name = doc_vector[query_term]['field_name']
				field_boost= field_boosts.get(field_name, 1)
				dot_product += query_score['score']**field_boost * doc_vector[query_term]['score']
				matching_terms += 1
		# coord
		dot_product = dot_product * ( matching_terms / num_terms_in_query )
		doc_vector_norm = get_vector_norm(doc_vector)
		dot_product = dot_product / (query_vector_norm * doc_vector_norm)
		field_matches = dict()
		for value in doc_vector.values():
			field_matches[value['field_name']] = value['field_text']
		ranking_list.append(
			{
				'doc_idx': doc_idx,
				'ranking': round(dot_product, 4),
				'field_matches': field_matches,
				'terms': ', '.join(doc_vector.keys()),
			}
		)
	ranking_list = sorted(ranking_list, key=lambda x: x['ranking'], reverse=True)
	if num_results:
		return ranking_list[:num_results]
	else:
		return ranking_list

class SearchEngine:
	def __init__(self, docs, use_field_norms=False):
		self.use_field_norms = use_field_norms
		self.doc_count = len(docs)
		self.create_inverted_index(docs)
		self.index_documents(docs)

	def create_inverted_index(self, docs):
		self.inverted_index = get_inverted_index(docs)

	def index_documents(self, docs):
		doc_index = dict()
		for idx, doc in enumerate(docs):
			doc_index[idx] = {
				'doc': doc,
				'weights': get_doc_with_weights(
						doc,
						self.doc_count,
						self.inverted_index,
						self.use_field_norms,
					)
				}
		self.docs = doc_index

	def query(self, phrase, num_results=10, field_boosts={}):
		self.phrase = phrase
		self.field_boosts = field_boosts
		tokenized_query = set(tokenize_field(phrase))
		num_terms_in_query = len(tokenized_query)
		self.query_vector = get_query_vector(self.doc_count, self.inverted_index, tokenized_query)
		self.doc_vectors = get_doc_vectors(self.docs, self.doc_count, self.inverted_index, tokenized_query)
		self.ranking_list = get_ranking_list(self.docs, num_terms_in_query, self.query_vector, self.doc_vectors, num_results, self.field_boosts)
		return self.print()

	def print(self):
		print('Query: ' + self.phrase)
		print('Search Results')
		print('------------------------------------------------')
		print('{0:<7} {1:<7} {2:<5} {3:<30}'.format('Ranking', 'Score', 'Idx', 'Terms'))
		for ranking_positition, doc in enumerate(self.ranking_list, 1):
			print('{0:<7} {1:<7} {2:<5} {3:<30}'.format(ranking_positition, doc['ranking'], doc['doc_idx'], doc['terms']))
			field_matches = '.\n'.join(['{} - {}'.format(key, value) for key, value in doc['field_matches'].items()])
			print(field_matches)
			print('------------------------------------------------')
