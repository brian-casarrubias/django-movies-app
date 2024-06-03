
// these are all my buttons, and sorting buttons
let findMoviesBtn = document.getElementById('js-search-movies');
let loadingSpinner = document.getElementById('js-loading-spinner');
let highRatingBtn = document.getElementById('js-toprated');
let leastRatingBtn = document.getElementById('js-leastrated');

// these are my variables to control weather im on one or not
// im only going to be able to click on the btns if they are currently false
//each btn will disable the other, and that will let me access 
let isTop = false;
let isLeast = false;

findMoviesBtn.addEventListener('click', () => {
 
    loadingSpinner.classList.add('show-loader');
})
highRatingBtn.addEventListener('click', () => {
    loadingSpinner.classList.add('show-loader');
})
leastRatingBtn.addEventListener('click', () => {
    loadingSpinner.classList.add('show-loader');
})

function removeSpinner(){
    loadingSpinner.classList.remove('show-loader');
}

document.addEventListener('DOMContentLoaded', function() {
     // Listen to HTMX events to hide the spinner when the request is completed
     document.body.addEventListener('htmx:afterRequest', removeSpinner);

});

