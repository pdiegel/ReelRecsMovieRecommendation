document.addEventListener('DOMContentLoaded', () => {
    const parsedElements = ['json-data', 'rated-movies', 'favorite-movies', 'watchlist-movies']
        .map(id => [id, JSON.parse(document.getElementById(id).textContent)]);
    const parsedData = Object.fromEntries(parsedElements);
    const { 'json-data': movies, 'rated-movies': ratedMovies, 'favorite-movies': favoriteMovies, 'watchlist-movies': watchlistMovies } = parsedData;

    fetchLoggedInStatus()
        .then(isLoggedIn => displayMovies(movies, isLoggedIn, ratedMovies, favoriteMovies, watchlistMovies))
        .catch(console.error);
});

const fetchJSON = async url => {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Error with fetch call, HTTP status ${response.status}`);
    }
    return await response.json();
};

const fetchLoggedInStatus = () => fetchJSON('http://127.0.0.1:5000/api/logged_in')
    .then(data => data.logged_in);

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

function formatDate(movie_release_date) {
    let date = new Date(movie_release_date);

    let day = date.getDate();
    let monthIndex = date.getMonth();
    let year = date.getFullYear();

    let monthNames = ["January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];

    let suffix;
    if (day > 3 && day < 21) suffix = 'th';
    else switch (day % 10) {
        case 1: suffix = "st"; break;
        case 2: suffix = "nd"; break;
        case 3: suffix = "rd"; break;
        default: suffix = "th"; break;
    }

    let formattedDate = `${monthNames[monthIndex]} ${day}${suffix}, ${year}`;

    return formattedDate;
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

function similarMovieRedirect(movieId, movieTitle) {
    window.location.href = `/similar-movies/${movieId}/?title=${movieTitle}`;
}

function displayWatchlistButton(movieId, cardButtons, inWatchlist) {
    const watchlistButton = createButton('watchlist-button', inWatchlist ? 'Drop from Watchlist' : 'Add to Watchlist', function () {
        modifyWatchlist(movieId, this);
    });

    watchlistButton.dataset.inWatchlist = inWatchlist ? 'true' : 'false';
    cardButtons.append(watchlistButton);

    return watchlistButton;
}

async function modifyWatchlist(movieId, watchlistButton) {
    let inWatchlist = watchlistButton.dataset.inWatchlist === 'true';

    inWatchlist = !inWatchlist;
    watchlistButton.dataset.inWatchlist = inWatchlist ? 'true' : 'false';
    watchlistButton.textContent = inWatchlist ? 'Drop from Watchlist' : 'Add to Watchlist';

    let payload = {movie_id: movieId, watchlist: inWatchlist}

    flask_post_request("watchlist_movie/", payload)
        .then(data => {
            if (data.success) {
                console.info('Successfully watchlisted movie:', movieId);
            } else {
                console.error('Error watchlisting movie:', data.error);
            }
        })
        .catch(console.error);
}

function displayFavoriteButton(movieId, cardButtons, inFavorites) {
    const favoritesButton = createButton('favorite-button', inFavorites ? 'Unfavorite' : 'Favorite', function () {
        modifyFavorites(movieId, this);
    });

    favoritesButton.dataset.inFavorites = inFavorites ? 'true' : 'false';
    cardButtons.append(favoritesButton);

    return favoritesButton;
}

async function modifyFavorites(movieId, favoritesButton) {
    let inFavorites = favoritesButton.dataset.inFavorites === 'true';

    inFavorites = !inFavorites;
    favoritesButton.dataset.inFavorites = inFavorites ? 'true' : 'false';
    favoritesButton.textContent = inFavorites ? 'Unfavorite' : 'Favorite';

    let payload = {movie_id: movieId, favorite: inFavorites}

    flask_post_request("favorite_movie/", payload)
        .then(data => {
            if (data.success) {
                console.info('Successfully favorited movie:', movieId);
            } else {
                console.error('Error favoriting movie:', data.error);
            }
        })
        .catch(console.error);
}

const flask_post_request = (endpoint, payload) => fetch(`http://127.0.0.1:5000/${endpoint}`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
}).then(res => res.json());

function createButton(className, textContent, eventListener) {
    const button = document.createElement('button');
    button.classList.add(className);
    button.textContent = textContent;
    button.addEventListener('click', eventListener);
    return button;
}
