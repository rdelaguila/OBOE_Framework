from lark import Lark, Transformer
import joblib 
import rulesets
import importlib.util
importlib.reload(rulesets)
from nltk.corpus import wordnet as wn
from googletrans import Translator

from rulesets import *

#@lark.v_args(inline=True)
class myStack:
    def __init__(self):
        self.container = []  # You don't want to assign [] to self - when you do that, you're just assigning to a new local variable called `self`.  You want your stack to *have* a list, not *be* a list.
        
    def isEmpty(self):
        return self.size() == 0   # While there's nothing wrong with self.container == [], there is a builtin function for that purpose, so we may as well use it.  And while we're at it, it's often nice to use your own internal functions, so behavior is more consistent.

    def push(self, item):
        self.container.append(item)  # appending to the *container*, not the instance itself.

    def pop(self):
        if self.isEmpty():
            return ''
        return self.container.pop()  # pop from the container, this was fixed from the old version which was wrong
    
    def peek(self):
        if self.isEmpty():
            raise Exception("Stack empty!")
        return self.container[-1]  # View element at top of the stack

    def size(self):
        return len(self.container)  # length of the container

    def show(self):
        return self.container  # display the entire stack as list
from queue import SimpleQueue

class MyTransformer(Transformer):

    def __init__(self,positive_class='',lang='es'):
        self.nplist = []
        self.items_visitados = []
        self.last_visited=myStack()
        self.cont = 0
        self.termcont = 1
        self.explicacion = ''
        self.relevancia1=''
        self.relevancia2=''
        self.positive_class=positive_class
        self.message = ''
        if lang=='en':
            self.lang = 'en'
        else:
            self.lang = 'es'
            
    def start(self, items):
        #caracter = 'En el contexto de encontrar y justificar la categoría a la que pertenece un texto, se ha podido deducir a partir de los textos analizados y de la configuración utilizada en el proceso de la generación de reglas explicativas, que cuando: '
        caracter = 'En el contexto de encontrar y justificar la temática de un texto, hemos podido deducir que cuando \n ' if self.lang=='es' else 'In the context of finding and justifying the theme of a text, we have been able to deduce that whenever '
        cont = 1
        while self.last_visited.isEmpty() == False:
        
            caracter+= '' +self.last_visited.pop()+' '
        
        if self.lang == 'es':
            if "se encuentra en niveles comprendidos entre tiene importancia media y tiene importancia media en dicho texto" in caracter:
                caracter=caracter.replace('se encuentra en niveles comprendidos entre tiene importancia media y tiene importancia media en dicho texto',' tiene importancia media en dicho texto')
            elif "se encuentra en niveles comprendidos entre no tiene importancia y no tiene importancia en dicho texto" in caracter:
                caracter=caracter.replace("se encuentra en niveles comprendidos entre no tiene importancia y no tiene importancia en dicho texto", "no tiene importancia en dicho texto")
            elif "se encuentra en niveles comprendidos entre es poco importante y es poco importante en dicho texto" in caracter:
                caracter=caracter.replace("se encuentra en niveles comprendidos entre es poco importante y es poco importante en dicho texto", "es poco importante en dicho texto")

            elif "se encuentra en niveles comprendidos entre es importante y es importante en dicho texto" in caracter:
                caracter=caracter.replace("se encuentra en niveles comprendidos entre es importante y es importante en dicho texto","es importante en dicho texto")

            elif "se encuentra en niveles comprendidos entre es muy importante en dicho texto y es muy importante en dicho texto" in caracter:
                caracter=caracter.replace("se encuentra en niveles comprendidos entre es muy importante y es muy importante en dicho texto","es muy importante en dicho texto")
            else:
                caracter+=""
        else:
            if "is at levels between being of medium importance and being of medium importance in that text" in caracter:
                caracter=caracter.replace('is at levels between is of medium importance and is of medium importance in that text','is of medium importance in that text')
            elif "is at levels between is very unimportant and is very unimportant in that text" in caracter:
                caracter=caracter.replace("is at levels between is very unimportant and is very unimportant in that text", "is very unimportant in that text")
                
            elif "is at levels between is unimportant and is unimportant in that text" in caracter:
                caracter=caracter.replace("is at levels between is unimportant and is unimportant in that text", "is unimportant in that text")

            elif "is at levels between is important and is important in that text" in caracter:
                caracter=caracter.replace("is at levels between is important and is important in that text","is important in that text")

            elif "is at levels between is very important and is very important in that text" in caracter:
                caracter=caracter.replace("is at levels between is very important and is very important in that text","is very important in that text")
            else:
                caracter+=""
      #  elif "se encuentra en niveles comprendidos entre está en el máximo nivel posible de relevancia y está en el máximo nivel posible de relevancia" in caracter:
      #      caracter=caracter.replace("se encuentra en niveles comprendidos entre está en el máximo nivel posible de relevancia y está en el máximo nivel posible de relevancia","está en el máximo nivel posible de relevancia")
       
        #caracter +=", entonces el texto analizado puede pertenecer a la categoria "+self.positive_class
        caracter +=", entonces el texto analizado podría tratar del tema: "+self.positive_class if self.lang == 'es' else "then the text analyzed could be related to the topic: "+self.positive_class

        print(caracter)
        
        self.message = caracter
        self.message = self.message.replace (' , ',', ')
        self.message = self.message.replace('and and','and')
        self.message = self.message.replace('y y','y')
       

    def devuelveMensaje(self):
        return self.message
    
    def expresion_and(self,items):
        self.cont = self.cont + 1
        expresion2 = self.last_visited.pop()
        expresion1 = self.last_visited.pop()
        #print (expresion1 + ' _ Y _ '+ expresion2)
        print('\nEXPRESION AND '+str(self.cont)+': '+expresion2 + ' _ Y _ '+ expresion1)

        if len(expresion1)>0:
            
            if expresion2.startswith('and') or expresion2.startswith('(and') or expresion2.startswith('y') or expresion2.startswith('(y'):
                if expresion2.startswith('('):
                    expresion2 = expresion2[1:]
                    expresion2 = expresion2[:-1]
                self.last_visited.push(''+expresion1 + ' '+ expresion2+'')
            else:
                if self.lang == 'es':
                    self.last_visited.push(''+expresion1 + ' y '+ expresion2+'')
                else:
                    self.last_visited.push(''+expresion1 + ' and '+ expresion2+'')
        else:
            self.last_visited.push(expresion2)        
        
        self.relevancia1=''
        self.relevancia2=''
        #self.last_visited.put( 'AND',block=False )
      
    def expresion_or (self,items):
        self.cont = self.cont + 1

        expresion2 = self.last_visited.pop()
        expresion1 = self.last_visited.pop()

        if  len(expresion1)>0:
            print('\n EXPRESION OR '+str(self.cont)+': '+expresion1 + ' o '+ expresion2)
            print('range true '+str(self.relevancia1)+'----'+str(self.relevancia2))

            if self.relevancia1 == self.relevancia2 and len(self.relevancia1)>0:
                print('Haciendo push de '+expresion1)
                self.last_visited.push(expresion1)
            else:
                print('Haciendo push de '+'('+expresion1 + ' o '+ expresion2+')')

                if self.lang == 'es':
                    self.last_visited.push(''+expresion1 + ' o '+ expresion2+'')
                else:
                    self.last_visited.push(''+expresion1 + ' or '+ expresion2+'')
        else:
            self.last_visited.push(expresion2)

        self.relevancia1=''
        self.relevancia2=''
