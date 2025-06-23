import pickle
import streamlit as st
import requests

st.set_page_config(
    page_title="Movie Recommender",
    layout="wide",
    initial_sidebar_state="auto"
)

st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #1f1c2c, #928dab);
        color: white;
    }
    .main {
        background: transparent;
    }
    .stButton>button {
        background-color: #6a11cb;
        color: white;
        font-weight: bold;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #2575fc;
        transform: scale(1.05);
        cursor: pointer;
    }
    .movie-title {
        font-size: 18px;
        font-weight: bold;
        color: #f1c40f;
        text-align: center;
        margin-top: 10px;
    }
    /* Poster container for zoom + shadow */
    .poster-container {
        overflow: hidden;
        border-radius: 10px;
        cursor: pointer;
        margin-bottom: 8px;
    }
    .poster-container img {
        width: 100%;
        height: auto;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        display: block;
        border-radius: 10px;
    }
    .poster-container:hover img {
        transform: scale(1.07);
        box-shadow: 0 12px 28px rgba(241, 196, 15, 0.85);
    }
    </style>
""", unsafe_allow_html=True)


#fetching full movie details from TMDB
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()

    return {
        "poster_path": "https://image.tmdb.org/t/p/w500/" + data.get('poster_path', ''),
        "overview": data.get('overview', 'No description available'),
        "release_date": data.get('release_date', 'N/A'),
        "rating": data.get('vote_average', 'N/A'),
        "genres": [genre['name'] for genre in data.get('genres', [])]
    }


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movies = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        details = fetch_movie_details(movie_id)
        recommended_movies.append({
            "title": movies.iloc[i[0]].title,
            "poster": details["poster_path"],
            "overview": details["overview"],
            "release_date": details["release_date"],
            "rating": details["rating"],
            "genres": details["genres"]
        })

    return recommended_movies


movies = pickle.load(open('artifacts/movie_list.pkl', 'rb'))
similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))

st.markdown("<h1 style='text-align: center; color: white;'>🎬 Movie Recommender System </h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #d1d1d1;'>Find your next favorite movie in seconds</h4>", unsafe_allow_html=True)

movie_list = movies['title'].values
selected_movies = st.selectbox(
    'Type or select a movie to get recommendations',
    movie_list
)

if st.button('Show Recommendations'):
    with st.spinner('🔄 Fetching recommendations, please wait...'):
        recommended_movies = recommend(selected_movies)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            
            st.markdown(f"""
                <div class="poster-container">
                    <img src="{recommended_movies[i]['poster']}" alt="{recommended_movies[i]['title']} poster">
                </div>
                <div class='movie-title'>{recommended_movies[i]['title']}</div>
            """, unsafe_allow_html=True)

            with st.expander("📖 More Info"):
                st.markdown(f"**🎭 Genres:** {', '.join(recommended_movies[i]['genres'])}")
                st.markdown(f"**📅 Release Date:** {recommended_movies[i]['release_date']}")
                st.markdown(f"**⭐ Rating:** {recommended_movies[i]['rating']} / 10")
                st.markdown(f"**📝 Overview:** {recommended_movies[i]['overview']}")
