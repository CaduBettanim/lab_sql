Para que o workshop ocorra sem problemas, é necessário o provisionamento de alguns recursos e a garantia de algumas permissões. Para isso, este lab inclui dois notebooks auxiliares: **`workshop_prep_checker`** cuida da preparação do ambiente e da checagem dos requisitos, e **`workshop_teardown`** remove os recursos criados para o workshop.

# Preparando para o workshop
O **`workshop_prep_checker`** é idempotente (seguro re-executar) e requer **admin de conta**.

**Passos:**
1. Importe o seguinte notebook dentro do Workspace:
```
https://raw.githubusercontent.com/CaduBettanim/lab_sql/refs/heads/main/preparation_and_teardown/workshop_prep_checker.py
```
2. Abra o notebook e rode as **duas primeiras células** para exibir os widgets.
3. Selecione os **participantes** e ajuste os alternadores.
4. Clique em **Run all** — todas as células devem terminar com sucesso.
5. Confira o veredito na seção **5. Relatório final**. O esperado é
   `✅ CHECKS COMPLETOS`. Se houver ❌ ou ⚠️, corrija e re-execute o notebook inteiro.

Ele cria: grupo `dbacademy_workshop` (participantes + acessos), catálogo `dbacademy`,
SQL Warehouse, cluster multiuso e as concessões; e testa o acesso à internet.


# Revertendo ao estado anterior
Após a finalização do workshop, um administrador pode importar e rodar o notebook `workshop_teardown` para remover os recursos criados pelo notebook `workshop_prep_checker` (o `DROP CATALOG` vem desativado).
