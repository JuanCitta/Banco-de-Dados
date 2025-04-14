import random
from faker import Faker
import psycopg2

fake = Faker('pt_BR')

NUM_PROFESSORES = 15
NUM_ALUNOS = 60
MAX_ALUNOS_POR_TCC = 4
MAX_DISCIPLINAS_POR_SEMESTRE = 7
SEMESTRE_PARA_TCC = 8
INICIO_INTERVALO_ANO = 2018
FINAL_INTERVALO_ANO = 2025
FINAL_INTERVALO_SEMESTRE = 8

TEMAS_TCC = [
    "machine learning", "blockchain", "IoT", "nuvem", "big data",
    "segurança cibernética", "LGPD", "inteligência artificial", "devops"
]

DEPARTAMENTOS = {
    '1': 'Computação', 
    '2':'Matemática', 
    '3':'Linguagem e Idiomas',
    '4':'Engenharia Elétrica',
    '5': 'Física', 
    '6':'Química',
    '7': 'Ciências Sociais e Jurídicas', 
}
DISCIPLINAS = {
    '1': ['Algoritmos e Programação', 'Estrutura de Dados', 'Inteligência Artificial', 'Redes de Computadores', 'Banco de Dados', 'Engenharia de Software', 'Sistemas Operacionais', 'Computação Gráfica', 'Segurança da Informação', 'Programação Web', 'Machine Learning', 'Arquitetura de Computadores'],
    '2': ['Cálculo Diferencial e Integral', 'Álgebra Linear', 'Matemática Discreta', 'Cálculo Numérico', 'Equações Diferenciais', 'Probabilidade e Estatística', 'Geometria Analítica', 'Teoria dos Grafos', 'Otimização Matemática', 'Matemática Financeira'],
    '3': ['Língua Portuguesa', 'Inglês Técnico', 'Literatura Brasileira', 'Espanhol Instrumental', 'Comunicação Científica'],
    '4': ['Circuitos Elétricos', 'Eletrônica Digital', 'Sistemas de Controle', 'Eletrônica Analógica', 'Microcontroladores', 'Telecomunicações', 'Robótica Industrial', 'Automação', 'Processamento Digital de Sinais', 'Instalações Elétricas'],
    '5': ['Física Geral', 'Mecânica Clássica', 'Eletromagnetismo', 'Termodinâmica', 'Física Moderna', 'Fisica Óptica', 'Física Computacional'],
    '6': ['Química Geral', 'Química Orgânica', 'Físico-Química', 'Química Inorgânica'],
    '7': ['Introdução ao Direito', 'Ética Profissional']
}
CURSOS = {
    '1': 'Ciência da Computação',   
    '2': 'Engenharia de Dados', 
    '3': 'Sistemas de Informação',
    '4': 'Ciência de Dados',
    '5': 'Engenharia de Produção'
}
#Funcoes auxiliares------------------------------------------
def gerar_nome():
    return f"{fake.first_name()} {fake.last_name()}"


def dividir_em_grupos(alunos, tamanho_grupo=4):
    grupos = []
    i = 0
    while i < len(alunos):
        grupo = alunos[i:i + tamanho_grupo]
        grupos.append(grupo)
        i += tamanho_grupo
    return grupos

def avancar_semestre(data_semestre):
    ano, semestre = map(int, str(data_semestre).split('.'))
    if semestre == 1:
        semestre = 2
    else:
        semestre = 1
        ano += 1
    return f"{ano}.{semestre}"
##-----------------------------------------------------------
def gerar_professores():
    professores = []
    departamentos = list(DEPARTAMENTOS.keys())
    pesos = [9, 9, 4, 7, 3, 2, 1]
    id_prof = 1 
    for id_departamento in departamentos:
        professores.append((id_prof, gerar_nome(), id_departamento))
        id_prof += 1

    restante = NUM_PROFESSORES - len(professores)
    for _ in range(restante):
        id_departamento = random.choices(departamentos, weights=pesos, k=1)[0]
        professores.append((id_prof, gerar_nome(), id_departamento))
        id_prof += 1

    return professores


def gerar_alunos():
    alunos = []
    for ra in range(1, NUM_ALUNOS + 1):
        id_curso = random.choice(list(CURSOS.keys()))
        alunos.append((ra, gerar_nome(), id_curso))
    return alunos


