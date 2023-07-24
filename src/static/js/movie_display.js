document.addEventListener('DOMContentLoaded', function() {
    const movies = JSON.parse(document.getElementById('json-data').textContent);
    const ratedMovies = JSON.parse(document.getElementById('rated-movies').textContent);

    fetch('http://127.0.0.1:5000/api/logged_in')
        .then(response => response.json())
        .then(data => {
            const isLoggedIn = data.logged_in;
            console.info('User logged in:', isLoggedIn);

            if (Array.isArray(movies)) {
                movies.forEach((movie) => {
                    const movieCard = createMovieCard(movie, isLoggedIn, ratedMovies);
                    document.getElementById('movie-list').append(movieCard);
                });
            } else {
                console.error('Error fetching movies:', "movies is not an array");
            }
        })
        .catch(error => console.error('Error with fetch call:', error));

    console.log('Rated movies:', ratedMovies);
});

function createMovieCard(movie, isLoggedIn, ratedMovies) {
    const movieCard = document.createElement('div');
    movieCard.classList.add('movie-card');

    const moviePoster = document.createElement('img');
    moviePoster.classList.add('movie-poster');
    moviePoster.src = "https://image.tmdb.org/t/p/original/"+movie.poster_path;

    const movieInfo = document.createElement('div');
    movieInfo.classList.add('movie-info');

    const releaseYear = movie.release_date ? "("+movie.release_date.slice(0,4)+")" : '';

    const movieName = document.createElement('h3');
    movieName.classList.add('movie-name');
    movieName.textContent = movie.title + " " + releaseYear;

    const movieStats = document.createElement('h5');
    movieStats.classList.add('movie-stats');
    movieStats.textContent = formatDate(movie.release_date) + " | " + "Rated " + movie.vote_average;

    const movieDescription = document.createElement('p');
    movieDescription.classList.add('movie-description');
    movieDescription.textContent = movie.overview;

    movieInfo.append(movieName, movieStats, movieDescription);
    movieCard.append(moviePoster, movieInfo);

    movieCard.dataset.movieId = movie.id;  // Add movie ID as a data attribute for later reference
    movieCard.id = 'movie-card-' + movie.id;  // Add unique ID to each movie card

    // If the user is logged in and the movie isn't rated, create and append the Rate Movie button
    if (isLoggedIn) {
        const userRating = ratedMovies.find(ratedMovie => ratedMovie.id === movie.id)?.account_rating.value;
        console.log('User rating:', userRating)
        const starContainer = createStarContainer(movie, userRating);
        

        // Check if the current page is the "My Ratings" page
        if (window.location.pathname === '/rated-movies') {
            // Only append the stars if the movie has been rated by the user
            if (userRating) {
                movieCard.append(starContainer);
                displayDeleteRatingButton(movie.id, movieCard);
            }

        } else if (!userRating) {
            // On other pages, always append the stars
            movieCard.append(starContainer);
            console.info('Movie not rated:', movie.title);
        }

        
    }

    return movieCard;
}

function createStarContainer(movie, userRating) {
    const starContainer = document.createElement('div');
    starContainer.classList.add('stars');

    for (let i = 0; i < 5; i++) {
        const star = document.createElement('span');
        star.classList.add('star');
        star.dataset.value = 12 - (i + 1) * 2;  // 2, 4, 6, 8, 10
        star.innerHTML = '&#9733;';  // Unicode character for a star

        // If the user has rated the movie and the rating is greater than or equal to the star's value, color the star gold
        if (userRating && userRating >= (star.dataset.value)) {
            star.style.color = "gold";
        }

        starContainer.appendChild(star);

        star.addEventListener('click', function() {
            rateMovie(this, movie);
        });
    }

    return starContainer;
}

function rateMovie(event, movie) {
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
    const movieId = movie.id;
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
        } else {
            console.error('Error rating movie:', data.error);
        }
    })
    .catch(error => console.error('Error with fetch call:', error));
}


function formatDate(movie_release_date){
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
    case 1:  suffix = "st"; break;
    case 2:  suffix = "nd"; break;
    case 3:  suffix = "rd"; break;
    default: suffix = "th"; break;
    }

    let formattedDate = `${monthNames[monthIndex]} ${day}${suffix}, ${year}`;

    return formattedDate;
}

function displayDeleteRatingButton(movieId, movieCard) {
    const deleteRatingButton = document.createElement('button');
    deleteRatingButton.classList.add('delete-rating-button');
    deleteRatingButton.textContent = 'Delete Rating';
    movieCard.append(deleteRatingButton);

    deleteRatingButton.addEventListener('click', function() {
        deleteRating(movieId, movieCard);
    });

    return deleteRatingButton;
}

async function deleteRating(movieId, movieCard) {
    const sessionId = await getSessionId();
    const auth = await getAuth();

    fetch('https://api.themoviedb.org/3/movie/' + movieId + '/rating?session_id=' + sessionId, {
        method: 'DELETE',
        headers: {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + auth
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.info('Successfully deleted movie rating:', movieId);
            movieCard.remove();
        } else {
            console.error('Error deleting movie rating:', data.error);
        }
    })
    .catch(error => console.error('Error with fetch call:', error));
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