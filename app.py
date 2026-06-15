from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)


# ──────────────────────────────────────────
# Conexão com o banco
# ──────────────────────────────────────────
def conectar():
    port_env = os.getenv('MYSQLPORT')
    # Evita quebrar com int(None) se a variável não estiver configurada
    port = int(port_env) if port_env else 3306
    
    return mysql.connector.connect(
        host=os.getenv('MYSQLHOST'),
        user=os.getenv('MYSQLUSER'),
        password=os.getenv('MYSQLPASSWORD'),
        database=os.getenv('MYSQL_DATABASE'),
        port=port,
        autocommit=False  # commit manual para controle transacional
    )


# ──────────────────────────────────────────
# Página inicial
# ──────────────────────────────────────────
@app.route('/')
def index():
    return render_template('siteReforco.html')


# ══════════════════════════════════════════
# ALUNOS
# ══════════════════════════════════════════

@app.route('/api/alunos', methods=['GET'])
def get_alunos():
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM alunos")
        alunos = cursor.fetchall()
        return jsonify(alunos), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


@app.route('/api/alunos/<int:id_aluno>', methods=['GET'])
def get_aluno(id_aluno):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM alunos WHERE id_aluno = %s", (id_aluno,))
        aluno = cursor.fetchone()
        if not aluno:
            return jsonify({"erro": "Aluno não encontrado"}), 404
        return jsonify(aluno), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


@app.route('/api/alunos', methods=['POST'])
def add_aluno():
    dados = request.get_json() or request.form

    nome = dados.get('nome')
    email = dados.get('email')
    telefone = dados.get('telefone')
    nivel = dados.get('nivel')

    if not nome:
        return jsonify({"erro": "Nome é obrigatório"}), 400
    if not email:
        return jsonify({"erro": "Email é obrigatório"}), 400

    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO alunos (nome, email, telefone, nivel) VALUES (%s, %s, %s, %s)",
            (nome, email, telefone, nivel)
        )
        conexao.commit()
        return jsonify({"mensagem": "Aluno cadastrado com sucesso!"}), 201
    except Exception as e:
        if conexao:
            conexao.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


@app.route('/api/alunos/<int:id_aluno>', methods=['PUT'])
def update_aluno(id_aluno):
    dados = request.get_json() or request.form

    nome = dados.get('nome')
    email = dados.get('email')
    telefone = dados.get('telefone')
    nivel = dados.get('nivel')

    if not nome:
        return jsonify({"erro": "Nome é obrigatório"}), 400
    if not email:
        return jsonify({"erro": "Email é obrigatório"}), 400

    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
            """UPDATE alunos
               SET nome = %s, email = %s, telefone = %s, nivel = %s
               WHERE id_aluno = %s""",
            (nome, email, telefone, nivel, id_aluno)
        )
        if cursor.rowcount == 0:
            return jsonify({"erro": "Aluno não encontrado"}), 404
        conexao.commit()
        return jsonify({"mensagem": "Aluno atualizado com sucesso!"}), 200
    except Exception as e:
        if conexao:
            conexao.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


@app.route('/api/alunos/<int:id_aluno>', methods=['DELETE'])
def delete_aluno(id_aluno):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM alunos WHERE id_aluno = %s", (id_aluno,))
        if cursor.rowcount == 0:
            return jsonify({"erro": "Aluno não encontrado"}), 404
        conexao.commit()
        return jsonify({"mensagem": "Aluno removido com sucesso!"}), 200
    except Exception as e:
        if conexao:
            conexao.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# ══════════════════════════════════════════
# CURSOS
# ══════════════════════════════════════════

@app.route('/api/cursos', methods=['GET'])
def get_cursos():
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cursos")
        cursos = cursor.fetchall()
        return jsonify(cursos), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


@app.route('/api/cursos/<int:id_curso>', methods=['GET'])
def get_curso(id_curso):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cursos WHERE id_curso = %s", (id_curso,))
        curso = cursor.fetchone()
        if not curso:
            return jsonify({"erro": "Curso não encontrado"}), 404
        return jsonify(curso), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


@app.route('/api/cursos', methods=['POST'])
def add_curso():
    dados = request.get_json() or request.form

    if not dados.get('nome'):
        return jsonify({"erro": "Nome do curso é obrigatório"}), 400
    if not dados.get('nivel'):
        return jsonify({"erro": "Nível é obrigatório"}), 400
    if not dados.get('vagas_totais'):
        return jsonify({"erro": "Quantidade de vagas é obrigatória"}), 400

    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO cursos (nome, nivel, vagas_totais) VALUES (%s, %s, %s)",
            (dados.get('nome'), dados.get('nivel'), dados.get('vagas_totais'))
        )
        conexao.commit()
        return jsonify({"mensagem": "Curso cadastrado com sucesso!"}), 201
    except Exception as e:
        if conexao:
            conexao.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


