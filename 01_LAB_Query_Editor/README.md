
<img src="https://raw.githubusercontent.com/Databricks-BR/lab_sql/main/images/header_handson_sql.png">

# Hands-On LAB 01 - Explorando o Editor de Query

Treinamento Hands-on na plataforma Databricks com foco nas funcionalidades de Analytics (SQL, Query, DataViz, Genie).


## Objetivos do Exercício

O objetivo desse laboratório é conhecer as funcionalidades de consulta (_Query_) da plataforma Databricks, utilizando a linguagem SQL (e as interfaces visuais), explorando os potenciais Analíticos. </br>
</br>
Os exercícios deverão ser executados na opção do Menu lateral "**SQL Editor**".

<img src="https://github.com/Gabriel-Rangel/lab_sql/blob/main/images/v2_lab01_1.png">


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

## Exercício 01.01 - Criação do database

``` sql
CREATE CATALOG IF NOT EXISTS dbacademy; 

CREATE DATABASE IF NOT EXISTS <seu_nome_login>;

USE CATALOG dbacademy;

USE <seu_nome_login>;
```

## Exercício 01.02 - Criação da Tabela

``` sql
CREATE OR REPLACE TABLE porte_empresa 
  ( id_natureza_juridica    INT     COMMENT "codigo do porte da empresa",
    sig_natureza_juridica   STRING  COMMENT "sigla que representa a natureza juridica da empresa",
    desc_natureza_juridica  STRING  COMMENT "descricao da natura juridica" )
COMMENT "Tabela auxiliar do tipo de natureza juridica das empresas"
```

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


DELETE 
FROM porte_empresa 
WHERE id_natureza_juridica = 7;
```

## Exercício 01.06 - Visualizando o Histórico de Atualizações da tabela

 ``` sql
DESCRIBE HISTORY porte_empresa 
```

## Exercício 01.07 - Visualizando o conteúdo da tabela na versão anterior (TIME TRAVEL)

 ``` sql
SELECT * FROM porte_empresa VERSION AS OF 5
```

## Exercício 01.08 - RESTAURANDO o conteúdo da tabela na versão anterior (TIME TRAVEL)

 ``` sql
RESTORE TABLE porte_empresa TO VERSION AS OF 5 
```

## Exercício 01.09 - Visualizando as propriedades da Tabela

 ``` sql
DESCRIBE DETAIL porte_empresa 
```

## Exercício 01.10 - Visualizando as informações DETALHADAS da Tabela

 ``` sql
DESCRIBE TABLE EXTENDED porte_empresa
```
