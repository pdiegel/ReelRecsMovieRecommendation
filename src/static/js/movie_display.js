document.addEventListener('DOMContentLoaded', function () {
    const movies = JSON.parse(document.getElementById('json-data').textContent);
    const ratedMovies = JSON.parse(document.getElementById('rated-movies').textContent);

    fetchLoggedInStatus()
        .then(isLoggedIn => displayMovies(movies, isLoggedIn, ratedMovies))
        .catch(error => console.error('Error with fetch call:', error));
});

async function fetchLoggedInStatus() {
    const response = await fetch('http://127.0.0.1:5000/api/logged_in');
    const data = await response.json();
    return data.logged_in;
}

function displayMovies(movies, isLoggedIn, ratedMovies) {
    if (Array.isArray(movies)) {
        movies.forEach((movie) => {
            const movieCard = createMovieCard(movie, isLoggedIn, ratedMovies);
            document.getElementById('movie-list').append(movieCard);
        });
    } else {
        console.error('Error fetching movies:', "movies is not an array");
    }
}


function createMovieCard(movie, isLoggedIn, ratedMovies) {
    const movieCard = document.createElement('div');
    movieCard.classList.add('movie-card');

    const moviePoster = document.createElement('img');
    moviePoster.classList.add('movie-poster');
    moviePoster.src = "https://image.tmdb.org/t/p/original/" + movie.poster_path;

    const movieInfo = document.createElement('div');
    movieInfo.classList.add('movie-info');

    const releaseYear = movie.release_date ? "(" + movie.release_date.slice(0, 4) + ")" : '';

    const movieName = document.createElement('h3');
    movieName.classList.add('movie-name');
    movieName.textContent = movie.title + " " + releaseYear;

    const movieStats = document.createElement('h5');
    movieStats.classList.add('movie-stats');
    movieStats.textContent = formatDate(movie.release_date) + " | " + "Rated " + movie.vote_average;

    const movieDescription = document.createElement('p');
    movieDescription.classList.add('movie-description');
    movieDescription.textContent = movie.overview;

    const similarMoviesButton = document.createElement('button');
    similarMoviesButton.classList.add('similar-movies-button');
    similarMoviesButton.textContent = 'Similar Movies';
    similarMoviesButton.addEventListener('click', similarMovieRedirect.bind(null, movie.id, movie.title)); 

    movieInfo.append(movieName, movieStats, movieDescription);
    movieCard.append(moviePoster, movieInfo, similarMoviesButton);

    movieCard.dataset.movieId = movie.id;  // Add movie ID as a data attribute for later reference
    movieCard.id = 'movie-card-' + movie.id;  // Add unique ID to each movie card

    // If the user is logged in, create and append the Rate Movie button
    if (isLoggedIn) {
        const userRating = ratedMovies.find(ratedMovie => ratedMovie.id === movie.id)?.account_rating.value;
        const starContainer = createStarContainer(movie, userRating, movieCard, window.location.pathname);

        if (userRating) {
            movieInfo.append(starContainer);
            displayDeleteRatingButton(movie.id, movieCard, window.location.pathname);
        }
        else {
            // On other pages, always append the stars
            movieInfo.append(starContainer);
        }
    }

    return movieCard;
}

function createStarContainer(movieData, userRating, movieCard, pathname) {
    const starContainer = document.createElement('div');
    starContainer.classList.add('stars');

    for (let i = 0; i < 5; i++) {
        const star = document.createElement('span');
        star.classList.add('star');
        // 2, 4, 6, 8, 10
        // Subtracting 12 because the stars are in reverse order
        star.dataset.value = 12 - (i + 1) * 2;  
        // Unicode character for a star
        star.innerHTML = '&#9733;';  

        // If the user has rated the movie and the rating is greater than 
        // or equal to the star's value, color the star gold
        if (userRating && userRating >= (star.dataset.value)) {
            star.style.color = "gold";
        }

        starContainer.appendChild(star);

        star.addEventListener('click', function () {
            rateMovie(this, movieData, movieCard, pathname);
        });
    }

    return starContainer;
}

function rateMovie(event, movieData, movieCard, pathname) {
    const clickedStar = event;
    console.info('Clicked star:', clickedStar)
    const stars = Array.from(clickedStar.parentElement.children).reverse();
    const clickedStarIndex = stars.indexOf(clickedStar);

    stars.forEach((star, index) => {
        if (index <= clickedStarIndex) {
            star.style.color = "gold";
        } else {
            star.style.color = "gray";
        }
    });

    // Send the rating to the server
    const movieId = movieData.id;
    const rating = (clickedStarIndex + 1) * 2;  // Multiply by 2 because ratings are from 0.0 to 10.0 in increments of 0.5

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
                displayDeleteRatingButton(movieId, movieCard, pathname)
            } else {
                console.error('Error rating movie:', data.error);
            }
        })
        .catch(error => console.error('Error with fetch call:', error));
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

function displayDeleteRatingButton(movieId, movieCard, pathname) {
    const deleteRatingButton = document.createElement('button');
    deleteRatingButton.classList.add('delete-rating-button');
    deleteRatingButton.textContent = 'Delete Rating';
    movieCard.append(deleteRatingButton);

    deleteRatingButton.addEventListener('click', function () {
        deleteRating(movieId, movieCard);
        if (pathname === '/rated-movies') {
            movieCard.remove();
        }
    });

    return deleteRatingButton;
}

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


async function getSessionId() {
    const response = await fetch('http://127.0.0.1:5000/api/session_id');
    const data = await response.json();
    const sessionId = data.session_id;

    if (sessionId) {
        return sessionId;
    } else {
        console.error('Error fetching session ID:', "session ID is empty");
    }
}

async function getAuth() {
    const response = await fetch('http://127.0.0.1:5000/api/token');
    const data = await response.json();
    const accessToken = data.access_token;

    if (accessToken) {
        return accessToken;
    } else {
        console.error('Error fetching access token:', "access token is empty");
    }
}

function resetStarColor(movieCard) {
    const stars = movieCard.querySelectorAll('.star');
    stars.forEach(star => star.style.color = "gray");
}

function removeDeleteRatingButton(movieCard) {
    const deleteRatingButton = movieCard.querySelector('.delete-rating-button');
    deleteRatingButton.remove();
}

function similarMovieRedirect(movieId, movieTitle) {
    window.location.href = `/similar-movies/${movieId}/?title=${movieTitle}`;
}