def gerar_departamentos(professores):
    departamentos = []
    for id_depto in DEPARTAMENTOS.keys():
        profs = [p for p in professores if p[2] == id_depto]
        if not profs:
            coordenador = random.choice(professores)
        else:
            coordenador = random.choice(profs)
        id_coordenador = coordenador[0]
        nome_departamento = DEPARTAMENTOS[id_depto]
        departamentos.append((id_depto, nome_departamento, id_coordenador))
    return departamentos
            
def gerar_cursos(professores):
    cursos = []
    for id_curso in CURSOS.keys():
        coordenador = random.choice(professores)
        id_coordenador = coordenador[0]
        titulo_curso = CURSOS[id_curso]
        cursos.append((id_curso, titulo_curso, id_coordenador))
    return cursos

def gerar_disciplinas():
    disciplinas = []
    id_disciplina = 1
    for id_depto in DISCIPLINAS.keys():
        for nome_disciplina in DISCIPLINAS[id_depto]:
            id_disciplina+= 1
            disciplinas.append((id_disciplina,nome_disciplina,id_depto))
    return disciplinas
            
def gerar_curso_disciplina(disciplinas, cursos):
    curso_disciplina = []
    for disciplina in disciplinas:
        n = random.randint(1,5)
        cursos_associados = random.sample(cursos,n)
        for curso in cursos_associados:
            curso_disciplina.append((disciplina[0],curso[0]))
    return curso_disciplina
                
def gerar_matriz_curricular(cursos, disciplinas):
    matriz_curricular = []
    for curso in cursos:
        disciplinas_curso = disciplinas.copy()
        random.shuffle(disciplinas_curso)
        
        for semestre in range(1, 9):
            num_disciplinas = random.randint(4, MAX_DISCIPLINAS_POR_SEMESTRE)
           
            for _ in range(num_disciplinas+1):
                if not disciplinas_curso:
                    break  
                disciplina = disciplinas_curso.pop()
                matriz_curricular.append((curso[0], disciplina[0], semestre))
    
    return matriz_curricular


def gerar_tccs(professores, escuta):
    id_tcc = 1
    tccs = []
    tccs_aluno = []
    alunos_por_semestre = {}

    for entrada in escuta:
        ra, _, semestre, _, ciclo_aluno = entrada
        if ciclo_aluno == SEMESTRE_PARA_TCC:
            if semestre not in alunos_por_semestre:
                alunos_por_semestre[semestre] = set()
            alunos_por_semestre[semestre].add(ra)

    for semestre, alunos in alunos_por_semestre.items():
        grupos = dividir_em_grupos(list(alunos))
        for grupo in grupos:
            for ra in grupo:
                tccs_aluno.append((id_tcc, ra))

            titulo = f"Estudo sobre {random.choice(TEMAS_TCC)}".capitalize()
            id_professor = random.randint(1, len(professores))
            nota = random.randint(5,10)
            
            tccs.append((
                    id_tcc, 
                    id_professor, 
                    titulo, 
                    nota,
                    semestre
                ))

            id_tcc += 1  

    return tccs, tccs_aluno


def gerar_profere(professores, disciplinas, escuta):
    profere = set()
    mapa_disc_depto = {d[0]: d[2] for d in disciplinas}  
    disc_semestre_processados = set()  
    
    for entrada in escuta:
        _, id_disc, semestre, _, _ = entrada
        chave = (id_disc, semestre)
        
        if chave in disc_semestre_processados:
            continue
        
        id_depto = mapa_disc_depto.get(id_disc)
        if id_depto is None:
            continue
            
        profs_do_depto = [p[0] for p in professores if p[2] == id_depto]
        if not profs_do_depto:
            continue
        
        prof_escolhido = random.choice(profs_do_depto)
        profere.add((prof_escolhido, id_disc, semestre))
        
        disc_semestre_processados.add(chave)
    
    return list(profere)
    
