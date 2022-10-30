

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR-SECRET-KEY'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

IMDB_API = "IMDB_API"


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(205), nullable=True)


db.create_all()


class RatingReviewForm(FlaskForm):
    rating = StringField("Rating", validators=[DataRequired()])
    review = StringField("Review", validators=[DataRequired()])
    submit = SubmitField("Done")


class FindMovie(FlaskForm):
    title = StringField("Title of the movie", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


@app.route("/")
def home():
    # movie = db.session.query(Movie).all()
    # return render_template("index.html", movies=movie)

    # This line creates a list of all the movies sorted by rating
    all_movies = Movie.query.order_by(Movie.rating).all()

    # This line loops through all the movies
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = RatingReviewForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", form=form)


@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=["GET", "POST"])
def add():
    form = FindMovie()

    if form.validate_on_submit():
        response = requests.get("https://imdb-api.com/en/API/SearchMovie/",
                                params={"apiKey": IMDB_API, "expression": form.title.data})
        options = response.json()["results"]
        return render_template("select.html", options=options)
    return render_template("add.html", form=form)


@app.route("/find")
def find():
    movie_id = request.args.get("id")

    if movie_id:
        response = requests.get("https://imdb-api.com/en/API/Title/", params={"apiKey": IMDB_API, "id": movie_id})
        data = response.json()

        new_movie = Movie(
            title=data["title"],
            year=data["year"],
            description=data["plot"],
            img_url=data["image"]
        )

        db.session.add(new_movie)
        db.session.commit()

        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)
