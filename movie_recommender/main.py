import pickle
import time
import pandas as pd
import requests
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

st.set_page_config(
    page_title="Match My Movie",
    page_icon="🎬",
    layout="wide"
)
@st.cache_resource
def get_similarity():
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vector = cv.fit_transform(movies['tags'])
    return cosine_similarity(vector)
@st.cache_data
def get_poster_path(movie_title, release_year):
    api_key = "45031b9ed78f35196bb9ef5f4d2a366c"
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}"
    try:
        response = requests.get(url, timeout=5).json()
        results = response.get('results', [])
        for movie in results:
            release_date = movie.get('release_date', '')
            if str(release_year) in release_date:
                path = movie.get('poster_path')
                if path:
                    return "https://image.tmdb.org/t/p/w500" + path

        if results and results[0].get('poster_path'):
            return "https://image.tmdb.org/t/p/w500" + results[0].get('poster_path')

    except Exception as e:
        print(f"Error for {movie_title}: {e}")

    return "https://images.pexels.com/photos/8273630/pexels-photo-8273630.jpeg?_gl=1*1g0ydd7*_ga*MTAxODcwNTA0Ni4xNzcyMzU4ODY5*_ga_8JE65Q40S6*czE3NzIzNTg4NjgkbzEkZzEkdDE3NzIzNTg4ODEkajQ3JGwwJGgw"

def recommend(movie_title):
    movie_row = movies[movies['title'] == movie_title].iloc[0]
    index = movie_row.name
    selected_type = movie_row['type']
    distances = list(enumerate(similarity[index]))

    filtered_distances = [
        i for i in distances
        if movies.iloc[i[0]]['type'] == selected_type and i[0] != index
    ]

    sorted_distances = sorted(filtered_distances, key=lambda x: x[1], reverse=True)

    top5 = []
    top5_year = []
    top5_photos = []
    for i in sorted_distances[:5]:
        title = movies.iloc[i[0]].title
        movie_year = movies.iloc[i[0]].release_year
        top5.append(title)
        top5_year.append(movie_year)
        time.sleep(0.5)
        top5_photos.append(get_poster_path(title,movie_year))

    return top5, top5_photos,top5_year

st.title('Movie recommender')

current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, 'movies_list.pkl')
movies = pickle.load(open(file_path, 'rb'))
movies = pd.DataFrame(movies)
similarity = get_similarity()

ott_list = st.selectbox(
    "Select the platform for recommendation",
     ['All platforms','netflix','amazonprime','jiohotstar'],
    index=None,
    placeholder="Select the platform for recommendation",
)
Type = st.selectbox(
    "Select the Type for recommendation",
     ['Movie','TV Show','Any Type'],
    index=None,
    placeholder="Select the Type for recommendation",
)
filtered_movies = movies.copy()
if ott_list and ott_list != 'All platforms':
    filtered_movies = filtered_movies[filtered_movies['platform'] == ott_list].sort_values(by= 'title')
if Type and Type != 'Any Type':
    filtered_movies = filtered_movies[filtered_movies['type'] == Type].sort_values(by= 'title')
available_titles = filtered_movies['title'].unique()

movies_list = st.selectbox(
    "Select the movie for recommendation",
    options=available_titles,
    index=None,
    placeholder="Select the movie for recommendation",
)

if st.button("Recommend",type="primary"):
  if movies_list:
      top5, top5_photos, top5_year = recommend(movies_list)
      col1, col2, col3, col4, col5 = st.columns(5,gap="medium")

      with col1:
        st.image(top5_photos[0])
        st.markdown(f"**{top5[0]}**")
        st.write(f"({top5_year[0]})")

      with col2:
        st.image(top5_photos[1])
        st.markdown(f"**{top5[1]}**")
        st.write(f"({top5_year[1]})")

      with col3:
        st.image(top5_photos[2])
        st.markdown(f"**{top5[2]}**")
        st.write(f"({top5_year[2]})")

      with col4:
        st.image(top5_photos[3])
        st.markdown(f"**{top5[3]}**")
        st.write(f"({top5_year[3]})")

      with col5:
        st.image(top5_photos[4])
        st.markdown(f"**{top5[4]}**")
        st.write(f"({top5_year[4]})")
  else:
      st.write("Please select a movie to recommend")


