<img src="https://raw.githubusercontent.com/Databricks-BR/lab_sql/main/images/header_handson_sql.png">

# Hands-On LAB 07 - Funcionalidades de Generative AI no SQL

Treinamento Hands-on na plataforma Databricks com foco nas funcionalidades de Analytics (SQL, Query, Dask, DataViz, SQL end-point).


## Exercício 07.01 - Sobre as Funcionalidades:


Uma forma de aplicar os modelos de IA Generativa é utilizar as Databricks AI SQL Functions.

Estas permitem a utilização de SQL, uma linguagem amplamente utiliza por analistas de dados e de negócio, para executar uma LLM sobre nossos bancos de dados corporativos. Com isso, também podemos criar novas tabelas com as informações extraídas para serem utilizadas em nossas análises mais facilmente.

Existem funções nativas para executar tarefas pré-definidas ou enviar qualquer instrução desejada para ser executada. Seguem as descrições abaixo:


%md

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


</br></br></br></br>
Para esse exercício, vamos explorar as funcionalidades citadas,  conforme exemplo abaixo:


``` md

SELECT ai_translate('Hello, how are you?', 'br') as traducao;


```

</br></br>
</br></br>