def gerar_escuta(alunos, cursos_disciplinas):
    aluno_disciplina = []
    for aluno in alunos:
        ano_atual = random.randint(INICIO_INTERVALO_ANO,FINAL_INTERVALO_ANO)
        
        if ano_atual >= INICIO_INTERVALO_ANO+4:
            ciclo_aluno = 1
        else:
            ciclo_aluno = random.randint(1, FINAL_INTERVALO_SEMESTRE)
            
        semestre_atual = 1
        ra, nome, curso_id = aluno
        disciplinas_reprovadas = []
        disciplinas_concluidas = []

        while ano_atual != 2025 or semestre_atual != 2:
            disciplinas_semestre = []
            novas_reprovadas = []
            if ciclo_aluno >= 8 and (not disciplinas_reprovadas or disciplinas_semestre):
                break
            
            for d in cursos_disciplinas:
                if d[0] == curso_id and ciclo_aluno == d[2]:
                    if d[1] not in disciplinas_concluidas:
                        disciplinas_semestre.append(d[1])

            for d in disciplinas_reprovadas:
                if d not in disciplinas_concluidas and d not in disciplinas_semestre:
                    disciplinas_semestre.append(d)

            for d in disciplinas_semestre:
                nota = min(10, max(0, round(random.normalvariate(6, 1), 2)))
                semestre_formatado = f"{ano_atual}.{semestre_atual}"
                aluno_disciplina.append((ra, d, semestre_formatado, nota, ciclo_aluno))

                if nota < 5:
                    novas_reprovadas.append(d)
                else:
                    disciplinas_concluidas.append(d) 

            disciplinas_reprovadas = novas_reprovadas

            if semestre_atual == 1:
                semestre_atual = 2
            else:
                semestre_atual = 1
                ano_atual += 1
            ciclo_aluno += 1

    return aluno_disciplina



