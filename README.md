# Banco-de-Dados
Projeto para a matéria CC5232-Banco de Dados

Feito por: 
Juan Manuel Citta 24.123.022-6
Sebastian Citta 24.123.068-9
Luis Fernando Souza Goncalves 24.123.052-3

##Descrição:
O banco de dados foi projetado para simular um database de uma faculdade.

Os dados são gerados pelo arquivo script_criacao_e_insercao.py e tem consistência e continuidade (e.g. um aluno repete disciplinas que não tirou nota > 5, continuidade de semestres, etc.).

Esses dados podem ser validados utilizando o arquivo validar_dados.py, que imprimirá mensagens de erro caso encontre algum erro de consistência. A validação é majoritariamente voltada para os diversos ids,
checkando se são válidos e algumas tabelas (e.g. escuta e matriz_curricular) são checkadas por continuidade e consistência.

Com o arquivo queries.py o usuário pode escolher entre as 15 queries requisitadas pelo projeto e o resultado será imprimido na tela do terminal.

##Como executar:


Para o arquivo queries.py basta executar o arquivo python no terminal ou com um IDE de preferência. Depois para navegar o menu basta digitar o número com a query que deseja ver. As queries também estão disponíveis no arquivo Queries do repositório.
![image](https://github.com/user-attachments/assets/bbf3e4b0-7c2e-4934-9f79-43973d281b76)

Para o arquivo scrip_criacao_e_insercao.py fazer o mesmo. Porém o código rodará sozinho e imprimirá mensagens de confirmação no terminal. (A inserção de profere e escuta pode demorar).

![image](https://github.com/user-attachments/assets/92006501-8c8f-4602-be80-e199e8eb6a57)

Para o arquivo validar_dados.py fazer o mesmo que no script de criação.

![image](https://github.com/user-attachments/assets/87989c6e-97b7-42c6-a4c3-57086477421c)




##Diagrama:

![image](https://github.com/user-attachments/assets/4f52f13d-24f2-4646-bf5e-cd0cf051affa)

##MER: 
![mermaid-diagram-2025-04-16-140701](https://github.com/user-attachments/assets/d125d61f-cd82-492c-bfa8-f9363821d9fb)




