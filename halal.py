import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_agraph import agraph, Node, Edge, Config
from streamlit_folium import st_folium
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

@st.cache
def get_data():
		return pd.read_csv("data.csv" ,sep='\t')

def get_databotsol():
	databotsol = pd.read_csv("botsolxhalaladded.csv")
	dataabove80 = pd.read_csv("above_80.csv")
	datamerge = pd.concat([databotsol,dataabove80])
	return datamerge

def split_query(q):
	qlist=q.lower().split()
	qlist="|".join(qlist)
	return qlist
	
def jaccard_similarity(list1, list2):
	s1 = set(list1)
	s2 = set(list2)
	return float(len(s1.intersection(s2)) / len(s1.union(s2)))

datahalal = get_data()
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
	certified = databotsol.loc[~databotsol['No Sertifikat'].isnull()]
	uncertified = databotsol.loc[databotsol['No Sertifikat'].isnull()]
	mapit = folium.Map(location=[-7.277674, 112.694906], zoom_start=12)
	if opsi == 'Tersertifikasi Halal':
		for index, row in certified.iterrows():
			folium.Marker(
				location=[row['Latitude'], row['Longitude']],
				popup=row['Name'],
				tooltip=row['Name'],
				icon=folium.Icon(color="green")
				).add_to(mapit)
	elif opsi == 'Belum Tersertifikasi Halal':
		for index, row in uncertified.iterrows():
			folium.Marker(
				location=[row['Latitude'], row['Longitude']],
				popup=row['Name'],
				tooltip=row['Name'],
				icon=folium.Icon(color="red")
				).add_to(mapit)
	else:
		for index, row in certified.iterrows():
			folium.Marker(
				location=[row['Latitude'], row['Longitude']],
				popup=row['Name'],
				tooltip=row['Name'],
				icon=folium.Icon(color="green")
				).add_to(mapit)
		for index, row in uncertified.iterrows():
			folium.Marker(
				location=[row['Latitude'], row['Longitude']],
				popup=row['Name'],
				tooltip=row['Name'],
				icon=folium.Icon(color="red")
				).add_to(mapit)
	return mapit

st.title("City Halal Directory")
st.write('Halo masyarakat Jawa Timur! Apakah anda pecinta kuliner? Pernahkah anda berfikir kuliner yang disajikan sudah tersertifikasi halal? Sebagai seorang muslim memang suatu kebutuhan dan diwajibkan memakanan makanan dan minuman halal, baik dari bahan dan cara pengolahannya. Kalau anda penasaran kuliner yang biasanya anda makan halal atau tidak. Aplikasi ini membantu mengecek sertifikasi halal warung/restaurant/warung/bakery dan kuliner lainnya di Kota Surabaya. Aplikasi ini menggabungkan data google maps dan data SIHALAL BPJPH menggunakan algoritma Jaccard Similarity.')
st.write('Anda dapat melihat source code dan dataset [di sini](https://github.com/adeindriawan/inovboyo)')
st.write('Data didapatkan dengan melakukan crawling data Google Maps restoran di kota Surabaya. Data dilakukan cleaning terlebih dahulu dan jumlah data yang siap digunakan sebanyak 1339 restoran di seluruh 31 kecamatan surabaya. Restoran restoran tersebut dikategorikan ke dalam 6 kategori berdasarkan keyword yang digunakan pada saat crawling: Cafe, Restoran, Warung, Bakery, Warung kopi, dan Kopi.')
st.write('Disclaimer: Beberapa nama warung/restoran yang ditampilkan pada data google maps berbeda dengan data  SIHALAL BPJPH. Hal ini dikarenakan terdapat warung/restoran menggunakan nama pemilik usaha atau nama PT bukan nama komersil yang biasa ditemukan di google maps')
st.write("Pendaftaran sertifikasi halal silahkan kunjungi http://halal.its.ac.id/")

# search restoran halal

st.title("Peta Restoran dan Warung Di Kota")

select_data = st.radio(
    "Pilih Data yang ingin ditampilkan",
    ("Semua", "Tersertifikasi Halal","Belum Tersertifikasi Halal")
)
st.write('Lokasi usaha makanan/minuman yang: '+ select_data)

# peta folium restoran
st_data = st_folium(get_coordinates(select_data), width = 825)

