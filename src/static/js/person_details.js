document.addEventListener('DOMContentLoaded', () => {
    const parsedElements = ['person-info', 'person-portraits', 'person-tagged-images', 'person-movie-credits']
        .map(id => [id, JSON.parse(document.getElementById(id).textContent)]);
    const parsedData = Object.fromEntries(parsedElements);
    const { 'person-info': personDetails, 'person-portraits': personPortraits, 'person-tagged-images': personTaggedImages, 'person-movie-credits': personMovieCredits } = parsedData;
    console.log(personDetails);
    console.log(personPortraits);
    console.log(personTaggedImages);
    console.log(personMovieCredits);

    displayPersonDetailPage(personDetails, personPortraits, personTaggedImages, personMovieCredits);
});

function displayPersonDetailPage(personDetails, personPortraits, personTaggedImages, personMovieCredits) {
    createPersonDetails(personDetails, personPortraits, personTaggedImages, personMovieCredits);
}

function createPersonDetails(personDetails, personPortraits, personTaggedImages, personMovieCredits) {
    const person = personDetails;
    const portraitPath = "https://image.tmdb.org/t/p/original" + person.profile_path;

    const personPortrait = document.createElement('img');
    personPortrait.classList.add('person-portrait');
    personPortrait.src = portraitPath;

    const personInfo = document.createElement('div');
    personInfo.classList.add('person-info');

    const personName = document.createElement('h2');
    personName.textContent = person.name;

    const biographyHeader = document.createElement('h3');
    biographyHeader.textContent = "Biography";

    const biographyText = person.biography.replace(/\n/g, '<br>');

    const personBiography = document.createElement('p');
    personBiography.innerHTML = biographyText;

    personInfo.append(personName, biographyHeader, personBiography);

    document.getElementById('person-banner-wrapped').append(personPortrait, personInfo);
    createPersonImages(personPortraits);
    createPersonTaggedImages(personTaggedImages);
    createPersonMovieCredits(personMovieCredits);
}

function createPersonImages(personPortraits) {
    personPortraits = personPortraits.profiles;

    const portraitContainer = document.createElement('div');
    portraitContainer.classList.add('person-portraits');

    if (Array.isArray(personPortraits)) {
        personPortraits.forEach(portrait => {
            let portraitPath = "https://image.tmdb.org/t/p/original" + portrait.file_path;
            let portraitImage = document.createElement('img');
            portraitImage.classList.add('person-image');
            portraitImage.src = portraitPath;
            portraitContainer.append(portraitImage);
        });
    }
    document.getElementById('person-images').append(portraitContainer);
}

function createPersonTaggedImages(personTaggedImages) {
    personTaggedImages = personTaggedImages.results;
    console.log("personTaggedImages: ", personTaggedImages)

    const taggedImagesContainer = document.createElement('div');
    taggedImagesContainer.classList.add('person-tagged-images');

    if (Array.isArray(personTaggedImages)) {
        personTaggedImages.forEach(image => {
            let taggedImagePath = "https://image.tmdb.org/t/p/original" + image.file_path;
            let taggedImage = document.createElement('img');
            taggedImage.classList.add('person-tagged-image');
            taggedImage.src = taggedImagePath;
            taggedImagesContainer.append(taggedImage);
        });
    }
    document.getElementById('person-tagged-images-div').append(taggedImagesContainer);

}

function createPersonMovieCredits(personMovieCredits) {
    personMovieCredits = personMovieCredits.cast;
    console.log("personMovieCredits: ", personMovieCredits)

    const movieCreditContainer = document.createElement('div');
    movieCreditContainer.classList.add('person-movie-credit-container');

    if (Array.isArray(personMovieCredits)) {
        personMovieCredits.forEach(movieCredit => {
            if (createMovieCreditDiv(movieCredit) == null) {
                return;
            }
            movieCreditContainer.append(createMovieCreditDiv(movieCredit));
        });
    }
    document.getElementById('person-movie-credit-div').append(movieCreditContainer);
}

function createMovieCreditDiv(movieCredit) {
    const movie = document.createElement('div');
    movie.classList.add('person-movie-credit');
    const movieLink = document.createElement('a');
    const moviePoster = document.createElement('img');
    const movieName = document.createElement('h5');
    moviePoster.classList.add('person-movie-credit-poster');
    movieName.textContent = movieCredit.title;

    if (movieCredit.poster_path == null) {
        return;
    }

    moviePoster.src = "https://image.tmdb.org/t/p/w150_and_h225_bestv2" + movieCredit.poster_path;
    movieLink.href = "/movie/" + movieCredit.id;
    movieLink.append(moviePoster);
    movie.append(movieLink, movieName);
    return movie;
}