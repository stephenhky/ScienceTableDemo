
import os
import json
from glob import glob
import asyncio

import streamlit as st
import requests
import pandas as pd


# wide screen
st.set_page_config(layout="wide")


def compute_sentence_similarity(text1, text2):
    url = "https://y6wrl4j6v7.execute-api.us-east-1.amazonaws.com/default/SentenceSimilarity"
    payload = json.dumps({'text1': text1, 'text2': text2})
    headers = {'Content-Type': 'application/json'}
    response = requests.request('GET', url, headers=headers, data=payload)
    similarity = json.loads(response.text).get('similarity')
    return similarity


async def compute_similarity_vs_onedoc(text, docpath):
    item = json.load(open(docpath, 'r'))
    similarity = compute_sentence_similarity(text, item['text'])
    resultitem = {'filename': os.path.basename(docpath), 'title': item['title'], 'similarity': similarity, 'text': item['text']}
    return resultitem


async def getting_result_df(text):
    resultitems = await asyncio.gather(*[
        compute_similarity_vs_onedoc(text, docpath)
        for docpath in glob(os.path.join('data', 's*.json'))
    ])
    df = pd.DataFrame.from_records(resultitems)
    df['distance'] = 1 - df['similarity']
    df = df.sort_values(by='similarity', ascending=False)
    return df


# Presentation details
st.header('Science Similarity Detection')


# demonstration
st.header('Demonstration')
st.write('Disclaimer: This is a demonstration. The models used are of public domain, and are not trained with any private or sensitive data such as PII or PHI.')


demotext = """Understanding flow and transport of bacteria in porous media is crucial to technologies such as bioremediation, 
biomineralization or enhanced oil recovery. Low and transport experiments performed in microfluidic chips containing randomly 
placed obstacles confirmed that the distributions of non-motile particles stays compact, 
whereas for the motile strains, the distributions are characterized by both significant retention 
as well as fast downstream motion. 
For motile bacteria, the detailed microscopic study of individual bacteria trajectories 
reveals two salient features, namely, the emergence of an active retention process triggered by motility, 
and enhancement of dispersion due to the exchange between fast flow channels and low flow regions 
in the vicinity of the solid grains. 
We propose a physical model based on a continuous time random walk approach. 
"""
text = st.text_area('Document', demotext)
if st.button('Find Similar Researches!'):
    df = asyncio.run(getting_result_df(text))
    st.dataframe(df[:10])
