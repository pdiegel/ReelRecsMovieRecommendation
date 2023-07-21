document.addEventListener('DOMContentLoaded', function() {
    let movies = JSON.parse(document.getElementById('json-data').textContent);

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

            const movieName = document.createElement('h2');
            movieName.classList.add('movie-name');
            movieName.textContent = movie.title + " " + releaseYear;

            const movieDescription = document.createElement('p');
            movieDescription.classList.add('movie-description');
            movieDescription.textContent = movie.overview;

            movieInfo.append(movieName, movieDescription);
            movieCard.append(moviePoster, movieInfo);

            document.getElementById('movie-list').append(movieCard);
        });
    } else {
        console.error('Error fetching movies:', "movies is not an array");
    }
});