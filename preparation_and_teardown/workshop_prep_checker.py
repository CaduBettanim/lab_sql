# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# MAGIC %md
# MAGIC # Preparação e Verificação do Workshop: Databricks SQL Lab (`lab_sql`)
# MAGIC
# MAGIC Execute este notebook como **administrador do workspace** para **preparar** os recursos
# MAGIC compartilhados do workshop SQL (Labs 01–07) e depois **verificar** que cada participante
# MAGIC tem o que precisa.
# MAGIC
# MAGIC **Este notebook é idempotente**: se executado novamente, reutiliza qualquer recurso que
# MAGIC já existe (criar se não existir + `GRANT`s idempotentes). Portanto, é seguro re-executar.
# MAGIC
# MAGIC > ⚠️ **Importante:** rode as **duas primeiras células** para exibir os widgets, selecione os
# MAGIC > participantes e use **Run all**. **Todas as células devem ser executadas e terminar com
# MAGIC > sucesso** — só assim há garantia de que todos os participantes conseguirão seguir o workshop.
# MAGIC > Se qualquer célula falhar (❌ ou ⚠️), corrija a causa e **re-execute o notebook inteiro**
# MAGIC > antes do início do treinamento. O veredito final aparece na seção **5. Relatório final**.
# MAGIC
# MAGIC O que a **preparação** faz (cada passo é opcional por meio dos alternadores no topo):
# MAGIC 1. Garantir um grupo do workshop **`dbacademy_workshop`** e adicionar os participantes selecionados.
# MAGIC 2. Criar o catálogo **`dbacademy`** (se o metastore não tiver armazenamento padrão, será
# MAGIC    interrompido e pedirá que você crie o catálogo manualmente).
# MAGIC 3. Criar um SQL Warehouse **`dbacademy_workshop_wh`** e um cluster multiuso
# MAGIC    **`dbacademy_workshop_cluster`** (Compartilhado, autoscaling 2→8).
# MAGIC 4. Conceder ao grupo tudo o que os participantes precisam: USE CATALOG, CREATE SCHEMA,
# MAGIC    warehouse CAN_USE e cluster CAN_ATTACH_TO. Isso permite que criem schemas pessoais
# MAGIC    (`dbacademy.<username>`).
# MAGIC 5. Verificar se a computação do workshop pode acessar a internet (carrega um CSV do GitHub).
# MAGIC
# MAGIC Depois, a **verificação** exibe uma matriz por participante (✅ / ❌ / ⚠️ / ➖).

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Parâmetros

# COMMAND ----------

# Conectar ao workspace e reunir os usuários do workspace que preenchem o seletor de participantes.
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

_PICK_ATT = "(escolha participantes)"
_user_choices = sorted({u.user_name for u in w.users.list(attributes="userName") if u.user_name})
_attendee_opts = [_PICK_ATT] + _user_choices

print(f"Encontrados {len(_user_choices)} usuário(s) do workspace para o seletor de participantes.")

more_than_1024_users = len(_attendee_opts) > 1024

if more_than_1024_users:
    print("⚠️  Esse workspace possui mais usuários do que o suportado pelo widget multisseletor. Será necessário preencher a lista de participantes manualmente na célula a seguir.")

# COMMAND ----------

# Criar os widgets de entrada.
# (Se você vir uma mensagem de erro "widget already exists with a different type",
#  execute Edit menu -> Clear all widget values (uma vez) e depois re-execute esta célula.)
dbutils.widgets.dropdown("create_catalog", "true", ["true", "false"], "1. Criar Catálogo")
dbutils.widgets.dropdown("create_warehouse", "true", ["true", "false"], "2. Criar SQL Warehouse")
dbutils.widgets.dropdown("create_cluster", "true", ["true", "false"], "3. Criar Cluster Multiuso")
if not more_than_1024_users:
    dbutils.widgets.multiselect("attendees", _PICK_ATT, _attendee_opts, "4. Participantes (usuários do workspace)")

