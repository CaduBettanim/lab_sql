
<img src="https://raw.githubusercontent.com/Databricks-BR/lab_sql/main/images/header_handson_sql.png">

# Hands-On LAB 03 - Explorando o Query Profiler 

Treinamento Hands-on na plataforma Databricks com foco nas funcionalidades de Analytics (SQL, Query, DataViz, Genie).


## Objetivos do Exercício

O objetivo desse laboratório é explorar as funcionalidade de plano de execução das consultas (Query Profiler). Sabendo identificar os gargalos e oportunidades de melhoria de desempenho. </br>
</br>


<img src="https://raw.githubusercontent.com/Databricks-BR/lab_sql/main/images/desnormaliza.png">

Vamos utilizar o "Editor SQL".

## Exercício 03.01 - Criação da Query

``` sql
CREATE OR REPLACE TABLE big_table AS
SELECT 
  ve.id_loja AS id_loja,
  lo.cod AS codigo_loja,
  lo.varejista AS varejista,
  lo.nlj AS nome_da_loja,
  lo.tipo AS tipo_de_loja,
  lo.cep AS cep,
  lo.lat_long AS lat_long,
  ve.id_produto AS id_produto,
  me.nome_medicamento AS nome_medicamento,
  me.categoria_regulatoria AS categoria_regulatoria,
  me.numero_registro_produto AS numero_registro_produto,
  me.data_vencimento_registro AS data_vencimento_registro,
  me.numero_processo AS numero_processo,
  me.classe_terapeutica AS classe_terapeutica,
  me.cod_empresa AS cod_empresa,
  me.empresa_detentora_registro AS empresa_detentora_registro,
  me.principio_ativo AS principio_ativo,
  es.id_estoque AS id_estoque,
  es.data_estoque AS data_estoque,
  es.estoque AS quantidade_estoque,
  ve.id_venda AS id_venda,
  ve.dt_venda AS data_venda,
  ve.qt_venda AS quantidade_venda,
  ve.vl_venda AS vl_venda
FROM bronze_vendas ve
LEFT JOIN bronze_dim_loja lo
  ON ve.id_loja = lo.cod
LEFT JOIN bronze_dim_medicamento me
  ON ve.id_produto = me.id_produto
LEFT JOIN bronze_estoque es
  ON me.id_produto = es.id_produto

```

## Exercício 03.02 - Visualizando o Histórico de execução das Consultas


No Menu, escolha a opção "Query History"

<img src="https://raw.githubusercontent.com/Databricks-BR/lab_sql/main/images/lab03_1.png" style="height: 200px;">

Filtre as Consultas (p.ex.  Selecione suas próprias Queries):

<img src="https://raw.githubusercontent.com/Databricks-BR/lab_sql/main/images/lab03_2.png" style="height: 300px;">

## Exercício 03.03 - Analisando o Detalhe da Execução

<img src="https://raw.githubusercontent.com/Databricks-BR/lab_sql/main/images/lab03_3.png" style="height: 200px;">


## Exercício 03.04 - Analisando o Query Profiler

<img src="https://raw.githubusercontent.com/Databricks-BR/lab_sql/main/images/lab03_4.png" style="height: 200px;">


## Exercício 03.05 - Analisando o Plano de Execução

<img src="https://raw.githubusercontent.com/Databricks-BR/lab_sql/main/images/lab03_5.png" style="height: 250px;">

<img src="https://raw.githubusercontent.com/Databricks-BR/lab_sql/main/images/lab03_6.png" style="height: 700px;">


