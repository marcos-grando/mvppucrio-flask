
function adm_cadastro() {

    fetch('/adm_cadastro', {
        method: 'GET'
    })
    .then(response => response.text())
    .then(html => {
        // tira as divs "convidado(a)" e "organizador(a)""
        document.querySelector('.autoridade').style.display = 'none';
        document.querySelector('.login-div').innerHTML = html;
    })
    .catch(error => console.error('Erro ao carregar dados:', error));
}
function user_cadastro() {
    fetch('/user_cadastro', {
        method: 'GET'
    })
    .then(response => response.text())
    .then(html => {
        // tira as divs "convidado(a)" e "organizador(a)""
        document.querySelector('.autoridade').style.display = 'none';
        document.querySelector('.login-div').innerHTML = html;
    })
    .catch(error => console.error('Erro ao carregar dados:', error));
}

function cadastro_valida_id(cadastro_tipo) {
    const cadastro_id = document.querySelector('#cadastro-id').value;

    fetch('/cadastro_valida_id', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            cadastro_id: cadastro_id,
            cadastro_tipo: cadastro_tipo
         })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'error1') {
            alert('Tipo de cadastro não definido. Por favor fale com nosso suporte.');

        } else if (data.status === 'error2') {
            alert('Convite não encontrado.');

        } else if (data.status === 'error3') {
            alert('Convite já registrado.');

        } else if (data.status === 'success') {
            // Atualiza os campos de nome, designação e mesa dinamicamente
            if (cadastro_tipo === 'cadastro_user') {
                document.querySelector('#cadastro-nome').value = data.cadastro_nome;
                document.querySelector('#cadastro-designacao').value = data.cadastro_desig;
                document.querySelector('#cadastro-mesa').value = data.cadastro_mesa;

                document.querySelector('#cadastro-contato').readOnly = false;
                document.querySelector('#cadastro-email').readOnly = false;
                document.querySelector('#cadastro-senha').readOnly = false;

            } else if (cadastro_tipo === 'cadastro_adm') {
                document.querySelector('#cadastro-nome').value = data.cadastro_nome;
                document.querySelector('#cadastro-funcao').value = data.cadastro_funcao;
                document.querySelector('#cadastro-email').value = data.cadastro_email;

                document.querySelector('#cadastro-senha').readOnly = false;
            }
        }
    })
    .catch(error => {
        console.error('Erro:', error);
    });
}

function formatarTelefone(input) {
    let valor = input.value.replace(/\D/g, ''); // Remove tudo que não é dígito

    if (valor.length <= 2) {
        input.value = `(${valor}`;
    } else if (valor.length <= 5) {
        input.value = `(${valor.slice(0, 2)}) ${valor.slice(2)}`;
    } else if (valor.length <= 10) {
        input.value = `(${valor.slice(0, 2)}) ${valor.slice(2, 7)}-${valor.slice(7)}`;
    } else {
        input.value = `(${valor.slice(0, 2)}) ${valor.slice(2, 7)}-${valor.slice(7, 11)}`;
    }
}

function novo_cadastro(event, cadastro_tipo) {
    event.preventDefault();

    const cadastro_id = document.querySelector('#cadastro-id').value;
    const cadastro_senha = document.querySelector('#cadastro-senha').value;

    if (cadastro_senha.length < 2) {
        event.preventDefault();
        alert('Dados insuficientes ou senha menor que 2 caracteres.');
        return
    }

    const validar = {
        cadastro_id: cadastro_id,
        cadastro_senha: cadastro_senha,
        cadastro_tipo: cadastro_tipo
    }

    if (cadastro_tipo === 'cadastro_user') {
        validar.cadastro_idade = document.querySelector('#cadastro-idade').value;
        validar.cadastro_contato = document.querySelector('#cadastro-contato').value;
        validar.cadastro_email = document.querySelector('#cadastro-email').value;
    }

    fetch('/novo_cadastro', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify( validar )
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (cadastro_tipo == 'cadastro_user') {
                autoridade('user');
            } else if (cadastro_tipo == 'cadastro_adm') {
                autoridade('adm')
            } else {
                console.log('erro')
            }
            
        } else {
            alert(data.mensagem || "Erro na geração do convite. Tente mais tarde.");
        }
    })
    .catch(error => {
        console.error('Erro:', error);
    });
}