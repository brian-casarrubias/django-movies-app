

let signInButton = document.getElementById('js-signin-btn');
let closeIconButton = document.getElementById('js-close-icon');
let loginMenu = document.getElementById('container-login');

let menuOpened = false; // this is the boolean to know if the menu is opened. It will be off by deffault

signInButton.addEventListener('click', () => {

    // if our menu is not opened, then we can open it
    if (!menuOpened){
        // now its set to true, so we cant click open again until we hit the close icon/button
        menuOpened = true;
        loginMenu.classList.add('open-menu');
        console.log(loginMenu)
    }
})

closeIconButton.addEventListener('click', () => {
    if(menuOpened){ // if our menu is opened, then we can close it, if not then we cant
        menuOpened = false; // now that its opened lets set it to false
        loginMenu.classList.remove('open-menu');
        console.log(loginMenu)

    }
});