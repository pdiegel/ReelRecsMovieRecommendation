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










