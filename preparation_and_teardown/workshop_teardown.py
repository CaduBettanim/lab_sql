# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# MAGIC %md
# MAGIC # Desmontagem do Workshop: Databricks SQL Lab (`lab_sql`)
# MAGIC
# MAGIC Reverte os recursos criados por `lab_sql_prep_checker`. **Idempotente**: qualquer coisa
# MAGIC já ausente é ignorada, portanto é seguro re-executar.
# MAGIC
# MAGIC Cada alternador é `true`/`false`. Os padrões removem os recursos **específicos do workshop**
# MAGIC (grupo, warehouse, cluster). Deletar o grupo também revoga todas as concessões feitas a ele.
# MAGIC
# MAGIC ⚠️ **`DROP CATALOG dbacademy` padrão é `false`**: o catálogo pertence ao administrador e contém
# MAGIC o schema `dbacademy.<username>` de cada participante e seus dados. Defina como `true` apenas se o notebook
# MAGIC de preparação criou o catálogo e o workshop foi completamente encerrado.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Parâmetros

# COMMAND ----------

dbutils.widgets.dropdown("delete_group", "true", ["true", "false"], "1. Excluir grupo do workshop")
dbutils.widgets.dropdown("delete_warehouse", "true", ["true", "false"], "2. Excluir SQL Warehouse")
dbutils.widgets.dropdown("delete_cluster", "true", ["true", "false"], "3. Excluir Cluster Multiuso")
dbutils.widgets.dropdown("delete_catalog", "false", ["true", "false"], "4. REMOVER CATÁLOGO (DESTRUTIVO)")

# COMMAND ----------

from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Convenções fixas, deve corresponder ao notebook de preparação.
CATALOG = "dbacademy"
GROUP = "dbacademy_workshop"
WAREHOUSE_NAME = "dbacademy_workshop_wh"
CLUSTER_NAME = "dbacademy_workshop_cluster"

DELETE_GROUP = dbutils.widgets.get("delete_group") == "true"
DELETE_WAREHOUSE = dbutils.widgets.get("delete_warehouse") == "true"
DELETE_CLUSTER = dbutils.widgets.get("delete_cluster") == "true"
DELETE_CATALOG = dbutils.widgets.get("delete_catalog") == "true"

OK, NO, ERR, NA = "✅", "❌", "⚠️", "➖"

def _acct_scim(method, path, **kw):
    return w.api_client.do(method, f"/api/2.0/account/scim/v2{path}", **kw)