st.header("Cari Produk/Restaurant Halal di Jawa Timur")
cari = st.text_input("Data diperoleh dari Sihalal http://info.halal.go.id/cari/", "kopi susu")
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
# cast Reviews value to float
databotsol['Reviews'] = databotsol['Reviews'].str.replace(',', '').astype(float)
with col1:
    st.header("Data Restoran tiap Kecamatan")
    restokec = st.slider("Jumlah Restoran", 5, 20, step=5)
    select = st.selectbox('Pilih Kecamatan',databotsol['Kecamatan'].unique())
    urut = st.selectbox('Diurutkan berdasarkan',('Rating','Reviews'))

with col2:
    kec = databotsol[databotsol['Kecamatan'] == select][['Name','Address','Rating','Reviews']].sort_values(urut,ascending=False).head(restokec)
    st.table(kec.style.format({'Rating': '{:.1f}', 'Reviews': '{:.0f}'}))

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
listkec = databotsol['Kecamatan'].unique()
listkec=np.insert(listkec, 0, 'All', axis=0)
selectkeckategori = st.selectbox('Pilih Kecamatan ',listkec)
if(selectkeckategori=='All'):
	datafilter = databotsol.copy()
else:
	datafilter = databotsol[databotsol['Kecamatan']==selectkeckategori]
col3, col4 = st.columns(2)
with col3:
	st.header("Barplot Jumlah Restoran per Kategori")
	st.text(f"Kecamatan : {selectkeckategori}")
	kateg = datafilter[['Name','kategori']].groupby("kategori").count().reset_index().sort_values(by=['Name'],ascending=True)
	kateg.rename(columns = {'Name':'Jumlah','kategori':'Kategori'}, inplace = True)
	figkateg = px.bar(kateg, x='Kategori', y='Jumlah')
	figkateg.update_layout(
		width=600,
		height=550,
	)
	st.plotly_chart(figkateg)

with col4:
	st.header("Wordcloud Kuliner Kota")
	st.text(f"Kecamatan : {selectkeckategori}")
	dfkeccopy = datafilter.copy()
	dfkeccopy['Name'] = dfkeccopy['Name'].str.lower()
	dfkeccopy['Name'] = dfkeccopy['Name'].str.replace(r'[^\w\s]'," ")
	dfkeccopy['Name'] = dfkeccopy['Name'].str.strip()
	dfkeccopy.Name = dfkeccopy.Name.replace(r'\s+', ' ', regex=True)
	listname = dfkeccopy['Name']
	stop = ['warung', 'bakery', 'cafe', 'surabaya', 'kopi', 'warkop', 'restaurant', 'coffee']
	pat = r'\b(?:{})\b'.format('|'.join(stop))  #joining all words in one line separated by |
	listnamestop = listname.str.replace(pat, '')  # replace stopword
	listnamestop = listnamestop.str.replace(r'\s+', ' ')  #space tidying

	comment_words = ''
	for val in listnamestop:
		val = str(val)
		tokens = val.split()
		for i in range(len(tokens)):
			tokens[i] = tokens[i].lower()
		comment_words += " ".join(tokens)+" "
	wordcloud = WordCloud(width = 800, height = 800,
					background_color ='white',
					min_font_size = 10).generate(comment_words)
	fig, ax = plt.subplots(figsize = (12, 8))
	ax.imshow(wordcloud)
	plt.axis('off')
	plt.tight_layout(pad = 0)
	plt.show()
	st.pyplot(fig)

st.header("Visualisasi Graph Restoran di Kota")
config = Config(height=600, width=1400, nodeHighlightBehavior=True, highlightColor="#F7A7A6", directed=True,
                  collapsible=True)

def get_datagraph():
	return pd.read_csv("graphnode.csv")

graphdf = get_datagraph()
graphdfsmall = graphdf[graphdf['jac']>=0.5]
listgrapha = graphdfsmall['Name-a'].unique()
listgraphb = graphdfsmall['Name-b'].unique()
listgraph = list(set(listgrapha) | set(listgraphb))

nodes = []
edges = []
for item in listgraph:
    nodes.append(Node(id=item, size=400) )
for index,row in graphdfsmall.iterrows():
    edges.append( Edge(source=row['Name-a'], target=row['Name-b'], type="CURVE_SMOOTH"))
agraph(nodes, edges, config)

# FOOTER

st.header("Dipersembahkan oleh")
st.image("logo.png")

st.markdown("***")
st.markdown("Inovasi dan Teknologi (INOTEK AWARD) Jawa Timur")


