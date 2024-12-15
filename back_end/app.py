from flask import Flask, render_template, jsonify, request, url_for, redirect, session, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import bcrypt
import sqlite3
import os

app = Flask(__name__, template_folder='../front_end/templates', static_folder='../front_end')

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'database/database-projeto.db')   # banco de dados abastecido para visualizar no projeto
# db_path = os.path.join(current_dir, 'database/database.db')   # banco de dados simples com poucas informações

CORS(app)
app.secret_key = os.urandom(24)


SWAGGER_URL = '/openapi/swagger'
API_URL = '/static/openapi.json'
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Swagger APIs"
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
@app.route('/static/openapi.json')
def serve_openapi():
    return send_from_directory('.', 'openapi.json')

# ======================================================
# Abaixo todas as API's utilizadas

@app.route('/')
def index():
    return render_template('index.html')

# ======================================================
# Define se é um convidado ou organizador, e retorna o login correspondente
# ======================================================

@app.route('/autoridade', methods=['POST'])
def autoridade():
    """
        Define qual template vai carregar no index.html.
        Ou seja, se aparece a seção de login para 
        convidados (user) ou para organizadores (adm)
    """
    data = request.get_json()
    tipo_acesso = data.get('tipo')
    if tipo_acesso == 'user':
        url = url_for('login_user')
    elif tipo_acesso == 'adm':
        url = url_for('login_adm')
    else:
        return jsonify({'mensagem': 'Não encontrado!!'}), 400

    return jsonify({'url': url})

@app.route('/login_adm')
def login_adm():
    return render_template('login_adm.html')

@app.route('/login_user')
def login_user():
    return render_template('login_user.html')

# ------------------------------------------------------


# ======================================================
# Valida os dados para fazer login (redirecionando para pag_adm ou pag_user)
# ======================================================