else:
    attendees_manual = [
        # preencha essa lista com os emails dos participantes apenas se indicado na célula acima
    ]


# COMMAND ----------

# MAGIC %md
# MAGIC ## Ação necessária
# MAGIC Preencha o widget `4. Participantes (usuários do workspace)` com todos os participantes e prossiga

# COMMAND ----------

# Convenções fixas para os recursos que este notebook gerencia.
CATALOG = "dbacademy"
GROUP = "dbacademy_workshop"
WAREHOUSE_NAME = "dbacademy_workshop_wh"
CLUSTER_NAME = "dbacademy_workshop_cluster"

# Ler os alternadores + seleção de participantes.
CREATE_CATALOG = dbutils.widgets.get("create_catalog") == "true"
CREATE_WAREHOUSE = dbutils.widgets.get("create_warehouse") == "true"
CREATE_CLUSTER = dbutils.widgets.get("create_cluster") == "true"
ATTENDEES = [a.strip() for a in dbutils.widgets.get("attendees").split(",") if a.strip() and a.strip() != _PICK_ATT] if not more_than_1024_users else attendees_manual

if not ATTENDEES:
    dbutils.notebook.exit("⏳ Escolha pelo menos um participante acima e execute a célula 'Run all'.")

def nice_print(resource: str, resource_name: str, should_create = None):
    print(f"{resource}:".rjust(16), resource_name.ljust(28), f"(criar={should_create})" if should_create is not None else "")
    print("-"*70)

