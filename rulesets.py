import numpy as np
import pandas as pd
import datatable
import itertools as it
from owlready2 import *
import math
import joblib
import copy
import pickle
from sklearn.feature_selection import mutual_info_classif
from collections import Counter
#para depurar los que letras que no están en el codigo ascii
import unicodedata
import functools
import spacy
import stanfordnlp
#from spacy_stanfordnlp import StanfordNLPLanguage
from sklearn.decomposition import LatentDirichletAllocation
from sklearn import metrics
#from wiki_dump_reader import Cleaner, iterate
from sklearn.decomposition import TruncatedSVD

from sklearn.preprocessing import normalize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import pairwise_distances

from sklearn.preprocessing import normalize


import random
import joblib

#import gensim
#import gensim.corpora as corpora
#from gensim.models import CoherenceModel
#from gensim.models import HdpModel


import spacy
import time 

import json 

warnings.filterwarnings("ignore")

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from multiprocessing import  Pool
import math
import scipy.sparse as sp


class Igualdad(object):
    def __init__(self,variable,valor):
        self._variable = variable
        self._valor = valor
        self._operator = '=='
    def __str__(self):
        return (self._variable + self._operator+ str(self._valor))
    @property 
    def variable(self):
        return self._variable
    def getvariable(self):
        return self.variable
    @property
    def valor(self):
        return self._valor
    def getvalor(self):
        return self.valor
    @property 
    def operator(self):
        return self._operator
    @variable.setter
    def variable(self,value):
        self._variable = value
    @valor.setter
    def valor(self,value):
        self._valor = value
    @operator.setter
    def operator(self,value):
        self._operator = value        
        
    def toString(self):
        return self.__str__()
    def cambiaroperador(self,mayor):
        if mayor:
            self._operator='>='
        else:
            self._operator='<='
        
class Disyuncion(object):
    def __init__(self,igualdad1,igualdad2=None):
        self.igualdad1=igualdad1
        self.igualdad2=igualdad2
    @property 
    def igualdad1(self):
        return self._igualdad1
    @property 
    def igualdad2(self):
        return self._igualdad2
    @igualdad1.setter
    def igualdad1(self,igualdad):
        self._igualdad1=igualdad
    @igualdad2.setter
    def igualdad2(self,igualdad):
        self._igualdad2=igualdad
        
    def toString(self,operadorAnd=True):
        string = self.igualdad1.toString()
        if self.igualdad2 is not None: ##antes estaba con un and!?
            if operadorAnd==True and self.igualdad1.operator!='==':
                string = '('+string + ' and ' +self.igualdad2.toString()+')'
                print('operator 1'+self.igualdad1.operator)
            else:
                string = '('+string + ' or ' +self.igualdad2.toString()+')'
            
        return string
    def longitud(self):
        if self.igualdad2 is None:
            return 1
        else:
            return 2
## a concretar
class IgualdadSemantica(Igualdad):
    def __init__(self,Igualdad):
        super().__init__(igualdad.getvariable(),igualdad.getvalor())
        self.componente_semantico=dictionary()
    def setComponenteSemantico(componente):
        self.componente_semantico = componente
        

from itertools import combinations
class ColeccionCandidatos(object):
    def __init__(self):
        self._candidatos = set()
        self._diccionario = dict()
        self._combinaciones = list()
    @property 
    def candidatos(self):
        return self._candidatos 
    @property 
    def diccionario(self):
        return self._diccionario
    @property
    def combinaciones (self):
        return self._combinaciones
    
    @candidatos.setter
    def candidatos(self,value):
        self._candidatos = value
    @diccionario.setter
    def diccionario(self,value):
        self._diccionario = value
    @combinaciones.setter
    def combinaciones(self,value):
        self._combinaciones = value
        
    def append(self,igualdad):
        self.candidatos.add(igualdad)
    
    def sincronizar (self):
        self.diccionario = { candidato.__str__() : candidato for candidato in list(self.candidatos) }
        
    def getdiccionario(self):
        return self.diccionario
    
    def getcandidatos(self):
        return list(self.candidatos)
        
    def getCandidatosDeVariable(self,value,min_rel):
        keys = self.diccionario.keys()
        devolver = set()
        for key in keys:
            llave = key.split("==")[0]
            if value == llave:
                if int( key.split("==")[1])>=min_rel:
                    devolver.add(key)
                 
        return devolver
    
    def generarCombinaciones(self,minl,maxl):
        keys = list( self.diccionario.keys())
        for i in range(minl,maxl+1):
            comb = list(combinations(keys,i))
            self.combinaciones.extend(comb)
            
    def getcombinaciones(self):
        return (self.combinaciones)
    

#meter esto en explain. Ojo, los positivos se tiene que reducir... pq estamos cogiendo los del primer antecedente!!
import more_itertools as mit