print(f"Grupo:     {GROUP}            (excluir={DELETE_GROUP})")
print(f"Warehouse: {WAREHOUSE_NAME}   (excluir={DELETE_WAREHOUSE})")
print(f"Cluster:   {CLUSTER_NAME}     (excluir={DELETE_CLUSTER})")
print(f"Catálogo:  {CATALOG}          (REMOVER={DELETE_CATALOG})  {'⚠️ DESTRUTIVO' if DELETE_CATALOG else ''}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Desmontagem (idempotente)

# COMMAND ----------

print("=" * 70)
print("DESMONTAGEM")
print("=" * 70)

# --- Cluster ---------------------------------------------------------------
if DELETE_CLUSTER:
    _cl = next((c for c in w.clusters.list() if c.cluster_name == CLUSTER_NAME), None)
    if _cl:
        try:
            w.clusters.permanent_delete(cluster_id=_cl.cluster_id)
            print(f"{OK} Cluster '{CLUSTER_NAME}' excluído.")
        except Exception as e:
            print(f"{NO} Não foi possível excluir o cluster '{CLUSTER_NAME}': {e}")
    else:
        print(f"{OK} Cluster '{CLUSTER_NAME}' já ausente.")
else:
    print(f"{NA} Cluster '{CLUSTER_NAME}' mantido (excluir=false).")

# --- Warehouse -----------------------------------------------------------
if DELETE_WAREHOUSE:
    _wh = next((x for x in w.warehouses.list() if x.name == WAREHOUSE_NAME), None)
    if _wh:
        try:
            w.warehouses.delete(id=_wh.id)
            print(f"{OK} Warehouse '{WAREHOUSE_NAME}' excluído.")
        except Exception as e:
            print(f"{NO} Não foi possível excluir o warehouse '{WAREHOUSE_NAME}': {e}")
    else:
        print(f"{OK} Warehouse '{WAREHOUSE_NAME}' já ausente.")
else:
    print(f"{NA} Warehouse '{WAREHOUSE_NAME}' mantido (excluir=false).")

# --- Grupo do workshop (revogar concessões, desassociar, excluir) ----
if DELETE_GROUP:
    # Melhor esforço para revogar as concessões do catálogo enquanto o grupo ainda existe.
    try:
        w.catalogs.get(CATALOG)
        spark.sql(f"REVOKE USE CATALOG, CREATE SCHEMA ON CATALOG {CATALOG} FROM `{GROUP}`")
        print(f"{OK} Concessões de catálogo revogadas de {GROUP}.")
    except Exception as e:
        print(f"{NA} Revogação de catálogo omitida ({type(e).__name__}).")

    _found = _acct_scim("GET", "/Groups", query={"filter": f'displayName eq "{GROUP}"'}).get("Resources") or []
    if _found:
        _gid = _found[0]["id"]
        try:
            w.api_client.do("DELETE", f"/api/2.0/preview/permissionassignments/principals/{_gid}")
        except Exception:
            pass  # a atribuição pode já ter sido removida
        try:
            _acct_scim("DELETE", f"/Groups/{_gid}")
            print(f"{OK} Grupo de conta '{GROUP}' (id {_gid}) excluído. Suas concessões/associações também foram removidas.")
        except Exception as e:
            print(f"{NO} Não foi possível excluir o grupo de conta '{GROUP}': {e}")
    else:
        print(f"{OK} Grupo de conta '{GROUP}' já ausente.")

    # Também remover qualquer grupo local de workspace obsoleto do mesmo nome.
    for _g in w.groups.list(filter=f'displayName eq "{GROUP}"'):
        _meta = w.groups.get(_g.id).meta
        if _meta and _meta.resource_type == "WorkspaceGroup":
            w.groups.delete(_g.id)
            print(f"  removido grupo obsoleto local de workspace '{GROUP}' (id {_g.id}).")
else:
    print(f"{NA} Grupo '{GROUP}' mantido (excluir=false). Suas concessões permanecerão.")

# --- Catálogo (DESTRUTIVO, ativação manual) --------------------------------
if DELETE_CATALOG:
    try:
        spark.sql(f"DROP CATALOG IF EXISTS {CATALOG} CASCADE")
        print(f"{OK} Catálogo '{CATALOG}' removido (CASCADE: todos os schemas/dados removidos).")
    except Exception as e:
        print(f"{NO} Não foi possível remover o catálogo '{CATALOG}': {e}")
else:
    print(f"{NA} Catálogo '{CATALOG}' mantido (REMOVER=false). Schemas/dados dos participantes preservados.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Relatório final
# MAGIC ✅ = revertido (recurso agora ausente) · ➖ = mantido por escolha · ❌ = ainda presente · ⚠️ = desconhecido.

# COMMAND ----------

import pandas as pd

def _account_group_exists(group):
    try:
        return len(_acct_scim("GET", "/Groups", query={"filter": f'displayName eq "{group}"'}).get("Resources") or []) > 0
    except Exception:
        return None

def _row(label, requested, still_present):
    if not requested:
        return {"Item": label, "Status": NA, "Note": "mantido (excluir=false)"}
    if still_present is None:
        return {"Item": label, "Status": ERR, "Note": "não foi possível verificar"}
    return {"Item": label, "Status": OK if not still_present else NO,
            "Note": "removido" if not still_present else "AINDA PRESENTE"}

try:
    w.catalogs.get(CATALOG); _catalog_present = True
except Exception:
    _catalog_present = False

report = [
    _row(f"Cluster '{CLUSTER_NAME}'",     DELETE_CLUSTER,   any(c.cluster_name == CLUSTER_NAME for c in w.clusters.list())),
    _row(f"Warehouse '{WAREHOUSE_NAME}'", DELETE_WAREHOUSE, any(x.name == WAREHOUSE_NAME for x in w.warehouses.list())),
    _row(f"Grupo '{GROUP}'",              DELETE_GROUP,     _account_group_exists(GROUP)),
    _row(f"Catálogo '{CATALOG}'",         DELETE_CATALOG,   _catalog_present),
]

_done = all(r["Status"] in (OK, NA) for r in report)
print("GERAL:", "✅ Desmontagem concluída: tudo o que foi solicitado foi revertido."
      if _done else "❌ Alguns itens ainda estão presentes: veja abaixo.")
display(pd.DataFrame(report, columns=["Item", "Status", "Note"]))
