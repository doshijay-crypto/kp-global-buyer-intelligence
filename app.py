import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

BASE=Path(__file__).parent
DATA=BASE/'data'/'importers.csv'

st.set_page_config(page_title='KP Global Buyer Intelligence',page_icon='🌍',layout='wide')

if 'saved' not in st.session_state: st.session_state.saved=[]

def load():
    return pd.read_csv(DATA)

def ai_intent(q):
    ql=q.lower()
    product='Dehydrated Onion/Garlic'
    if 'garlic' in ql and 'onion' not in ql: product='Dehydrated Garlic'
    if 'onion' in ql and 'garlic' not in ql: product='Dehydrated Onion'
    country='Any country'
    countries=sorted(load()['Country'].dropna().unique())
    for c in countries:
        if c.lower() in ql: country=c
    return product,country

st.title('🌍 KP Global Buyer Intelligence')
st.caption('AI-powered export buyer research workspace • KP International')

t1,t2,t3,t4,t5=st.tabs(['🤖 AI Search','🌎 Global Importers','🏢 Company Intelligence','⭐ Saved Buyers','⚙️ Data Sources'])

with t1:
    st.subheader('🤖 AI Search')
    q=st.text_area('Ask your buyer-research question',placeholder='USA માં Indiaમાંથી dehydrated onion import કરતા regular buyers શોધો',height=100)
    if st.button('🔎 Run AI Search',type='primary',use_container_width=True):
        if not q.strip(): st.warning('Please enter a search question.')
        else:
            df=load(); product,country=ai_intent(q)
            if country!='Any country': df=df[df.Country.str.lower()==country.lower()]
            if product=='Dehydrated Onion': df=df[df.Product.str.contains('Onion',case=False,na=False)]
            elif product=='Dehydrated Garlic': df=df[df.Product.str.contains('Garlic',case=False,na=False)]
            if 'regular' in q.lower() or 'recurring' in q.lower(): df=df[df.RegularImporter.eq('Yes')]
            st.success(f'Interpreted intent: {product} • {country}')
            st.dataframe(df,use_container_width=True,hide_index=True)
            st.caption('AI Search in this build uses the structured importer index. Live web/trade connectors can be added with licensed/public APIs.')
    st.info('Example: “Find regular dehydrated onion buyers in USA that source from India.”')

with t2:
    st.subheader('🌎 Global Dehydrated Onion & Garlic Importers')
    df=load()
    c1,c2,c3,c4=st.columns(4)
    country=c1.selectbox('Country',['All']+sorted(df.Country.unique()))
    product=c2.selectbox('Product',['All']+sorted(df.Product.unique()))
    regular=c3.selectbox('Regular importer',['All','Yes','No'])
    confidence=c4.selectbox('Confidence',['All']+sorted(df.Confidence.unique()))
    q2=st.text_input('Search company / supplier / city / source')
    if country!='All': df=df[df.Country.eq(country)]
    if product!='All': df=df[df.Product.eq(product)]
    if regular!='All': df=df[df.RegularImporter.eq(regular)]
    if confidence!='All': df=df[df.Confidence.eq(confidence)]
    if q2: df=df[df.astype(str).apply(lambda x:x.str.contains(q2,case=False,na=False)).any(axis=1)]
    st.metric('Importer records',len(df))
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button('⬇️ Export CSV',df.to_csv(index=False),'kp_importers.csv','text/csv')

with t3:
    st.subheader('🏢 Company Intelligence')
    name=st.text_input('Company name / domain')
    df=load()
    if name:
        m=df[df.Company.str.contains(name,case=False,na=False)]
        if len(m):
            r=m.iloc[0]
            a,b,c=st.columns(3)
            a.metric('Company',r.Company); b.metric('Country',r.Country); c.metric('Confidence',r.Confidence)
            st.write('**Website:**',r.Website or 'Not found')
            st.write('**Products:**',r.Product)
            st.write('**Forms:**',r.Form)
            st.write('**Import frequency:**',r.ImportFrequency)
            st.write('**Supplier/origin:**',r.Supplier, '/', r.Origin)
            st.write('**Last shipment/activity:**',r.LastShipment)
            st.write('**Source:**',r.Source)
            if st.button('⭐ Save Buyer'): 
                if r.Company not in st.session_state.saved: st.session_state.saved.append(r.Company)
                st.success('Saved to Buyers / CRM')
        else: st.warning('No matching indexed company found.')
    else: st.info('Enter a company name to view its indexed intelligence profile.')

with t4:
    st.subheader('⭐ Saved Buyers / CRM')
    df=load(); saved=df[df.Company.isin(st.session_state.saved)]
    if saved.empty: st.info('No buyers saved yet.')
    else:
        st.dataframe(saved,use_container_width=True,hide_index=True)
        st.download_button('⬇️ Export saved buyers',saved.to_csv(index=False),'saved_buyers.csv','text/csv')

with t5:
    st.subheader('⚙️ Data Sources & Verification')
    st.markdown('''
**Production source layers**
- Public company websites and registries
- Permitted web search and public business pages
- Licensed trade/shipment data providers where the user has access
- Public professional/business contact information

**Evidence rule:** each important field should retain source, last-verified date and confidence.
The system should never bypass logins, paywalls, robots restrictions, or source terms.

**Coverage rule:** no single database contains every importer worldwide. The production system merges permitted/licensed sources and preserves provenance.
''')
    st.write('Build timestamp:',datetime.now().strftime('%Y-%m-%d %H:%M'))