class Rule (object):
    def __init__(self,max_igualdad=None,interval=None):
        self._antecedente = list()
        self._consecuente = 0.0
        self._max_igualdad = max_igualdad
        self._contador = 0
        self._interval = interval
        self._confianza = 0
        self._disyuncion = list()
    
    @property
    def consecuente(self):
        return self._consecuente
    
    @consecuente.setter
    def consecuente(self,value):
        self._consecuente = value
        
    @property 
    def confianza(self):
        return self._confianza
    @confianza.setter
    def confianza(self,value):
        self._confianza=value
    @property
    def antecedente(self):
        return self._antecedente
    
    @antecedente.setter
    def antecedente(self,value):
        self._antecedente = value
    
    @property 
    def disyuncion(self):
        return self._disyuncion
    
    @disyuncion.setter
    def disyuncion(self,value):
        self._disyuncion = value
    
    @property 
    def max_igualdad(self):
        return self._max_igualdad
    @max_igualdad.setter
    def max_igualdad(self,value):
        self._max_igualdad=value
        
    @property 
    def contador(self):
        return self._contador
    
    @contador.setter
    def contador(self,value):
        
        self._contador = value
    def getvalor(self):
        return self.consecuente
    
    def isNew(self):
        return (len(self.antecedente)==0)
    
    def append(self,Igualdad,esDisyuncion=False):
        if self.max_igualdad is not None and self.contador > self.max_igualdad:
            raise Exception ('maximo numero de igualdades excedidas')
        if esDisyuncion==False:
            self.antecedente.append(Igualdad)
            self.contador = self.contador + 1
        else:
            self.disyuncion.append(Igualdad) 
    
    def finish(self,valor,confianza):
        self.consecuente = valor
        self.confianza = confianza
        
    def toQuery(self):
        string=''
        for igualdad in self.antecedente:
            string = string + str(igualdad.toString()) + ' and '
        if len(self.disyuncion)==0:
            string = string[:-5] #quto el && final
        else:
            string = string + '(' ###dis
            contdis = 0
            antecedente_ant = ''
            flag_cambio = False
            len_ant = 0
            for dis in self.disyuncion:
                variable = dis.igualdad1.variable
                if dis.longitud() == 1 and len_ant==1 and len(self.antecedente)>0:
                    if variable != antecedente_ant:
                        flag_cambio = True
                        string = string[:-4]
                        if dis.igualdad1.operator=='==':
                            string = string + ' or '
                        else:
                            string = string + ' and '
                    else:
                        flag_cambio = False
                    antecedente_ant = variable
                else:
                    antecedente_ant=''
                if len(self.antecedente)>0:
                    print('debería entrar aqui si tengo antecedentes, por cada disyuncion')
                    if dis.igualdad1.operator=='==':
                        print('OPERATOR IGUAL '+dis.toString(False)+'--'+dis.toString(True))
                        string = string + dis.toString(False)+ ' or '
                        print(string)
                    else:
                        print('OPERATOR GREATER OR LOWER THAN')
                        string = string + dis.toString(True)+ ' or '
                        
                   # string = string + dis.toString((len (self.antecedente)>0))+ ' or ' #ojo raul, te entra aqui con operator and, pero qué pasa, que no es un and pq son varios windows iguales
                    print(string)
                else: ##en funcion de los operadores
                    print('debería entrar aqui si no tengo antecedentes')
                    if dis.igualdad1.operator=='==':
                        print('OPERATOR IGUAL')
                        string = string + dis.toString((len (self.antecedente)>0))+ ' or '
                        print(string)
                    else:
                        print('OPERATOR GREATER OR LOWER THAN')
                        string = string + dis.toString(True)+ ' or '
                        #para reglas del tipo si book>5 and book<8
                    #antecedente_ant=variable
                len_ant =dis.longitud()
            string = string[:-4]
            string = string + ')'
                    
        return(string)
    
    def toString(self):
        string = ''
        string = string+ self.toQuery()
       # paso = self.consecuente / self.interval
        string = string + ' => p('+str(self.consecuente)+'), conf('+str(self.confianza)+')'
        return string
    
    def len(self):
        return len(self.antecedente)
    
    def estaEnRegla(self,atributo):
        for igualdad in self.antecedente:
            if igualdad.getvariable()==atributo:
                return True
    
    def getIgualdad(self,antecedente):
        for igualdad in self.antecedente:
            if igualdad.variable==antecedente:
                return igualdad
        for d in self.disyuncion:
            if d.igualdad1.variable == antecedente:
                return igualdad
            if d.igualdad2 is not None and d.igualdad2.getvariable()==antecedente:
                return igualdad

    def getAntecedentes(self,todos=False):
        antecedentes = [igualdad.variable for igualdad in self.antecedente]
        if todos==True:
            for d in self.disyuncion:
                antecedentes.append(d.igualdad1.variable)
                if d.igualdad2 is not None:
                    antecedentes.append(d.igualdad2.variable)
        return copy.deepcopy(antecedentes)
    
    def updateIgualdad(self,igualdad):
        for eq in self.antecedente:
            if eq.variable==igualdad.variable:
                self.antecedente.remove(eq)
                self.antecedente.append(igualdad)
                return
        for dis in self.disyuncion:
            if dis.igualdad1.variable==igualdad.variable:
                newdis = dis
                newdis.igualdad1 = igualdad
                self.disyuncion.remove(dis)
                self.disyuncion.append(dis)
                return
            if dis.igualdad2 is not None and dis.igualdad2.variable==igualdad.variable:
                newdis = dis
                newdis.igualdad2 = igualdad
                self.disyuncion.remove(dis)
                self.disyuncion.append(dis)
                return
                
