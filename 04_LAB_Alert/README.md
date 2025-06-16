<img src="https://raw.githubusercontent.com/Databricks-BR/lab_sql/main/images/header_handson_sql.png">

# Hands-On LAB 04 - Criação de um ALERTA

Treinamento Hands-on na plataforma Databricks com foco nas funcionalidades de Analytics (SQL, Query, Dask, DataViz, SQL end-point).


## Objetivos do Exercício

O objetivo desse laboratório é explorar as funcionalidade de criação de um ALERTA
</br></br>

## Exercício 04.01 - Criando o Alerta

Vamos utilizar a opção do menu  "**ALERTS**".

<img src="https://github.com/Gabriel-Rangel/lab_sql/blob/main/images/v2_lab04_1.png?raw=true" style="height: 200px;">

</br></br>

Clique no botão **CREATE ALERT**

O SQL Editor agora é integrado ao Alerta, copia a query abaixo e clique em **RUN**
``` sql

SELECT close AS valor_apple
FROM dbacademy.SEU_NOME.bronze_stock_bigtech
WHERE stock = 'AAPL'
ORDER BY date DESC;

```
<img src="https://github.com/Gabriel-Rangel/lab_sql/blob/main/images/v2_lab04_2.png?raw=true">
</br></br>

A query rodando com sucesso, habilitara a parte de configuração a esqueda, configura conforme imagem abaixo

Não esqueça de nomear seu alerta: Sugestão: "Query_Alert"+ <SEU_LOGIN> e clique em **CREATE**


<img src="https://github.com/Gabriel-Rangel/lab_sql/blob/main/images/v2_lab04_3.png?raw=true" style="height: 700px;">


