document.addEventListener('DOMContentLoaded', () => {
    const parsedElements = ['movie-details', 'account-states', 'movie-cast', 'media-items']
        .map(id => [id, JSON.parse(document.getElementById(id).textContent)]);
    const parsedData = Object.fromEntries(parsedElements);
    const { 'movie-details': movieDetails, 'account-states': accountStates, 'movie-cast': movieCast, 'media-items': mediaItems } = parsedData;
    console.log(movieDetails);

    fetchLoggedInStatus()
        .then(isLoggedIn => displayMovieDetailPage(isLoggedIn, movieDetails, accountStates, movieCast, mediaItems))
        .catch(console.error);
});

function displayMovieDetailPage(isLoggedIn, movieDetails, accountStates, movieCast, mediaItems) {
    createMovieDetails(isLoggedIn, movieDetails, accountStates);
    movieCast = movieCast.cast;
    if (Array.isArray(movieCast)) {
        // Iterate only up to the first ten items
        for (let i = 0; i < Math.min(movieCast.length, 10); i++) {
            const castMember = movieCast[i];
            const castCard = createCastCard(castMember);
            document.getElementById('main-cast').append(castCard);
        }
    } else {
        console.error('Error fetching cast:', "cast is not an array");
    }

    mediaItems = mediaItems.results;
    if (Array.isArray(mediaItems)) {
        createMediaCarousel(mediaItems);
    } else {
        console.error('Error fetching media:', "media is not an array");
    }
}

function createMovieDetails(isLoggedIn, movieDetails, accountStates) {
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
}

function createCastCard(castMember) {
    const castCard = document.createElement('div');
    castCard.classList.add('cast-card');

    const castImage = document.createElement('img');
    castImage.classList.add('cast-image');
    if (castMember.profile_path == null) {
        castImage.src = "https://www.allianceplast.com/wp-content/uploads/2017/11/no-image.png";
    }
    else { castImage.src = "https://image.tmdb.org/t/p/original/" + castMember.profile_path; }


    const castInfo = document.createElement('div');
    castInfo.classList.add('cast-info');

    const castName = document.createElement('h3');
    const castLink = document.createElement('a');
    castLink.href = "/person/" + castMember.id;
    castLink.append(castName);
    castName.classList.add('cast-name');
    castName.textContent = castMember.name + " - " + castMember.character;

    castInfo.append(castLink);
    castCard.append(castImage, castInfo);
    return castCard;
}

function createMediaCarousel(mediaItems) {
    const videos = mediaItems.map(item => item.key);
    console.log("Videos = ", videos);

    let currentVideo = 0;
    let mediaSource = getMediaSource(videos, currentVideo);
    console.log(mediaSource)
    document.getElementById('videoPlayer').src = mediaSource;

    document.getElementById('previousVideoButton').addEventListener('click', function () {
        currentVideo--;
        if (currentVideo < 0) currentVideo = videos.length - 1;
        mediaSource = getMediaSource(videos, currentVideo);
        document.getElementById('videoPlayer').src = mediaSource;
    });

    document.getElementById('nextVideoButton').addEventListener('click', function () {
        currentVideo++;
        if (currentVideo >= videos.length) currentVideo = 0;
        mediaSource = getMediaSource(videos, currentVideo);
        document.getElementById('videoPlayer').src = mediaSource;
    });
}

function getMediaSource(videos, currentVideo){
    return "https://www.youtube.com/embed/" + videos[currentVideo];
}