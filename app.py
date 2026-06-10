from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def conectar():

    return mysql.connector.connect(
        host=os.getenv('MYSQLHOST'),
        user=os.getenv('MYSQLUSER'),
        password=os.getenv('MYSQLPASSWORD'),
        database=os.getenv('MYSQLDATABASE'),
        port=int(os.getenv('MYSQLPORT')),
        autocommit=True
    )

app = Flask(__name__)
CORS(app) # comunicação direta entre o Front-end e o Back-end

@app.route('/')
def index():

    return render_template('siteReforco.html')



# ENDPOINTS DE ALUNOS
@app.route('/api/alunos', methods=['GET'])
def get_alunos():

    conexao = conectar()

    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM alunos")

    alunos = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(alunos), 200

@app.route('/api/alunos', methods=['POST'])
def add_aluno():

    dados = request.get_json() or request.form

    nome = dados.get('nome')
    email = dados.get('email')
    telefone = dados.get('telefone')
    nivel = dados.get('nivel')

    conexao = conectar()

    cursor = conexao.cursor()

    sql = '''
    INSERT INTO alunos
    (nome, email, telefone, nivel)
    VALUES (%s, %s, %s, %s)
    '''

    valores = (
        nome,
        email,
        telefone,
        nivel
    )

    cursor.execute(sql, valores)

    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Aluno cadastrado"
    }), 201


# ENDPOINTS DE CURSOS
@app.route('/api/cursos', methods=['GET'])
def get_cursos():

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM cursos")

    cursos = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(cursos), 200

@app.route('/api/cursos', methods=['POST'])
def add_curso():

    dados = request.get_json() or request.form

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    INSERT INTO cursos
    (nome, nivel, vagas_totais)
    VALUES (%s,%s,%s)
    """

    cursor.execute(
        sql,
        (
            dados.get('nome'),
            dados.get('nivel'),
            dados.get('vagas_totais')
        )
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Curso cadastrado com sucesso!"
    }), 201


# ENDPOINTS DE MATRÍCULAS 
@app.route('/api/matriculas', methods=['GET'])
def get_matriculas():

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

    cursor.close()
    conexao.close()

    return jsonify(matriculas), 200

@app.route('/api/matriculas', methods=['POST'])
def add_matricula():

    dados = request.get_json() or request.form

    aluno_id = dados.get('aluno_id')
    curso_id = dados.get('curso_id')
    data_mat = dados.get('data')

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM cursos WHERE id_curso = %s",
        (curso_id,)
    )

    curso = cursor.fetchone()

    if not curso:
        return jsonify({
            "erro": "Curso não encontrado."
        }), 404

    vagas = (
        curso['vagas_totais']
        - curso['vagas_ocupadas']
    )

    if vagas <= 0:
        return jsonify({
            "erro": "Não há vagas."
        }), 400

    cursor.execute(
        """
        INSERT INTO matriculas
        (id_aluno,id_curso,data_matricula)
        VALUES (%s,%s,%s)
        """,
        (
            aluno_id,
            curso_id,
            data_mat
        )
    )

    cursor.execute(
        """
        UPDATE cursos
        SET vagas_ocupadas = vagas_ocupadas + 1
        WHERE id_curso = %s
        """,
        (curso_id,)
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Matrícula realizada com sucesso!"
    }), 201

# ENDPOINTS DE ATENDIMENTOS (
@app.route('/api/atendimentos', methods=['GET'])
def get_atendimentos():

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
    JOIN alunos al
        ON al.id_aluno = at.id_aluno
    """)

    atendimentos = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(atendimentos), 200

@app.route('/api/atendimentos', methods=['POST'])
def add_atendimento():

    dados = request.get_json() or request.form

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO atendimentos
        (id_aluno,data,horario,motivo)
        VALUES (%s,%s,%s,%s)
        """,
        (
            dados.get('id_aluno'),
            dados.get('data'),
            dados.get('horario'),
            dados.get('motivo')
        )
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Atendimento agendado com sucesso!"
    }), 201

if __name__ == '__main__':

    porta = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=porta)