#print (expresion1 + ' _ O _ '+ expresion2)
    def expresion (self, items):
        self.cont = self.cont + 1

        self.rangeFrom=False
        self.rangeTo=False
        if items[0]!='(':
            termino = items[0]
            operator = items[1]
            rele = int(str(items[2]))
            operador = ''
            lpar = ''
            rpar=''#items[len(items)-1]
            #if items[len(items)-1]=='':
                #rpar=''
        else:
            termino = items[1]
            operator = items[2]
            rele = int(str(items[3]))
            operador = ''
            lpar = '('
            rpar=''#items[len(items)-1]
            #if items[len(items)-1]=='': 
            #    rpar=''   
        print ('\n'+str(self.cont)+' analizado: ' + termino+operator+str(rele)+'\n') 
        if (operator=='>'):
            operador = 'se encuentra en niveles comprendidos entre' if self.lang == 'es' else 'is at levels between'
            self.rangeFrom = True
            self.rangeTo=False
            print('range from!!!!')
        elif operator=='<' or operator =='<=':
            operador='y' if self.lang == 'es' else 'and'
            
            self.rangeTo=True
            self.rangeFrom = False
            print('range To!!!!!!!')
        elif operator=='==':
            operador = ''
        elif operator=='>=':
            operador = 'se encuentra en niveles comprendidos entre' if self.lang == 'es' else 'is at levels between'
            self.rangeFrom = True
            self.rangeTo = False
            print('range from!!!!')

        else:
            operador = ''
        
        if operador=='==':
            self.last_visited=''
        final = ' en dicho texto' if self.lang == 'es' else ' in that text'
        if  rele>=0 and rele<=2:
            relevancia = ' no tiene importancia' if self.lang == 'es' else ' is very unimportant'
            if self.rangeFrom==True:
                self.relevancia1=copy.deepcopy(relevancia)
                print('si estoy metiendo self relevancia1'+self.relevancia1)

            if self.rangeTo==True:
                self.relevancia2 = copy.deepcopy(relevancia)
                
        elif rele>=3 and rele<5:
            relevancia = ' es poco importante' if self.lang == 'es' else ' is unimportant'
            if self.rangeFrom==True:
                self.relevancia1=copy.deepcopy(relevancia)
                print('si estoy metiendo self relevancia1'+self.relevancia1)

            if self.rangeTo==True:
                self.relevancia2 = copy.deepcopy(relevancia)
        elif rele>=5 and rele<7:
            relevancia = 'tiene importancia media' if self.lang == 'es' else 'is of medium importance'

            if self.rangeFrom==True:
                self.relevancia1=copy.deepcopy(relevancia)
                print('si estoy metiendo self relevancia1'+self.relevancia1)

            if self.rangeTo==True:
                self.relevancia2 = copy.deepcopy(relevancia)
        elif rele>=7 and rele<=8:
            relevancia = 'es importante' if self.lang == 'es' else 'is important'
            if self.rangeFrom==True:
                self.relevancia1=copy.deepcopy(relevancia)
                print('si estoy metiendo self relevancia1'+self.relevancia1)

            if self.rangeTo==True:
                self.relevancia2 = copy.deepcopy(relevancia)
        
        elif rele>=9 and rele<=10:
            relevancia = 'es muy importante' if self.lang == 'es' else ' is very important'
            if self.rangeFrom==True:
                self.relevancia1=copy.deepcopy(relevancia)
                print('si estoy metiendo self relevancia1'+self.relevancia1)

            if self.rangeTo==True:
                self.relevancia2 = copy.deepcopy(relevancia)
        #else:
        #    relevancia = 'está en el máximo nivel posible de relevancia'
        #    if self.rangeFrom==True:
        #        self.relevancia1=copy.deepcopy(relevancia)
        #        print('si estoy metiendo self relevancia1'+self.relevancia1)
        #    if self.rangeTo==True:
        #        self.relevancia2 = copy.deepcopy(relevancia)
            #if termino in self.items_visitados:
        if operator=='<' or operator =='<=':
            if self.rangeTo==True:
                if self.relevancia1.strip()==self.relevancia2.strip():
                    operador = ''
                    anterior = self.last_visited.pop()
                    if anterior.startswith('('):
                        lpar = '('
                    
                    print('OJITO QUE ME PULO '+anterior)
                    
                    self.relevancia2 =''
                    print ('Adding simplified to'+ termino + ' '+ operador +' '+ relevancia+')' )
                    self.last_visited.push (''+ termino + ' '+ operador +' '+ relevancia+''+final  )
                    if '('+self.termcont+')' in anterior == False:
                        self.termcont = self.termcont + 1
                else:
                    print('Adding not simplified: r1'+self.relevancia1+ '- r2:'+self.relevancia2+'::'+lpar+operador +' '+ relevancia+rpar)
                    self.last_visited.push (''+operador +' '+ relevancia+''+final)
                    self.termcont = self.termcont + 1
        else:
            #if rangeFrom==True:
            #    rpar=''
            #else:
            #    rpar=''
            print('Adding '+lpar+ termino + ' '+ operador +' '+ relevancia+rpar)
            if self.rangeFrom==True:
                self.last_visited.push ('('+str(self.termcont)+') '+ termino + ' '+ operador +' '+ relevancia+''  ) #range from no meter relevancia
                self.termcont = self.termcont + 1
            else:
                self.last_visited.push ('('+str(self.termcont)+') '+ termino + ' '+ operador +' '+ relevancia+''+final  )
                self.termcont = self.termcont + 1
                
    def transform(self, tree):
        self.termcont=1
        self._transform_tree(tree)
        return self.nplist
        
