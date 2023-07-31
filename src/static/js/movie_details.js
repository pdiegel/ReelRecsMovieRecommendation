document.addEventListener('DOMContentLoaded', () => {
    const parsedElements = ['movie-details', 'account-states']
        .map(id => [id, JSON.parse(document.getElementById(id).textContent)]);
    const parsedData = Object.fromEntries(parsedElements);
    const { 'movie-details': movieDetails, 'account-states': accountStates } = parsedData;

    fetchLoggedInStatus()
        .then(isLoggedIn => displayMovieDetails(isLoggedIn, movieDetails, accountStates))
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

function displayMovieDetails(isLoggedIn, movieDetails, accountStates) {
    const movie = movieDetails;

    const movieCard = document.createElement('div');
    movieCard.classList.add('movie-details-card');

    const moviePoster = document.createElement('img');
    moviePoster.classList.add('movie-details-poster');
    moviePoster.src = "https://image.tmdb.org/t/p/original/" + movie.poster_path;

    const movieInfo = document.createElement('div');
    movieInfo.classList.add('movie-details-info');

    const releaseYear = movie.release_date ? "(" + movie.release_date.slice(0, 4) + ")" : '';

    const movieName = document.createElement('h3');
    const movieLink = document.createElement('a');
    movieLink.href = "/movie/" + movie.id;
    movieLink.append(movieName);
    movieName.classList.add('movie-name');
    movieName.textContent = movie.title + " " + releaseYear;

    const movieStats = document.createElement('h5');
    movieStats.classList.add('movie-stats');
    movieStats.textContent = formatDate(movie.release_date) + " | Rated " + movie.vote_average + " | " + movie.genres.map(genre => genre.name).join(', ');

    const movieTagline = document.createElement('p');
    movieTagline.classList.add('movie-details-tagline');
    movieTagline.textContent = movie.tagline;

    const OverviewText = document.createElement('h4');
    OverviewText.textContent = "Overview";

    const movieDescription = document.createElement('p');
    movieDescription.classList.add('movie-description');
    movieDescription.textContent = movie.overview;

    const cardButtons = document.createElement('div');
    cardButtons.classList.add('movie-details-buttons');

    const similarMoviesButton = document.createElement('button');
    similarMoviesButton.classList.add('similar-movies-button');
    similarMoviesButton.textContent = 'Similar Movies';
    similarMoviesButton.addEventListener('click', similarMovieRedirect.bind(null, movie.id, movie.title));
    cardButtons.append(similarMoviesButton);

    movieInfo.append(movieLink, movieStats);
    movieCard.append(moviePoster, movieInfo);

    movieCard.dataset.movieId = movie.id;  // Add movie ID as a data attribute for later reference
    movieCard.id = 'movie-card-' + movie.id;  // Add unique ID to each movie card

    // If the user is logged in, create and append the Rate Movie button
    if (isLoggedIn) {
        console.log(accountStates);
        const inWatchlist = accountStates.watchlist;
        const inFavorites = accountStates.favorite;

        displayWatchlistButton(movie.id, cardButtons, inWatchlist);
        displayFavoriteButton(movie.id, cardButtons, inFavorites);
        movieInfo.append(cardButtons, movieTagline, OverviewText, movieDescription);
    }


    document.getElementById('banner-wrapped').append(movieCard);
    document.getElementById('banner-div').style.backgroundImage = "url('https://image.tmdb.org/t/p/original/" + movie.backdrop_path + "')";
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

    let payload = { movie_id: movieId, watchlist: inWatchlist }

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

    let payload = { movie_id: movieId, favorite: inFavorites }

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
