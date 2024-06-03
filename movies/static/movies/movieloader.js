
let findMoviesBtn = document.getElementById('js-search-movies');
let loadingSpinner = document.getElementById('js-loading-spinner');

findMoviesBtn.addEventListener('click', () => {
    loadingSpinner.classList.add('show-loader');
})