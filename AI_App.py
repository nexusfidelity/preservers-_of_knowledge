import streamlit as st
import requests
import json
import pandas as pd
import numpy as np

#nltk initializers
# from nltk.sentiment import SentimentIntensityAnalyzer
# sia = SentimentIntensityAnalyzer()

# import gensim
# from gensim.utils import simple_preprocess
# from gensim.parsing.preprocessing import STOPWORDS
# from nltk.stem import WordNetLemmatizer, SnowballStemmer
# from nltk.stem.porter import *

# np.random.seed(2018)
# import nltk
# nltk.download('wordnet')

# import spacy
# import en_core_web_sm
# nlp = en_core_web_sm.load()
import texthero as hero
from texthero import preprocessing

st.set_page_config(
    page_title="Preservers of Knowledge",
    page_icon="🤖",
    layout = "wide",
    # layout="wide",
    initial_sidebar_state="expanded",
)

st.title('NASA space app challenge')

sidebar = st.sidebar.radio('App Navigation', ['General Info','Project Demo'])

if sidebar=='General Info':
    st.header('General Info')
if sidebar=='Project Demo':
    st.header('Project Demo')
    df = pd.DataFrame()
    topic=st.text_input('select abstract')
    response = requests.get("https://ntrs.nasa.gov/api/openapi/")
    parameters={#"abstract":"acid",
           "abstract":topic
           }
    response = requests.get("https://ntrs.nasa.gov/api/citations/search", params=parameters)
    x=response.json()
    
    for y in range(len(x['results'])):
        title = str(x['results'][y]['title'])
        abstract = str(x['results'][y]['abstract'])
        subject_category = str(x['results'][y]['subjectCategories'])
        downloadble = str(x['results'][0]['downloadsAvailable'])
        new_row = {'title':title,'abstract':abstract,'subject_category':subject_category,'is_downloadable':downloadble}
        df = df.append(new_row, ignore_index=True)
        
    #cleaning
    category_custom_pipeline = [preprocessing.remove_punctuation,
                                preprocessing.lowercase,
                                preprocessing.remove_whitespace
                               ]
    df['subject_category'] = hero.clean(df['subject_category'], category_custom_pipeline)
    
    custom_pipeline = [preprocessing.remove_stopwords,
                       preprocessing.remove_punctuation,
                       preprocessing.fillna,
                       preprocessing.lowercase,
                       preprocessing.remove_whitespace]
    df['abstract'] = hero.clean(df['abstract'], custom_pipeline)
    
    st.dataframe(df)
    
    narrow_by_category = pd.DataFrame()

    category_list = pd.Series(df['subject_category'].unique())
    options = st.multiselect('choose narrowed subject category',category_list,default=None)
    
    if options:
        for x in range(len(options)):
            narrow_by = df[df['subject_category']==options[x]]
            narrow_by_category = narrow_by_category.append(narrow_by)
        
    st.dataframe(narrow_by_category)
    
    options_named_entities = st.selectbox('choose named_entities in abstract',['PERSON', 'NORP', 'FAC', 'ORG','GPE','LOC','PRODUCT','EVENT','WORK_OF_ART','LAW','LANGUAGE','DATE','TIME','PERCENT','MONEY','QUANTITY','ORDINAL','CARDINAL'])
    
#    st.dataframe(narrow_by_category['abstract'])
    narrow_by_category['abstract_entities'] = hero.named_entities(narrow_by_category['abstract'])
    
    
    narrow_by_entities= pd.DataFrame()

    for x in range(len(narrow_by_category['abstract_entities'])):
        try:
            data = [item for item in narrow_by_category['abstract_entities'][x] if options_named_entities in item]
            dataformat = pd.DataFrame(data, columns=['Name', 'Label', 'starting character','ending character'])
            dataformat['index']=x
            narrow_by_entities = narrow_by_entities.append(dataformat)
        except KeyError:
            continue

    narrow_by_entities=narrow_by_entities[['index','Name','Label']]
    st.dataframe(narrow_by_entities)
    
    #visualization
    wordcloudfig = hero.wordcloud(df['abstract'])
    st.set_option('deprecation.showPyplotGlobalUse', False)
    col1, col2 = st.columns([3,1])
    col1.subheader('Word Cloud')
    col1.pyplot(wordcloudfig)
    col2.subheader('Top Words')
    col2.dataframe(hero.top_words(df['abstract']))