from spotlight import *
class TextAnalyzer(object):
    def __init__(self,nlp):
        self.nlp = nlp 
        
    # allow the class instance to be called just like
    # just like a function and applies the preprocessing and
    # tokenize the document
    @staticmethod      
    def remove_special_lines(texto):
        texto = re.sub("^upright=.*[\r|\n]", '', texto)
        texto = re.sub("^upright = .*[\r|\n]", '', texto)
        texto = re.sub("Category:.*[\r|\n]",'',texto)
        texto = re.sub("Cat\D*:.*[\r|\n]",'',texto)
        texto = re.sub("[[][\d]+[]]",'',texto)
        texto = re.sub("thumb",'',texto)
        texto = re.sub("[|]",'',texto)
        texto = re.sub("\d+px",'',texto)
        return (texto)
    @staticmethod
    def strip_formatting(string):
        string = string.lower()
        string = re.sub(r"([.!?,;-_'/|()]=-<>+*`)", r"", string)
        string = re.sub(r'https?:\/\/.*?[\s]', '', string) 
        return string

    def get_nlp(self):
        return self.nlp
    
    def __call__(self, doc):
        tokens = nlp(doc)
        lemmatized_tokens = [(token.lemma_.lower()) for token in tokens
                                                   if not (token.is_stop or token.is_punct)]
            
        return(lemmatized_tokens)
    
    def is_present (self,word,text):
        lemmatized_tokens =  lambda text: " ".join(token.lemma_.lower() for token in nlp(text) if not (token.is_stop or token.is_punct))
        normalizado = lemmatized_tokens(text)    
        return (word in (normalizado))

