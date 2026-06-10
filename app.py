from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# ──────────────────────────────────────────
# CONEXÃO SEGURA COM MYSQL
# ──────────────────────────────────────────
def conectar():
    return mysql.connector.connect(
        host=os.getenv('MYSQLHOST'),
        user=os.getenv('MYSQLUSER'),
        password=os.getenv('MYSQLPASSWORD'),
        database=os.getenv('MYSQLDATABASE'),
        port=int(os.getenv('MYSQLPORT')),
        autocommit=False  # Transações controladas manualmente por commit/rollback
    )

# ──────────────────────────────────────────
# HOME
# ──────────────────────────────────────────
@app.route('/')
def index():
    return render_template('siteReforco.html')


# ══════════════════════════════════════════
# ALUNOS
# ══════════════════════════════════════════

@app.route('/api/alunos', methods=['GET'])
def get_alunos():
    conexao = cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM alunos")
        alunos = cursor.fetchall()
        return jsonify(alunos), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()


@app.route('/api/alunos/<int:id_aluno>', methods=['GET'])
def get_aluno(id_aluno):
    conexao = cursor = None
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
        if cursor: cursor.close()
        if conexao: conexao.close()


@app.route('/api/alunos', methods=['POST'])
def add_aluno():
    conexao = cursor = None
    try:
        dados = request.get_json() or request.form
        nome = dados.get('nome')
        email = dados.get('email')
        telefone = dados.get('telefone')
        nivel = dados.get('nivel')

        if not nome or not email:
            return jsonify({"erro": "Nome e email são obrigatórios"}), 400

        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO alunos (nome, email, telefone, nivel) VALUES (%s, %s, %s, %s)",
            (nome, email, telefone, nivel)
        )
        conexao.commit()
        return jsonify({"mensagem": "Aluno cadastrado com sucesso!"}), 201
    except Exception as e:
        if conexao: conexao.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()


@app.route('/api/alunos/<int:id_aluno>', methods=['DELETE'])
def delete_aluno(id_aluno):
    conexao = cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM alunos WHERE id_aluno = %s", (id_aluno,))

        if cursor.rowcount == 0:
            return jsonify({"erro": "Aluno não encontrado"}), 404

        conexao.commit()
        return jsonify({"mensagem": "Aluno removido com sucesso!"}), 200
    except Exception as e:
        if conexao: conexao.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()


# ══════════════════════════════════════════
# CURSOS
# ══════════════════════════════════════════

@app.route('/api/cursos', methods=['GET'])
def get_cursos():
    conexao = cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cursos")
        cursos = cursor.fetchall()
        return jsonify(cursos), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()


@app.route('/api/cursos', methods=['POST'])
def add_curso():
    conexao = cursor = None
    try:
        dados = request.get_json() or request.form
        if not dados.get('nome') or not dados.get('nivel') or not dados.get('vagas_totais'):
            return jsonify({"erro": "Campos obrigatórios faltando"}), 400

        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO cursos (nome, nivel, vagas_totais) VALUES (%s, %s, %s)",
            (dados['nome'], dados['nivel'], dados['vagas_totais'])
        )
        conexao.commit()
        return jsonify({"mensagem": "Curso cadastrado com sucesso!"}), 201
    except Exception as e:
        if conexao: conexao.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()


# ══════════════════════════════════════════
# MATRÍCULAS
# ══════════════════════════════════════════

@app.route('/api/matriculas', methods=['GET'])
def get_matriculas():
    conexao = cursor = None
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
        if cursor: cursor.close()
        if conexao: conexao.close()


@app.route('/api/matriculas', methods=['POST'])
def add_matricula():
    conexao = cursor = None
    try:
        dados = request.get_json() or request.form
        aluno_id = dados.get('aluno_id')
        curso_id = dados.get('curso_id')
        data_mat = dados.get('data')

        if not aluno_id or not curso_id:
            return jsonify({"erro": "Aluno e curso são obrigatórios"}), 400

        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        # Verifica existência do curso
        cursor.execute("SELECT * FROM cursos WHERE id_curso = %s", (curso_id,))
        curso = cursor.fetchone()

        if not curso:
            return jsonify({"erro": "Curso não encontrado"}), 404

        # Tratamento seguro caso vagas_ocupadas seja None no banco
        vagas_ocupadas = curso.get('vagas_ocupadas') or 0
        vagas_livres = curso['vagas_totais'] - vagas_ocupadas

        if vagas_livres <= 0:
            return jsonify({"erro": "Sem vagas disponíveis"}), 400

        # Verifica duplicidade
        cursor.execute(
            "SELECT * FROM matriculas WHERE id_aluno=%s AND id_curso=%s",
            (aluno_id, curso_id)
        )
        if cursor.fetchone():
            return jsonify({"erro": "Aluno já matriculado neste curso"}), 409

        # Reutilizando o mesmo cursor para as alterações (Garante o fechamento correto no final)
        cursor.execute(
            "INSERT INTO matriculas (id_aluno, id_curso, data_matricula) VALUES (%s, %s, %s)",
            (aluno_id, curso_id, data_mat)
        )
        cursor.execute(
            "UPDATE cursos SET vagas_ocupadas = vagas_ocupadas + 1 WHERE id_curso = %s",
            (curso_id,)
        )

        conexao.commit()
        return jsonify({"mensagem": "Matrícula realizada com sucesso!"}), 201

    except Exception as e:
        if conexao: conexao.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()


# ══════════════════════════════════════════
# ATENDIMENTOS
# ══════════════════════════════════════════

@app.route('/api/atendimentos', methods=['GET'])
def get_atendimentos():
    conexao = cursor = None
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
        if cursor: cursor.close()
        if conexao: conexao.close()


@app.route('/api/atendimentos', methods=['POST'])
def add_atendimento():
    conexao = cursor = None
    try:
        dados = request.get_json() or request.form
        if not dados.get('id_aluno') or not dados.get('data') or not dados.get('horario'):
            return jsonify({"erro": "Campos obrigatórios faltando"}), 400

        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO atendimentos (id_aluno, data, horario, motivo) VALUES (%s, %s, %s, %s)",
            (dados['id_aluno'], dados['data'], dados['horario'], dados.get('motivo'))
        )
        conexao.commit()
        return jsonify({"mensagem": "Atendimento agendado!"}), 201
    except Exception as e:
        if conexao: conexao.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()


# ──────────────────────────────────────────
# START
# ──────────────────────────────────────────
if __name__ == '__main__':
    porta = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=porta)