print("-"*70)
nice_print("Catálogo", CATALOG, CREATE_CATALOG)
nice_print("Grupo", GROUP)
nice_print("Warehouse", WAREHOUSE_NAME, CREATE_WAREHOUSE)
nice_print("Cluster", CLUSTER_NAME, CREATE_CLUSTER)
print(f"Participantes ({len(ATTENDEES)}):".rjust(16), *[f"\t\t- {attendee}" for attendee in ATTENDEES], sep="\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Configuração: Funções auxiliares

# COMMAND ----------

from urllib.parse import quote  # (WorkspaceClient `w` foi criado na seção de Parâmetros)

# --- Permissões efetivas de Unity Catalog (resolve herança de grupo) -------

def uc_effective_privileges(securable_type, full_name, principal):
    try:
        resp = w.api_client.do(
            "GET",
            f"/api/2.1/unity-catalog/effective-permissions/{securable_type}/{quote(full_name, safe='')}",
            query={"principal": principal},
        )
    except Exception:
        return None
    privs = set()
    for pa in (resp.get("privilege_assignments") or []):
        for p in (pa.get("privileges") or []):
            if p.get("privilege"):
                privs.add(p["privilege"])
    return privs

def uc_has(privs, needed):
    if privs is None:
        return None
    return ("ALL_PRIVILEGES" in privs) or (needed in privs)

# --- Pesquisas SCIM -------------------------------------------------------

def get_user_info(email):
    """(grupos, direitos de acesso) para um usuário; direitos de acesso unionados dos grupos do usuário."""
    users = list(w.users.list(filter=f'userName eq "{email}"',
                              attributes="userName,groups,entitlements,active"))
    if not users:
        return None
    u = users[0]
    groups = {g.display for g in (u.groups or []) if g.display}
    ents = {e.value for e in (u.entitlements or []) if e.value}
    for gname in groups:
        ents |= GROUP_ENTITLEMENTS.get(gname, set())
    return {"groups": groups, "entitlements": ents, "active": u.active}

# --- Resolução de ACL de computação (direto + via grupo) --------------------

def acl_has_permission(acl, user_email, user_groups, accepted_levels):
    if acl is None:
        return None, "recurso/ACL indisponível"
    email_l = user_email.lower()
    for entry in acl:
        levels = {p.permission_level.value for p in (entry.all_permissions or []) if p.permission_level}
        if not (levels & accepted_levels):
            continue
        if entry.user_name and entry.user_name.lower() == email_l:
            return True, "direto"
        if entry.group_name and entry.group_name in user_groups:
            return True, f"grupo:{entry.group_name}"
    return False, "não concedido"

OK, NO, ERR, NA = "✅", "❌", "⚠️", "➖"
print("Funções auxiliares definidas.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Preparação (idempotente)
# MAGIC Cria ou reutiliza o grupo do workshop, catálogo, warehouse e cluster, e concede ao grupo
# MAGIC o acesso que os participantes precisam. Re-executar é seguro.

# COMMAND ----------

from databricks.sdk.service.compute import (
    AutoScale, DataSecurityMode, ClusterAccessControlRequest, ClusterPermissionLevel,
)
from databricks.sdk.service.sql import (
    WarehouseAccessControlRequest, WarehousePermissionLevel, CreateWarehouseRequestWarehouseType,
)

print("=" * 70)
print("PREPARAÇÃO")
print("=" * 70)

# --- 3a. Grupo do workshop (nível de CONTA, para que Unity Catalog possa conceder) ----
# UC aceita apenas grupos no nível de CONTA como principais de concessão. Um grupo local de workspace
# (SCIM de workspace simples) falha com PRINCIPAL_DOES_NOT_EXIST. Portanto, provisionamos um grupo
# de conta, o atribuímos a este workspace e adicionamos os participantes como usuários de conta.
import time

def _acct_scim(method, path, **kw):
    return w.api_client.do(method, f"/api/2.0/account/scim/v2{path}", **kw)

def _acct_user_id(email):
    res = _acct_scim("GET", "/Users", query={"filter": f'userName eq "{email}"'}).get("Resources") or []
    return res[0]["id"] if res else None

def grant_with_retry(sql, attempts=5, delay=3):
    """Tentar novamente uma concessão enquanto UC se atualiza para um principal recém-criado/atribuído."""
    last = None
    for _ in range(attempts):
        try:
            spark.sql(sql)
            return True
        except Exception as e:
            last = e
            if "PRINCIPAL_DOES_NOT_EXIST" in str(e) or "Could not find principal" in str(e):
                time.sleep(delay)
                continue
            raise
    raise last

try:
    # Remover qualquer grupo local de workspace remanescente do mesmo nome (evita ambiguidade).
    for _g in w.groups.list(filter=f'displayName eq "{GROUP}"'):
        _meta = w.groups.get(_g.id).meta
        if _meta and _meta.resource_type == "WorkspaceGroup":
            w.groups.delete(_g.id)
            print(f"  removido grupo obsoleto local de workspace '{GROUP}' (id {_g.id}).")

    # Garantir que o grupo no nível de conta existe.
    _found = _acct_scim("GET", "/Groups", query={"filter": f'displayName eq "{GROUP}"'}).get("Resources") or []
    if _found:
        GROUP_ID = _found[0]["id"]
        print(f"{OK} Grupo de conta '{GROUP}' existe (id {GROUP_ID}).")
    else:
        GROUP_ID = _acct_scim("POST", "/Groups",
            body={"schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"], "displayName": GROUP})["id"]
        print(f"{OK} Criado grupo de conta '{GROUP}' (id {GROUP_ID}).")

    # Atribuir o grupo a ESTE workspace (necessário para ACLs de warehouse/cluster + visibilidade).
    w.api_client.do("PUT", f"/api/2.0/preview/permissionassignments/principals/{GROUP_ID}",
                    body={"permissions": ["USER"]})
    print(f"{OK} Grupo atribuído a este workspace.")

    # Adicionar os participantes selecionados (resolvidos para IDs de usuário de CONTA) como membros.
    _existing = {m["value"] for m in (_acct_scim("GET", f"/Groups/{GROUP_ID}").get("members") or [])}
    _to_add = []
    for _email in ATTENDEES:
        _uid = _acct_user_id(_email)
        if not _uid:
            print(f"  {ERR} não encontrado como usuário de conta, não é possível adicionar: {_email}")
            continue
        if _uid not in _existing:
            _to_add.append(_uid)
    if _to_add:
        _acct_scim("PATCH", f"/Groups/{GROUP_ID}",
            body={"schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
                  "Operations": [{"op": "add", "path": "members",
                                  "value": [{"value": u} for u in _to_add]}]})
    print(f"{OK} Associação ao grupo: {len(_existing)} já membros, {len(_to_add)} adicionados.")

    # Definir os direitos de acesso do workspace NO GRUPO (não contar com o grupo 'users' integrado).
    _ws_gid = None
    for _ in range(6):
        _wsg = list(w.groups.list(filter=f'displayName eq "{GROUP}"', attributes="id"))
        if _wsg:
            _ws_gid = _wsg[0].id
            break
        time.sleep(3)
    if _ws_gid:
        w.api_client.do("PATCH", f"/api/2.0/preview/scim/v2/Groups/{_ws_gid}",
            body={"schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
                  "Operations": [{"op": "add", "path": "entitlements",
                                  "value": [{"value": "workspace-access"}, {"value": "databricks-sql-access"}]}]})
        print(f"{OK} Direitos de acesso garantidos para '{GROUP}': workspace-access, databricks-sql-access.")
    else:
        print(f"{ERR} Grupo não está visível no SCIM do workspace para definir direitos de acesso; re-execute para aplicar.")
except Exception as e:
    if any(k in str(e) for k in ("403", "PERMISSION_DENIED")) or "not authorized" in str(e).lower():
        raise RuntimeError(
            "Provisionar o grupo no nível de conta requer ADMIN DE CONTA. Execute este notebook "
            f"como administrador de conta, ou no console da conta, crie um grupo de conta chamado '{GROUP}', "
            "atribua-o a este workspace, adicione os participantes e re-execute o restante da preparação."
        ) from e
    raise

# COMMAND ----------

# --- 3b. Catálogo (lidar com metastore sem armazenamento) --------------------
try:
    w.catalogs.get(CATALOG)
    print(f"{OK} Catálogo '{CATALOG}' existe (criação omitida).")
except Exception:
    if CREATE_CATALOG:
        try:
            spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
            print(f"{OK} Catálogo '{CATALOG}' pronto.")
        except Exception as e:
            msg = str(e).lower()
            if any(k in msg for k in ["managed location", "storage location", "default storage",
                                    "location is required", "no metastore storage", "storage root"]):
                raise RuntimeError(
                    f"Catálogo '{CATALOG}' não pode ser criado automaticamente: este metastore não tem "
                    f"armazenamento padrão, portanto o catálogo precisa de um LOCAL DE GERENCIAMENTO explícito. Crie-o manualmente, por exemplo:\n"
                    f"    CREATE CATALOG {CATALOG} MANAGED LOCATION 'gs://<bucket>/<path>';  -- ou s3://... / abfss://...\n"
                    f"depois re-execute este notebook com 'Create Catalog' = false."
                ) from e
            raise
    else:
        print(f"{NO} Catálogo '{CATALOG}' não encontrado e 'Create Catalog' = false. Crie-o ou ative a opção.")

# --- 3c. Conceder acesso ao nível de catálogo ao grupo -----
try:
    grant_with_retry(f"GRANT USE CATALOG, CREATE SCHEMA ON CATALOG {CATALOG} TO `{GROUP}`")
    print(f"{OK} Concedidos USE CATALOG + CREATE SCHEMA em {CATALOG} para {GROUP}.")
except Exception as e:
    print(f"{NO} Não foi possível conceder permissões no catálogo '{CATALOG}': {e}")

# COMMAND ----------

# --- 3d. SQL Warehouse ---------------------------------------------------
def ensure_warehouse(name):
    existing = next((x for x in w.warehouses.list() if x.name == name), None)
    if existing:
        return existing.id, "existe"
    try:
        w.warehouses.create(name=name, cluster_size="Small", min_num_clusters=1,
                            max_num_clusters=3, auto_stop_mins=30, enable_serverless_compute=True,
                            warehouse_type=CreateWarehouseRequestWarehouseType.PRO)
    except Exception as e:
        print(f"  criação de warehouse sem servidor falhou ({type(e).__name__}); tentando novamente com PRO clássico")
        w.warehouses.create(name=name, cluster_size="Small", min_num_clusters=1,
                            max_num_clusters=3, auto_stop_mins=30, enable_serverless_compute=False,
                            warehouse_type=CreateWarehouseRequestWarehouseType.PRO)
    wid = next((x.id for x in w.warehouses.list() if x.name == name), None)
    return wid, "criado"

WAREHOUSE_ID = None
if CREATE_WAREHOUSE:
    try:
        WAREHOUSE_ID, _st = ensure_warehouse(WAREHOUSE_NAME)
        print(f"{OK} Warehouse '{WAREHOUSE_NAME}' {_st} (id {WAREHOUSE_ID}).")
    except Exception as e:
        print(f"{NO} Não foi possível criar o warehouse '{WAREHOUSE_NAME}': {e}")
else:
    WAREHOUSE_ID = next((x.id for x in w.warehouses.list() if x.name == WAREHOUSE_NAME), None)
    print(f"{OK if WAREHOUSE_ID else NO} Warehouse '{WAREHOUSE_NAME}' "
          f"{'encontrado' if WAREHOUSE_ID else 'não encontrado'} (criação omitida).")

if WAREHOUSE_ID:
    try:
        w.warehouses.update_permissions(warehouse_id=WAREHOUSE_ID, access_control_list=[
            WarehouseAccessControlRequest(group_name=GROUP, permission_level=WarehousePermissionLevel.CAN_USE)])
        print(f"{OK} Concedido CAN_USE do warehouse para {GROUP}.")
    except Exception as e:
        print(f"{NO} Não foi possível conceder permissão de warehouse: {e}")

# COMMAND ----------

# --- 3e. Cluster Multiuso (Compartilhado, autoscaling 2->8, consciente da nuvem) ---
def ensure_cluster(name):
    existing = next((c for c in w.clusters.list() if c.cluster_name == name), None)
    if existing:
        return existing.cluster_id, "existe"
    # Mesmo tipo de nó para driver + workers: consciente da nuvem E evita a incompatibilidade ARM/não-ARM
    # que ocorre quando os seletores de driver e worker pousam em arquiteturas diferentes.
    _node = w.clusters.select_node_type(min_memory_gb=32, local_disk=True)
    w.clusters.create(
        cluster_name=name,
        spark_version=w.clusters.select_spark_version(latest=True, long_term_support=True),
        node_type_id=_node,
        driver_node_type_id=_node,
        autoscale=AutoScale(min_workers=2, max_workers=8),
        autotermination_minutes=240,
        data_security_mode=DataSecurityMode.USER_ISOLATION,  # Modo de acesso compartilhado (multi-usuário + UC)
    )
    cid = next((c.cluster_id for c in w.clusters.list() if c.cluster_name == name), None)
    return cid, "criado"

CLUSTER_ID = None
if CREATE_CLUSTER:
    try:
        CLUSTER_ID, _st = ensure_cluster(CLUSTER_NAME)
        print(f"{OK} Cluster '{CLUSTER_NAME}' {_st} (id {CLUSTER_ID}). Observação: auto-encerramento funciona apenas quando ocioso.")
    except Exception as e:
        print(f"{NO} Não foi possível criar o cluster '{CLUSTER_NAME}': {e}")
else:
    CLUSTER_ID = next((c.cluster_id for c in w.clusters.list() if c.cluster_name == CLUSTER_NAME), None)
    print(f"{OK if CLUSTER_ID else NO} Cluster '{CLUSTER_NAME}' "
          f"{'encontrado' if CLUSTER_ID else 'não encontrado'} (criação omitida).")

if CLUSTER_ID:
    try:
        w.clusters.update_permissions(cluster_id=CLUSTER_ID, access_control_list=[
            ClusterAccessControlRequest(group_name=GROUP, permission_level=ClusterPermissionLevel.CAN_ATTACH_TO)])
        print(f"{OK} Concedido CAN_ATTACH_TO do cluster para {GROUP}.")
    except Exception as e:
        print(f"{NO} Não foi possível conceder permissão de cluster: {e}")

# COMMAND ----------

# --- 3f. Teste de conectividade: carregar dados de laboratório de uma URL (Lab 02 usa dados externos) ---
import pandas as pd

CSV_URL = "https://raw.githubusercontent.com/CaduBettanim/lab_sql/refs/heads/main/dados/dim_medicamento.csv"
CSV_OK = False
try:
    df = pd.read_csv(CSV_URL)
    CSV_OK = True
    print(f"{OK} Carregadas {len(df)} linhas / {len(df.columns)} colunas da URL do CSV. "
          f"Esta computação tem saída de internet.")
except Exception as e:
    print(f"{NO} Não foi possível ler o CSV do GitHub. A computação do workshop pode não ter saída de internet "
          f"(participantes encontrarão o mesmo problema no Lab 02): {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Verificação: Matriz de permissões por participante
# MAGIC | Coluna | Requisito | Necessário por |
# MAGIC |---|---|---|
# MAGIC | Acesso ao workspace | Direito de acesso `workspace-access` | Todos os labs |
# MAGIC | Databricks SQL | Direito de acesso `databricks-sql-access` | 01, 03, 04, 05, 06 |
# MAGIC | USE CATALOG | `USE CATALOG` no catálogo | Todos os labs |
# MAGIC | CREATE SCHEMA | `CREATE SCHEMA` no catálogo | Todos os labs |
# MAGIC | Warehouse CAN USE | `CAN_USE` no SQL Warehouse | 01, 03, 04, 05, 06 |
# MAGIC | Cluster CAN ATTACH | `CAN_ATTACH_TO` no cluster | 02 (Notebook) |

# COMMAND ----------

import pandas as pd

# Reconstruir o mapa de grupo->direitos de acesso DEPOIS da preparação para refletir o novo grupo.
GROUP_ENTITLEMENTS = {}
for g in w.groups.list(attributes="displayName,entitlements"):
    if g.display_name:
        GROUP_ENTITLEMENTS[g.display_name] = {e.value for e in (g.entitlements or []) if e.value}

# Resolver a computação gerenciada (por nome fixo) e ler ACLs.
WAREHOUSE = next((x for x in w.warehouses.list() if x.name == WAREHOUSE_NAME), None)
CLUSTER = next((c for c in w.clusters.list() if c.cluster_name == CLUSTER_NAME), None)
WAREHOUSE_ACL = w.warehouses.get_permissions(warehouse_id=WAREHOUSE.id).access_control_list if WAREHOUSE else None
CLUSTER_ACL = w.clusters.get_permissions(cluster_id=CLUSTER.cluster_id).access_control_list if CLUSTER else None

# As concessões/associações de grupo recém-aplicadas levam alguns segundos para chegar ao UC.
# Fazer uma pesquisa breve para que a primeira execução "Run all" não reporte ❌ falsos
# (sem operação em re-execuções onde as concessões já se propagaram).
import time
for _ in range(6):
    _p = uc_effective_privileges("catalog", CATALOG, ATTENDEES[0])
    if _p and ("USE_CATALOG" in _p or "ALL_PRIVILEGES" in _p):
        break
    time.sleep(3)

COLUMNS = ["Acesso ao workspace", "Databricks SQL", "USE CATALOG", "CREATE SCHEMA",
           "Warehouse CAN USE", "Cluster CAN ATTACH"]
matrix_rows, detail_rows = {}, []

def note(email, col, symbol, message):
    if symbol in (NO, ERR):
        detail_rows.append({"Participante": email, "Verificação": col, "Status": symbol, "Detalhe": message})

for email in ATTENDEES:
    row = {c: NA for c in COLUMNS}
    info = get_user_info(email)
    if info is None:
        matrix_rows[email] = {c: ERR for c in COLUMNS}
        detail_rows.append({"Participante": email, "Verificação": "(pesquisa de usuário)", "Status": ERR,
                            "Detalhe": "Usuário não encontrado no workspace (SCIM)."})
        continue
    groups, ents = info["groups"], info["entitlements"]

    row["Acesso ao workspace"] = OK if "workspace-access" in ents else NO
    note(email, "Acesso ao workspace", row["Acesso ao workspace"], "Direito de acesso 'workspace-access' faltando")
    row["Databricks SQL"] = OK if "databricks-sql-access" in ents else NO
    note(email, "Databricks SQL", row["Databricks SQL"], "Direito de acesso 'databricks-sql-access' faltando")

    cat_privs = uc_effective_privileges("catalog", CATALOG, email)
    for col, priv in [("USE CATALOG", "USE_CATALOG"), ("CREATE SCHEMA", "CREATE_SCHEMA")]:
        res = uc_has(cat_privs, priv)
        row[col] = OK if res else (NO if res is False else ERR)
        if res is False:
            note(email, col, NO, f"Nenhum {priv} no catálogo '{CATALOG}'")
        elif res is None:
            note(email, col, ERR, f"Não foi possível ler permissões efetivas no catálogo '{CATALOG}'")

    ok, _ = acl_has_permission(WAREHOUSE_ACL, email, groups, {"CAN_USE", "CAN_MANAGE"})
    row["Warehouse CAN USE"] = OK if ok else (NO if ok is False else ERR)
    if ok is False:
        note(email, "Warehouse CAN USE", NO, f"Nenhum CAN_USE no warehouse '{WAREHOUSE_NAME}'")
    elif ok is None:
        note(email, "Warehouse CAN USE", ERR, f"Warehouse '{WAREHOUSE_NAME}' não encontrado / ACL ilegível")

    ok, _ = acl_has_permission(CLUSTER_ACL, email, groups, {"CAN_ATTACH_TO", "CAN_RESTART", "CAN_MANAGE"})
    row["Cluster CAN ATTACH"] = OK if ok else (NO if ok is False else ERR)
    if ok is False:
        note(email, "Cluster CAN ATTACH", NO, f"Nenhum CAN_ATTACH_TO no cluster '{CLUSTER_NAME}'")
    elif ok is None:
        note(email, "Cluster CAN ATTACH", ERR, f"Cluster '{CLUSTER_NAME}' não encontrado / ACL ilegível")

    matrix_rows[email] = row

matrix_df = pd.DataFrame.from_dict(matrix_rows, orient="index", columns=COLUMNS)
matrix_df.index.name = "Participante"
print(f"Verificados {len(ATTENDEES)} participante(s). Legenda: {OK} aprovado  {NO} ausente  {ERR} não foi possível verificar  {NA} n/a")
display(matrix_df.reset_index())

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4b. Detalhes: apenas falhas e avisos

# COMMAND ----------

if detail_rows:
    display(pd.DataFrame(detail_rows, columns=["Participante", "Verificação", "Status", "Detalhe"]))
else:
    print("Sem falhas ou avisos. Todos os participantes têm todas as permissões verificadas. 🎉")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Relatório final
# MAGIC Um único ✅ / ❌ por item que foi preparado ou verificado (⚠️ = não foi possível determinar).
# MAGIC Sinalizadores de recursos que um notebook não pode verificar estão listados no final como lembretes manuais.

# COMMAND ----------

def _sym(v):
    return OK if v is True else (NO if v is False else ERR)

def _group_has_uc(securable_type, full_name, group, needed):
    """Retorna True se o grupo detém todos os privilégios `needed` (ou ALL_PRIVILEGES) no recurso protegido."""
    try:
        r = w.api_client.do("GET",
            f"/api/2.1/unity-catalog/permissions/{securable_type}/{quote(full_name, safe='')}",
            query={"principal": group})
        privs = {p for pa in (r.get("privilege_assignments") or []) for p in (pa.get("privileges") or [])}
        return ("ALL_PRIVILEGES" in privs) or needed.issubset(privs)
    except Exception:
        return None

def _group_in_acl(acl, group, levels):
    if acl is None:
        return None
    for e in acl:
        if e.group_name == group and (
                {p.permission_level.value for p in (e.all_permissions or []) if p.permission_level} & levels):
            return True
    return False

def _account_group_exists(group):
    try:
        return len(_acct_scim("GET", "/Groups", query={"filter": f'displayName eq "{group}"'}).get("Resources") or []) > 0
    except Exception:
        return None

try:
    w.catalogs.get(CATALOG)
    _catalog_exists = True
except Exception:
    _catalog_exists = False

# Todos os participantes passam em todas as verificações por participante? (detail_rows é vazio quando todos estão verdes)
_attendees_ok = (len({d["Participante"] for d in detail_rows}) == 0) if ATTENDEES else None

report = [
    ("Grupo do workshop existe e foi atribuído",      _account_group_exists(GROUP)),
    ("Direitos de acesso do grupo (workspace + Databricks SQL)", {"workspace-access", "databricks-sql-access"}.issubset(GROUP_ENTITLEMENTS.get(GROUP, set()))),
    ("Catálogo existe",                               _catalog_exists),
    ("Permissões do catálogo para o grupo (USE CATALOG + CREATE SCHEMA)", _group_has_uc("catalog", CATALOG, GROUP, {"USE_CATALOG", "CREATE_SCHEMA"})),
    ("SQL Warehouse existe",                          WAREHOUSE is not None),
    ("CAN_USE de warehouse concedido ao grupo",       _group_in_acl(WAREHOUSE_ACL, GROUP, {"CAN_USE", "CAN_MANAGE"})),
    ("Cluster Multiuso existe",                       CLUSTER is not None),
    ("CAN_ATTACH_TO de cluster concedido ao grupo",   _group_in_acl(CLUSTER_ACL, GROUP, {"CAN_ATTACH_TO", "CAN_MANAGE"})),
    ("Saída de internet da computação (carregamento de CSV)", CSV_OK),
    (f"Todos os {len(ATTENDEES)} participante(s) passam em todas as verificações", _attendees_ok),
]

_all_ok = all(v is True for _, v in report)
if _all_ok:
    print("=" * 70)
    print(f"{OK} CHECKS COMPLETOS: todos os {len(ATTENDEES)} participante(s) selecionado(s) têm as "
          f"permissões necessárias para participar do workshop.")
    print("   O ambiente está pronto: grupo, catálogo, warehouse, cluster e concessões preparados e")
    print("   verificados, e a computação tem saída de internet. Pode iniciar o treinamento. 🎉")
    print("=" * 70)
else:
    print("=" * 70)
    print(f"{NO} AMBIENTE NÃO PRONTO: um ou mais itens estão ❌/⚠️ abaixo. Corrija a causa e "
          f"re-execute o notebook inteiro")
    print("   antes do treinamento (veja os detalhes por participante na seção 4b).")
    print("=" * 70)
display(pd.DataFrame([{"Item": label, "Status": _sym(val)} for label, val in report],
                     columns=["Item", "Status"]))
