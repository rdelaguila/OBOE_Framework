from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import pandas as pd
import math
import numpy as np
import array
from collections import defaultdict
import scipy.sparse as sp

class WeightedTfidfVectorizer(TfidfVectorizer):
   

    def __init__(self, input='content', encoding='utf-8',
                 decode_error='strict', strip_accents=None, lowercase=True,
                 preprocessor=None, tokenizer=None, analyzer='word',
                 stop_words=None, token_pattern=r"(?u)\b\w\w+\b",
                 ngram_range=(1, 1), max_df=1.0, min_df=1,
                 max_features=None, vocabulary=None, binary=False,
                 dtype=np.float64, norm='l2', use_idf=True, smooth_idf=True,
                 sublinear_tf=False):

        super().__init__(
            input=input, encoding=encoding, decode_error=decode_error,
            strip_accents=strip_accents, lowercase=lowercase,
            preprocessor=preprocessor, tokenizer=tokenizer, analyzer=analyzer,
            stop_words=stop_words, token_pattern=token_pattern,
            ngram_range=ngram_range, max_df=max_df, min_df=min_df,
            max_features=max_features, vocabulary=vocabulary, binary=binary,
            dtype=dtype)

    def calc_fti(self,term,raw_documents):
        columnclase = raw_documents.columns[1]
        nclasses = np.unique(raw_documents.iloc[:,1]).shape
        classes = np.unique(raw_documents.iloc[:,1])
        target = raw_documents.columns[1]
        text = raw_documents.columns[0]
        list_Fti = dict()
        fti_global = 0
        cont = 1
        for clase in classes:
            #fti numero de documentos q tienen a t en la clase i

            fti = sum(raw_documents.loc[ raw_documents[columnclase]==clase,text ].str.contains(term, regex=False, case=False, na=False).astype(int))
            #print ('termino {0} fti en clase {1} es {2}'.format(text,clase,fti))
            avgfti = 0
            i  = 1
            for clase2 in classes:
                #print(str(i))
                avgfti += sum(raw_documents.loc[ raw_documents[columnclase]==clase2,text ].str.contains(term, regex=False, case=False, na=False).astype(int))
            avgfti = (1/len(classes))*avgfti
            cont = cont  + 1

            fti_global += math.pow((fti - avgfti),2)
            #print('fti para clase {0}  es fti - avg fti {1} - {2} al cuadrado, lo que resulta en {3}'.format(clase,fti,avgfti,fti_global))

        fti_final = ((1/len(classes))*fti_global)
        return fti_final 

    def _count_vocab(self,raw_documents, fixed_vocab=False):
        """Create sparse feature matrix, and vocabulary where fixed_vocab=False,
           In this case we consider that raw_documents has a nX2 shape
        """
        if fixed_vocab:
            vocabulary = self.vocabulary_
        else:
            # Add a new value when a new vocabulary item is seen
            vocabulary = defaultdict()
            vocabulary.default_factory = vocabulary.__len__

        analyze = super().build_analyzer()
       
        j_indices = []
        indptr = []

        values = array.array(str('f'))
        indptr.append(0)
        for doc in raw_documents:
            #doc = tupla[0]
            feature_counter = {}
            #texttlist = doc.split(sep=" ")
            for feature in analyze(doc):#texttlist:
                try:
                   
                    # Ignore out-of-vocabulary items for fixed_vocab=True
                    feature_idx = vocabulary[feature]
                    #print(feature_idx)
                    #fti_feature = calc_fti(feature,raw_documents)
                    
                    if feature_idx not in feature_counter:
                        feature_counter[feature_idx] = 1
                    else:
                        feature_counter[feature_idx] += 1
                    #print(feature_counter[feature_idx])
                except KeyError:
                    # Ignore out-of-vocabulary items for fixed_vocab=True
                    continue


            j_indices.extend(feature_counter.keys())
            values.extend(feature_counter.values())
            indptr.append(len(j_indices))

        if not fixed_vocab:
            # disable defaultdict behaviour
            vocabulary = dict(vocabulary)
            if not vocabulary:
                raise ValueError("empty vocabulary; perhaps the documents only"
                                 " contain stop words")

        if indptr[-1] > np.iinfo(np.int32).max:  # = 2**31 - 1
            if _IS_32BIT:
                raise ValueError(('sparse CSR array has {} non-zero '
                                  'elements and requires 64 bit indexing, '
                                  'which is unsupported with 32 bit Python.')
                                 .format(indptr[-1]))
            indices_dtype = np.int64

        else:
            indices_dtype = np.int32
        
        j_indices = np.asarray(j_indices, dtype=indices_dtype)
        indptr = np.asarray(indptr, dtype=indices_dtype)
        
        #print (vocabulary)
        X = sp.csr_matrix((values, j_indices, indptr),
                          shape=(len(indptr) - 1, len(vocabulary)),
                          dtype=np.float32)
        X.sort_indices()        
       
        self.vocabulary_calculated = vocabulary

        return vocabulary, X
    
    def cal_term_fti(self,raw_documents):
        self.diccionario_fti = dict()
        array_def = array.array(str('f'))
        for termino in list(self.vocabulary_.keys()):
            indice = self.vocabulary_.get(termino)
            #print(matriz[:,indice])
            fti = self.calc_fti(termino,raw_documents)
            self.diccionario_fti.update({indice:fti})
            #array_def.append(np.apply_along_axis(lambda x :x * fti,0,matriz[:,indice]))
            
            #print('matriz tras indice')
            #print (matriz[:,indice])
        
    def fit(self, raw_documents, y=None):
        """Learn vocabulary and idf from training set.
        Parameters
        ----------
        raw_documents : iterable
            An iterable which yields either str, unicode or file objects.
        y : None
            This parameter is not needed to compute tfidf.
        Returns
        -------
        self : object
            Fitted vectorizer.
        """

        X = super().fit_transform(raw_documents) #now pandas return matrix 
        self._tfidf.fit(X)
        ##arqui
        return self

    def fit_transform(self, raw_documents, y=None):
        """Learn vocabulary and idf, return term-document matrix.
        This is equivalent to fit followed by transform, but more efficiently
        implemented.
        Parameters
        ----------
        raw_documents : iterable
            An iterable which yields either str, unicode or file objects.
        y : None
            This parameter is ignored.
        Returns
        -------
        X : sparse matrix, [n_samples, n_features]
            Tf-idf-weighted document-term matrix.
        """
        #self.diccionario_fti.update({indice:fti})
        textos = raw_documents.iloc[:,0]
        X = super().fit_transform(textos)
        self.cal_term_fti(raw_documents)

        X2 = X.todense()
        for indice in list(self.diccionario_fti.keys()):
            fti = self.diccionario_fti.get(indice)
            #print('indice {0} valor')
            X2[:,indice]=np.transpose(np.apply_along_axis(lambda x :x * fti,0,X2[:,indice]))
            
            #print('matriz tras indice')
            #print (matriz[:,indice])
        matrizfinal = sp.csr_matrix(X2,X.shape)
        #aqui
        return matrizfinal

    def transform(self, raw_documents, copy="deprecated"):
          
        return self.fit_transform(raw_documents)

    def _more_tags(self):
        return {'X_types': ['string'], '_skip_test': True}
    