class SemanticAnalyzer(TextAnalyzer):
    def __init__(self,nlp,endpoint='http://192.168.99.100:2222/rest/annotate/',soporte=1,confianza=0.1,umbral=0.1):
        super().__init__(nlp)
        self.endpoint = endpoint
        self.soporte=soporte
        self.confianza = confianza
        self.alfa = umbral
    
    def __call__(self, doc):
        try:
            annotations = spotlight.annotate(self.endpoint,
                                     doc,
                                      confidence=self.confianza, support=self.soporte, spotter='Default')
            diccionario =  dict()
            for annotation in annotations:
                lista = list(annotation.items())
                print(lista)
                URI = lista[0]
                key = lista[3]
                score = lista[5]
               # if (score[1]>self.alfa):
                diccionario[key[1]]=URI[1]
        
            return(diccionario)
        except Exception as ex:
            print(ex)

#cargamos dbpedia y sumo

class OntologyOracle(object):
    def __init__(self,nlp,dict_onto,dict_graph):

        self.dict_onto = dict_onto
        self.dict_graph = dict_graph
        
        self.prefijos = """  PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
                                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                                PREFIX dbr:    <http://dbpedia.org/resource/>
                                PREFIX dbo:    <http://dbpedia.org/ontology/>
                                PREFIX dct:    <http://purl.org/dc/terms/>
                                PREFIX owl:    <http://www.w3.org/2002/07/owl#>
                                PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                                PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
                                PREFIX schema: <http://schema.org/>
                                PREFIX skos:   <http://www.w3.org/2004/02/skos/core#>
                                PREFIX xsd:    <http://www.w3.org/2001/XMLSchema#>
                                PREFIX SUMO: <http://www.adampease.org/OP/SUMO.owl#>
                                PREFIX SUMOR: <http://www.ontologyportal.org/SUMO.owl#>
                            """
        self.sa = SemanticAnalyzer(nlp)
      
    
    
    def isSubclassOf(self,term1,term2,isDbo):
        
        consulta = self.prefijos + """
        ASK  { 
                """+term1+""" rdfs:subClassOf """+term2+""" }"""
          
        if (isDbo==False):
            return (list(self.dict_graph.get('SUMO').query(consulta)))  
        else:
            return (list(self.dict_graph.get('dbo').query(consulta)))
    
    
    def isSuperclassOf (self,term1,term2,isDbo):
        consulta = self.prefijos + """
        ASK  {  
                """+term2+""" rdfs:subClassOf """+term1+""" }"""
          
        if (isDbo==False):
            return (list(self.dict_graph.get('SUMO').query(consulta)))  
        else:
            return (list(self.dict_graph.get('dbo').query(consulta)))
    
        
    def areRelated (self,term1,term2,isDbo):
        consulta = self.prefijos + """
        ASK  {  """+term1+""" ?property """+term2+""" }"""
          
        if (isDbo==False):
            return (list(self.dict_graph.get('SUMO').query(consulta)))  
        else:
            return (list(self.dict_graph.get('dbo').query(consulta)))
        
    def getRelation(self,term1,term2,isDbo):
        consulta = self.prefijos + """
        select ?property where  {  """+term1+""" ?property """+term2+""" }"""
          
        if (isDbo==False):
            return (list(self.dict_graph.get('SUMO').query(consulta)))  
        else:
            return (list(self.dict_graph.get('dbo').query(consulta)))
    
    def isDbo (self,term):
        res = self.dict_onto.get('dbo').search(label=term,_case_sensitive=False)
        if (len(res)>0):
            return True
        res = self.dict_onto.get('SUMO').search(label=term,_case_sensitive=False)
        if (len(res)>0):
            return False
        else:
            return None

    def _getBaseConcept(self,term,isDbo):
        if (isDbo):
            res = self.dict_onto.get('dbo').search(label=term,_case_sensitive=False)
            if (len(res)>0):
                return str(res[0]).replace('.',':')
        
        else:
            res = self.dict_onto.get('SUMO').search(label=term,_case_sensitive=False)
        
        if (len(res)>0):
            return str(res[0]).replace('.',':')
        else:
            return None
        
    def _getHierarchy(self,concept,isDbo,isSuperclass):
        
        consulta = self.prefijos + """SELECT ?x
            WHERE {
                ?x a owl:Class .
                ?x rdfs:subClassOf """+concept+"""
                }"""
        columna = 'superclass'
        if isSuperclass == False:
            columna='subclass'
            consulta = self.prefijos + """SELECT ?x
            WHERE {
                ?x a owl:Class .
                """+concept+""" rdfs:subClassOf ?x 
                }"""
                
        if (isDbo==False):
            resultado =  (list(self.dict_graph.get('SUMO').query(consulta)))  
        else:
            resultado =  (list(self.dict_graph.get('dbo').query(consulta)))
           
        newresult = [r for res in resultado for r in res ]
        print(newresult)
        columnas = [columna]
        res = pd.DataFrame(data=newresult,columns=columnas)
        return newresult
    
    def _getRelationships(self,concept,isDbo):
        consulta = self.prefijos + """select distinct  ?property ?value where {
                  """+concept+""" ?property ?value .
                  filter ( ?property not in ( rdf:type ) )
                   filter ( ?property not in ( rdfs:label ) )
                   filter ( ?property not in ( rdf:type ) )
                   filter ( ?property not in ( rdfs:isDefinedBy ) )
                   filter ( ?property not in ( SUMOR:externalImage ) )
                   filter ( ?property not in ( SUMOR:axiom ) )
                   
                  optional {?property rdfs:comment ?comment}
                  optional {?property rdfs:range ?range} 
                  optional {?property rdfs:domain ?domain} 
                }
        """
        #print(consulta)
        if (isDbo==False):
            resultado =  (list(self.dict_graph.get('SUMO').query(consulta)))  
            res = pd.DataFrame(data = resultado, columns = ['property','element'])
            wordnetlist = list()
            for wne in res.element:
                uri = wne.n3()
                uri = uri.replace('http://www.adampease.org/OP/wn','./ontologias/WordNet.owl')
                wnconsulta = self.prefijos + """select distinct ?label ?comment where {
               """+uri+"""  rdf:type owl:Thing .
               """+uri+"""   rdfs:label ?label .
                """+uri+"""   rdfs:comment ?comment .
                
                
                }"""
                
                resultado = self.dict_graph.get('wn').query(wnconsulta)

                wordnetlist.append([r for res in resultado for r in res]) 
            res['explicacion']=wordnetlist

        else:
            resultado = (list(self.dict_graph.get('dbo').query(consulta)))
            res = pd.DataFrame(data = resultado, columns = ['property','element'])

        res['term'] = concept
        res.set_index(res.term)
        return res #(res.to_json())

            
    def getSemanticsOfTerm(self,term,isDbo=None):
        
        if isDbo == None:
            isDbo = self.isDbo(term)
        #if (isDbo):
        #    resources = {} #self.sa(term)
        #else:
        #    resources = {}
        if isDbo is None:
            #devolvemos semantica de WN
            wordnetSemantics = list()
            sentidos = wn.synsets(term) 
            wordnetSemantics.append([(lemma.name(), sysnet.definition()) for sysnet in sentidos for lemma in sysnet.lemmas()])
            resultado = pd.DataFrame(data=wordnetSemantics, columns=['termino','significado'])
            return False, resultado
        
        concept = self._getBaseConcept(term,isDbo)
        if concept is None:
            return None
        superclasses = self._getHierarchy(str(concept),isDbo,False)
        subclasses = self._getHierarchy(str(concept), isDbo,True)
        relationships = self._getRelationships(str(concept),isDbo)
        
        termino = dict({'concepto':concept,'padres':superclasses,'hijos':subclasses,'relaciones':relationships})
        
        return True,termino
    
