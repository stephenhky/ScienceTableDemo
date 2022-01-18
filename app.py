
import os
import json
from glob import glob
import asyncio

import streamlit as st
import requests
import pandas as pd


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
    df = df.sort_values(by='similarity', ascending=False)
    return df

# Presentation details
st.header('Science Similarity Detection')
col1, col2 = st.columns((2, 1))
col1.text('Goal: Automate the process of identifying and withdrawing duplicated or overlapping grant applications.')
col1.text('Achievement and Impact:')
col1.text('- Reduces ~95% of the workload.')
col1.text('- Processes 18k-23k~ grant applications bi-monthly.')
col1.text('- Manually verified 99.9% accuracy.')
col1.text('- Picks up similar sciences missed by human review.')
col2.image('histscisim.png')

# demonstration
st.header('Demonstration')
st.write('Disclaimer: This is a demonstration. The models used are of public domain, and are not trained with any private or sensitive data such as PII or PHI.')

demotext = 'NIH funds a lot of great science projects.'
text = st.text_area('Document', demotext)

df = asyncio.run(getting_result_df(text))
st.dataframe(df)
