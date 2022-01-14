
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
    item = json.loads(docpath)
    similarity = compute_sentence_similarity(text, item['text'])
    resultitem = {'filename': os.path.basename(docpath), 'title': item['title'], 'similarity': similarity}
    return resultitem


async def getting_result_table(text):
    resultitems = await asyncio.gather(*[
        compute_sentence_similarity(text, docpath)
        for docpath in glob(os.path.join('data', 's*.json'))
    ])
    df = pd.DataFrame.from_records(resultitems)
    df = df.sort_values(by='similarity', ascending=False)
    return df



st.text('Science Similarity')
st.write('Disclaimer: This is a demonstration. The models used are of public domain, and are not trained with any private or sensitive data such as PII or PHI.')

demotext = 'NIH funds a lot of great science projects.'
text = st.text_area('Document', demotext)

df = asyncio.run(getting_result_table(text))
st.dataframe(df)