class SemanticRuleExplainer (object):
    
    def __init__(self,n_terms=3, lang='es'):
        self.n_terms = n_terms
        self.lang = 'en' if lang!='es' else 'es'
    
    def construirRelatoTermino(self,alfred,term,isDbo): 
        relatos=''
        sentidos = wn.synsets(term)
        translator = Translator()
        if sentidos is None:
            relatos +='\tNo se ha encontrado el término :<'+term+'> en Wordnet. Compruebe si se trata de un error en la redacción o si es un término específico de un dominio concreto.\n'
        else:
            relatos += '\El término: <'+term+'> ha sido encontrado en WordNet. Mostrando '+str(self.n_terms)+' definiciones\n'
            cont = 0
            for synset in sentidos:
                for lemma in synset.lemma_names('spa'):
                    relatos+='\t\t'+str(cont)+'. Posible definición para <'+term+'>, de acuerdo con la forma: '+lemma+'. Definición: '+ translator.translate(synset.definition(),dest='es').text+'\n'
                    cont = cont + 1 
                    if cont >= self.n_terms:
                        break
                if cont >= self.n_terms:
                    break
                       
       
        try:
            valor,dboTerms = alfred.getSemanticsOfTerm(term,False)

            #print(dboTerms)
            #print(type(dboTerms))
            if dboTerms is not None:
                relatos+='\n\tEl concepto relativo al término <'+term+'> fue encontrado en la ontología SUMO: <'+dboTerms.get('concepto')+'>\n'

                relatos +='\t\tSeguidamente se detallan las super clases del concepto:\n'

                elementos = dboTerms.get('padres')
                for elemento in elementos:
                    relatos+='\t\t-\t<'+str(elemento)+'>\n'

        #        print('Hijos: ')
        #        mdFile.new_header(level=4, title='Hijos de: '+term)

        #        elementos = dboTerms.get('hijos')
        #        listah = list()
        #        listah = [elemento for elemento in elementos]
        #        mdFile.new_list(items=listah)



        #        relatos+= 'Some relations have been found: '

        #        relaciones = dboTerms.get('relaciones')
        #        lista  = ["Property", "Descriptions"]
        #        fila = 1

        #        for index, rows in relaciones.iterrows():
        #            relatos+='\t{0}: {1} {2}\n'.format(str(fila),rows['property'],rows['explicacion'].__str__())
        #            fila = fila+1
        except:
            relatos +='\n\tEl concepto relativo al término <'+term+'> no fue encontrado en SUMO'

      
        if isDbo == True:
            #relatos+=('\n********************Retrieving semantics in DBO********************\n')
            try:
                valor,dboTerms = alfred.getSemanticsOfTerm(term,True)

                #print(dboTerms)
                #print(type(dboTerms))
                if dboTerms is not None:
                    relatos+='\n\tEl concepto relativo al término <'+term+'> fue encontrado en DBpedia:<'+dboTerms.get('concepto')+'>\n'

                    relatos +='\t\tSeguidamente se detallan las super clases del concepto:\n'

                    elementos = dboTerms.get('padres')
                    for elemento in elementos:
                        relatos+= '\t\t-\t<'+str(elemento)+'>\n'
            except:
                relatos +='\tEl concepto relativo al término <'+term+'> no fue encontrado en DBpedia'

