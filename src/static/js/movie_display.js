document.addEventListener('DOMContentLoaded', function() {
    let movies = JSON.parse(document.getElementById('json-data').textContent);
    let ratedMovies = JSON.parse(document.getElementById('rated-movies').textContent);

    // Check if user is logged in
    fetch('http://127.0.0.1:5000/api/logged_in')
        .then(response => response.json())
        .then(data => {
            const isLoggedIn = data.logged_in;
            console.info('User logged in:', isLoggedIn);

            if (Array.isArray(movies)) {
                movies.forEach((movie) => {
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
        
                    const movieDescription = document.createElement('p');
                    movieDescription.classList.add('movie-description');
                    movieDescription.textContent = movie.overview;
        
                    movieInfo.append(movieName, movieDescription);
                    movieCard.append(moviePoster, movieInfo);
                    
                    movieCard.dataset.movieId = movie.id;  // Add movie ID as a data attribute for later reference
                    movieCard.id = 'movie-card-' + movie.id;  // Add unique ID to each movie card

                    // If the user is logged in and the movie isn't rated, create and append the Rate Movie button
                    if (isLoggedIn && !ratedMovies.some(ratedMovie => ratedMovie.id === movie.id)) {
                        const rateButton = document.createElement('button');
                        rateButton.textContent = "Rate Movie";
                        rateButton.onclick = function() {
                            const movieId = movie.id;
                            const rating = 8.50;  // Update with user's rating value

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
                                    // Remove the Rate Movie button if the rating was successful
                                    rateButton.remove();
                                    console.info('Successfully rated movie:', movieId);
                                } else {
                                    console.error('Error rating movie:', data.error);
                                }
                            })
                            .catch(error => console.error('Error with fetch call:', error));
                        }
                        movieCard.append(rateButton);
                        console.info('Movie not rated:', movie.title);
                    }

                    document.getElementById('movie-list').append(movieCard);
                });
            } else {
                console.error('Error fetching movies:', "movies is not an array");
            }
        })
        .catch(error => console.error('Error with fetch call:', error));

    console.log('Rated movies:', ratedMovies);
});
