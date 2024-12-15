
window.onload = function() {
    autoridade('user');
    // user_cadastro()
    // adm_cadastro()
}

function autoridade(tipo_acesso) {
    fetch('/autoridade', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ tipo: tipo_acesso })
    })
    .then(response => response.json())
    .then(data => {

        // muda para display flex quando a função "cadastro_user" altera para 'none'
        document.querySelector('.autoridade').style.display = 'flex';

        // remoção e adição da classe modo-select para ativar estilo no login.css
        document.querySelectorAll('.modo').forEach(element => { 
            element.classList.remove('modo-select');
        });
        document.querySelector(`#${tipo_acesso}`).classList.add('modo-select');

        fetch(data.url) // vai fazer a requisição do url /login_user ou o url /login_adm
            .then(response => response.text())
            .then(html => {
                document.querySelector('.login-div').innerHTML = html; // vai inserir os dados dentro de "block conteudo_login" da página determinada pelo tipo_acesso (ou seja, user=login_user, adm=login_adm)

                document.querySelector('form').addEventListener('submit', function(event) {
                    event.preventDefault();
                    
                    const email = document.querySelector('#id-email').value;
                    const senha = document.querySelector('#id-password').value;
                    const numId = document.querySelector('#id-numId') ? document.querySelector('#id-numId').value : '';
                    const tipo_acesso = document.querySelector('.modo-select').id;
                    
                    fetch('/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ email: email, senha: senha, id: numId, tipo: tipo_acesso })
                    })
                    .then(response => response.json())
                    .then(data => {
                        // vai acessar o site se o Flask validar todos os dados como correto (True), se não ou vai apresentar um erro ou vai apresentar os dados inválidos
                        if (data.acessar) {
                            window.location.href = data.acessar // acessar ou user=pag_user ou adm=pag_adm
                        } else if (data.mensagem) { 
                            document.querySelectorAll('.bi-validar').forEach(element => { 
                                element.classList.remove('bi-check', 'bi-x-circle');
                            });
                            alert(data.mensagem);
                        } else {
                            document.querySelectorAll('.bi-validar').forEach(element => { 
                                element.classList.remove('bi-check', 'bi-x-circle');
                            });
                            
                            validar_email = data.login_email ? 'bi-check' : 'bi-x-circle';
                            document.querySelector('#email-div .bi-validar').classList.add(validar_email);

                            validar_senha = data.login_senha ? 'bi-check' : 'bi-x-circle';
                            document.querySelector('#senha-div .bi-validar').classList.add(validar_senha);

                            if (tipo_acesso == 'user') {
                                validar_numId = data.login_numId ? 'bi-check' : 'bi-x-circle';
                                document.querySelector('#numId-div .bi-validar').classList.add(validar_numId);
                            };
                        }
                    })
                    .catch(error => {
                        console.error('Erro:', error);
                    });
                });
            });
    })
    .catch(error => {
        console.error('Erro:', error);
    });
}

