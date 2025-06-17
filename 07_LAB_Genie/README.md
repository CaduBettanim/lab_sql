<img src="https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/header_genie.png">

# Hands-On LAB 03 - Criando o AI/BI Genie

Treinamento Hands-on na plataforma Databricks com foco nas funcionalidades de perguntas e respostas usando linguagem natural.

</br></br>

## Objetivos do Exercício

O objetivo desse laboratório é usar o AI/BI Genie para permitir a análise de dados de vendas utilizando somente **Português**.

</br></br>

## Exercício 03.00 - Preparação

1. Em alguns momentos, utilizaremos o SQL Editor. Deixe-o preparado em uma outra janela e selecione seu database.

<img src="https://github.com/Gabriel-Rangel/lab_sql/blob/main/images/v2_genie_1.png?raw=true">

</br></br>

## Exercício 03.01 - Criar AI/BI Genie

Vamos começar criando uma Genie para fazer nossas perguntas. Para isso, vamos seguir os passos abaixo:

1. No menu principal (à esquerda), clique em `New` > `Genie space`

<img src="https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/genie_01.png"><br><br>

2. Configure sua Genie
    - Selecione as seguintes tabelas:
        - vendas
        - estoque
        - dim_medicamento
        - dim_loja
    - Clique em `Create`

<img src="https://github.com/Gabriel-Rangel/lab_sql/blob/main/images/v2_genie_3.png?raw=true" width=800>

3. Altere o nome da sua Genie Space e seu espaço deve ficar assim:
<img src="https://github.com/Gabriel-Rangel/lab_sql/blob/main/images/v2_genie_4.png?raw=true">

</br></br>

## Exercício 03.02 - Fazendo perguntas ao AI/BI Genie

Com nossa Genie preparada, podemos começar a fazer nossas análises!

Basta usar o chat para fazer as perguntas abaixo:

- Qual o faturamento em out/22?
- Agora, quebre por produto
- Mantenha somente os 10 produtos com maior faturamento
- Monte um gráfico de barras
- Qual o total de produtos vendidos em genéricos?
- Qual o valor total vendido de ansiolíticos?
- Quais produtos tiveram uma proporção de vendas por estoque maior que 0.8 em Outubro de 2022?

<img src="https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/genie_05.png"><br><br>

Notem que, mesmo com muito pouco contexto, a Genie já conseguiu:
- Inferir quais as tabelas e colunas relevantes para responder nossas perguntas
- Aplicar filtros e agregações
- Responder perguntas adicionais sobre uma resposta anterior
- Entender como utilizar jargões
- Combinar diferentes tabelas
- Calcular métricas derivadas

Aproveitem para explorar e fazer perguntas adicionais!

</br></br>

## Exercício 03.03 - Usando comentários

Mesmo assim, podem ocorrer cenários onde precisaremos fornecer algum contexto adicional à Genie para obter respostas mais precisas.

Agora, vamos explorar algumas formas de auxiliar a Genie quando identificarmos alguma necessidade.

A primeira delas é documentar nossas tabelas. Todos os comentários que adicionamos às tabelas são utilizados pela Genie para entender melhor o que é aquele dado.

Vamos ver como funciona!

1. Faça a seguinte pergunta:
    - Qual o valor total de venda por loja? Exiba o nome da loja

2. Ops, parece que a Genie não conseguiu descobrir qual coluna contém o nome da loja. Use o SQL Editor para adicionar um comentário na coluna **nlj** da tabela **dim_loja** e explicar que ela contém essa informação
    - `ALTER TABLE dim_loja ALTER COLUMN nlj COMMENT 'Nome da loja'`

<img src="https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/genie_06.png"><br><br>

3. Faça novamente a pergunta anterior<br><br>

Percebam que dessa vez a Genie utilizou a coluna correta que contém o nome da loja.

Documentar suas tabelas com comentários é sempre uma boa prática! Isso ajuda a compreensão, a descoberta e o reaproveitamento desses dados por outras pessoas. Além disso, vai acabar ajudando a melhorar as respostas da Genie.

No entanto, nossa consulta ainda não retornou nenhum resultado. Vamos buscar uma solução!

</br></br>

## Exercício 03.04 - Usando chaves primárias

Aparentemente, a coluna **id_loja** da tabela **dim_loja** não é o melhor campo para fazer os cruzamentos com a tabela de vendas. Na verdade, a coluna correta é a **cod**!

Vamos então adicionar chaves primárias e estrangeiras nessas tabelas para que a Genie não precise inferir como fazer esse cruzamento!

1. Use o SQL Editor para adicionar as chaves primárias e estrangeiras nas tabelas `dim_loja` e `vendas`

``` sql
alter table dim_loja alter column cod set not null;
ALTER TABLE dim_loja ADD CONSTRAINT pk_dim_loja PRIMARY KEY (cod);
ALTER TABLE vendas ADD CONSTRAINT fk_venda_dim_loja FOREIGN KEY (id_loja) REFERENCES dim_loja(cod);
```
2. Faça novamente a pergunta anterior na Genie