def inserir_no_banco(dados):
    try:
        conn = psycopg2.connect(
            host="db.gmuoinhzwkcxwoinnqit.supabase.co",
            database="postgres",
            user="postgres",
            password="zGcUhOCaI1EUmLDX"
        )
        cursor = conn.cursor()

        tabelas = [
            "tcc_aluno", "tcc", "profere", "escuta", "matriz_curricular", "curso_disciplina",
            "disciplina", "aluno", "curso", "professor", "departamento"
        ]
        for tabela in tabelas:
            cursor.execute(f"DROP TABLE IF EXISTS {tabela} CASCADE;")
        
        comandos_sql = [

             """
            CREATE TABLE IF NOT EXISTS professor (
                id_prof VARCHAR NOT NULL PRIMARY KEY,
                nome VARCHAR NOT NULL,
                id_depto VARCHAR NULL
            );
            """,

            """
            CREATE TABLE IF NOT EXISTS departamento (
                id_depto VARCHAR NOT NULL PRIMARY KEY,
                nome_depto VARCHAR NOT NULL,
                id_coord VARCHAR NULL,
                CONSTRAINT departamento_id_coord_fkey FOREIGN KEY (id_coord) REFERENCES professor (id_prof)
            );
            """,

            """
            CREATE TABLE curso (
                id_curso VARCHAR PRIMARY KEY,
                titulo_curso VARCHAR NOT NULL,
                id_coord VARCHAR NULL,
                CONSTRAINT curso_id_coord_fkey FOREIGN KEY (id_coord) REFERENCES professor (id_prof) ON DELETE SET NULL
            );
            """,

            """
            CREATE TABLE aluno (
                ra VARCHAR PRIMARY KEY,
                nome VARCHAR NOT NULL,
                id_curso VARCHAR,
                CONSTRAINT aluno_id_curso_fkey FOREIGN KEY (id_curso) REFERENCES curso (id_curso)
            );
            """,

            """
            CREATE TABLE disciplina (
                id_disc VARCHAR PRIMARY KEY,
                nome_disc VARCHAR NOT NULL,
                id_depto VARCHAR,
                CONSTRAINT disciplina_id_depto_fkey FOREIGN KEY (id_depto) REFERENCES departamento (id_depto)
            );
            """,

            """
            CREATE TABLE curso_disciplina (
                id_disc VARCHAR NOT NULL,
                id_curso VARCHAR NOT NULL,
                PRIMARY KEY (id_disc, id_curso),
                CONSTRAINT curso_disciplina_id_curso_fkey FOREIGN KEY (id_curso) REFERENCES curso (id_curso),
                CONSTRAINT curso_disciplina_id_disc_fkey FOREIGN KEY (id_disc) REFERENCES disciplina (id_disc)
            );
            """,

            """
            CREATE TABLE matriz_curricular (
                id_curso VARCHAR NOT NULL,
                id_disciplina VARCHAR NOT NULL,
                semestre NUMERIC,
                PRIMARY KEY (id_curso, id_disciplina),
                CONSTRAINT matriz_curricular_id_curso_fkey FOREIGN KEY (id_curso) REFERENCES curso (id_curso),
                CONSTRAINT matriz_curricular_id_disciplina_fkey FOREIGN KEY (id_disciplina) REFERENCES disciplina (id_disc)
            );
            """,

            """
            CREATE TABLE escuta (
                ra_aluno VARCHAR NOT NULL,
                id_disc VARCHAR NOT NULL,
                semestre TEXT NOT NULL,
                nota NUMERIC,
                ciclo_aluno TEXT NOT NULL,
                PRIMARY KEY (ra_aluno, id_disc, semestre),
                CONSTRAINT escuta_id_disc_fkey FOREIGN KEY (id_disc) REFERENCES disciplina (id_disc),
                CONSTRAINT escuta_ra_aluno_fkey FOREIGN KEY (ra_aluno) REFERENCES aluno (ra)
            );
            """,

            """
            CREATE TABLE profere (
                id_prof VARCHAR NOT NULL,
                id_disc VARCHAR NOT NULL,
                semestre TEXT NOT NULL,
                PRIMARY KEY (id_prof, id_disc, semestre),
                CONSTRAINT profere_id_disc_fkey FOREIGN KEY (id_disc) REFERENCES disciplina (id_disc),
                CONSTRAINT profere_id_prof_fkey FOREIGN KEY (id_prof) REFERENCES professor (id_prof)
            );
            """,

            """
            CREATE TABLE tcc (
                id_tcc VARCHAR PRIMARY KEY,
                id_prof VARCHAR NOT NULL,
                titulo VARCHAR,
                nota INT,
                semestre TEXT,
                CONSTRAINT tcc_id_prof_fkey FOREIGN KEY (id_prof) REFERENCES professor (id_prof)
            );
            """,

            """
            CREATE TABLE tcc_aluno (
                id_tcc VARCHAR NOT NULL,
                ra VARCHAR NOT NULL,
                PRIMARY KEY (id_tcc, ra),
                CONSTRAINT tcc_aluno_id_tcc_fkey FOREIGN KEY (id_tcc) REFERENCES tcc (id_tcc),
                CONSTRAINT tcc_aluno_ra_fkey FOREIGN KEY (ra) REFERENCES aluno (ra)
            );
            """
        ]
        
        for comando in comandos_sql:
            cursor.execute(comando)
        print("Tabelas Criadas.")
        cursor.executemany("INSERT INTO professor VALUES (%s, %s, %s)", dados['professores'])
        cursor.executemany("INSERT INTO departamento VALUES (%s, %s, %s)", dados['departamentos'])
        cursor.executemany("INSERT INTO curso VALUES (%s, %s, %s)", dados['cursos'])
        print("Professores, departamentos e cursos inseridos.")
        cursor.executemany("INSERT INTO aluno VALUES (%s, %s, %s)", dados['alunos'])
        cursor.executemany("INSERT INTO disciplina VALUES (%s, %s, %s)", dados['disciplinas'])
        cursor.executemany("INSERT INTO curso_disciplina VALUES (%s, %s)", dados['curso_disciplina'])
        print("Alunos, Disciplinas e curso_disciplina inseridos.")
        cursor.executemany("INSERT INTO matriz_curricular VALUES (%s, %s, %s)", dados['matriz_curricular'])
        cursor.executemany("INSERT INTO escuta VALUES (%s, %s, %s, %s, %s)", dados['escuta'])
        cursor.executemany("INSERT INTO profere VALUES (%s, %s, %s)", dados['profere'])
        print("Matriz_Curricular, Escuta e Profere inseridos.")
        cursor.executemany("INSERT INTO tcc VALUES (%s, %s, %s, %s, %s)", dados['tccs'])
        cursor.executemany("INSERT INTO tcc_aluno VALUES (%s, %s)", dados['tcc_aluno'])
        print("TCCs e TCC_aluno inserido")
        conn.commit()

    except Exception as e:
        print(f"Erro: {e}")
        return False

    finally:
        if 'conn' in locals():
            conn.close()


def main():
    
    disciplinas = gerar_disciplinas()
    professores = gerar_professores()
    alunos = gerar_alunos()
    departamentos = gerar_departamentos(professores)
    cursos = gerar_cursos(professores)
    curso_disciplina = gerar_curso_disciplina(disciplinas,cursos)
    matriz_curricular = gerar_matriz_curricular(cursos, disciplinas)
    escuta = gerar_escuta(alunos, matriz_curricular)
    profere = gerar_profere(professores, disciplinas,escuta)
    tccs, tcc_aluno = gerar_tccs(professores, escuta)
    dados = {
        'professores': professores,
        'alunos': alunos,
        'departamentos': departamentos,
        'cursos': cursos,
        'disciplinas': disciplinas,
        'curso_disciplina': curso_disciplina,
        'matriz_curricular': matriz_curricular,
        'escuta': escuta,
        'profere': profere,
        'tccs': tccs,
        'tcc_aluno': tcc_aluno
    }

    inserir_no_banco(dados)
if __name__ == "__main__":
    main()
