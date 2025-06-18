
<img src="https://raw.githubusercontent.com/Databricks-BR/lab_sql/main/images/header_handson_sql.png">

# Hands-On LAB 01 - Explorando o Editor de Query

Treinamento Hands-on na plataforma Databricks com foco nas funcionalidades de Analytics (SQL, Query, DataViz, Genie).


## Objetivos do Exercício

O objetivo desse laboratório é conhecer as funcionalidades de consulta (_Query_) da plataforma Databricks, utilizando a linguagem SQL (e as interfaces visuais), explorando os potenciais Analíticos. </br>
</br>
Os exercícios deverão ser executados na opção do Menu lateral "**SQL Editor**".

<img src="https://github.com/Gabriel-Rangel/lab_sql/blob/main/images/v2_lab01_1.png?raw=true">


</br></br></br>
## Sessão 01:  Estrutura TABELAS, DATABASE e CATÁLOGOS

<img src="https://raw.githubusercontent.com/Databricks-BR/lab_sql/main/images/lab01_uc.png">


| Tópico | Comando |
| -- | -- |
| **Catálogo** | CREATE CATALOG <nome_catalogo> |
| **Schema** | CREATE DATABASE IF NOT EXISTS <nome_catalogo>.<nome_database>; |
| **Tabela** | CREATE OR REPLACE TABLE  <nome_catalogo>.<nome_database>.<nome_tabela>; |
| **View** |  CREATE OR REPLACE VIEW  <nome_catalogo>.<nome_database>.<nome_tabela> AS ...; |

#### Referência:
* [Databricks Help - DDL Syntax](https://docs.databricks.com/sql/language-manual/sql-ref-syntax-ddl-create-table.html)

## Exercício 01.01 - Criação do catálago e database

``` sql
GRANT CREATE CATALOG ON METASTORE TO `account users`;
CREATE CATALOG IF NOT EXISTS dbacademy;
USE CATALOG dbacademy;

CREATE DATABASE IF NOT EXISTS <seu_nome>;
USE <seu_nome>;
```

## Exercício 01.02 - Criação da Tabela
1. Na primeira query do laboratório realizamos a criação de catálago e database w utilizamos a cláusula *USE*, mas ela só é persistida em tempo de execução;
2. Devemos sempre atribuir o nome do catálago e database antes do nome da tabela separado por "." (dbacademy.<seu_nome>.porte_empresa)</br>
ou podemos especificar o catálago e database que queremos usar no próprio editor conforme imagem abaixo:
</br></br>
<img src="https://github.com/Gabriel-Rangel/lab_sql/blob/main/images/v2_lab01_setcatalago.png?raw=true">
</br></br>
3. Crie a tabela a seguir:
``` sql
CREATE OR REPLACE TABLE porte_empresa 
  ( id_natureza_juridica    INT     COMMENT "codigo do porte da empresa",
    sig_natureza_juridica   STRING  COMMENT "sigla que representa a natureza juridica da empresa",
    desc_natureza_juridica  STRING  COMMENT "descricao da natura juridica" )
COMMENT "Tabela auxiliar do tipo de natureza juridica das empresas"
```
</br>

 ## Exercício 01.03 - Inserindo dados na Tabela através de SQL INSERT

 ``` sql
 INSERT INTO porte_empresa VALUES (1, "MEI", "Microempreendedor Individual") ;
 INSERT INTO porte_empresa VALUES (2, "EI", "Empresario Individual") ;
 INSERT INTO porte_empresa VALUES (3, "SLU", "Sociedade Limitada Unipessoal") ;
 INSERT INTO porte_empresa VALUES (4, "LTDA", "Sociedade Empresaria Limitada") ;
 INSERT INTO porte_empresa VALUES (5, "SS", "Sociedade Simples") ;
 INSERT INTO porte_empresa VALUES (6, "S/A", "Sociedade Anônima") ;
 INSERT INTO porte_empresa VALUES (7, "NULL", "NULL") ;
```

 ## Exercício 01.04 - Verificando o conteúdo da TABELA

 ``` sql
SELECT * 
FROM porte_empresa 
ORDER BY id_natureza_juridica
```

 ## Exercício 01.05 - Alterando o conteúdo da TABELA

 ``` sql
UPDATE porte_empresa  
SET desc_natureza_juridica = "OUTROS" 
WHERE id_natureza_juridica = 7;
```

``` sql
SELECT * 
FROM porte_empresa
WHERE id_natureza_juridica = 7
```

``` sql
DELETE 
FROM porte_empresa 
WHERE id_natureza_juridica = 7;
```

``` sql
SELECT * FROM porte_empresa
```

## Exerício 01.06 - Liquid Clustering
O Liquid clustering substitui o particionamento de tabelas e o ZORDER para simplificar as decisões de disposição de dados e otimizar o desempenho das consultas. Ele oferece a flexibilidade de redefinir a chave clustering sem reescrever os dados existentes, permitindo que a disposição dos dados evolua junto com as necessidades analíticas ao longo do tempo.

Mas quando aplicar liquid clustering ?
* Tabelas normalmente filtradas por colunas de alta cardinalidade.</br>
* Tabelas com grande distorção na distribuição de dados.</br>
* Tabelas que crescem rapidamente e exigem manutenção e ações de ajuste.</br>
* Tabelas com requisitos de gravação concorrente.</br>
* Tabelas com padrões de acesso que mudam com o tempo.</br>
* Tabelas em que uma chave de partição típica poderia deixar a tabela com muitas ou poucas partições.</br>

A sintaxe para habilitar essa funcionalidade em uma tabela já criada é: </br>
<span style="color:red"> **NÃO EXECUTAR** </span>
```sql
ALTER TABLE <table_name>
CLUSTER BY (<clustering_columns>)
```
Além disso podemos deixar a própria Plataforma de dados inteligente da databricks definir quais são as melhores colunas da nossa tabela para serem definidas como *clustering*.</br>
<span style="color:green"> **VAMOS EXECUTAR ESSE EXEMPLO** </span>
```sql
ALTER TABLE porte_empresa
CLUSTER BY AUTO
```
#### Referências:
* [Databricks Liquid Clustering](https://docs.databricks.com/aws/pt/delta/clustering)
* [BLOG - Announcing Automatic Liquid Clustering](https://www.databricks.com/blog/announcing-automatic-liquid-clustering)

## Exercício 01.07 - Visualizando o Histórico de Atualizações da tabela

 ``` sql
DESCRIBE HISTORY porte_empresa 
```

## Exercício 01.08 - Visualizando o conteúdo da tabela na versão anterior (TIME TRAVEL)

 ``` sql
SELECT * FROM porte_empresa VERSION AS OF 7
```

## Exercício 01.09 - RESTAURANDO o conteúdo da tabela na versão anterior (TIME TRAVEL)

 ``` sql
RESTORE TABLE porte_empresa TO VERSION AS OF 7
```

## Exercício 01.10 - Visualizando as propriedades da Tabela

 ``` sql
DESCRIBE DETAIL porte_empresa 
```

## Exercício 01.11 - Visualizando as informações DETALHADAS da Tabela

 ``` sql
DESCRIBE TABLE EXTENDED porte_empresa
```