@app.route('/api/cursos/<int:id_curso>', methods=['PUT'])
def update_curso(id_curso):
    dados = request.get_json() or request.form

    if not dados.get('nome'):
        return jsonify({"erro": "Nome do curso é obrigatório"}), 400
    if not dados.get('nivel'):
        return jsonify({"erro": "Nível é obrigatório"}), 400
    if not dados.get('vagas_totais'):
        return jsonify({"erro": "Quantidade de vagas é obrigatória"}), 400

    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
            """UPDATE cursos
               SET nome = %s, nivel = %s, vagas_totais = %s
               WHERE id_curso = %s""",
            (dados.get('nome'), dados.get('nivel'), dados.get('vagas_totais'), id_curso)
        )
        if cursor.rowcount == 0:
            return jsonify({"erro": "Curso não encontrado"}), 404
        conexao.commit()
        return jsonify({"mensagem": "Curso updated com sucesso!"}), 200
    except Exception as e:
        if conexao:
            conexao.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


@app.route('/api/cursos/<int:id_curso>', methods=['DELETE'])
def delete_curso(id_curso):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM cursos WHERE id_curso = %s", (id_curso,))
        if cursor.rowcount == 0:
            return jsonify({"erro": "Curso não encontrado"}), 404
        conexao.commit()
        return jsonify({"mensagem": "Curso removido com sucesso!"}), 200
    except Exception as e:
        if conexao:
            conexao.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# ══════════════════════════════════════════
# MATRÍCULAS
# ══════════════════════════════════════════

@app.route('/api/matriculas', methods=['GET'])
def get_matriculas():
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                m.id_matricula,
                a.nome AS aluno,
                c.nome AS curso,
                m.data_matricula
            FROM matriculas m
            JOIN alunos a ON a.id_aluno = m.id_aluno
            JOIN cursos c ON c.id_curso = m.id_curso
        """)
        matriculas = cursor.fetchall()
        return jsonify(matriculas), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


@app.route('/api/matriculas', methods=['POST'])
def add_matricula():
    dados = request.get_json() or request.form

    aluno_id = dados.get('aluno_id')
    curso_id = dados.get('curso_id')
    data_mat = dados.get('data')

    if not aluno_id:
        return jsonify({"erro": "Aluno é obrigatório"}), 400
    if not curso_id:
        return jsonify({"erro": "Curso é obrigatório"}), 400

    conexao = None
    cursor = None
    cursor2 = None
    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        # Verifica se o curso existe e tem vagas
        cursor.execute("SELECT * FROM cursos WHERE id_curso = %s", (curso_id,))
        curso = cursor.fetchone()

        if not curso:
            return jsonify({"erro": "Curso não encontrado"}), 404

        vagas_livres = curso['vagas_totais'] - curso['vagas_ocupadas']
        if vagas_livres <= 0:
            return jsonify({"erro": "Não há vagas disponíveis neste curso"}), 400

        # Verifica se o aluno já está matriculado nesse curso
        cursor.execute(
            "SELECT * FROM matriculas WHERE id_aluno = %s AND id_curso = %s",
            (aluno_id, curso_id)
        )
        if cursor.fetchone():
            return jsonify({"erro": "Aluno já matriculado neste curso"}), 409

        # Insere matrícula e atualiza vagas em uma transação
        cursor2 = conexao.cursor()
        cursor2.execute(
            "INSERT INTO matriculas (id_aluno, id_curso, data_matricula) VALUES (%s, %s, %s)",
            (aluno_id, curso_id, data_mat)
        )
        cursor2.execute(
            "UPDATE cursos SET vagas_ocupadas = vagas_ocupadas + 1 WHERE id_curso = %s",
            (curso_id,)
        )
        conexao.commit()
        return jsonify({"mensagem": "Matrícula realizada com sucesso!"}), 201
    except Exception as e:
        if conexao:
            conexao.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if cursor2:
            cursor2.close()
        if conexao:
            conexao.close()


@app.route('/api/matriculas/<int:id_matricula>', methods=['DELETE'])
def delete_matricula(id_matricula):
    conexao = None
    cursor = None
    cursor2 = None
    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        # Busca a matrícula para saber qual curso atualizar
        cursor.execute("SELECT * FROM matriculas WHERE id_matricula = %s", (id_matricula,))
        matricula = cursor.fetchone()
        if not matricula:
            return jsonify({"erro": "Matrícula não encontrada"}), 404

        cursor2 = conexao.cursor()
        cursor2.execute("DELETE FROM matriculas WHERE id_matricula = %s", (id_matricula,))
        cursor2.execute(
            "UPDATE cursos SET vagas_ocupadas = vagas_ocupadas - 1 WHERE id_curso = %s",
            (matricula['id_curso'],)
        )
        conexao.commit()
        return jsonify({"mensagem": "Matrícula cancelada com sucesso!"}), 200
    except Exception as e:
        if conexao:
            conexao.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if cursor2:
            cursor2.close()
        if conexao:
            conexao.close()


# ══════════════════════════════════════════
# ATENDIMENTOS
# ══════════════════════════════════════════

@app.route('/api/atendimentos', methods=['GET'])
def get_atendimentos():
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                at.id_atendimento,
                al.nome AS aluno,
                at.data,
                at.horario,
                at.motivo,
                at.status
            FROM atendimentos at
            JOIN alunos al ON al.id_aluno = at.id_aluno
        """)
        atendimentos = cursor.fetchall()
        return jsonify(atendimentos), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


