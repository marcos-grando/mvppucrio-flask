
window.onload = function() {
    load_section_adm('adm_lista');
}

// É chamado ao clicar na aba desejada, carregando a section correspondente
function load_section_adm(optSection) {
    fetch(`/load_section_adm/${optSection}`, {
        method: 'GET'
    })
    .then(response => response.text())
    .then(html => {
        // Insere o HTML retornado dentro da div section_user
        document.querySelector('#section_adm').innerHTML = html;
    })
    .catch(error => console.error('Erro ao carregar o template:', error));
}


// REMOVER/ADD CONVIDADOS

function remover_convidado(event, user_id, user_nome) {
    event.preventDefault();
    console.log(user_nome, user_id)

    if (confirm(`Deseja remover ${user_nome}?`)) {
        fetch('/adm_remover_convidado', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id : user_id }),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data)
            if (data.success) {
                load_section_adm('adm_lista');
            } else {
                alert(data.mensagem || "Erro na remoção de convidado. Tente mais tarde.");
            }
        })
        .catch(error => console.error('Erro:', error));
    }
}

// É chamado ao clicar em "+", carregando o formulário de novo convite
function load_form_add() {
    fetch('/load_form_add', {
        method: 'GET'
    })
    .then(response => response.text())
    .then(html => {
        document.querySelector('#tfoot-add').innerHTML = html;
    })
    .catch(error => console.error('Erro ao carregar o template:', error));
}

function form_novo_convite(event) {
    event.preventDefault()

    const nome = document.querySelector('input[name="nome"]').value;
    const designacao = document.querySelector('select[name="designacao"]').value;
    const mesa = document.querySelector('input[name="mesa"]').value;

    console.log(nome, designacao, mesa)

    fetch('/novo_convite', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            nome: nome,
            designacao: designacao,
            mesa: mesa
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            load_section_adm('adm_lista');
        } else {
            alert(data.mensagem || "Erro na geração do convite. Tente mais tarde.");
        }
    })
    .catch(error => {
        console.error('Erro:', error);
    });
}




// REMOVER/ADD FUNCIONÁRIOS

function remover_funcionario(event, adm_id, adm_nome) {
    event.preventDefault();
    console.log(adm_nome, adm_id)

    if (confirm(`Deseja remover ${adm_nome}?`)) {
        fetch('/adm_remover_funcionario', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ adm_id : adm_id }),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data)
            if (data.success) {
                load_section_adm('adm_staff');
            } else {
                alert(data.mensagem || "Erro na remoção do funcionário. Tente mais tarde.");
            }
        })
        .catch(error => console.error('Erro:', error));
    }
}

// É chamado ao clicar em "+", carregando o formulário de novo convite
function load_form_add_func() {
    fetch('/load_form_add_func', {
        method: 'GET'
    })
    .then(response => response.text())
    .then(html => {
        document.querySelector('#tfoot-add').innerHTML = html;
    })
    .catch(error => console.error('Erro ao carregar o template:', error));
}

function form_novo_funcionario(event) {
    event.preventDefault()

    const nome = document.querySelector('input[name="nome"]').value;
    const funcao = document.querySelector('input[name="funcao"]').value;
    const email = document.querySelector('input[name="email"]').value;

    console.log(nome, funcao, email)

    fetch('/novo_funcionario', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            nome: nome,
            funcao: funcao,
            email: email
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            load_section_adm('adm_staff');
        } else {
            alert(data.mensagem || "Erro na geração do convite. Tente mais tarde.");
        }
    })
    .catch(error => {
        console.error('Erro:', error);
    });
}

function email_copiar(emailCopiado) {
    const email = emailCopiado.getAttribute('data-copiar');
    navigator.clipboard.writeText(email)
        .then(() => alert('Email copiado!'))
        .catch(err => console.error('Erro ao copiar email: ', err));
}


function user_dados(event, user_id) {
    event.preventDefault();
    
    fetch('/adm_user_dados', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: user_id })
    })
    .then(response => response.text())
    .then(html => {
        document.querySelector('#section_adm').innerHTML = html;
    })
    .catch(error => console.error('Erro ao carregar dados:', error));
}