#                relatos+= 'Some relations have been found: '

#                relaciones = dboTerms.get('relaciones')
#                lista  = ["Property", "Descriptions"]
#                fila = 1

#                for index, rows in relaciones.iterrows():
#                    relatos+='\t{0}: {1} {2}\n'.format(str(fila),rows['property'],rows['explicacion'].__str__())
#                    fila = fila+1

            
        return relatos
    
    def construirRelatoSimplificadoTermino(self,term): 
        relatos=''
        sentidos = wn.synsets(term)
        translator = Translator()
        if sentidos is None:
            relatos +='\tNo se ha encontrado el término :<'+term+'>. Compruebe si se trata de un error en la redacción o si es un término demasiado específico a un tema concreto.\n' if self.lang == 'es' else '\tTerm :<'+term+'> was not found. Check your spelling or maybe is a domain specific term'
        else:
            relatos += ' Mostrando '+str(self.n_terms)+' posibles definiciones para el término: <'+term+'> \n' if self.lang == 'es' else ' Showing '+str(self.n_terms)+' possible definitions for the term: <'+term+'> \n'
            cont = 0
            if self.lang == 'es':
                for synset in sentidos:
                    for lemma in synset.lemma_names('spa'):
                        relatos+='\t\t'+str(cont)+'. Posible definición para <'+term+'>, de acuerdo con el sentido: '+lemma+'. Definición: '+ translator.translate(synset.definition(),dest='es').text+'\n'
                        cont = cont + 1 
                        if cont >= self.n_terms:
                            break
                    if cont >= self.n_terms:
                        break
            else:
                for synset in sentidos:
                    for lemma in synset.lemma_names('eng'):
                        relatos+='\t\t'+str(cont)+'. Definition of <'+term+'>, in compliance with the semantic meaning: '+lemma+'. Definition: '+ synset.definition()+'\n'
                        cont = cont + 1 
                        if cont >= self.n_terms:
                            break
                    if cont >= self.n_terms:
                        break

            
        return relatos