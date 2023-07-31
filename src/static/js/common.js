const fetchJSON = async url => {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Error with fetch call, HTTP status ${response.status}`);
    }
    return await response.json();
};

const fetchLoggedInStatus = () => fetchJSON('http://127.0.0.1:5000/api/logged_in')
    .then(data => data.logged_in);

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