@app.route('/login', methods=['POST'])
def fazendo_login():

    """
        Realiza um login de usuário com bases nas informações fornecidas e no tipo de acesso que está sendo feito;
    
        - Recebe o email, senha, ID digitado pelo usuário que está fazendo login;
        - Recebe o tipo de acesso, ou seja, se é login sendo feito por USER ou ADM;

        Se tipo de acesso for 'adm'
        - Define 'tabela' como 'organizadores';
        - E 'dados_acesso' como 'nome, senha'

        Se tipo de acesso for 'user'
        - define 'tabela' como 'convidados';
        - E 'dados_acesso' como 'nome, senha, id';

        E então segue alguns passos que a API faz:

        1- busca no banco de dados:
        - O email fornecido pelo usuário na tabela definida em "tabela"
        - Retornando se o email existe e corresponde;

        2- Outra busca no banco de dados:
        - Os dados definidos em "dados_acesso" na tabela definida em "tabela";
        - Retornando se esses dados correspondem;

        3- As validações:
        - Cada um dos dados retornados são validadads sobre sua existências;
        - Sua existência retorna True à variável, caso contrário retorna False;

        - Essas validações de True e False são colocadas numa lista;
        - Essa lista então é verificada com um FOR;
        - Se houver algum False na lista, o FOR é quebrado e retorna um erro;

        - Finalizando o FOR, todos os dados são verdadeiros, portanto, o login será feito;
                
        - - valor = recebido (errado ou certo)
        - - valor_db = valor recebido database
        - - login_valor = True ou False

    """

    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')
    numId = data.get('id')
    tipo_acesso = data.get('tipo')
    
    tabela = 'organizadores' if tipo_acesso == 'adm' else 'convidados'
    dados_acesso = 'nome, senha' if tipo_acesso == 'adm' else 'nome, senha, id'

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    conteudo_sql = f"SELECT email FROM {tabela} WHERE email = ?"
    cursor.execute(conteudo_sql, (email,))
    resultado = cursor.fetchone()
    
    if resultado is None:
        conn.close()
        return jsonify({"status": "Erro", "mensagem": "Email não encontrado!"}), 404
    else:
        login_validar = []

        login_email = True
        login_validar.append(login_email)

        conteudo_sql = f"SELECT {dados_acesso} FROM {tabela} WHERE email = ?"
        cursor.execute(conteudo_sql, (email,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado is None:
            return jsonify({"status": "Erro", "mensagem": "Erro ao tentar validar dados! Volte mais tarde."})
        else:
            nome_db = resultado[0]
            senha_db = resultado[1]
            numId_db = resultado[2] if len(resultado) > 2 else None

            login_senha = True if bcrypt.checkpw(senha.encode('utf-8'), senha_db) else False
            login_validar.append(login_senha)

            if numId_db: 
                login_numId = True if int(numId) == numId_db else False 
                login_validar.append(login_numId)
            else: 
                login_numId = ""

            validar = True
            for dados in login_validar:
                if dados == False:
                    validar = False 
                    break
                else:
                    continue

            if validar == True:
                session['email'] = email
                url = url_for('pag_adm', email=email, nome=nome_db) if tipo_acesso == 'adm' else url_for('pag_user', email=email, nome=nome_db)
                return jsonify({"acessar": url}), 200
            else:
                return jsonify({"login_email": login_email, 
                                "login_senha": login_senha, 
                                "login_numId": login_numId}), 401

@app.route('/user_cadastro', methods=['GET'])
def user_cadastro():
    return render_template('cadastro.html')

@app.route('/adm_cadastro', methods=['GET'])
def adm_cadastro():
    return render_template('cadastro_adm.html')

# ------------------------------------------------------


# ======================================================
# Oficializando cadastros de convidados/funcionários
# ======================================================

@app.route('/cadastro_valida_id', methods=['POST'])
def cadastro_valida_id():

    """
        Faz a validação do cadastro com base no ID;
        A API usa o ID para buscar dados no banco de dados;
        É necessário que exista um "pré-cadastro" feito por um ADM;

        cadastro_tipo: 
        - define o tipo de cadastro que está sendo feito;

        cadastro_user:
        - busca o ID na tabela "convidados" e então busca 'email';
        - Se já existir um email = "cadastro já existe"; Se não existir um email vai retornar alguns dados pré cadastrados e apresentar ao usuário;

        cadastro_adm:
        - busca o ID na tabela "organizadores" e então busca 'senha', pois o email deve ser pré cadastrado por um ADM;
        - se já existir uma senha = "cadastro já existe"; Se não existir uma senha irá retornar com alguns dados pré cadastrados e apresentar ao usuário;
    """

    data = request.get_json()
    cadastro_id = data.get('cadastro_id')
    cadastro_tipo = data.get('cadastro_tipo')

    if cadastro_tipo not in ('cadastro_user', 'cadastro_adm'):
        return jsonify({'status': 'error1'}), 400  # Erro caso o cadastro_tipo não tiver sido definido no parâmetro em JS
    if not cadastro_id:
        return jsonify({'status': 'error2'}), 400  # Erro de 'Convite/ID não fornecido'

    with sqlite3.connect(db_path, timeout=10) as conn:
        cursor = conn.cursor()
        
        if cadastro_tipo == 'cadastro_user':
            conteudo_sql = "SELECT email FROM convidados WHERE id = ?"
            cursor.execute(conteudo_sql, (cadastro_id,))
            validar = cursor.fetchone()
            
            if not validar:
                return jsonify({'status': 'error2'})  # Erro de 'Convite/ID não encontrado'
            email_encontrado = validar[0]
            if email_encontrado:
                return jsonify({'status': 'error3'})  # Email já registrado

            conteudo_sql2 = 'SELECT nome, designacao, mesa FROM convidados WHERE id = ?'
            cursor.execute(conteudo_sql2, (cadastro_id,))
            resultado = cursor.fetchone()

            cadastro_nome = resultado[0]
            cadastro_desig = resultado[1]
            cadastro_mesa = resultado[2]

            return jsonify({
                'status': 'success',
                'cadastro_nome': cadastro_nome,
                'cadastro_desig': cadastro_desig,
                'cadastro_mesa': cadastro_mesa
            })

        elif cadastro_tipo == 'cadastro_adm':
            conteudo_sql = "SELECT email, senha FROM organizadores WHERE id = ?"
            cursor.execute(conteudo_sql, (cadastro_id,))
            validar = cursor.fetchone()

            if not validar:
                return jsonify({'status': 'error2'}), 400  # ID não encontrado
            email_encontrado, senha_encontrada = validar

            if not email_encontrado:
                return jsonify({'status': 'error2'}), 400  # Email não encontrado
            if senha_encontrada is not None:
                return jsonify({'status': 'error3'}), 400  # Senha já registrada

            conteudo_sql2 = 'SELECT nome, funcao, email FROM organizadores WHERE id = ?'
            cursor.execute(conteudo_sql2, (cadastro_id,))
            resultado = cursor.fetchone()

            cadastro_nome = resultado[0]
            cadastro_funcao = resultado[1]
            cadastro_email = resultado[2]

            return jsonify({
                'status': 'success',
                'cadastro_nome': cadastro_nome,
                'cadastro_funcao': cadastro_funcao,
                'cadastro_email': cadastro_email
            })
        
    return jsonify({'status': 'error1'})

@app.route('/novo_cadastro', methods=['PUT'])
def novo_cadastro():

    """
        Processa o novo cadastro com base no ID fornecido.

        Para o usuário da página web será como um novo cadastro, para os dados aqui será um UPDATE (ou seja, atualização de dados);

        - Faz o recebimento dos dados preenchidos pelo usuário (de acordo com o 'cadastro_tipo');
        - faz uma busca no banco de dados se existe o email do usuário;
        - Torna a senha digitados em qualquer um dos dois cadastro em senha criptografada com bcrypt

        cadastro_user:
        - Atualiza os dados com base no ID da tabela 'convidados' (sendo eles nulos ou pré cadastrados): idade, contato, email, senha;

        cadastro_adm:
        - Atualiza a 'senha' com base no ID da tabela 'organizadores' (sendo nula ou pré cadastrada);
    """

    data = request.get_json()
    cadastro_id = data.get('cadastro_id')
    cadastro_tipo = data.get('cadastro_tipo')

    if cadastro_tipo not in ('cadastro_user', 'cadastro_adm'):
        return jsonify({'status': 'error1'}), 400  # Erro caso o cadastro_tipo não tiver sido definido no parâmetro em JS
    if not cadastro_id:
        return jsonify({'status': 'error2'}), 400  # Erro de 'Convite/ID não fornecido'

    if cadastro_tipo == 'cadastro_user':
        cadastro_idade = data.get('cadastro_idade')
        cadastro_contato = data.get('cadastro_contato')
        cadastro_email = data.get('cadastro_email')
        cadastro_senha = data.get('cadastro_senha')
    elif cadastro_tipo == 'cadastro_adm':
        cadastro_senha = data.get('cadastro_senha')

    with sqlite3.connect(db_path, timeout=10) as conn:
        cursor = conn.cursor()

        if cadastro_tipo == 'cadastro_user':
            conteudo_sql = "SELECT 1 FROM organizadores WHERE email = ? UNION SELECT 1 FROM convidados WHERE email = ?"
            cursor.execute(conteudo_sql, (cadastro_email, cadastro_email))
            email_existe = cursor.fetchone()
            if email_existe:
                return jsonify({"mensagem": "Email já cadastrado em nosso banco de dados."}), 400

        cadastro_senha = bcrypt.hashpw(cadastro_senha.encode('utf-8'), bcrypt.gensalt())

        if cadastro_tipo == 'cadastro_user':
            conteudo_sql2 = "UPDATE convidados SET idade = ?, contato = ?, email = ?, senha = ? WHERE id = ?"
            cursor.execute(conteudo_sql2, (cadastro_idade, cadastro_contato, cadastro_email, cadastro_senha, cadastro_id))
            conn.commit()
            convidado_commit = cursor.rowcount

        elif cadastro_tipo == 'cadastro_adm':
            conteudo_sql2 = "UPDATE organizadores SET senha = ? WHERE id = ?"
            cursor.execute(conteudo_sql2, (cadastro_senha, cadastro_id))
            conn.commit()
            convidado_commit = cursor.rowcount

        if convidado_commit > 0:
            return jsonify({"success": True, "autoridade": "user"})
        else:
            return jsonify({"success": False, "mensagem": "Algo deu errado"}), 500


# ======================================================
# Login como USER_MODE

@app.route('/user_mode/pag_user', methods=['GET'])
def pag_user():
    user_email = session.get('email')
    if not user_email:
        return redirect(url_for('index'))

    return render_template('user_mode/pag_user.html')

@app.route('/load_section_user/<opt_section>', methods=['GET'])
def load_section_user(opt_section):

    """
        load_section para login feito por "convidados"

        Carrega uma seção específica com base na escolha de "aba" do usuário;
        Essas abas estão presente no "menu" de navegação da página HTML;

        - Inicialmente faz a verificaçao se a opt_section está presente;
        - Estando presente, leva o valor para a url, tornando assim uma url para um template;
        
        - Faz a verificação do email do usuário;
        - Com base nesse email, faz uma busca na tabela "convidados" retornando o ID, nome, designacao, mesa, contato e situacao;

        - faz a renderização do template posto na 'url', junto dos dados pessoais retornados;
    """

    if not opt_section:
        return jsonify({"mensagem": "Ocorreu um erro ao carregar o conteúdo! Volte mais tarde"}), 500
    url = f"user_mode/{opt_section}.html"

    # user_email = session.get('email') if session.get('email') else redirect(url_for('index'))
    user_email = session.get('email')
    if not user_email:
        return redirect(url_for('index'))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    conteudo_sql = f"SELECT id, nome, designacao, mesa, contato, situacao FROM convidados WHERE email = ?"
    cursor.execute(conteudo_sql, (user_email,))
    user_resultado = cursor.fetchone()
    conn.close()

    if not user_resultado:
        return jsonify({"mensagem": "Usuário não encontrado ou email errado. Tente novamente."}), 404

    return render_template(url,user_id = user_resultado[0],
                               user_nome = user_resultado[1],
                               user_designacao = user_resultado[2],
                               user_mesa = user_resultado[3],
                               user_contato = user_resultado[4],
                               user_situacao = user_resultado[5])


@app.route('/user_situacao', methods=['POST'])
def confirmar_presenca():

    """
        OBS: dados pessoais já carregados pela função "load_section_user(opt_section)"

        - A API confirmar_presenca() recebe o email da sessão;
        - E recebe o valor do javascript de "Aceito" ou "Recusado", feito por um formulário na página HTML;

        - Com esse valor, a API faz a atualização na tabela "convidados" do usuário logado co base no email e commita;
        
        - Após commitar, se deu certo, envia para JS "user_dados" para que o Javascript recarregue a section (atualizando dinamicamente o conteúdo da "situacao");
    """

    data = request.get_json()
    user_situacao = data.get('user_situacao')
    user_email = session.get('email')

    if not user_situacao:
        return jsonify({"mensagem": "Ocorreu um erro! Volte mais tarde"})
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    conteudo_sql = f"UPDATE convidados SET situacao = ? WHERE email = ?"
    cursor.execute(conteudo_sql, (user_situacao, user_email,))
    
    conn.commit()
    user_commit = cursor.rowcount
    conn.close()

    if user_commit > 0:
        # Retorne um status de sucesso e o nome da seção que deseja carregar
        return jsonify({"success": True, "section": "user_dados"})
    else:
        return jsonify({"success": False, "mensagem": "Algo deu errado"})

# Fim das funcionalidades como USER_MODE
# ======================================================


# ======================================================
# Login como ADM_MODE

@app.route('/adm_mode/pag_adm')
def pag_adm():

    """
        Carrega a página de ADM após ser feito login como 'adm';
    """

    adm_email = session.get('email')
    if not adm_email:
        return redirect(url_for('index'))
    return render_template('adm_mode/pag_adm.html')

@app.route('/load_section_adm/<opt_section>', methods=['GET'])
def load_section_adm(opt_section):

    """
        load_section para login feito por "organizadores"

        Carrega uma seção específica com base na escolha de "aba" do usuário;
        Essas abas estão presente no "menu" de navegação da página HTML;

        - Inicialmente faz a verificaçao se a opt_section está presente;
        - Estando presente, leva o valor para a url, tornando assim uma url para um template;
        
        - Faz a verificação do email do usuário;
        - Com base nesse email, faz uma busca na tabela "organizadores" retornando nome e função;

        - Além disso fazer uma sério de busca no banco de dados:
        - "lista_staff": Lista de todos os organizadores com IDs, nomes, funções e emails.
        - "total_staff": Número total de organizadores.
        - "lista_funcao": Contagem de organizadores agrupados por função.
        - "lista_convidados": Lista de todos os convidados com IDs, nomes, designações e situações.
        - "total_convites": Número total de convidados.
        - "total_aceitos": Número de convidados com situação 'Aceito'.
        - "total_pendentes": Número de convidados com situação 'Pendente'.
        - "total_recusados": Número de convidados com situação 'Recusado'.
        - "total_mesas": Número total de mesas distintas.
        - "user_mesas": Contagem de convidados por mesa, agrupada por mesa.

        - faz a renderização do template posto na 'url', junto dos dados pessoais retornados;
    """

    if not opt_section:
        return jsonify({"mensagem": "Ocorreu um erro ao carregar o conteúdo! Volte mais tarde"})
    url = f"adm_mode/{opt_section}.html"

    adm_email = session.get('email')
    if not adm_email:
        return redirect(url_for('index'))

    with sqlite3.connect(db_path, timeout=10) as conn: # foi a solução que encontrei para lidar com acessos simultâneos no db
        cursor = conn.cursor()

        conteudo_sql = "SELECT nome, funcao FROM organizadores WHERE email = ?"
        cursor.execute(conteudo_sql, (adm_email,))
        adm_resultado = cursor.fetchone()

        cursor.execute("SELECT id, nome, funcao, email FROM organizadores")
        lista_staff = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM organizadores")
        total_staff = cursor.fetchone()[0]

        cursor.execute("SELECT funcao, COUNT(*) AS in_funcao FROM organizadores GROUP BY funcao")
        lista_funcao = cursor.fetchall()

        cursor.execute("SELECT id, nome, designacao, situacao FROM convidados")
        lista_convidados = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM convidados")
        total_convites = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM convidados WHERE situacao = 'Aceito'")
        total_aceitos = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM convidados WHERE situacao = 'Pendente'")
        total_pendentes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM convidados WHERE situacao = 'Recusado'")
        total_recusados = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT mesa) AS total_mesas FROM convidados")
        total_mesas = cursor.fetchone()[0]
        cursor.execute("SELECT mesa, COUNT(*) AS in_mesa FROM convidados GROUP BY mesa")
        user_mesas = cursor.fetchall()
        
    if not adm_resultado:
        return jsonify({"mensagem": "Usuário não encontrado ou email errado. Tente novamente."})
    return render_template(url, adm_nome=adm_resultado[0], 
                                adm_funcao=adm_resultado[1],
                                lista_convidados=lista_convidados,
                                total_convites=total_convites,
                                total_aceitos=total_aceitos,
                                total_pendentes=total_pendentes,
                                total_recusados=total_recusados,
                                total_mesas=total_mesas,
                                user_mesas=user_mesas,
                                lista_staff=lista_staff,
                                total_staff=total_staff,
                                lista_funcao=lista_funcao)

# -------------------------------
# remoção e adição de convidados

@app.route('/adm_remover_convidado', methods=['DELETE'])
def adm_remover_convidado():

    """
        Remove um convidado da tabela "convidados" com base no ID fornecido por um ADM;
        - user_id: ID do convidado a ser removido;
    """

    data = request.get_json()
    user_id = data.get('user_id')

    if user_id:
        # Conectar ao banco de dados e deletar o item
        with sqlite3.connect(db_path, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM convidados WHERE id = ?", (user_id,))
            conn.commit()

            return jsonify({"success": True}) if cursor.rowcount > 0 else jsonify({"success": False, "mensagem": "Item não encontrado"})
    else:
        return jsonify({"success": False, "mensagem": "Nº de convite inválido"})

@app.route('/load_form_add')
def load_form_add():

    """
        Carrega o template na "janelinha" de "novo convite"
    """

    return render_template('adm_mode/adm_lista_registro.html')

@app.route('/novo_convite', methods=['POST'])
def adm_novo_convite():

    """
        Adiciona um novo convite na tabela "convidados";
        - Basicamente, faz um "pré cadastro";

        - A API recebe os valores de nome, designação e mesa, fornecido pelo ADM;
        - Então com esses valores insere um novo registro na tabela "convidados";

        - Se commitado corretamente, retorna "adm_lista" para ser carregado no javascript pela API "load_section_adm()";
    """

    data = request.get_json()
    convite_nome = data.get('nome')
    convite_designacao = data.get('designacao')
    convite_mesa = data.get('mesa')

    if not convite_nome or not convite_designacao or not convite_mesa:
        return jsonify({"mensagem": "Todos os campos são obrigatórios!"}), 400

    with sqlite3.connect(db_path, timeout=10) as conn:
        cursor = conn.cursor()
        conteudo_sql = "INSERT INTO convidados (nome, designacao, mesa) VALUES (?, ?, ?)"
        cursor.execute(conteudo_sql, (convite_nome, convite_designacao, convite_mesa,))
        conn.commit()
        convite_commit = cursor.rowcount

    if convite_commit > 0:
        return jsonify({"success": True, "section": "adm_lista"})
    else:
        return jsonify({"success": False, "mensagem": "Algo deu errado"}), 500

# -------------------------------


# -------------------------------
# remoção e adição de funcionários

@app.route('/adm_remover_funcionario', methods=['DELETE'])
def adm_remover_funcionario():
    
    """
        Remove um funcionário da tabela "organizadores" com base no ID fornecido por um ADM;
        - adm_id: ID do funcionário a ser removido;
    """
    
    data = request.get_json()
    adm_id = data.get('adm_id')

    if adm_id:
        # Conectar ao banco de dados e deletar o item
        with sqlite3.connect(db_path, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM organizadores WHERE id = ?", (adm_id,))
            conn.commit()

            return jsonify({"success": True}) if cursor.rowcount > 0 else jsonify({"success": False, "mensagem": "Item não encontrado"})
    else:
        return jsonify({"success": False, "mensagem": "Nº de convite inválido"})

@app.route('/load_form_add_func')
def load_form_add_func():

    """
        Carrega o template na "janelinha" de "novo funcionário"
    """
        
    return render_template('adm_mode/adm_staff_registro.html')

@app.route('/novo_funcionario', methods=['POST'])
def adm_novo_funcionario():

    """
        Adiciona um novo funcionário na tabela "organizadores";
        - Basicamente, faz um "pré cadastro";

        - A API recebe os valores de nome, função e email, fornecido pelo ADM;
        - Então com esses valores insere um novo registro na tabela "organizadores";

        - Se commitado corretamente, retorna "adm_staff" para ser carregado no javascript pela API "load_section_adm()";
    """

    data = request.get_json()
    funcionario_nome = data.get('nome')
    funcionario_funcao = data.get('funcao')
    funcionario_email = data.get('email')

    if not funcionario_nome or not funcionario_funcao:
        return jsonify({"mensagem": "Faltou alguma informação, tente novamente."}), 400

    with sqlite3.connect(db_path, timeout=10) as conn:
        cursor = conn.cursor()

        if funcionario_email:
            conteudo_sql = "SELECT 1 FROM organizadores WHERE email = ? UNION SELECT 1 FROM convidados WHERE email = ?"
            cursor.execute(conteudo_sql, (funcionario_email, funcionario_email))
            email_existe = cursor.fetchone()
            if email_existe:
                return jsonify({"mensagem": "Email já cadastrado em nosso banco de dados."}), 400

        conteudo_sql2 = "INSERT INTO organizadores (nome, funcao, email) VALUES (?, ?, ?)"
        cursor.execute(conteudo_sql2, (funcionario_nome, funcionario_funcao, funcionario_email,))
        conn.commit()
        funcionario_commit = cursor.rowcount

    if funcionario_commit > 0:
        return jsonify({"success": True, "section": "adm_staff"})
    else:
        return jsonify({"success": False, "mensagem": "Algo deu errado"}), 500

@app.route('/adm_user_dados', methods=['POST'])
def adm_user_dados():

    """
        Essa API é acionada junto com função javascript pelo ícone de "busca" que fica ao lado do dos nomes dos convidados;

        - A API recebe o valor do ID do convidado que o ADM clicou; 
        
        - Com esse ID faz uma busca completa com todos os dados do convidado;

        - Além disso, faz uma busca de todos os outros convidados que estão na mesma mesa, retornando o nome e função de cada convidado;
    """

    data = request.get_json()
    user_id = data.get('user_id')

    if user_id:
        with sqlite3.connect(db_path, timeout=10) as conn:
            cursor = conn.cursor()

            conteudo_sql = "SELECT id, nome, idade, designacao, mesa, situacao, contato, email FROM convidados WHERE id = ?"
            cursor.execute(conteudo_sql, (user_id,))
            dados_resultado = cursor.fetchone()

            conteudo_sql2 = "SELECT nome, designacao FROM convidados WHERE mesa = (SELECT mesa FROM convidados WHERE id = ?)"
            cursor.execute(conteudo_sql2, (user_id,))
            dados_mesa = cursor.fetchall()

            if dados_resultado:
                return render_template('adm_mode/adm_dados.html', dados_resultado=dados_resultado, dados_mesa=dados_mesa)
            else:
                return jsonify({"success": False, "mensagem": "Dados não encontrados."}), 404
    else:
        return jsonify({"success": False, "mensagem": "Falha ao carregar dados."})

# -------------------------------

# Fim das funcionalidades como ADM_MODE
# ======================================================

@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('nome', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='localhost', port=1234, debug=True)
