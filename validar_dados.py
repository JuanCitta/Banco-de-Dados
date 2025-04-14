import psycopg2

ULTIMO_SEM = 2025.1

def validar_dados():
    try:
        conn = psycopg2.connect(
            host="db.gmuoinhzwkcxwoinnqit.supabase.co",
            database="postgres",
            user="postgres",
            password="zGcUhOCaI1EUmLDX"
        )
        cursor = conn.cursor()

        tabelas = [
            "aluno", "disciplina", "professor", "curso", "departamento",
            "curso_disciplina", "matriz_curricular", "escuta", "profere", "tcc", "tcc_aluno"
        ]

        dados = {}
        for tabela in tabelas:
            cursor.execute(f"SELECT * FROM {tabela}")
            dados[tabela] = cursor.fetchall()

        erros = []
        ids_departamentos = set()
        for linha in dados["departamento"]:
            ids_departamentos.add(linha[0])

        ids_cursos = set()
        for linha in dados["curso"]:
            ids_cursos.add(linha[0])

        ids_alunos = set()
        for linha in dados["aluno"]:
            ids_alunos.add(linha[0])

        ids_disciplinas = set()
        for linha in dados["disciplina"]:
            ids_disciplinas.add(linha[0])

        ids_professores = set()
        for linha in dados["professor"]:
            ids_professores.add(linha[0])

        ids_tccs = set()
        for linha in dados["tcc"]:
            ids_tccs.add(linha[0])

        for linha in dados["aluno"]:
            ra = linha[0]
            id_curso = linha[2]
            if id_curso not in ids_cursos:
                erros.append(f"Aluno RA {ra} tem curso invalido: {id_curso}")
                
        for linha in dados["disciplina"]:
            id_disciplina = linha[0]
            id_departamento = linha[2]
            if id_departamento not in ids_departamentos or id_departamento is None:
                erros.append(f"Disciplina {id_disciplina} tem departamento invalido: {id_departamento}")
                
        departamentos_sem_professor = []
        for linha in dados["professor"]:
            id_professor = linha[0]
            id_departamento = linha[2]
            if id_departamento not in ids_departamentos:
                erros.append(f"Professor {id_professor} tem departamento invalido: {id_departamento}")
            for id_depto in ids_departamentos:
                tem_professor = any(linha[2] == id_depto for linha in dados["professor"])
                if not tem_professor:
                    departamentos_sem_professor.append(id_depto)
            if departamentos_sem_professor:
                erros.append(f"Departamentos sem professores: {departamentos_sem_professor}")
                
        for linha in dados["curso"]:
            id_curso = linha[0]
            id_coordenador = linha[2]
            if id_coordenador not in ids_professores or id_coordenador is None:
                erros.append(f"Curso {id_curso} tem coordenador invalido: {id_coordenador}")
                
        for id_disciplina, id_curso in dados["curso_disciplina"]:
            if id_curso not in ids_cursos:
                erros.append(f"Curso_disciplina: curso invalido {id_curso}")
            if id_disciplina not in ids_disciplinas:
                erros.append(f"Curso_disciplina: disciplina invalida {id_disciplina}")
            

        disciplina_semestre = set ()
        for id_curso, id_disciplina, semestre in dados["matriz_curricular"]:
            tupla = (id_disciplina, semestre)
            if id_curso not in ids_cursos or id_curso is None:
                erros.append(f"Matriz_curricular: curso invalido {id_curso}")
            if id_disciplina not in ids_disciplinas or id_disciplina is None:
                erros.append(f"Matriz_curricular: disciplina invalida {id_disciplina}")
                if tupla in disciplina_semestre:
                    erros.append(f"Matriz_Curricular: Disciplina {id_disciplina} duplicada no semestre {semestre}")
            else:
                disciplina_semestre.add(tupla)
        
        DP = []
        for linha in dados["escuta"]:
            ra = linha[0]
            id_disciplina = linha[1]
            nota = linha[3]
            ciclo = linha[4]
            if ra not in ids_alunos:
                erros.append(f"Escuta: RA invalido {ra}")
            if id_disciplina not in ids_disciplinas:
                erros.append(f"Escuta: disciplina invalida {id_disciplina}")
            if nota < 5:
                DP.append(linha)

        for ra, id_disciplina, sem, nota, ciclo in DP:
            fez_DP = False
        for linha in dados["escuta"]:
            ra2 = linha[0]
            id_disciplina2 = linha[1]
            sem2 = linha[2]
            nota2 = float(linha[3])

            if ra == ra2 and id_disciplina == id_disciplina2:
                if float(sem2) > float(sem) and nota2 >= 5:
                    fez_DP = True
                    break

        if not fez_DP and float(sem) != 2025.1:
            erros.append(f"Aluno {ra} reprovou e nao refez a disciplina {id_disciplina} {sem}")

                    

        for linha in dados["profere"]:
            id_professor = linha[0]
            id_disciplina = linha[1]
            semestre = linha[2]
            if id_professor not in ids_professores:
                erros.append(f"Profere: professor invalido {id_professor}")
            if id_disciplina not in ids_disciplinas:
                erros.append(f"Profere: disciplina invalida {id_disciplina}")
            if float(semestre)>= 2025.2 :
                erros.append(f"Ano ou semestre invalido Semestre:{semestre}")
            for l in dados["profere"]:
                if l[1] == id_disciplina and id_professor != l[0] and l[2] == semestre:
                    erros.append(f"Profere: mesma disciplina {l[1]} dada por dois professores de ids:{id_professor} e {l[0]} no semestre {semestre}")
                

        for linha in dados["tcc"]:
            id_tcc = linha[0]
            id_professor = linha[1]
            semestre = linha[4]
            if id_professor not in ids_professores:
                erros.append(f"TCC {id_tcc}: professor invalido {id_professor}")
            if float(semestre) > ULTIMO_SEM or semestre == "":
                erros.append(f"TCC {id_tcc}: semestre invalido {semestre}")

        for linha in dados["tcc_aluno"]:
            id_tcc = linha[0]
            ra = linha[1]
            if id_tcc not in ids_tccs:
                erros.append(f"TCC_aluno: id_tcc invalido {id_tcc}")
            if ra not in ids_alunos:
                erros.append(f"TCC_aluno: RA invalido {ra}")

        if len(erros) > 0:
            print("Erros de consistencia encontrados:")
            for erro in erros:
                print(" -", erro)
        else:
            print("Todas as tabelas estao consistentes.")

    except Exception as e:
        print(f"Erro: {e}")
        
    finally:
        if 'conn' in locals():
            conn.close()
validar_dados()
