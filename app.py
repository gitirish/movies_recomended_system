from flask import Flask ,url_for, render_template , request,redirect, jsonify
import pickle
import pandas as pd
import os
import requests
from patsy import dmatrices
app = Flask(__name__)
# Define paths
MODEL_PATH = os.path.join('models', 'model.pkl')
DATA_PATH = os.path.join('models', 'movies_df.pkl')


with open(MODEL_PATH, 'rb') as f:
    similarities = pickle.load(f)

df = pd.read_pickle(DATA_PATH)

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=2e5bc585e44065fe88e54b127ec09206".format(movie_id)
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP request errors
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
        else:
            return "Poster path not found."
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"


def recommended(movie):
    
    movie_index = df[df['title'] == movie].index[0]
    distance = similarities[movie_index]
    movies_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies_name = []
    recommended_movies_poster = []        
    
    for i in movies_list:
        movie_id=df.iloc[i[0]].movie_id
        recommended_movies_name.append(df.iloc[i[0]].title)
        recommended_movies_poster.append(fetch_poster(movie_id))
    return recommended_movies_name,recommended_movies_poster

@app.route("/")
def ho():
    return render_template('home.html')

@app.route("/intro")
def intro():
    return render_template('about.html')

@app.route('/recommend',methods=['GET','POST'])
def recommend():
    movie_list = df['title'].values
    status =False
    if request.method == "POST":
        try:
            if request.form:
               movie_name = request.form.get('movie')
               print(movie_name)
               recommended_movies_name,recommended_movies_poster= recommended(movie_name)
               print(recommended_movies_name)
               status =True
               return render_template('index.html',movies = recommended_movies_name,poster=recommended_movies_poster,movie_list = movie_list,status=status)
        except Exception as e:
            return render_template("index.html",movie_list = movie_list,status=status)
    else:    
      return render_template("index.html",movie_list = movie_list,status=status)


if __name__ == '__main__':
    app.run(debug=True)