import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import re
import string
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

@st.cache
def get_data():
		return pd.read_csv("data.csv" ,sep='\t')
def get_databotsol():
	return pd.read_csv("botsolready.csv")

def split_query(q):
	qlist=q.lower().split()
	qlist="|".join(qlist)
	return qlist
	
def jaccard_similarity(list1, list2):
	s1 = set(list1)
	s2 = set(list2)
	return float(len(s1.intersection(s2)) / len(s1.union(s2)))

datahalal=get_data()
databotsol = get_databotsol()

def get_response(q):
	query=split_query(q)
	mask = datahalal[datahalal['produk'].str.contains(query) | datahalal['perusahaan'].str.contains(query,case=False)]
	mask=mask.reset_index()
	similarity=np.zeros((len(mask)))
	numsort=mask.size
	if (numsort > 20):
		numsort=20
	for ind in mask.index:
		line=mask['produk'][ind]+' '+mask['perusahaan'][ind]
		if (type(line)==str):
			qlist=q.lower().split()
			linelist=line.lower().split()
			similarity[ind]=jaccard_similarity(qlist,linelist)
	idx=(-similarity).argsort()[:numsort]
	data = []
	for y in idx:
				data.append([mask['produk'][y], mask['perusahaan'][y], mask['sertifikat'][y],mask['tanggal'][y]])
	
	return(data)

def get_coordinates(opsi):
	#botsol_data = get_databotsol()

	mapit = folium.Map(location=[-7.277674, 112.694906], zoom_start=12)
	for index, row in databotsol.iterrows():
		folium.Marker(location=[row['Latitude'], row['Longitude']], popup=row['Name'], tooltip=row['Name']).add_to(mapit)
	return mapit
	

			
st.title("Surabaya Halal Directory")

# search restoran halal


st.title("Peta Restoran dan Warung Di Surabaya")

select_data = st.radio(
    "Pilih Data yang ingin ditampilkan",
    ("Semua", "Halal","BelumHalal")
)

# peta folium restoran
st_data = st_folium(get_coordinates(select_data), width = 825)

cari = st.text_input("Cari Produk/Restaurant Halal di Jawa Timur", "kopi susu")
cariflag=False  
mydata =[]
if(st.button('Submit')):
	result = cari.title()
	if(result):
		st.write("Hasil Pencarian "+result)
		mydata=get_response(result)
		hasil = pd.DataFrame(mydata, columns=['produk', 'perusahaan','sertifikat','tanggal'])
		st.table(hasil)
		cariflag=True
	else:
		st.error("Masukkan input ya")


# selectbox tabel restoran tiap kecamatan
col1, col2 = st.columns(2)

with col1:
    st.header("Data Restoran tiap Kecamatan")
    restokec = st.slider("Jumlah Restoran", 5, 20, step=5)
    select = st.selectbox('Pilih Kecamatan',databotsol['Kecamatan'].unique())

with col2:
    kec = databotsol[databotsol['Kecamatan'] == select][['Name','Address','Rating']].sort_values("Rating",ascending=False).head(restokec)
    st.table(kec)

# bar plot kecamatan
st.header("Barplot Jumlah Restoran tiap Kecamatan")
kec2 = databotsol[['Name','Kecamatan']].groupby("Kecamatan").count().reset_index().sort_values(by=['Name'],ascending=True)
kec2.rename(columns = {'Name':'Jumlah'}, inplace = True)
figkec = px.bar(kec2, x='Jumlah', y='Kecamatan',orientation='h')
figkec.update_layout(
    width=900,
    height=1200
)
st.plotly_chart(figkec)

# bar plot kategori
st.header("Barplot Jumlah Restoran per Kategori")
kateg = databotsol[['Name','kategori']].groupby("kategori").count().reset_index().sort_values(by=['Name'],ascending=True)
kateg.rename(columns = {'Name':'Jumlah','kategori':'Kategori'}, inplace = True)
figkateg = px.bar(kateg, x='Kategori', y='Jumlah')
figkateg.update_layout(
    width=500,
    height=450,
)
st.plotly_chart(figkateg)

# FOOTER
st.header("UMKM Binaan Pusat Kajian Halal ITS")
st.markdown("Kunjungi binaan halal ITS [disini](http://halal.its.ac.id/binaan) ")

st.header("Linked Open Data Halal")
st.markdown("Kunjungi Linked Open Data Halal ITS [disini](http://halal.addi.is.its.ac.id) ")

st.markdown("---")
st.markdown("**Awards**")
st.markdown("- [Best Graphistry app at Tigergraph Hackathon 2021](https://devpost.com/software/halal-food)")
st.markdown("- [Neo4J Graphie Award Winner 2020](https://neo4j.com/graphies/#panel1)")
st.markdown("- Best Paper at International Conference on Halal Innovation in Products and Services 2018")

st.header("Dipersembahkan oleh")
st.image("logo.png")