Pronto! Com essa informação a Genie já consegue responder nossa pergunta corretamente!

</br></br>

## Exercício 03.05 - Usando instruções

Como vimos, a Genie utiliza toda a documentação das nossas tabelas para conseguir responder nossas perguntas. No entanto, por motivos de segurança, ela não tem acesso aos dados em si!

Por isso, para complementar o conhecimento que a Genie já possui sobre nossas bases de dados, podemos também criar instruções!

**Instruções** são nada mais que um conjunto de sentenças em linguagem natural que podem explicar para a Genie informações importantes como:
- Significado de abreviações e termos técnicos comumente utilizadas na sua empresa
- Formato do dado (por exemplo, se os registros estão em maiúsculas ou minúsculas)
- Tratamentos necessários para determinados campos
- Cálculos de métricas

Vamos ver como funciona:

1. Faça a pergunta:
    - Calcule a quantidade de itens vendidos para prescrição

2. Me parece que o resultado não está correto! Na nossa base, o termo prescrição realmente não é mencionado nenhuma vez. Mas acontece que aqui consideramos como medicamentos de prescrição aqueles que não são genéricos. Por isso, adicione a seguinte instrução:
    - `* para calcular indicadores sobre prescrição use categoria_regulatoria <> 'GENÉRICO'`

<img src="https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/genie_07.png">

3. Faça novamente a pergunta anterior

Pronto! Agora a Genie já pode responder perguntas sobre prescrições também!

</br></br>

## Exercício 03.06 - Usando exemplos de queries

Em alguns casos, precisamos fazer cruzamentos e cálculos bastante complexos para conseguir responder às nossas perguntas e a Genie pode não entender como montar todo o racional necessário.

Nesses casos, podemos fornecer exemplos de queries validadas e certificadas pelos times responsáveis. Este também é um mecanismo interessante para garantir a acurácia das respostas.

Vamos ver como funciona:

1. Faça a pergunta:
    - Calcule a quantidade de itens vendidos por janela móvel de 3 meses 

2. Aqui a Genie já até fez uma soma em janela móvel, porém não ficou exatamente do jeito que nós gostaríamos. Então, adicione um exemplo de query seguindo os passos abaixo:
    - Clique em `Instructions`, no menu à esquerda
    - Clique em `Add Example Query`
    - Insira a pergunta anterior no campo superior
    - Insira a query abaixo no campo inferior
        - `SELECT window.end AS dt_venda, SUM(vl_venda) FROM vendas GROUP BY WINDOW(dt_venda, '90 days', '1 day')`

<img src="https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/genie_08.png">

3. Faça novamente a pergunta anterior

Notem que agora a Genie conseguiu responder corretamente a nossa pergunta!

</br></br>

## Exercício 03.07 - Usando funções

Outro recurso que podemos utilizar para ajudar a Genie com cálculos complexos são as funções!

**Funções** permitem guardarmos e parametrizar lógicas complexas dentro do nosso catálogo para serem reutilizadas por outras pessoas e/ou outras consultas de forma simples – inclusive fora da Genie. 

No nosso contexto, as funções também vão funcionar como ferramentas validades e certificadas pelos times responsáveis que a Genie pode decidir utilizar nas suas respostas.

Vamos ver na prática:

1. Faça a pergunta:
    - Qual o lucro projetado do AAS?

2. Realmente, não temos informações suficientes na nossa base para responder à essa pergunta! Para isso, crie a função abaixo com a lógica do cálculo do lucro médio projetado de um produto:

``` sql
CREATE OR REPLACE FUNCTION calc_lucro(medicamento STRING)
  RETURNS TABLE(nome_medicamento STRING, lucro_projetado DOUBLE)
  COMMENT 'Use esta função para calcular o lucro projetado de um medicamento'
  RETURN 
    SELECT
      m.nome_medicamento,
      sum(case when m.categoria_regulatoria == 'GENÉRICO' then 1 else 0.5 end * v.vl_venda) / sum(v.qt_venda) as lucro_projetado
    FROM vendas v
    LEFT JOIN dim_medicamento m
    ON v.id_produto = m.id_produto
    WHERE m.nome_medicamento = calc_lucro.medicamento
    GROUP BY ALL
```

3. Adicione esta função a sua Genie

<img src="https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/genie_09.png">

4. Faça novamente a pergunta anterior

Pronto! Com isso, conseguimos calcular o lucro médio do nosso produto!

<br><br>

# Parabéns!

Você concluiu o laboratório do **AI/BI Genie**!

Agora, você já sabe como utilizar a Genie para analisar seus dados usando somente linguagem natural – além dos principais recursos para refinar sua acurácia e conseguir responder as perguntas mais complexas!
