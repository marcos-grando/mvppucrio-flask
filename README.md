### Desenvolvimento Full Stack - PUC-Rio

## MVP Full Stack Básico com Flask: Gerenciamento dos Convidados e Funcionários de Casamento 📋

O MVP foi desenvolvido utilizando Flask para criar um sistema web de gerenciamento de convidados e funcionários de um casamento. O sistema permite que convidados confirmem sua presença e acessem informações sobre o evento, enquanto administradores têm ferramentas para o gerenciamento.

O sistema interage com um banco de dados **SQLite** e possui APIs documentadas via **Swagger** para facilitar a integração e entendimento das funcionalidades.

---

## 🚀 Funcionalidades Principais

### Administradores (ADM)
- Visualizar a lista de convidados e funcionários. (p/ todos funcionários)
- Emitir convites para convidados. (p/ Administrador)
- Adicionar ou remover convidados. (p/ Administrador)
- Adicionar ou remover funcionários (p/ Administrador Geral).

### Convidados (User)
- Criar conta usando o número do convite.
- Visualizar mais informações (mapa, endereço do evento, etc).
- Confirmar ou recusar a presença no evento.


### Lógica Geral
- O processo abaixo é utilizado em diferentes tipos de operações, como criação, atualização ou consulta de dados.

##### Conexão com banco de dados
- Feita utilizando o módulo sqlite3 para conectar ao banco de dados SQLite.
```
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
```

##### Execução de queries SQL
- As APIs executam os comandos SQL (seja UPDATE, SELECT, DELETE, etc) com os dados fornecidos pelo usuário.
```
conteudo_sql = f"UPDATE convidados SET situacao = ? WHERE email = ?"
cursor.execute(conteudo_sql, (user_situacao, user_email))
```

##### Recebendo dados via Fetch
- O front-end utiliza **fetch** para enviar dados para a API.
```
fetch('/user_situacao', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        user_situacao: user_situacao
    })
})
```

##### Finalizando a conexão
- A após executado a query SQL, a transação é confirmada.
```
conn.commit()
```
- Conexão com o banco de dados encerrada ao final de cada API.
```
conn.close()
```

---

## 💾 Banco de Dados

O sistema utiliza um banco de dados **SQLite** com as seguintes tabelas:

### Tabela: `convidados`
| Coluna      | Descrição                         |
|-------------|-----------------------------------|
| id          | Número do convite (chave primária)|
| nome        | Nome do convidado                 |
| idade       | Idade do convidado                |
| designacao  | Tipo de relação (familiar, etc)   |
| mesa        | Número da mesa                    |
| contato     | Número de celular                 |
| situacao    | Aceito, recusado ou pendente      |
| email       | Email do convidado                |
| senha       | Senha criptografada com bcrypt    |

### Tabela: `organizadores`
| Coluna      | Descrição                         |
|-------------|-----------------------------------|
| id          | Identificador (chave primária)    |
| nome        | Nome do organizador               |
| funcao      | Função assumida no evento         |
| email       | Email do funcionário              |
| senha       | Senha criptografada com bcrypt    |

---

## 🛠️ Tecnologias Utilizadas

- [Flask](https://flask.palletsprojects.com/)
- [Flask-CORS](https://flask-cors.readthedocs.io/)
- [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [HTML5](https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5)
- [CSS3](https://developer.mozilla.org/en-US/docs/Web/CSS)
- [SQLite](https://www.sqlite.org/index.html)
- [Bcrypt](https://pypi.org/project/bcrypt/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)

---

## 📂 Estrutura do Projeto

Atendendo à solicitação do professor, organizei o projeto em pastas separadas para back_end e front_end, mantendo uma clara distinção entre os componentes.

```
mvppucrio-flask/
├── back_end/
│   ├── database/
│   │   ├── database-projeto.db # Banco de dados com informações pré-carregadas
│   │   └── database.db         # Banco de dados inicial (opcional)
│   ├── app.py              # Arquivo principal com APIs do Flask
│   └── openapi.json        # Documentação das APIs no padrão OpenAPI
│
├── front_end/
│   ├── estilos/            # Arquivos CSS
│   ├── midia/              # Imagens do projeto
│   ├── scriptsjs/          # Arquivos JavaScript
│   └── templates/          # Templates HTML
├── requirements.txt    # Dependências do projeto
└── README.md           # Documentação do projeto
```

---

## ⚙️ Instalação e Execução

Após clonar ou baixar o projeto, siga as etapas a seguir:

1. **Crie um ambiente virtual e ative**
   ```
   - Windows:
     "python -m venv venv"
     "venv\Scripts\activate"
   - Linux/Mac:
     "python3 -m venv venv"
     "source venv/bin/activate"
   ``` 

2. **Instale as dependências**
   ```
    "pip install -r requirements.txt"
   ```

3. **Execute o servidor Flask**
   ```
   "flask run"
   ```

4. **Acesse o projeto**
   ```
   "http://localhost:5000/"
   ```

5. **Documentação Swagger**
   ```
   "http://localhost:5000/openapi/swagger"
   ```

---

## 📄 Licença

Este projeto está sob a licença MIT.
