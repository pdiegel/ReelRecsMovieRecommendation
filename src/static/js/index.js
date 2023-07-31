document.addEventListener('DOMContentLoaded', () => {
    const parsedElements = ['json-data', 'rated-movies', 'favorite-movies', 'watchlist-movies']
        .map(id => [id, JSON.parse(document.getElementById(id).textContent)]);
    const parsedData = Object.fromEntries(parsedElements);
    const { 'json-data': movies, 'rated-movies': ratedMovies, 'favorite-movies': favoriteMovies, 'watchlist-movies': watchlistMovies } = parsedData;

    fetchLoggedInStatus()
        .then(isLoggedIn => displayMovies(movies, isLoggedIn, ratedMovies, favoriteMovies, watchlistMovies))
        .catch(console.error);
});

function displayMovies(movies, isLoggedIn, ratedMovies, favoriteMovies, watchlistMovies) {
    if (Array.isArray(movies)) {
        movies.forEach((movie) => {
            const movieCard = createMovieCard(movie, isLoggedIn, ratedMovies, favoriteMovies, watchlistMovies);
            document.getElementById('movie-list').append(movieCard);
        });
    } else {
        console.error('Error fetching movies:', "movies is not an array");
    }
}

function createMovieCard(movie, isLoggedIn, ratedMovies, favoriteMovies, watchlistMovies) {
    const movieCard = document.createElement('div');
    movieCard.classList.add('movie-card');

    const moviePoster = document.createElement('img');
    moviePoster.classList.add('movie-poster');
    moviePoster.src = "https://image.tmdb.org/t/p/original/" + movie.poster_path;

    const movieInfo = document.createElement('div');
    movieInfo.classList.add('movie-info');

    const releaseYear = movie.release_date ? "(" + movie.release_date.slice(0, 4) + ")" : '';

    const movieName = document.createElement('h3');
    const movieLink = document.createElement('a');
    movieLink.href = "/movie/" + movie.id;
    movieLink.append(movieName);
    movieName.classList.add('movie-name');
    movieName.textContent = movie.title + " " + releaseYear;

    const movieStats = document.createElement('h5');
    movieStats.classList.add('movie-stats');
    movieStats.textContent = formatDate(movie.release_date) + " | " + "Rated " + movie.vote_average;

    const movieDescription = document.createElement('p');
    movieDescription.classList.add('movie-description');
    movieDescription.textContent = movie.overview;

    const cardButtons = document.createElement('div');
    cardButtons.classList.add('card-buttons');

    const similarMoviesButton = document.createElement('button');
    similarMoviesButton.classList.add('similar-movies-button');
    similarMoviesButton.textContent = 'Similar Movies';
    similarMoviesButton.addEventListener('click', similarMovieRedirect.bind(null, movie.id, movie.title));
    cardButtons.append(similarMoviesButton);

    movieInfo.append(movieLink, movieStats, movieDescription);
    movieCard.append(moviePoster, movieInfo);

    movieCard.dataset.movieId = movie.id;  // Add movie ID as a data attribute for later reference
    movieCard.id = 'movie-card-' + movie.id;  // Add unique ID to each movie card

    // If the user is logged in, create and append the Rate Movie button
    if (isLoggedIn) {
        const userRating = ratedMovies.find(ratedMovie => ratedMovie.id === movie.id)?.rating;
        const watchlist = watchlistMovies.find(watchlistMovie => watchlistMovie.id === movie.id);
        const favorite = favoriteMovies.find(favoriteMovie => favoriteMovie.id === movie.id);

        const inWatchlist = watchlist !== undefined;
        const inFavorites = favorite !== undefined;
        const starContainer = createStarContainer(movie, userRating, movieCard, window.location.pathname, cardButtons);

        if (userRating) {
            movieInfo.append(starContainer);
            displayDeleteRatingButton(movie.id, movieCard, window.location.pathname, cardButtons, userRating);
        } else {
            movieInfo.append(starContainer);
        }

        displayWatchlistButton(movie.id, cardButtons, inWatchlist);
        displayFavoriteButton(movie.id, cardButtons, inFavorites);
        movieInfo.append(cardButtons)
    }

    return movieCard;
}

function createStarContainer(movieData, userRating, movieCard, pathname, cardButtons) {
    const starContainer = document.createElement('div');
    starContainer.classList.add('stars');

    for (let i = 0; i < 5; i++) {
        const star = document.createElement('span');
        star.classList.add('star');
        star.dataset.value = 12 - (i + 1) * 2;
        star.innerHTML = '&#9733;';

        if (userRating && userRating >= (star.dataset.value)) {
            star.style.color = "gold";
        }

        starContainer.appendChild(star);

        star.addEventListener('click', function () {
            rateMovie(this, movieData, movieCard, pathname, cardButtons);
        });
    }

    return starContainer;
}

function rateMovie(event, movieData, movieCard, pathname, cardButtons) {
    const clickedStar = event;
    const stars = Array.from(clickedStar.parentElement.children).reverse();
    const clickedStarIndex = stars.indexOf(clickedStar);

    stars.forEach((star, index) => {
        if (index <= clickedStarIndex) {
            star.style.color = "gold";
        } else {
            star.style.color = "gray";
        }
    });

    const movieId = movieData.id;
    const rating = (clickedStarIndex + 1) * 2;

    fetch('http://127.0.0.1:5000/rate_movie/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            movie_id: movieId,
            rating: rating
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.info('Successfully rated movie:', movieId);
                displayDeleteRatingButton(movieId, movieCard, pathname, cardButtons)
            } else {
                console.error('Error rating movie:', data.error);
            }
        })
        .catch(console.error);
}

function displayDeleteRatingButton(movieId, movieCard, pathname, cardButtons) {
    if (!cardButtons.querySelector('.delete-rating-button')) {
        const deleteRatingButton = createButton('delete-rating-button', 'Delete Rating', function () {
            deleteRating(movieId, movieCard);
            if (pathname === '/rated-movies') {
                movieCard.remove();
            }
        });
        cardButtons.append(deleteRatingButton);
    }
}

const getSessionId = () => fetchJSON('http://127.0.0.1:5000/api/session_id')
    .then(data => data.session_id || Promise.reject('Error fetching session ID: session ID is empty'));

const getAuth = () => fetchJSON('http://127.0.0.1:5000/api/token')
    .then(data => data.access_token || Promise.reject('Error fetching access token: access token is empty'));

async function deleteRating(movieId, movieCard) {
    try {
        const [sessionId, auth] = await Promise.all([getSessionId(), getAuth()]);
        const response = await fetch(`https://api.themoviedb.org/3/movie/${movieId}/rating?session_id=${sessionId}`, {
            method: 'DELETE',
            headers: {
                'accept': 'application/json',
                'Authorization': `Bearer ${auth}`
            },
        });
        const data = await response.json();
        if (data.success) {
            console.info('Successfully deleted movie rating:', movieId);
            resetStarColor(movieCard);
            removeDeleteRatingButton(movieCard);
        } else {
            console.error('Error deleting movie rating:', data.error);
        }
    } catch (error) {
        return console.error('Error with fetch call:', error);
    }
}

function resetStarColor(movieCard) {
    const stars = movieCard.querySelectorAll('.star');
    stars.forEach(star => star.style.color = "gray");
}

function removeDeleteRatingButton(cardButtons) {
    const deleteRatingButton = cardButtons.querySelector('.delete-rating-button');
    deleteRatingButton.remove();
}









