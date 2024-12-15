document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('.bi-exit').addEventListener('click', () => {
        fetch('/logout', {
            method: 'GET',
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            }
        })
        .catch(error => console.error('Erro ao fazer logout:', error));
    });
});
