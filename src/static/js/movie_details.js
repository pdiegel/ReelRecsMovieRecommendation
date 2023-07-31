document.addEventListener('DOMContentLoaded', () => {
    const parsedElements = ['movie-details', 'account-states', 'movie-cast']
        .map(id => [id, JSON.parse(document.getElementById(id).textContent)]);
    const parsedData = Object.fromEntries(parsedElements);
    const { 'movie-details': movieDetails, 'account-states': accountStates, 'movie-cast':movieCast } = parsedData;
    console.log(movieDetails);

    fetchLoggedInStatus()
        .then(isLoggedIn => displayMovieDetails(isLoggedIn, movieDetails, accountStates, movieCast))
        .catch(console.error);
});

function displayMovieDetails(isLoggedIn, movieDetails, accountStates, movieCast) {
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
        ratedMovies = accountStates.rated;
        const userRating = ratedMovies.find(ratedMovie => ratedMovie.id === movie.id)?.rating;
        const inWatchlist = accountStates.watchlist;
        const inFavorites = accountStates.favorite;
        const starContainer = createStarContainer(movie, userRating, movieCard, window.location.pathname, cardButtons);

        starContainer.classList.add('movie-details-star-container');
        if (userRating) {
            movieInfo.append(starContainer);
            displayDeleteRatingButton(movie.id, movieCard, window.location.pathname, cardButtons, userRating);
        } else {
            movieInfo.append(starContainer);
        }

        displayWatchlistButton(movie.id, cardButtons, inWatchlist);
        displayFavoriteButton(movie.id, cardButtons, inFavorites);
    }

    movieInfo.append(cardButtons, movieTagline, OverviewText, movieDescription);    

    document.getElementById('banner-wrapped').append(movieCard);
    document.getElementById('banner-div').style.backgroundImage = "url('https://image.tmdb.org/t/p/original/" + movie.backdrop_path + "')";
    displayCastCards(movieCast);
}

function displayCastCards(movieCast) {
    const cast = movieCast.cast;
    console.log(cast);

    const castCard = document.createElement('div');
    castCard.classList.add('cast-card');

    const castImage = document.createElement('img');
    castImage.classList.add('cast-image');
    castImage.src = "https://image.tmdb.org/t/p/original/" + cast.profile_path;

    const castInfo = document.createElement('div');
    castInfo.classList.add('cast-info');

    const castName = document.createElement('h3');
    const castLink = document.createElement('a');
    castLink.href = "/person/" + cast.id;
    castLink.append(castName);
    castName.classList.add('cast-name');
    castName.textContent = cast.name + " - " + cast.character;

    // const movieStats = document.createElement('h5');
    // movieStats.classList.add('movie-stats');
    // movieStats.textContent = formatDate(movie.release_date) + " | Rated " + movie.vote_average + " | " + movie.genres.map(genre => genre.name).join(', ');

    // const movieTagline = document.createElement('p');
    // movieTagline.classList.add('movie-details-tagline');
    // movieTagline.textContent = movie.tagline;

    // const OverviewText = document.createElement('h4');
    // OverviewText.textContent = "Overview";

    // const movieDescription = document.createElement('p');
    // movieDescription.classList.add('movie-description');
    // movieDescription.textContent = movie.overview;

    // const cardButtons = document.createElement('div');
    // cardButtons.classList.add('movie-details-buttons');

    // const similarMoviesButton = document.createElement('button');
    // similarMoviesButton.classList.add('similar-movies-button');
    // similarMoviesButton.textContent = 'Similar Movies';
    // similarMoviesButton.addEventListener('click', similarMovieRedirect.bind(null, movie.id, movie.title));
    // cardButtons.append(similarMoviesButton);

    castInfo.append(castLink);
    castCard.append(castImage, castInfo);
}