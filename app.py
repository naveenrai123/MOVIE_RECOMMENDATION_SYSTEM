import pickle
import streamlit as st
import requests
import urllib.parse

def fetch_poster(movie_id, title, year=None):
    """
    Fetch poster using OMDB API with multiple fallback strategies
    Returns poster URL or None if not found
    """
    try:
        # First try: Exact match using IMDb ID
        url = f"http://www.omdbapi.com/?i={movie_id}&apikey=950ed639 "
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('Poster') and data['Poster'] != 'N/A':
            return data['Poster']
        
        # Second try: Search by title + year
        encoded_title = urllib.parse.quote(title)
        search_url = f"http://www.omdbapi.com/?t={encoded_title}&y={year}&apikey=950ed639"
        search_response = requests.get(search_url)
        search_data = search_response.json()
        
        if search_data.get('Poster') and search_data['Poster'] != 'N/A':
            return search_data['Poster']
        
        # Third try: Search by title only
        search_url = f"http://www.omdbapi.com/?t={encoded_title}&apikey=950ed639"
        search_response = requests.get(search_url)
        search_data = search_response.json()
        
        return search_data.get('Poster') if search_data.get('Poster') != 'N/A' else None
    
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        
        recommendations = []
        for i in distances[1:6]:
            movie_data = movies.iloc[i[0]]
            poster_url = fetch_poster(
                movie_id=movie_data['movie_id'],
                title=movie_data['title'],
                year=movie_data.get('year')
            )
            
            # Fallback to OMDB's default movie icon if no poster found
            final_poster = poster_url if poster_url else \
                "https://m.media-amazon.com/images/G/01/imdb/images-ANDW73HA/favicon-192x192.png"
            
            recommendations.append({
                'title': movie_data['title'],
                'poster': final_poster,
                'year': movie_data.get('year', 'N/A')
            })
        
        return recommendations
    
    except Exception as e:
        st.error(f"Recommendation error: {str(e)}")
        return []

# Streamlit UI
st.header('🎬 Movie Recommender System (OMDB)')

# Load data with validation
try:
    movies = pickle.load(open('movie_list.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    
    # Validate dataset structure
    required_columns = {'title', 'movie_id'}
    if not required_columns.issubset(movies.columns):
        st.error(f"Dataset missing required columns: {required_columns - set(movies.columns)}")
        st.stop()
        
except FileNotFoundError:
    st.error("Data files not found!")
    st.stop()

movie_list = movies['title'].values
selected_movie = st.selectbox("Select a movie:", movie_list)

if st.button('Show Recommendations'):
    recommendations = recommend(selected_movie)
    
    if recommendations:
        cols = st.columns(5)
        for col, movie in zip(cols, recommendations):
            with col:
                st.image(movie['poster'], use_column_width=True, caption=movie['title'])
                st.caption(f"Year: {movie['year']}")
    else:
        st.warning("No recommendations found")