@app.route('/api/atendimentos', methods=['POST'])
def add_atendimento():
    dados = request.get_json() or request.form

    if not dados.get('id_aluno'):
        return jsonify({"erro": "Aluno é obrigatório"}), 400
    if not dados.get('motivo'):
        return jsonify({"erro": "Motivo é obrigatório"}), 400
    if not dados.get('data'):
        return jsonify({"erro": "Data é obrigatória"}), 400
    if not dados.get('horario'):
        return jsonify({"erro": "Horário é obrigatório"}), 400

    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO atendimentos (id_aluno, data, horario, motivo) VALUES (%s, %s, %s, %s)",
            (dados.get('id_aluno'), dados.get('data'), dados.get('horario'), dados.get('motivo'))
        )
        conexao.commit()
        return jsonify({"mensagem": "Atendimento agendado com sucesso!"}), 201
    except Exception as e:
        if conexao:
            conexao.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


@app.route('/api/atendimentos/<int:id_atendimento>/status', methods=['PATCH'])
def update_status_atendimento(id_atendimento):
    dados = request.get_json() or request.form
    novo_status = dados.get('status')

    STATUS_VALIDOS = ['agendado', 'confirmado', 'cancelado', 'realizado']
    if not novo_status:
        return jsonify({"erro": "Status é obrigatório"}), 400
    if novo_status not in STATUS_VALIDOS:
        return jsonify({"erro": f"Status inválido. Use: {', '.join(STATUS_VALIDOS)}"}), 400

    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
            "UPDATE atendimentos SET status = %s WHERE id_atendimento = %s",
            (novo_status, id_atendimento)
        )
        if cursor.rowcount == 0:
            return jsonify({"erro": "Atendimento não encontrado"}), 404
        conexao.commit()
        return jsonify({"mensagem": f"Status atualizado para '{novo_status}'"}), 200
    except Exception as e:
        if conexao:
            conexao.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


@app.route('/api/atendimentos/<int:id_atendimento>', methods=['DELETE'])
def delete_atendimento(id_atendimento):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM atendimentos WHERE id_atendimento = %s", (id_atendimento,))
        if cursor.rowcount == 0:
            return jsonify({"erro": "Atendimento não encontrado"}), 404
        conexao.commit()
        return jsonify({"mensagem": "Atendimento removido com sucesso!"}), 200
    except Exception as e:
        if conexao:
            conexao.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# ══════════════════════════════════════════
# MENSAGENS (simulação de envio)
# ══════════════════════════════════════════

@app.route('/api/mensagens', methods=['POST'])
def enviar_mensagem():
    dados = request.get_json() or request.form

    aluno = dados.get('aluno')
    tipo = dados.get('tipo')

    TIPOS_VALIDOS = ['confirmacao_matricula', 'lembrete_atendimento', 'aviso_geral']

    if not aluno:
        return jsonify({"erro": "Aluno é obrigatório"}), 400
    if not tipo:
        return jsonify({"erro": "Tipo da mensagem é obrigatório"}), 400
    if tipo not in TIPOS_VALIDOS:
        return jsonify({"erro": f"Tipo inválido. Use: {', '.join(TIPOS_VALIDOS)}"}), 400

    textos = {
        'confirmacao_matricula': f"Olá, {aluno}! Sua matrícula foi confirmada com sucesso.",
        'lembrete_atendimento': f"Olá, {aluno}! Lembramos que você tem um atendimento agendado.",
        'aviso_geral': f"Olá, {aluno}! Você tem um novo aviso da instituição."
    }

    return jsonify({
        "status": "sucesso",
        "tipo": tipo,
        "destinatario": aluno,
        "mensagem_enviada": textos[tipo]
    }), 200


# ──────────────────────────────────────────
# Inicialização
# ──────────────────────────────────────────
if __name__ == '__main__':
    porta = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=porta)