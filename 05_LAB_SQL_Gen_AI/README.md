<img src="https://raw.githubusercontent.com/Databricks-BR/lab_sql/main/images/header_handson_sql.png">

# Hands-On LAB 07 - Funcionalidades de Generative AI no SQL

Treinamento Hands-on na plataforma Databricks com foco nas funcionalidades de Analytics (SQL, Query, Dask, DataViz, SQL end-point).


## Exercício 07.01 - Sobre as Funcionalidades:


Uma forma de aplicar os modelos de IA Generativa é utilizar as Databricks AI SQL Functions.

Estas permitem a utilização de SQL, uma linguagem amplamente utiliza por analistas de dados e de negócio, para executar uma LLM sobre nossos bancos de dados corporativos. Com isso, também podemos criar novas tabelas com as informações extraídas para serem utilizadas em nossas análises mais facilmente.

Existem funções nativas para executar tarefas pré-definidas ou enviar qualquer instrução desejada para ser executada. Seguem as descrições abaixo:



| Gen AI SQL Function | Descrição |
| -- | -- |
| [ai_analyze_sentiment](https://docs.databricks.com/pt/sql/language-manual/functions/ai_analyze_sentiment.html) | Análise de Sentimento |
| [ai_classify](https://docs.databricks.com/pt/sql/language-manual/functions/ai_classify.html) | Classificação de Texto |
| [ai_extract](https://docs.databricks.com/pt/sql/language-manual/functions/ai_extract.html) | Extração de Termos |
| [ai_fix_grammar](https://docs.databricks.com/pt/sql/language-manual/functions/ai_fix_grammar.html) | Correção de Gramática |
| [ai_gen](https://docs.databricks.com/pt/sql/language-manual/functions/ai_gen.html) | Geração de Textos | 
| [ai_mask](https://docs.databricks.com/pt/sql/language-manual/functions/ai_mask.html) | Marcaramento de dados sensíveis |
| [ai_query](https://docs.databricks.com/pt/sql/language-manual/functions/ai_query.html) | Consultas Gen Ai |
| [ai_similarity](https://docs.databricks.com/pt/sql/language-manual/functions/ai_similarity.html) | Análise de Similaridade |
| [ai_summarize](https://docs.databricks.com/pt/sql/language-manual/functions/ai_summarize.html) | Sumarização de Textos |
| [ai_translate](https://docs.databricks.com/pt/sql/language-manual/functions/ai_translate.html) | Tradução de Textos |


</br></br>
Para esse exercício, vamos explorar as funcionalidades citadas,  conforme exemplo abaixo:

**ai_translate**
``` md
SELECT texto as original, 
       ai_translate(texto, 'br') as traducao
  FROM (select 'Hello, how are you?' as texto)
;
```
</br>

**ai_extract**

``` md
SELECT ai_extract(
    'Envie um email para jane.doe@example.com sobre a reunião que marcamos as 10am.',
    array('email', 'time')
  );
```

**ai_mask**.
``` md

SELECT ai_mask(
    'Me chamo Flavio Da Silva. Entre em contato comigo no 555-1234 ou nos visite na Av.Paulista, 1000',
    array('phone', 'address')
);
```

**ai_gen**
``` md
SELECT principio_ativo
     , ai_gen(concat('forneça mais detalhes de como o medicamento ',principio_ativo,' atua no organismo de uma pessoa adulta. Forneça um texto de até 50 palavras')) 
  FROM dbacademy.<seu_database>.dim_medicamento 
 LIMIT 10
 ;
```

Agora vamos pegar nossa tabela de medicamentos,</br> 
criar uma nova coluna atribuindo comentários a cada medicamento de forma aleatória  usando a função **ai_gen** </br>
e depois criar uma nova coluna com a análise de sentimento da coluna de comentários usando a função **ai_analyze_sentiment**.

``` md
WITH 
sizing AS (SELECT * FROM dbacademy.<seu_database>.dim_medicamento LIMIT 10),
comentarios AS (
    SELECT
    CASE
            WHEN rand() > 0.5 THEN ai_gen(CONCAT('Escreva em português um comentário positivo sobre o medicamento: ', nome_medicamento))
            ELSE ai_gen(CONCAT('Invente em português um comentário negativo sobre o medicamento', nome_medicamento,'. Esse medicamento nao existe. seja criativo'))
    END AS medicamento_review
    FROM sizing
)
    SELECT
    *,
    ai_analyze_sentiment(medicamento_review) AS sentimento_review
    FROM comentarios;
```
**ai_fix_grammar**.

``` md
SELECT ai_fix_grammar('Nóis tá com fome. Bora fazer um break e comer um pão de queijo minero dos bão?');
```

</br></br>
</br></br>