class RuleStringDecorator(object):
    def __init__(self,rule):
        self._mensaje = rule.toQuery()
        self._confianza = rule.confianza
    @property 
    def mensaje (self):
        return self._mensaje
    @property 
    def confianza(self):
        return self._confianza
    @mensaje.setter
    def mensaje(self,value):
        self._mensaje = value
    @confianza.setter
    def confianza(self,value):
        self._confianza = value
    def getString(self,confidence = True,positive_class='positive_class'):
        if confidence:
            return "if "+self.mensaje+ " then confidence = "+str(self.confianza)
        else:
            return "if "+self.mensaje+" then is a '" + positive_class+"'"
    
class ListaOrdenada(object):
    def __init__(self,lista=None):
        if lista is  None:
            self.lista = list()
        else:
            self.lista = lista
    @property 
    def lista(self):
        return self._lista
    @lista.setter
    def lista(self,value):
        self._lista = value
    def indexOf(self,item):
        i = 0
        while (i<len(self.lista)):
            if self.lista[i]==item:
                return i
            i = i +1
        return -1

    def isNext(self,item,item2,close=True):
        indice = self.indexOf(item)
        i = indice + 1
        if close==True:
            return (i<len(self.lista)) and (self.lista[i]==item2)
        else:
            while i < len(self.lista):
                if self.lista[i]==item2:
                    return True
                i = i +1
            return False

    

    def returnNext(self,item):
        indice = self.indexOf(item)
        i = indice + 1
        if i < len(self.lista):
            return self.lista[i]
        else:
            return None


    def extend(self,lista):
        self.lista.extend(lista)
       
    def append(self,item):
            self.lista.append(item)     
            
    def remove(self,item):
        self.lista.remove(item)
        
    def pop (self):
        return self.lista.pop()

    
class EqualRuleSet(object):
    def __init__(self):
        self.listado=ListaOrdenada()
        self.ultima_columna_comun_izda=''
    @property 
    def listado(self):
        return self._listado
    @property
    def ultima_columna_comun_izda(self):
        return self._ultima_columna_comun_izda
    @ultima_columna_comun_izda.setter
    def ultima_columna_comun_izda(self,value):
        self._ultima_columna_comun_izda=value
    @listado.setter
    def listado(self,value):
        self._listado = value

