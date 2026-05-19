from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def conectar():

    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        port=os.getenv('DB_PORT')
    )

app = Flask(__name__)
CORS(app) # Permite a comunicação direta entre o Front-end e o Back-end

# --- BANCO DE DADOS EM MEMÓRIA (Estrutura Inicial de Dados) ---
alunos = [
    {"id": 1, "nome": "Maria Souza", "email": "maria@email.com", "telefone": "71999998888", "nivel": "Intermediario"}
]

cursos = [
    {"id": 1, "nome": "Matemática Básica", "nivel": "Básico", "vagas_totais": 30, "vagas_ocupadas": 18}
]

matriculas = [
    {"id": 1, "aluno_id": 1, "curso_id": 1, "data": "2026-05-18"}
]

atendimentos = [
    {"id": 1, "aluno": "João Silva", "data": "2026-05-20", "horario": "14:00", "motivo": "Dificuldade em matemática", "status": "Agendado"}
]

# --- ROTA PARA SERVIR O FRONT-END ---
@app.route('/')
def index():
    # Serve o HTML original do aluno que está na pasta templates
    return render_template('siteReforco.html')

# --- ENDPOINTS DA API REST (EXIGÊNCIA DA ETAPA 2) ---

# 1. ENDPOINTS DE ALUNOS
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


# 2. ENDPOINTS DE CURSOS
@app.route('/api/cursos', methods=['GET'])
def get_cursos():
    return jsonify(cursos), 200

@app.route('/api/cursos', methods=['POST'])
def add_curso():
    dados = request.get_json() or request.form
    nome = dados.get('nome')
    nivel = dados.get('nivel')
    vagas_totais = dados.get('vagas_totais')

    if not nome or not nivel or not vagas_totais:
        return jsonify({"erro": "Campos obrigatórios ausentes para o curso."}), 400

    novo_curso = {
        "id": len(cursos) + 1,
        "nome": nome,
        "nivel": nivel,
        "vagas_totais": int(vagas_totais),
        "vagas_ocupadas": 0
    }
    cursos.append(novo_curso)
    return jsonify({"mensagem": "Curso cadastrado com sucesso!", "curso": novo_curso}), 201


# 3. ENDPOINTS DE MATRÍCULAS (COM REGRA DE NEGÓCIO DO PROJETO)
@app.route('/api/matriculas', methods=['GET'])
def get_matriculas():
    return jsonify(matriculas), 200

@app.route('/api/matriculas', methods=['POST'])
def add_matricula():
    dados = request.get_json() or request.form
    aluno_id = int(dados.get('aluno_id'))
    curso_id = int(dados.get('curso_id'))
    data_mat = dados.get('data')

    # REGRA DE NEGÓCIO: Verificar se o curso existe e tem vagas disponíveis
    curso_selecionado = next((c for c in cursos if c['id'] == curso_id), None)
    if not curso_selecionado:
        return jsonify({"erro": "Curso não encontrado."}), 44

    vagas_disponiveis = curso_selecionado['vagas_totais'] - curso_selecionado['vagas_ocupadas']
    
    if vagas_disponiveis <= 0:
        # Se não houver vagas, barra a matrícula (Regra pedida na Unijorge)
        return jsonify({"erro": "Matrícula recusada: Não há vagas disponíveis neste curso!"}), 400

    # Se tiver vagas, incrementa as ocupadas e confirma
    curso_selecionado['vagas_ocupadas'] += 1
    nova_mat = {
        "id": len(matriculas) + 1,
        "aluno_id": aluno_id,
        "curso_id": curso_id,
        "data": data_mat
    }
    matriculas.append(nova_mat)
    return jsonify({"mensagem": "Matrícula realizada com sucesso!", "matricula": nova_mat}), 201


# 4. ENDPOINTS DE ATENDIMENTOS (AGENDAMENTO DE REFORÇO)
@app.route('/api/atendimentos', methods=['GET'])
def get_atendimentos():
    return jsonify(atendimentos), 200

@app.route('/api/atendimentos', methods=['POST'])
def add_atendimento():
    dados = request.get_json() or request.form
    aluno = dados.get('aluno')
    data = dados.get('data')
    horario = dados.get('horario')
    motivo = dados.get('motivo')

    if not aluno or not data or not horario or not motivo:
        return jsonify({"erro": "Preencha todos os campos para o agendamento."}), 400

    novo_atendimento = {
        "id": len(atendimentos) + 1,
        "aluno": aluno,
        "data": data,
        "horario": horario,
        "motivo": motivo,
        "status": "Agendado"
    }
    atendimentos.append(novo_atendimento)
    
    print(f"\n[BACKEND LOG] Novo atendimento de reforço agendado para: {aluno} em {data} às {horario}")
    return jsonify({"mensagem": "Atendimento agendado com sucesso!", "atendimento": novo_atendimento}), 201

if __name__ == '__main__':

    porta = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=porta)
