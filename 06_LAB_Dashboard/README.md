<img src="https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/header_genie.png">

# Hands-On LAB 06 - Criando o Dashboard AI/BI

Treinamento Hands-on na plataforma Databricks com foco nas funcionalidades de Análise Exploratória e Painéis.
</br></br>

## Objetivos do Exercício

O objetivo desse laboratório é montar um Painel, utilizando os dados de ações das Big Tech da NASDAQ.</br> 
***Caso não tenha feito ainda, carregue os dados conforme descrito no Lab 02 - LAB_Notebook.***
</br></br>


## Exercício 06.01 - Criando o Dashboard

No Menu Lateral, escolha a opção DASHBOARDS:

Clique na opção **CREATE DASHBOARD**

Na tela do Dashboard, clique na ABA **"Data"** para adicionar uma fonte de dados:

<img src="https://raw.githubusercontent.com/Databricks-BR/lab_sql/main/images/lab05_ai_01.png" style="height: 300px;"></br>

Escolha a opção *"Add data source"*

<img src="https://github.com/Gabriel-Rangel/lab_sql/blob/main/images/v2_lab05_5.png?raw=true" style="height: 300px;">

Digite a palavra de busca **"<seu_database>.stock_bigtech"** escolha a tabela e depois volte para área do **CANVAS**

Clique no menu suspenso, para adicionar uma nova visualização.  </br>
Selecione com o mouse a área onde vai ficar o gráfico.

<img src="https://raw.githubusercontent.com/Databricks-BR/lab_sql/main/images/lab05_ai_04.png" style="height: 200px;">

</br></br>
Na lacuna de texto do ASSISTENTE (Generative AI), faça a seguinte solicitação:
``` md
gráfico de linhas do valor de fechamento por dia e por empresa
```

<img src="https://raw.githubusercontent.com/Databricks-BR/lab_sql/main/images/lab05_ai_05.png" style="height: 100px;"></br>


<img src="https://github.com/Gabriel-Rangel/lab_sql/blob/main/images/v2_lab05_1.png?raw=true" width="800px">
</br></br></br>

## Exercício 02.03 - Adicionando um FILTRO de página

Clique no menu azul suspenso no ícone de FILTRO.</br>
Escolha o atributo (Field):  "**company**"
</br></br>
<img src="https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/lab2_06.png" width="850px">
</br></br></br>


## Exercício 02.04 - Alterando o título do painel por uma imagem

No box de texto do títudo do painel, apague o texto anterior, </br>
e substitua pelo código (markdown) abaixo: </br>
</br>

``` sql
![image](https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/header_painel.png)
```

</br></br>
<img src="https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/lab2_07.png" width="700px">
</br></br></br>


Organize o layout do dashboard para que fique com a aparência da imagem abaixo.</br>
Faça o devido alinhamento do gráfico no layout.</br>
Altere o nome do Dashboard na barra superior.</br>
Clique no botão "**Publish**" para publicar o Painel.
</br></br>
<img src="https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/lab2_08.png" width="700px">
</br></br></br>


## Exercício 02.05 - Criando um NOVO contexto de dados

Vamos criar agora um novo contexto de dados.</br>
Para isso, entre na opção "**SQL Editor**" no MENU lateral do Databricks, </br>
selecione o Catálogo e o Schema na barra superior do Editor de Query,</br>
e escreva o texto abaixo:</br>

``` 

Selecione o nome da empresa, stock,
mínimo valor de fechamento, máximo valor de fechamento
e percentual de variação entre o mínimo e o máximo valor de fechamento
da tabela stock_bigtech
agrupando por empresa e stock.
Use a coluna company para achar o nome da empresa

```
</br></br>
<img src="https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/lab2_09.png" width="700px">
</br></br></br>

Acrescente ao resultado a linha de concatenação com o nome da ação (STOCK), </br>
com o LINK (URL) de uma imagem. </br>

``` sql

SELECT 
  "https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/" || stock || ".png" AS image,
  company,
  stock,
  MIN(close) AS min_close,
  MAX(close) AS max_close,
  ((MAX(close) - MIN(close)) / MIN(close) * 100) AS percentual_variacao
FROM dbacademy.<seu_database>.stock_bigtech
GROUP BY company, stock;

```
</br>
Ao executar a query (botão RUN),</br>
o resultado esperado é o mostrado abaixo:</br>
<img src="https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/lab2_10.png" width="700px">
</br></br></br>

## Exercício 02.06 - Adicionando o NOVO contexto de dados ao Dashboard

Agora vamos adicionar o novo contexto de dados (calculado na Query);</br>
como mais uma fonte de dados no Painel.</br>
Para isso, volte na opção "**Dashboards**" no menu lateral Databricks,</br>
Escolha o nome do Painel que foi criado,</br>
e Clique no botão (combo box) de "**Published**" para "**Draft**".
</br></br>
<img src="https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/lab2_10b.png" width="700px">
</br></br></br>

Clique na opção "**Data**".</br>
No item "Create another Dataset"</br>
clique no botão "**+Create from SQL**".</br>

</br></br>
<img src="https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/lab2_11.png" width="700px">
</br></br></br>

Faça o Copy&Paste do código SQL gerado no exercício anterior:

``` sql

SELECT 
  "https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/" || stock || ".png" AS image,
  company,
  stock,
  MIN(close) AS min_close,
  MAX(close) AS max_close,
  ((MAX(close) - MIN(close)) / MIN(close) * 100) AS percentual_variacao
FROM dbacademy.gabriel_rangel.stock_bigtech
GROUP BY company, stock;

```
E depois clique no botão "**RUN**"
</br>
<img src="https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/lab2_12.png" width="700px">
</br></br></br>

## Exercício 02.07 - Adicionando um novo Gráfico com o contexto novo de dados

1. Clique no menu azul suspenso na posição inferior do painel, </br>
no botão com o ícone de gráfico </br>
2. Na barra de configuração (lateral direita do painel),</br>
escolha o nome do nome Dataset (que veio da Query SQL).</br> 
3. Configure o tipo de Visualização para "Tabela"(Table).</br>
4. Marque a opção para incluir TODOS os campos na tabela.
5. Na configuração, clique no campo(coluna) com o nome de "**image**".</br>
</br></br>
<img src="https://github.com/Gabriel-Rangel/lab_sql/blob/main/images/v2_lab05_2.png?raw=true" width="700px">
</br></br></br>

6. Na opção de "Display", configure como "image".
7. Na opção de "SIZE", coloque o valor de "25" no campo "width".
8. Na opção de "Default column width", coloque o valor de "150".
</br></br>
<img src="https://github.com/Gabriel-Rangel/lab_sql/blob/main/images/v2_lab05_3.png?raw=true" width="700px">
</br></br></br>

Como resultado esperado, teremos a figura abaixo.</br>
Salve (Publique) novamente o Painel.
</br></br>
<img src="https://github.com/Gabriel-Rangel/lab_sql/blob/main/images/v2_lab05_4.png?raw=true" width="700px">
</br></br></br>