class RuleSet(object):
    def __init__(self):
        self._contador = 0
        self._dictionary = dict()
        self._rule_dictionary=dict()
        self._pds_original=None
        self._target = 'target'
        self._pds=None
        self._atributos = list()
    @property 
    def atributos (self):
        return self._atributos
    
    @property 
    def pds_original(self):
        return copy.deepcopy(self._pds_original)
    @property 
    def pds(self):
        return copy.deepcopy(self._pds)
    @property 
    def target(self):
        return self._target
    @property 
    def dictionary(self):
        return self._dictionary
    @property 
    def rule_dictionary(self):
        return self._rule_dictionary
    @property
    def contador(self):
        return self._contador
    
    @contador.setter
    def contador(self,val):
        self._contador = val
    @pds_original.setter
    def pds_original(self, value):
        self._pds_original = copy.deepcopy(value)
    @pds.setter
    def pds(self, value):
        self._pds = copy.deepcopy(value)
    
    @target.setter
    def target(self, value):
        self._target = value 
    @dictionary.setter
    def dictionary(self,value):
        self._dictionary = value
    @atributos.setter
    def atributos (self,value):
        self._atributos = value
    @rule_dictionary.setter
    def rule_dictionary(self,value):
        self._rule_dictionary = value    
        
    def reshapeDeletingRows(self,eliminadas):
        self.pds = self.pds.iloc[self.pds.index.isin(eliminadas)==False,:]
        return copy.deepcopy(self.pds)
    
    def reshapePdsIncludeByIndex(self,indexColumns):
        self.pds = self.pds.iloc[:,indexColumns]
        
    def reshapePdsIncludeByName(self,columns):
        #columns.append(self.target)
        self.pds = self.pds.loc[:,columns]
    
    def getColumnsNotExcluded(self,excluir):
        columnas = list(self.pds.columns)
        excluir.append(self.target)
        return self.list_diff(columnas,excluir)
    
    def setTarget(self,target):
        self.target=target
        
    def getPdsCopy(self,original=True):
        if original:
            return copy.deepcopy(self.pds_original)
        else:
            return copy.deepcopy(self.pds)
    
    def addRule(self,regla):
        antecedentes = regla.getAntecedentes()
        antecedentes_strings = "-".join(map(str, antecedentes))
        for antecedente in antecedentes:
            if antecedente not in self.atributos:
                self.atributos.append(antecedente)
        
        self.dictionary.update({self.contador:regla})
        self.contador = self.contador + 1
        self.rule_dictionary[antecedentes_strings]=self.contador
    
    def devolverReglasConMismoAntecedente(self,key):
        lista = list()
        visitados = list()
        print('diccionary')
        print(self.dictionary)
        regla1 = self.dictionary.get(key)
        claves = self.dictionary.keys()
        visitados.append(regla1.toString())
        visits = list()
        visits.append(key)
        #print('reglas con mismos antecedentes que '+regla1.toString()+' key: '+str(key))
        antecedentes1 = self.dictionary.get(key).getAntecedentes()
        antecedentes1.sort()
        lista.append(regla1)
        updated = False
        for key2 in claves:
            regla2 = self.dictionary.get(key2)
            if (regla1.toString() != regla2.toString()):
                antecedentes2 = regla2.getAntecedentes()
                antecedentes2.sort()

                if antecedentes1 != antecedentes2:
                    continue
                else:
                    if (regla2.toString() not in visitados):
                      #  print('se actualizado '+regla2.toString()+' key2: '+str(key2))
                        lista.append(regla2)
                        visitados.append(regla2.toString())
                        visits.append(key2)

                        #print('visitados '+' || '.join( visitados )) #no parece q lo haga bien, habrá q reiniciar

                        updated=True
        if updated:
            return lista,visits
        else:
            return None,visits
   
    
    def devolverAtributosQueVarian(self, lista_reglas): #está devolviendo todos ... if book = 1 and book = 8 book = 1 or book = 8, pero si tiene más de un antecedente, entonces uno se tiene que quedar fijo
        
        lista = list()
        i = 0
        j = 1
        for i in range(0,len(lista_reglas)):
            r1 = lista_reglas[i]
            for j in range(1,len(lista_reglas)):
                r2 = lista_reglas[j]
                if r1 == r2:
                    continue
                else:
                    if len(r1.getAntecedentes())==1:
                        antecedente = r1.getAntecedentes()[0] #los dos listados de reglas tienen los mismos antecedentes
                        valor1 = r1.getIgualdad(antecedente).getvalor()
                        valor2 = r2.getIgualdad(antecedente).getvalor()
                        if valor1 != valor2:
                            minilista = list()
                            minilista.append(antecedente)
                            lista.append(minilista)
                    else:
                        for antecedente in r1.getAntecedentes()[0]: #los dos listados de reglas tienen los mismos antecedentes
                            valor1 = r1.getIgualdad(antecedente).getvalor()
                            valor2 = r2.getIgualdad(antecedente).getvalor()
                            if valor1 != valor2:
                                minilista = list()
                                lista.append(antecedente)
        return lista
    
        
    def pos_index(self,pds=None,original=False):
        if pds is None and original == False:
            return self.pds.query(self.target+'==1').index
        elif pds is not None:
            return pds.query(self.target+'==1').index
        else:
            return self.pds_original.query(self.target+'==1').index
      
    def num_target(self,pds=None,tipo=1,original=True):
        if pds is None and original == False:
                return self.pds.query(self.target+'=='+str(tipo)).shape[0]
        elif pds is not None:
            return pds.query(self.target+'=='+str(tipo)).shape[0]
        else:
            return self.pds_original.query(self.target+'=='+str(tipo)).shape[0]
        
    def list_diff(self,list1, list2,include=False):
       
        if not include:
            out = [item for item in list1 if not item in list2]
        else:
            out = [item for item in list1 if item in list2]
            out.append(self.target)
        return out
    
    def getRows2Remove(self,rule):
        query = ''
        for key in self.dictionary.keys():
            rule = self.dictionary.get(key)
            query = query+'('+rule.toQuery()+') or '
        query = query[:-3]
        print('ruleset query' + query)
        indice = self.pds.query(query,engine='python').index
        return indice



    def devuelveAtributoConMaxGanancia(self,excluir):
        atributo = ''
        max_info = 0
        print('\t\t Buscando el atributo con ganancia maxima...')

        columnas = list (self.pds.columns)
        X_vec = self.pds.loc[:,self.getColumnsNotExcluded(excluir)]
        Y = self.pds.loc[:,self.target]
        mutual_info = mutual_info_classif(X_vec, Y, discrete_features=True)
        rpd = pd.DataFrame(zip(mutual_info,self.getColumnsNotExcluded(excluir))
                   ,columns=['val','att'])
        atributo= rpd[rpd['val']==rpd.val.max()]['att'].values[0]
        
        print('atributo con max ganancia: '+atributo)
        return atributo

    
    def generarCandidatos (self):
        candidatos = ColeccionCandidatos ()
        for columna in list(self.pds.columns): 
            if columna == self.target:
                continue
            values = self.pds.loc[:,columna].unique()
            for valor in values:
                candidatos.append(Igualdad(columna,valor))   

        candidatos.sincronizar()
        return candidatos

    def generarIgualdad(self,excluir,query,min_rel):

        #print('\n|1.| Generando igualdad: ')
        candidatos = self.generarCandidatos()
        terminado = False
        while not terminado:

            atributo = self.devuelveAtributoConMaxGanancia(excluir)
        #    print('\n|2.|atributo con máxima ganancia respecto a la target en el dataset que le toca: '+atributo)
                #indice = pds.columns.get_loc(atributo)
            claves = candidatos.getCandidatosDeVariable(atributo,min_rel) #pasarlo

        #    print('\n|3.| Evaluando las distintas claves de : '+atributo)

            min_relacion = 1000000000
            max_positivos = 0
            relacion=0

            claveusar = ''
            actualizado = False
            maximoEspecifico = False
            for clave in claves:
                if (query is None):
                    consultas = clave
                    print('\t\t |3.1| evaluando clave '+clave) #esto hay q tocarlo! es clave más la clave anterior
                    dataf = self.pds.query(consultas)
                else:
                    consultas = query + ' and ' + clave
                    print('\t\t |3.1| evaluando clave '+consultas) #esto hay q tocarlo! es clave más la clave anterior
                    dataf = self.pds.query(consultas)

                if dataf.shape[0]==0:
                    excluir.append(atributo)
                    continue

                positivos = dataf.target.sum() ## ojo revisar esto!!!!
                negativos = dataf.target.value_counts().get(0)
                rows_elim  = dataf.index
                
                if negativos is None:
                    relacion = 0
                    negativos = 0
                else:
                    relacion = negativos/positivos

                if  positivos is None  or  negativos>positivos:
                    print('\t\t\tpos: '+str(positivos)+' neg:'+str(negativos)+'-volviendo a buscar')
                    continue

                else:
                    if relacion<min_relacion or positivos>1.05*max_positivos:
                        min_relacion = relacion
                        max_positivos = positivos
                        claveusar = clave
                        if relacion == 0:
                            maximoEspecifico = True
                            break

            if claveusar != '':
                valor = claveusar.split("==")[1]
                igualdad = Igualdad(atributo,valor)
                #print (' Se genero la igualdad '+igualdad.tostring())
                terminado = True
            else:
                print ('\!!! El atributo '+atributo+' no ofrecio ninguna clave válida, volviendo a buscar atributo')
                excluir.append(atributo)
                result =  all(elem in excluir  for elem in self.pds.columns)
                if result == True:
                    print ('No se han encontrado atributos que generen una regla')
                    return excluir,None, None, None,None,None
                continue

        print('Igualdad generada: '+igualdad.toString()+'POSITIVOS '+str(positivos)+'NEGATIVOS: '+str(negativos))
        return excluir,igualdad, (1-relacion), rows_elim,maximoEspecifico,positivos


    def toDf(self,listado_reglas,columnas):
        listados_valores = list()
        for regla in listado_reglas:
            lista=list()
            for antecedente in regla.antecedente:
                lista.append(antecedente.valor)
            lista.append(regla.confianza)
            lista.append(regla.consecuente)
            listados_valores.append(lista)
        oldcol = copy.deepcopy(columnas)
        columnas.append('confianza')
        columnas.append('consecuente')
        df = pd.DataFrame(data=listados_valores,columns=columnas)
        df = df.sort_values(by=oldcol,axis=0)
        return df

    def toRuleList(self,df):

        sublistado_visit = list()
        for i, row in df.iterrows():
            rule = Rule(1000,10000)
            for column in list(df.columns):
                if column!='confianza' and column!='consecuente':
                    rule.append(Igualdad(column,row[column]))
            rule.confianza=row['confianza']
            rule.consecuente=row['consecuente']
            sublistado_visit.append(rule)
        return sublistado_visit

    def devolverGruposPorPrimerValorComun(self,lista_reglas):
        grupos = list()
        cont = 0
        minilista = list()
        lastvalor = lista_reglas[cont].antecedente[0].valor
        print('lastvalor '+str(lastvalor))
        minilista.append(lista_reglas[cont])
        new = False
        second = False
        for cont in range (1,len(lista_reglas)):
            if (lista_reglas[cont].antecedente[0].valor == lastvalor):
                minilista.append(lista_reglas[cont])
                second = True
                new=False
            else:
                new=True ##aqui!!!
                second = False
                grupos.append(minilista)
                print(len(grupos))
                lastvalor = lista_reglas[cont].antecedente[0].valor
                minilista = list()
                minilista.append(lista_reglas[cont])
                
        if (not new) or (new and not second):
            grupos.append(minilista)
        return grupos
   
    def devolverIgualdadesComunes(self,eqrs,antecedentes):
        listado_ands = list()
        listado_ors = set()
        variables_or = set()
        for variable in antecedentes: ## aqui solo me esta metiendo los rangos en or, no es asi
            cont = 0
            valor = eqrs.listado.lista[0].getIgualdad(variable).valor
            igualdad_original = Igualdad(variable,valor)
            encontrado = True
            for i in range(0,len(eqrs.listado.lista)):
                regla = eqrs.listado.lista[i]
                if regla.getIgualdad(variable).valor != valor:
                    encontrado = False
                    print('adding '+variable+':'+str(regla.getIgualdad(variable)))
                    listado_ors.add(regla.getIgualdad(variable))
                    variables_or.add(variable)
            if encontrado:
                listado_ands.append(igualdad_original)
            else:
                variables_or.add(variable)
                listado_ors.add(igualdad_original)
        return listado_ands,listado_ors,variables_or
    
    def devolverReglasConMaximoComun(self,sublistado_por_visitar,listado_variables):
        listaeqs = list()
        original = copy.deepcopy(sublistado_por_visitar)
        if (len(listado_variables.lista)<=2):
            eqrs = EqualRuleSet()
            for i in range (0,len(sublistado_por_visitar)):
                regla_actual = sublistado_por_visitar[i]
                eqrs.listado.append(regla_actual)
                eqrs.ultima_columna_comun_izda=listado_variables.lista[0] #cogemos la primera
            listaeqs.append(eqrs)
            return listaeqs
        else:   
            while len(sublistado_por_visitar)>0: # recorremos las reglas a visitar
                eqrs = EqualRuleSet()
                regla_actual = sublistado_por_visitar.pop()
                candidatas = list()
                eqrs.listado.append(regla_actual)
                eqrs.ultima_columna_comun_izda=listado_variables.lista[1] #cogemos la primera
                print('Nos quedan {0} reglas'.format(len(sublistado_por_visitar)))
                ##jugar con returnnext 
                i = 0
                print ('*****Vamos a analizar la regla: '+regla_actual.toString()+'******')
                max_matches = 1
                contador_matches = 1
                while i <len(sublistado_por_visitar):         ## recorremos el resto de reglas  
                    regla_siguiente = sublistado_por_visitar[i]
                    print ('\t\t+++ comparamos con *********************'+regla_siguiente.toString())
                    visitado = False

                    for variable in listado_variables.lista[1:]:
                        print('VARIABLE :'+variable)
                        if regla_actual.getIgualdad(variable).valor == regla_siguiente.getIgualdad(variable).valor:
                            contador_matches = contador_matches + 1

                        print('\t\t\tanalizando variable '+variable)

                    i = i+1

                    if (contador_matches>=max_matches) and (self.existeReglaConMasMatches(original, listado_variables.lista[1:],contador_matches,regla_actual))==False:
                        candidatas.clear()
                        candidatas.append(regla_siguiente)
                        max_matches=contador_matches
                print ('***********************hemos terminado de analizar '+regla_actual.toString()+'*************************************')    
                for regla in candidatas:
                    print('eliminando de candidatas '+regla.toString())
                    if regla in sublistado_por_visitar:
                        sublistado_por_visitar.remove(regla)
                ## ver que lo hace bie
                eqrs.listado.extend(candidatas)
                listaeqs.append(eqrs)
               # contadorglobal = contadorglobal + 1
               # if contadorglobal>10:
                #    break

        if len(sublistado_por_visitar)==1:
            print('hacer otro equal rule set de tamaño 1')
            eqrs = EqualRuleSet()
            eqrs.ultima_columna_comun_izda=listado_variables.lista[0]
            eqrs.listado.extend(sublistado_por_visitar[0])
            listaeqs.append(eqrs)
        return listaeqs

    def existeReglaConMasMatches(self,sublistado_por_visitar,listado_variables,contador_matches,regla):
        lista = list()
        for i in range(0,len(sublistado_por_visitar)):
            regla_siguiente = sublistado_por_visitar[i]
            cont = 1

            print ('\t\t+++ VAMOS A VER SI *********************'+regla_siguiente.toString()+'**********++ SUPERA EL CONTADOR '+str(contador_matches))

            for variable in listado_variables[1:]:
                if regla.getIgualdad(variable).valor == regla.getIgualdad(variable).valor:
                    cont = cont + 1

            print('Ha tenido '+str(cont))

            if cont > contador_matches:
                print('return true!')
                return True
        return False
    
    def modificarReglaConIgualdadesDeAntecedenteConRangos(self,eqrs,antecedentes,maxIgualdad):
        listado_reglas = list()

        lista_ands, lista_ors, variables_or = self.devolverIgualdadesComunes(eqrs,antecedentes)

        regla = Rule(maxIgualdad,maxIgualdad) #interval pulirselo

        for igualdad in lista_ands:
            regla.append(igualdad)

        # Ahora habrá que hacer disyunciones 

        for variable in variables_or:
            listado_valores = list()
            #xa cada variable, cogemos sus valores
            for igualdad in lista_ors:
                if igualdad.variable == variable:
                    listado_valores.append(igualdad.valor)

            listado_valores = list(map(int, listado_valores))
            listado_valores.sort()

            print("LISTADO VALORES")
            print(*listado_valores)
            listados = [list(xxx) for xxx in mit.consecutive_groups(listado_valores)]
            print(*listados)
            for lista in listados:
                if len(lista)==1:
                    igualdad = Igualdad(variable,lista[0])
                    print('LISTADO DE VALORES LONGITUD 1_disyuncion de long 1 '+igualdad.toString())

                    print ('añadiendo  de len 1: '+igualdad.toString())
                    dis = Disyuncion(igualdad)
                    regla.append(dis,esDisyuncion=True)
                else:
                    print('len lista>1')
                    igualdad1 = Igualdad(variable,lista[0])
                    igualdad1.cambiaroperador(True)
                    igualdad2 = Igualdad(variable,lista[len(lista)-1])
                    igualdad2.cambiaroperador(False)
                    print('añadiendo {0} y  {1}'.format(igualdad1.toString(),igualdad2.toString()))
                    dis = Disyuncion(igualdad1,igualdad2)
                    regla.append(dis,esDisyuncion=True)

        print ('la regla queda así: ')
        print('antecedentes')
        for igualdad in regla.antecedente:
            print(igualdad.toString())
        print('disyunciones')
        conti = 1
        for dis in regla.disyuncion:
            print(str(conti)+'-'+dis.toString())
            conti
        return regla
    
    def consolidar(self):
        newdict = dict()
        contador = 0
        actualizado=False
        contador=0
        visitados = list()
        maxpos = self.num_target(original=True)

        for key in self.dictionary.keys():
            if key not in visitados:
                visitados.append(key) ## revisar????
                print(key)
                listado_reglas,visits = self.devolverReglasConMismoAntecedente(key)
                visitados.extend(visits)
                
                print('visitados q no deben volver :'+ ' -- '.join(str(x) for x in visitados))
                if listado_reglas is None:
                    newdict.update({contador:self.dictionary.get(key)})
                    print('no he encontrado regla con mismo antecedente - '+str(key))
                    contador = contador + 1
                    continue
                else:
                    print ('listado de reglas con mismo antecedente:')
                    listado = copy.deepcopy(listado_reglas)
                    for regla in listado:
                        print(regla.toString())
                    print("=================================================================================")
                    listado_variables = ListaOrdenada()
                    
                    for igualdad in listado[0].antecedente:
                        listado_variables.append(igualdad.variable)
                    
                    print('listado_vari::')    
                    print(*listado_variables.lista)   
                    df = self.toDf(copy.deepcopy(listado),copy.deepcopy(listado_variables.lista))
                    print(df)
                    listado = self.toRuleList(df)
                    for regla in listado:
                        print(regla.toString())
                    
                    if len(listado_variables.lista)>1:

                        grupos = self.devolverGruposPorPrimerValorComun(listado)
                    else: #si no hacemos esto, no consolida reglas tipo if book = 8 or book = 9 or book = 10...
                        grupos = list()
                        grupos.append(listado)
                    print('Existen {0} grupos para ser añadidos con el primer valor comun'.format(len(grupos)))
                    for grupo in grupos:
                        
                        listaeqs = self.devolverReglasConMaximoComun(grupo,listado_variables)
                        for eqrs in listaeqs:
                            print('*********************************************')
                            print('last '+str(eqrs.ultima_columna_comun_izda))
                            for reglitas in eqrs.listado.lista:
                                print(reglitas.toString())

                            print('**********************************************')
                        for eqs in listaeqs:
                            
                            regla = self.modificarReglaConIgualdadesDeAntecedenteConRangos(eqs,listado_variables.lista,10000)
                            
                            print('la regla q se genera tiene esta query '+regla.toQuery())
                            subdf = self.pds_original.query(regla.toQuery())
                            negativos = subdf[subdf.target==0].shape[0]
                            positivos = subdf[subdf.target==1].shape[0]

                            relacion = negativos / float(positivos)
                            confianza = positivos/float(maxpos)
                            regla.finish(relacion,confianza)
                            newdict.update({contador:regla})
                            contador = contador + 1
        self.dictionary = newdict
        
        
        return newdict ##luego el algoritmo llamará a pds para simplificar y obtner el nuevo soporte y confianza
            #remove lis
    


