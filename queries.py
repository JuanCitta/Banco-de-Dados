import psycopg2
from tabulate import tabulate
import traceback

# Conexao com o banco de dados
def conectar():
    return psycopg2.connect(
        host="db.gmuoinhzwkcxwoinnqit.supabase.co",
        database="postgres",
        user="postgres",
        password="zGcUhOCaI1EUmLDX"
    )

# Descricoes e comandos SQL
queries = {
    1: (
        "Mostre todo o histórico escolar de um aluno que teve reprovação em uma disciplina, retornando inclusive a reprovação em um semestre e a aprovação no semestre seguinte",
        """
        SELECT * from escuta
        WHERE ra_aluno = '10'
        ORDER BY semestre;
        """
    ),
    2: (
        "Mostre todos os TCCs orientados por um professor junto com os nomes dos alunos que fizeram o projeto",
        """
        SELECT 
            p.nome AS Nome_do_Professor,
            t.id_tcc,
            t.titulo,
            t.nota,
            t.semestre,
            a.nome AS Nome_do_Aluno
        FROM tcc t
        JOIN professor p ON t.id_prof = p.id_prof
        JOIN tcc_aluno ta ON t.id_tcc = ta.id_tcc
        JOIN aluno a ON ta.ra = a.ra
        WHERE p.id_prof = '1'
        ORDER BY p.nome, t.id_tcc, a.nome;
        """
    ),
    3: (
        " Mostre a matriz curricular de pelo menos 2 cursos diferentes que possuem disciplinas em comum (e.g., Ciência da Computação e Ciência de Dados)."+ 
        "Este exercício deve ser dividido em 2 queries sendo uma para cada curso",
        """
        SELECT 
            c.titulo_curso AS Curso,
            d.nome_disc AS Disciplina,
            mc.semestre
        FROM 
            matriz_curricular mc
        JOIN curso c ON mc.id_curso = c.id_curso
        JOIN disciplina d ON mc.id_disciplina = d.id_disc
        WHERE c.titulo_curso = 'Ciência da Computação'
        ORDER BY mc.semestre, d.nome_disc;
        """
    ),
    4: (
        "Para um determinado aluno, mostre os códigos e nomes das diciplinas já cursadas junto com os nomes dos professores que lecionaram a disciplina para o aluno",
        """
        SELECT 
            d.id_disc AS "Cod. da Disciplina",
            d.nome_disc AS "Nome da Disciplina",
            p.nome AS "Professor",
            e.semestre AS "Semestre",
            e.nota AS "Nota",
            a.ra AS "RA do Aluno"
        FROM 
            escuta e
        JOIN 
            disciplina d ON e.id_disc = d.id_disc
        JOIN 
            profere pf ON e.id_disc = pf.id_disc AND e.semestre = pf.semestre
        JOIN 
            professor p ON pf.id_prof = p.id_prof
        JOIN 
            aluno a ON e.ra_aluno = a.ra
        WHERE 
            a.ra = '1'  
        ORDER BY 
            e.semestre, d.nome_disc
        LIMIT 300
        """
        
    ),
    5: (
        "Liste todos os chefes de departamento e coordenadores de curso em apenas uma query de forma que a primeira coluna seja o nome do professor," +
        "a segunda o nome do departamento coordena e a terceira o nome do curso que coordena. Substitua os campos em branco do resultado da query pelo texto nenhum",
        """
        SELECT 
            p.nome AS "Nome do Prof.",
            COALESCE(depto.nome_depto, 'nenhum') AS "Departamento",
            COALESCE(curso.titulo_curso, 'nenhum') AS "Curso"
        FROM 
            professor p
        LEFT JOIN 
            departamento depto ON p.id_prof = depto.id_coord
        LEFT JOIN 
            curso curso ON p.id_prof = curso.id_coord
        WHERE 
            depto.id_coord IS NOT NULL OR curso.id_coord IS NOT NULL
        ORDER BY 
            p.nome
        """
    ),
    6: (
        "Liste os IDs e nomes de todos os professores",
        """
        SELECT 
            p.id_prof as "ID do Prof.",
            p.nome as "Nome do Prof."
            FROM professor p
        """
    ),
    7: ("Encontre os nomes de todos os estudantes que cursaram 'Engenharia de Dados'",
        """
        SELECT 
            a.nome AS "Nome do Aluno"
        FROM 
            aluno a
        JOIN 
            curso c ON a.id_curso = c.id_curso
        WHERE 
            c.titulo_curso = 'Engenharia de Dados'
        """
    ),
    8: ("Liste todas as disciplinas do departamento de 'Computação' ou do de 'Matemática'que foram cursadas por estudantes ",
        """
        SELECT DISTINCT
            d.id_disc AS "Código da Disciplina",
            d.nome_disc AS "Nome da Disciplina",
            dep.nome_depto AS "Departamento da Disciplina"
        FROM
            escuta e
        JOIN
            aluno a ON e.ra_aluno = a.ra
        JOIN
            disciplina d ON e.id_disc = d.id_disc
        JOIN
            departamento dep ON d.id_depto = dep.id_depto
        WHERE
            dep.nome_depto IN ('Computação', 'Matemática')
        ORDER BY
            dep.nome_depto
        """
    ),
    9: ("Liste as disciplinas que são ministrados pelo professor de ID '1', juntamente com os títulos das disciplinas",
        """
        SELECT DISTINCT
            p.nome AS "Nome do Prof.",
            p.id_prof AS "ID do Prof.",
            d.nome_disc AS "Titulo da Disciplina"
        FROM 
            professor p
        JOIN profere ON profere.id_prof = p.id_prof
        JOIN disciplina d ON d.id_disc = profere.id_disc
        WHERE p.id_prof = '1'
        """
    ),
    10: ("Encontre os estudantes que cursaram tanto 'Algoritmos e Programação' quanto 'Álgebra Linear'",
         """
        SELECT 
            a.ra AS "RA",
            a.nome AS "Nome do Aluno"
        FROM 
            aluno a
        WHERE 
            EXISTS (
                SELECT 1 FROM escuta e
                JOIN disciplina d ON e.id_disc = d.id_disc
                WHERE e.ra_aluno = a.ra AND d.nome_disc = 'Algoritmos e Programação'
            )
            AND
            EXISTS (
                SELECT 1 FROM escuta e
                JOIN disciplina d ON e.id_disc = d.id_disc
                WHERE e.ra_aluno = a.ra AND d.nome_disc = 'Estrutura de Dados'
            )
        ORDER BY 
            a.nome;
         """
    ),
    11: (" Liste os nomes dos estudantes que não cursaram nenhum curso no departamento de 'Química'",
         """
         SELECT DISTINCT
            a.nome AS "Nome do Aluno",
            a.ra AS "RA do Aluno"
        FROM
            aluno a
        LEFT JOIN (
            SELECT DISTINCT e.ra_aluno
            FROM escuta e
            JOIN disciplina d ON e.id_disc = d.id_disc
            JOIN departamento dep ON d.id_depto = dep.id_depto
            WHERE dep.nome_depto = 'Química'
        ) quimica ON a.ra = quimica.ra_aluno
        WHERE
            quimica.ra_aluno IS NULL
        ORDER BY
            a.nome
         """
    ),
    12: ("Encontre o número de alunos matriculados em cada curso e liste-os por título de curso",
         """
         SELECT 
            c.titulo_curso AS "Curso",
            COUNT(a.ra) AS "Número de Alunos"
        FROM 
            curso c
        JOIN 
            aluno a ON c.id_curso = a.id_curso
        GROUP BY 
            c.titulo_curso
        ORDER BY 
            COUNT(a.ra) DESC;

         """
    ),
    13: ("Recupere os nomes de todos os estudantes que cursaram 'Estrutura de Dados' no semestre '2024.1'",
         """
         SELECT 
            a.ra AS "RA do Aluno",
            a.nome AS "Nome do Aluno",
            e.nota AS "Nota",
            e.semestre AS "Semestre"
        FROM 
            aluno a
        JOIN 
            escuta e ON a.ra = e.ra_aluno
        JOIN 
            disciplina d ON e.id_disc = d.id_disc
        WHERE 
            d.nome_disc = 'Estrutura de Dados'
            AND e.semestre = '2024.1'
        ORDER BY 
            a.nome
         """
    ),
    14: ("Recupere os nomes e IDs dos professores que ensinam disciplinas com mais de 30 alunos matriculados",
         """
         SELECT 
            p.id_prof AS "ID do Professor",
            p.nome AS "Nome do Professor",
            d.nome_disc AS "Disciplina",
            COUNT(e.ra_aluno) AS "Total de Alunos"
        FROM 
            professor p
        JOIN 
            profere pf ON p.id_prof = pf.id_prof
        JOIN 
            disciplina d ON pf.id_disc = d.id_disc
        JOIN 
            escuta e ON pf.id_disc = e.id_disc AND pf.semestre = e.semestre
        GROUP BY 
            p.id_prof, p.nome, d.nome_disc
        HAVING 
            COUNT(e.ra_aluno) > 30
        ORDER BY 
            COUNT(e.ra_aluno) DESC
        LIMIT 300
         """
    ),
    15: ("Encontre o número de alunos matriculados em cada disciplina e liste-os pelo nome da disciplina",
         """
         SELECT 
            d.nome_disc AS "Disciplina",
            COUNT(e.ra_aluno) AS "Alunos no Semestre",
            e.semestre AS "Semestre Atual" 
        FROM 
            disciplina d
        JOIN 
            escuta e ON d.id_disc = e.id_disc
        WHERE 
            e.semestre = '2025.1' 
        GROUP BY 
            d.nome_disc, e.semestre
        ORDER BY 
    COUNT(e.ra_aluno) DESC;
         """
    ),
    16: ("Parte Ciência de Dados",
         """
         SELECT 
            c.titulo_curso AS Curso,
            d.nome_disc AS Disciplina,
            mc.semestre
        FROM 
            matriz_curricular mc
        JOIN 
            curso c ON mc.id_curso = c.id_curso
        JOIN 
            disciplina d ON mc.id_disciplina = d.id_disc
        WHERE 
            c.titulo_curso = 'Ciência de Dados'
        ORDER BY 
            mc.semestre, d.nome_disc
         """)
}

# Funcao para executar e imprimir os resultados
def executar_query(numero):
    try:
        conn = conectar()
        cursor = conn.cursor()
        descricao, comando = queries[numero]
        print(f"\n {descricao}\n")
        cursor.execute(comando)
        resultados = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        print(tabulate(resultados, headers=colunas, tablefmt='fancy_grid'))
        
    except Exception as e:
        print(f"Erro ao executar a query {numero}: {e}")
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()

# Menu 
def menu():
    while True:
        print("\n Menu de Consultas SQL")
        for num, (desc, _) in queries.items():
            if num == 16:
                continue
            else:
                print(f"{num}. {desc}")
        try:
            escolha = int(input("\nDigite o número da query que deseja executar (ou 0 para sair): "))
            if escolha == 0:
                print("Saindo do programa.")
                break
            if escolha in queries:
                executar_query(escolha)
            if escolha == 3:
                executar_query(escolha)
                executar_query(16)
        except ValueError:
            print("Por favor, digite um número válido.")

if __name__ == "__main__":
    menu()
