
window.onload = function() {
    load_section_user('user_sobre');
}

function load_section_user(optSection) {
    fetch(`/load_section_user/${optSection}`, {
        method: 'GET'
    })
    .then(response => response.text())
    .then(html => {
        // Insere o HTML retornado dentro da div section_user
        document.querySelector('#section_user').innerHTML = html;
    })
    .catch(error => console.error('Erro ao carregar o template:', error));
}

function chama_load_section(event) {
    event.preventDefault();

    const user_situacao = document.querySelector('input[name="user_situacao"]:checked').value;

    fetch('/user_situacao', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_situacao: user_situacao
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            load_section_user('user_dados');
        } else {
            alert(data.mensagem || "Erro ao processar a solicitação.");
        }
    })
    .catch(error => {
        console.error('Erro:', error);
    });
}