class Explainer(object):
    def __init__(self,rs, min_rule_length,max_rule_length,max_rules,max_repeat_term=1000,vocabulary=None):
        self.rs = rs
        self.min_rule_length = min_rule_length
        self.max_rule_length = max_rule_length
        self.max_rules = max_rules
        self.max_repeat_term = max_repeat_term
        self.vocabulary = vocabulary
        
    def explain (self,interval=10,min_rel=5):
        max_pos = self.rs.num_target(original=True,tipo=1)
        
        pos = self.rs.pos_index(original=True)
        #pds_original = pds.copy()
        if self.vocabulary is not None:
            columnas = self.rs.list_diff(self.vocabulary,list(self.rs.pds.columns),include=True) ##aqui            
            self.rs.reshapePdsIncludeByName(columnas)
 
        pdsf = self.rs.getPdsCopy(False)
      
        cont = 1
        reglas = 1
        igualdades = 1
        nextIgualdad=True
        eliminadas=list()
        excluidos = list()
        usados = list() ## Este diccionario guardará por cada término el número de reglas que esta
        counter_usados = None
        print('*****************************Comienza la genreación del ruleset************************************************')
        while (len(pos)>0 and reglas <= self.max_rules ):
            
            regla = Rule(self.max_rule_length,interval) #set de Iguadad
            
            if counter_usados is not None:
                elementos = counter_usados.elements()
                for elemento in elementos:
                    valor = counter_usados.get(elemento)
                    if valor>self.max_repeat_term and elemento not in excluidos:
                        print (elemento+' se excluye definitivamente tras '+str(valor)+ ' veces')
                        excluidos.append(elemento)
            #1ª regla
            excluir = list()
            excluir.append(self.rs.target)
            query = None
            while (nextIgualdad==True):
                for element in list(excluidos):
                    if element not in excluir:
                        excluir.append(element)
                        
                excluir,igualdad, relacion, rows_elim, maximoEspecifico, positivos = self.rs.generarIgualdad (excluir,query,min_rel)
                if igualdad is None:
                    print ('No se han encontrado más igualdades con las que se pueda continuar la regla')
                    nextIgualdad = False
                else:    
                    print('Igualdad de la regla '+ igualdad.toString())
                    regla.append(igualdad)
                    if maximoEspecifico:
                        nextIgualdad = False
                        if regla.len()<self.min_rule_length:
                            raise Exception ('Se ha alcanzado un maximo especifico con una longitud inferior al de la regla')
                    excluir = regla.getAntecedentes()
                    query = regla.toQuery()
                    ##atributo con maxima ganancia
                    if (regla.len()>=self.max_rule_length):
                        nextIgualdad = False
                        continue


            ##qui
            subdf = self.rs.pds_original.query(regla.toQuery())
            negativos = subdf[subdf.target==0].shape[0]
            positivos = subdf[subdf.target==1].shape[0]
                    
            relacion = negativos / float(positivos)
            confianza = positivos/float(max_pos)
            regla.finish(relacion, confianza)
            antecedentes = regla.getAntecedentes()
            usados.extend(antecedentes)
            print('-----------------> COUNTER USADOS')
            counter_usados =  Counter(usados)
            print(counter_usados)
            print ('|2 - Regla generada: |{0} '.format(regla.toString()))
            self.rs.addRule(regla)
            #print ('\t |2.1 -Eliminando | {0} filas'.format(len(rows_elim)))
            eliminadas = self.rs.getRows2Remove(regla)
            
            pdsf = self.rs.reshapeDeletingRows(eliminadas)
             ##pparece q esto no lo hace bien revisar mañana!
            #print(pdsf.shape)
            #print('ACTUALIZANDO REGLAS '.format(reglas))
            reglas = reglas + 1
            maximoEspecifico=False
            pos = self.rs.pos_index(pdsf)
            print ('\t |2.1 -Quedan | {0} positivos, generadas {1} reglas'.format(len(pos),(reglas)))
            nextIgualdad=True

        return self.rs,pdsf
    