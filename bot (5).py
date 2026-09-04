import discord
from discord import app_commands
import sqlite3
import random
import json
import os


# ==================================================
# CONFIGURAÇÃO
# ==================================================

TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 1346237457372418108

# Cargo de Mestre/Pesquisador
PESQUISADOR_ROLE_ID = 1535729779087515678

# Cargo de jogador/Cobaia
COBAIA_ROLE_ID = 1541162367520477356


# ==================================================
# DISCORD
# ==================================================

intents = discord.Intents.default()

client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)

GUILD = discord.Object(id=GUILD_ID)


# ==================================================
# BANCO DE DADOS
# ==================================================

db = sqlite3.connect(
    "tavelada.db",
    check_same_thread=False
)

cursor = db.cursor()


# ==================================================
# FUNÇÕES DO BANCO
# ==================================================

def adicionar_coluna_se_nao_existir(tabela, coluna, tipo):
    cursor.execute(
        f"PRAGMA table_info({tabela})"
    )

    colunas = [
        linha[1]
        for linha in cursor.fetchall()
    ]

    if coluna not in colunas:
        cursor.execute(
            f"ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}"
        )

        print(
            f"Coluna '{coluna}' adicionada à tabela '{tabela}'."
        )

        db.commit()


# ==================================================
# TABELA DE FICHAS
# ==================================================

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS fichas (
        user_id INTEGER PRIMARY KEY,
        nome TEXT DEFAULT '',
        idade TEXT DEFAULT '',
        sexualidade TEXT DEFAULT '',
        altura TEXT DEFAULT '',
        peso TEXT DEFAULT '',
        descendencia TEXT DEFAULT '',
        linhagem_heroica TEXT DEFAULT '',
        sub_linhagem TEXT DEFAULT '',
        objetivo TEXT DEFAULT '',
        medos TEXT DEFAULT '',
        personalidade TEXT DEFAULT '',
        relacoes TEXT DEFAULT '',
        historia TEXT DEFAULT '',
        fisico INTEGER DEFAULT 0,
        conhecimento INTEGER DEFAULT 0,
        social INTEGER DEFAULT 0,
        vontade INTEGER DEFAULT 0,
        pericias TEXT DEFAULT '{}',
        xp INTEGER DEFAULT 0,
        nivel INTEGER DEFAULT 1
    )
    """
)


# ==================================================
# MIGRAÇÃO DA TABELA DE FICHAS
# ==================================================

COLUNAS_FICHA = {
    "nome": "TEXT DEFAULT ''",
    "idade": "TEXT DEFAULT ''",
    "sexualidade": "TEXT DEFAULT ''",
    "altura": "TEXT DEFAULT ''",
    "peso": "TEXT DEFAULT ''",
    "descendencia": "TEXT DEFAULT ''",
    "linhagem_heroica": "TEXT DEFAULT ''",
    "sub_linhagem": "TEXT DEFAULT ''",
    "objetivo": "TEXT DEFAULT ''",
    "medos": "TEXT DEFAULT ''",
    "personalidade": "TEXT DEFAULT ''",
    "relacoes": "TEXT DEFAULT ''",
    "historia": "TEXT DEFAULT ''",
    "fisico": "INTEGER DEFAULT 0",
    "conhecimento": "INTEGER DEFAULT 0",
    "social": "INTEGER DEFAULT 0",
    "vontade": "INTEGER DEFAULT 0",
    "pericias": "TEXT DEFAULT '{}'",
    "xp": "INTEGER DEFAULT 0",
    "nivel": "INTEGER DEFAULT 1"
}

for coluna, tipo in COLUNAS_FICHA.items():
    adicionar_coluna_se_nao_existir(
        "fichas",
        coluna,
        tipo
    )


# ==================================================
# TABELA DE NPCS
# ==================================================

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS npcs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        tipo TEXT DEFAULT 'NPC',
        vida INTEGER DEFAULT 0,
        fisico INTEGER DEFAULT 0,
        conhecimento INTEGER DEFAULT 0,
        social INTEGER DEFAULT 0,
        vontade INTEGER DEFAULT 0,
        pericias TEXT DEFAULT '{}',
        notas TEXT DEFAULT ''
    )
    """
)


# ==================================================
# TABELA DE COMBATE
# ==================================================

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS combate (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        rodada INTEGER DEFAULT 1,
        turno INTEGER DEFAULT 0,
        ativo INTEGER DEFAULT 0
    )
    """
)


# ==================================================
# TABELA DE COMBATENTES
# ==================================================

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS combatentes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        tipo TEXT NOT NULL,
        referencia_id INTEGER,
        iniciativa INTEGER DEFAULT 0,
        dado INTEGER DEFAULT 0,
        fisico INTEGER DEFAULT 0,
        atletismo INTEGER DEFAULT 0,
        vida INTEGER DEFAULT 0
    )
    """
)


# ==================================================
# HISTÓRICO DE ROLAGENS
# ==================================================

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS historico_rolagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        nome_usuario TEXT NOT NULL,
        tipo TEXT NOT NULL,
        resultado INTEGER NOT NULL,
        dado INTEGER NOT NULL,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
)

db.commit()


# ==================================================
# PERÍCIAS
# ==================================================

PERICIAS = {
    "Conhecimento": [
        "História",
        "Arcana",
        "Investigação",
        "Religião",
        "Sobrevivência"
    ],

    "Percepção": [
        "Percepção",
        "Intuição",
        "Sobrevivência"
    ],

    "Social": [
        "Persuasão",
        "Intimidação",
        "Enganação",
        "Liderança"
    ],

    "Físico": [
        "Atletismo",
        "Acrobacia",
        "Furtividade",
        "Prestidigitação"
    ],

    "Combate": [
        "Lâminas",
        "Armas Pesadas",
        "Pontaria",
        "Armas Leves",
        "Defesa",
        "Luta",
        "Grappling",
        "Montaria",
        "Duelo",
        "Arremesso"
    ]
}


# ==================================================
# CRIAR PERÍCIAS
# ==================================================

def criar_pericias():
    pericias = {}

    for categoria, lista in PERICIAS.items():
        for pericia in lista:
            chave = f"{categoria}:{pericia}"
            pericias[chave] = 0

    return pericias


# ==================================================
# CRIAR FICHA
# ==================================================

def criar_ficha(user_id):
    cursor.execute(
        "SELECT user_id FROM fichas WHERE user_id = ?",
        (user_id,)
    )

    existe = cursor.fetchone()

    if existe is None:
        cursor.execute(
            """
            INSERT INTO fichas (
                user_id,
                pericias,
                xp,
                nivel
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                json.dumps(
                    criar_pericias(),
                    ensure_ascii=False
                ),
                0,
                1
            )
        )

        db.commit()


# ==================================================
# BUSCAR FICHA
# ==================================================

def buscar_ficha(user_id):
    criar_ficha(user_id)

    cursor.execute(
        "SELECT * FROM fichas WHERE user_id = ?",
        (user_id,)
    )

    return cursor.fetchone()


# ==================================================
# BUSCAR FICHA COMO DICIONÁRIO
# ==================================================

def buscar_ficha_dict(user_id):
    criar_ficha(user_id)

    cursor.execute(
        "SELECT * FROM fichas WHERE user_id = ?",
        (user_id,)
    )

    ficha = cursor.fetchone()

    if ficha is None:
        return None

    colunas = [
        descricao[0]
        for descricao in cursor.description
    ]

    return dict(zip(colunas, ficha))


# ==================================================
# XP
# ==================================================

def xp_para_nivel(nivel):
    return max(1, nivel) * 100


def adicionar_xp(user_id, quantidade):
    ficha = buscar_ficha_dict(user_id)

    if ficha is None:
        return 1, 0, False

    nivel = int(ficha.get("nivel") or 1)
    xp = int(ficha.get("xp") or 0)

    xp += quantidade

    subiu = False
    nivel_antigo = nivel

    while xp >= xp_para_nivel(nivel):
        xp -= xp_para_nivel(nivel)
        nivel += 1
        subiu = True

    cursor.execute(
        """
        UPDATE fichas
        SET xp = ?, nivel = ?
        WHERE user_id = ?
        """,
        (
            xp,
            nivel,
            user_id
        )
    )

    db.commit()

    return nivel, nivel_antigo, subiu


def resetar_nivel_jogador(user_id):
    criar_ficha(user_id)

    cursor.execute(
        """
        UPDATE fichas
        SET
            xp = 0,
            nivel = 1
        WHERE user_id = ?
        """,
        (user_id,)
    )

    db.commit()


# ==================================================
# ORDEM PARANORMAL
# ==================================================

ORDEM_PERICIAS = [
    "Acrobacia", "Adestramento", "Artes", "Atletismo", "Atualidades",
    "Ciências", "Crime", "Diplomacia", "Enganação", "Fortitude",
    "Furtividade", "Iniciativa", "Intimidação", "Intuição", "Investigação",
    "Luta", "Medicina", "Ocultismo", "Percepção", "Pilotagem",
    "Pontaria", "Profissão", "Reflexos", "Religião", "Sobrevivência",
    "Tática", "Tecnologia", "Vontade"
]

ORDEM_PERICIA_ATRIBUTO = {
    "Acrobacia": "agilidade",
    "Adestramento": "presenca",
    "Artes": "presenca",
    "Atletismo": "forca",
    "Atualidades": "intelecto",
    "Ciências": "intelecto",
    "Crime": "agilidade",
    "Diplomacia": "presenca",
    "Enganação": "presenca",
    "Fortitude": "vigor",
    "Furtividade": "agilidade",
    "Iniciativa": "agilidade",
    "Intimidação": "presenca",
    "Intuição": "presenca",
    "Investigação": "intelecto",
    "Luta": "forca",
    "Medicina": "intelecto",
    "Ocultismo": "intelecto",
    "Percepção": "presenca",
    "Pilotagem": "agilidade",
    "Pontaria": "agilidade",
    "Profissão": "intelecto",
    "Reflexos": "agilidade",
    "Religião": "presenca",
    "Sobrevivência": "intelecto",
    "Tática": "intelecto",
    "Tecnologia": "intelecto",
    "Vontade": "presenca"
}

cursor.execute("""
CREATE TABLE IF NOT EXISTS fichas_ordem (
    user_id INTEGER PRIMARY KEY,
    nome TEXT DEFAULT '',
    jogador TEXT DEFAULT '',
    origem TEXT DEFAULT '',
    classe TEXT DEFAULT '',
    trilha TEXT DEFAULT '',
    nex INTEGER DEFAULT 5,
    agilidade INTEGER DEFAULT 1,
    forca INTEGER DEFAULT 1,
    intelecto INTEGER DEFAULT 1,
    presenca INTEGER DEFAULT 1,
    vigor INTEGER DEFAULT 1,
    pv INTEGER DEFAULT 0,
    pv_max INTEGER DEFAULT 0,
    pe INTEGER DEFAULT 0,
    pe_max INTEGER DEFAULT 0,
    san INTEGER DEFAULT 0,
    san_max INTEGER DEFAULT 0,
    defesa INTEGER DEFAULT 10,
    pericias TEXT DEFAULT '{}'
)
""")
db.commit()


def criar_pericias_ordem():
    return {pericia: 0 for pericia in ORDEM_PERICIAS}


def calcular_recursos_ordem(nex, vigor, presenca):
    nex = max(5, int(nex or 5))
    vigor = int(vigor or 1)
    presenca = int(presenca or 1)
    pv_max = 10 + (vigor * 5) + (nex // 5)
    pe_max = 2 + presenca + (nex // 5)
    san_max = 10 + (presenca * 5) + (nex // 5)
    return pv_max, pe_max, san_max


def pontos_atributo_ordem(nex):
    """Retorna o máximo de pontos de atributo permitidos pelo NEX.
    Base: 5 (1 em cada atributo).
    Ganha +1 em NEX 20, 50, 80 e 90.
    """
    nex = int(nex or 5)
    pontos = 5  # base (1 em cada)
    if nex >= 20:
        pontos += 1
    if nex >= 50:
        pontos += 1
    if nex >= 80:
        pontos += 1
    if nex >= 90:
        pontos += 1
    return pontos


def criar_ficha_ordem(user_id):
    pericias = criar_pericias_ordem()
    pv_max, pe_max, san_max = calcular_recursos_ordem(5, 1, 1)
    cursor.execute("""
        INSERT OR IGNORE INTO fichas_ordem (
            user_id, pv, pv_max, pe, pe_max, san, san_max, pericias
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, pv_max, pv_max, pe_max, pe_max, san_max, san_max,
          json.dumps(pericias, ensure_ascii=False)))
    db.commit()


def garantir_ficha_ordem(user_id):
    criar_ficha_ordem(user_id)
    cursor.execute("SELECT * FROM fichas_ordem WHERE user_id = ?", (user_id,))
    linha = cursor.fetchone()
    colunas = [d[0] for d in cursor.description]
    ficha = dict(zip(colunas, linha))
    try:
        ficha["pericias"] = json.loads(ficha["pericias"] or "{}")
    except:
        ficha["pericias"] = criar_pericias_ordem()
    for p in ORDEM_PERICIAS:
        ficha["pericias"].setdefault(p, 0)
    return ficha


def criar_embed_ficha_ordem(ficha):
    embed = discord.Embed(
        title="👁️ FICHA — ORDEM PARANORMAL",
        description=f"**{ficha['nome'] or 'Sem nome'}**",
        color=discord.Color.dark_red()
    )
    embed.add_field(
        name="📋 Informações",
        value=(
            f"**Jogador:** {ficha['jogador'] or '—'}\n"
            f"**Origem:** {ficha['origem'] or '—'}\n"
            f"**Classe:** {ficha['classe'] or '—'}\n"
            f"**Trilha:** {ficha['trilha'] or '—'}\n"
            f"**NEX:** {ficha['nex']}%"
        ),
        inline=False
    )
    total_atr = (ficha['agilidade'] + ficha['forca'] + ficha['intelecto'] +
                 ficha['presenca'] + ficha['vigor'])
    max_atr = pontos_atributo_ordem(ficha['nex'])

    embed.add_field(
        name="🧠 Atributos",
        value=(
            f"**AGI:** `{ficha['agilidade']}`\n"
            f"**FOR:** `{ficha['forca']}`\n"
            f"**INT:** `{ficha['intelecto']}`\n"
            f"**PRE:** `{ficha['presenca']}`\n"
            f"**VIG:** `{ficha['vigor']}`\n"
            f"────────\n"
            f"**Pontos:** `{total_atr}/{max_atr}`"
        ),
        inline=True
    )
    embed.add_field(
        name="❤️ Recursos",
        value=(
            f"**PV:** `{ficha['pv']}/{ficha['pv_max']}`\n"
            f"**PE:** `{ficha['pe']}/{ficha['pe_max']}`\n"
            f"**SAN:** `{ficha['san']}/{ficha['san_max']}`\n"
            f"**Defesa:** `{ficha['defesa']}`"
        ),
        inline=True
    )
    # Mostra só perícias com bônus != 0 para não estourar
    pericias_com_bonus = {k: v for k, v in ficha["pericias"].items() if v != 0}
    if pericias_com_bonus:
        texto = "\n".join(f"**{k}:** `{v:+d}`" for k, v in sorted(pericias_com_bonus.items()))
    else:
        texto = "Nenhuma perícia treinada ainda."
    embed.add_field(name="🎯 Perícias (treinadas)", value=texto[:1024], inline=False)
    embed.set_footer(text="Ordem Paranormal • Ficha privada")
    return embed


# ==================================================
# D&D 5e
# ==================================================

DND_SKILLS = {
    "Acrobatics": "dexterity",
    "Animal Handling": "wisdom",
    "Arcana": "intelligence",
    "Athletics": "strength",
    "Deception": "charisma",
    "History": "intelligence",
    "Insight": "wisdom",
    "Intimidation": "charisma",
    "Investigation": "intelligence",
    "Medicine": "wisdom",
    "Nature": "intelligence",
    "Perception": "wisdom",
    "Performance": "charisma",
    "Persuasion": "charisma",
    "Religion": "intelligence",
    "Sleight of Hand": "dexterity",
    "Stealth": "dexterity",
    "Survival": "wisdom"
}

cursor.execute("""
CREATE TABLE IF NOT EXISTS fichas_dnd (
    user_id INTEGER PRIMARY KEY,
    nome TEXT DEFAULT '',
    classe TEXT DEFAULT '',
    raca TEXT DEFAULT '',
    nivel INTEGER DEFAULT 1,
    strength INTEGER DEFAULT 10,
    dexterity INTEGER DEFAULT 10,
    constitution INTEGER DEFAULT 10,
    intelligence INTEGER DEFAULT 10,
    wisdom INTEGER DEFAULT 10,
    charisma INTEGER DEFAULT 10,
    hp INTEGER DEFAULT 0,
    hp_max INTEGER DEFAULT 0,
    ca INTEGER DEFAULT 10,
    proficiency INTEGER DEFAULT 2,
    skills TEXT DEFAULT '{}'
)
""")
db.commit()


def criar_skills_dnd():
    return {skill: 0 for skill in DND_SKILLS}


def mod_atributo(valor):
    return (int(valor) - 10) // 2


def criar_ficha_dnd(user_id):
    skills = criar_skills_dnd()
    cursor.execute("""
        INSERT OR IGNORE INTO fichas_dnd (
            user_id, hp, hp_max, skills
        ) VALUES (?, 10, 10, ?)
    """, (user_id, json.dumps(skills, ensure_ascii=False)))
    db.commit()


def garantir_ficha_dnd(user_id):
    criar_ficha_dnd(user_id)
    cursor.execute("SELECT * FROM fichas_dnd WHERE user_id = ?", (user_id,))
    linha = cursor.fetchone()
    colunas = [d[0] for d in cursor.description]
    ficha = dict(zip(colunas, linha))
    try:
        ficha["skills"] = json.loads(ficha["skills"] or "{}")
    except:
        ficha["skills"] = criar_skills_dnd()
    for s in DND_SKILLS:
        ficha["skills"].setdefault(s, 0)
    return ficha


def criar_embed_ficha_dnd(ficha):
    embed = discord.Embed(
        title="🐉 FICHA — D&D 5e",
        description=f"**{ficha['nome'] or 'Sem nome'}**",
        color=discord.Color.dark_green()
    )
    embed.add_field(
        name="📋 Informações",
        value=(
            f"**Classe:** {ficha['classe'] or '—'}\n"
            f"**Raça:** {ficha['raca'] or '—'}\n"
            f"**Nível:** `{ficha['nivel']}`\n"
            f"**Proficiência:** `+{ficha['proficiency']}`"
        ),
        inline=False
    )
    embed.add_field(
        name="🧠 Atributos",
        value=(
            f"**FOR:** `{ficha['strength']}` ({mod_atributo(ficha['strength']):+d})\n"
            f"**DES:** `{ficha['dexterity']}` ({mod_atributo(ficha['dexterity']):+d})\n"
            f"**CON:** `{ficha['constitution']}` ({mod_atributo(ficha['constitution']):+d})\n"
            f"**INT:** `{ficha['intelligence']}` ({mod_atributo(ficha['intelligence']):+d})\n"
            f"**SAB:** `{ficha['wisdom']}` ({mod_atributo(ficha['wisdom']):+d})\n"
            f"**CAR:** `{ficha['charisma']}` ({mod_atributo(ficha['charisma']):+d})"
        ),
        inline=True
    )
    embed.add_field(
        name="❤️ Combate",
        value=(
            f"**HP:** `{ficha['hp']}/{ficha['hp_max']}`\n"
            f"**CA:** `{ficha['ca']}`"
        ),
        inline=True
    )
    trained = {k: v for k, v in ficha["skills"].items() if v}
    if trained:
        texto = "\n".join(f"**{k}:** `{'✓' if v else ''}`" for k, v in sorted(trained.items()))
    else:
        texto = "Nenhuma skill treinada."
    embed.add_field(name="🎯 Skills treinadas", value=texto[:1024], inline=False)
    embed.set_footer(text="D&D 5e • Ficha privada")
    return embed


# ==================================================
# PATHFINDER (simplificado 2e style)
# ==================================================

PF_SKILLS = [
    "Acrobatics", "Arcana", "Athletics", "Crafting", "Deception",
    "Diplomacy", "Intimidation", "Medicine", "Nature", "Occultism",
    "Performance", "Religion", "Society", "Stealth", "Survival", "Thievery"
]

cursor.execute("""
CREATE TABLE IF NOT EXISTS fichas_pathfinder (
    user_id INTEGER PRIMARY KEY,
    nome TEXT DEFAULT '',
    classe TEXT DEFAULT '',
    ancestria TEXT DEFAULT '',
    nivel INTEGER DEFAULT 1,
    strength INTEGER DEFAULT 10,
    dexterity INTEGER DEFAULT 10,
    constitution INTEGER DEFAULT 10,
    intelligence INTEGER DEFAULT 10,
    wisdom INTEGER DEFAULT 10,
    charisma INTEGER DEFAULT 10,
    hp INTEGER DEFAULT 0,
    hp_max INTEGER DEFAULT 0,
    ac INTEGER DEFAULT 10,
    proficiency INTEGER DEFAULT 2,
    skills TEXT DEFAULT '{}'
)
""")
db.commit()


def criar_skills_pf():
    return {skill: 0 for skill in PF_SKILLS}


def criar_ficha_pathfinder(user_id):
    skills = criar_skills_pf()
    cursor.execute("""
        INSERT OR IGNORE INTO fichas_pathfinder (
            user_id, hp, hp_max, skills
        ) VALUES (?, 10, 10, ?)
    """, (user_id, json.dumps(skills, ensure_ascii=False)))
    db.commit()


def garantir_ficha_pathfinder(user_id):
    criar_ficha_pathfinder(user_id)
    cursor.execute("SELECT * FROM fichas_pathfinder WHERE user_id = ?", (user_id,))
    linha = cursor.fetchone()
    colunas = [d[0] for d in cursor.description]
    ficha = dict(zip(colunas, linha))
    try:
        ficha["skills"] = json.loads(ficha["skills"] or "{}")
    except:
        ficha["skills"] = criar_skills_pf()
    for s in PF_SKILLS:
        ficha["skills"].setdefault(s, 0)
    return ficha


def criar_embed_ficha_pathfinder(ficha):
    embed = discord.Embed(
        title="⚔️ FICHA — PATHFINDER",
        description=f"**{ficha['nome'] or 'Sem nome'}**",
        color=discord.Color.dark_gold()
    )
    embed.add_field(
        name="📋 Informações",
        value=(
            f"**Classe:** {ficha['classe'] or '—'}\n"
            f"**Ancestria:** {ficha['ancestria'] or '—'}\n"
            f"**Nível:** `{ficha['nivel']}`\n"
            f"**Proficiência:** `+{ficha['proficiency']}`"
        ),
        inline=False
    )
    embed.add_field(
        name="🧠 Atributos",
        value=(
            f"**STR:** `{ficha['strength']}` ({mod_atributo(ficha['strength']):+d})\n"
            f"**DEX:** `{ficha['dexterity']}` ({mod_atributo(ficha['dexterity']):+d})\n"
            f"**CON:** `{ficha['constitution']}` ({mod_atributo(ficha['constitution']):+d})\n"
            f"**INT:** `{ficha['intelligence']}` ({mod_atributo(ficha['intelligence']):+d})\n"
            f"**WIS:** `{ficha['wisdom']}` ({mod_atributo(ficha['wisdom']):+d})\n"
            f"**CHA:** `{ficha['charisma']}` ({mod_atributo(ficha['charisma']):+d})"
        ),
        inline=True
    )
    embed.add_field(
        name="❤️ Combate",
        value=(
            f"**HP:** `{ficha['hp']}/{ficha['hp_max']}`\n"
            f"**AC:** `{ficha['ac']}`"
        ),
        inline=True
    )
    trained = {k: v for k, v in ficha["skills"].items() if v}
    if trained:
        texto = "\n".join(f"**{k}:** `Trained`" for k in sorted(trained.keys()))
    else:
        texto = "Nenhuma skill treinada."
    embed.add_field(name="🎯 Skills treinadas", value=texto[:1024], inline=False)
    embed.set_footer(text="Pathfinder • Ficha privada")
    return embed


# ==================================================
# EMBED DA FICHA
# ==================================================

def criar_embed_ficha(ficha):
    if ficha is None:
        return discord.Embed(
            title="❌ Ficha não encontrada",
            description="Não foi possível carregar sua ficha.",
            color=discord.Color.red()
        )

    (
        user_id,
        nome,
        idade,
        sexualidade,
        altura,
        peso,
        descendencia,
        linhagem,
        sub_linhagem,
        objetivo,
        medos,
        personalidade,
        relacoes,
        historia,
        fisico,
        conhecimento,
        social,
        vontade,
        pericias_json,
        xp,
        nivel
    ) = ficha

    try:
        pericias = json.loads(
            pericias_json or "{}"
        )

        if not isinstance(pericias, dict):
            pericias = criar_pericias()

    except (json.JSONDecodeError, TypeError):
        pericias = criar_pericias()

    embed = discord.Embed(
        title=f"👤 FICHA — {nome or 'Sem nome'}",
        description="🔒 Esta ficha é privada.",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="📖 Informações",
        value=(
            f"**Nome:** {nome or '—'}\n"
            f"**Idade:** {idade or '—'}\n"
            f"**Sexualidade:** {sexualidade or '—'}\n"
            f"**Altura:** {altura or '—'}\n"
            f"**Peso:** {peso or '—'}\n"
            f"**Descendência:** {descendencia or '—'}\n"
            f"**Linhagem Heroica:** {linhagem or '—'}\n"
            f"**Sub-linhagem:** {sub_linhagem or '—'}"
        ),
        inline=False
    )

    embed.add_field(
        name="⭐ Progressão",
        value=(
            f"**Nível:** `{nivel}`\n"
            f"**XP:** `{xp}/{xp_para_nivel(nivel)}`"
        ),
        inline=False
    )

    embed.add_field(
        name="🎯 Objetivo e Medos",
        value=(
            f"**Objetivo:** {objetivo or '—'}\n"
            f"**Medos:** {medos or '—'}"
        ),
        inline=False
    )

    embed.add_field(
        name="🧠 Personalidade",
        value=personalidade or "—",
        inline=False
    )

    embed.add_field(
        name="🤝 Relações",
        value=relacoes or "—",
        inline=False
    )

    embed.add_field(
        name="📜 História",
        value=historia or "—",
        inline=False
    )

    embed.add_field(
        name="⚔️ Atributos",
        value=(
            f"**Físico:** `{fisico}`\n"
            f"**Conhecimento:** `{conhecimento}`\n"
            f"**Social:** `{social}`\n"
            f"**Vontade:** `{vontade}`"
        ),
        inline=False
    )

    for categoria, lista in PERICIAS.items():
        texto = ""

        for pericia in lista:
            chave = f"{categoria}:{pericia}"
            valor = pericias.get(chave, 0)

            texto += f"**{pericia}:** `{valor}`\n"

        embed.add_field(
            name=f"📋 {categoria}",
            value=texto or "—",
            inline=True
        )

    embed.set_footer(
        text="Tavelada RPG • Ficha privada"
    )

    return embed


# ==================================================
# MOSTRAR FICHA
# ==================================================

async def mostrar_ficha(interaction):
    ficha = buscar_ficha(
        interaction.user.id
    )

    embed = criar_embed_ficha(ficha)

    if interaction.response.is_done():
        await interaction.edit_original_response(
            embed=embed,
            view=FichaView()
        )
    else:
        await interaction.response.send_message(
            embed=embed,
            view=FichaView(),
            ephemeral=True
        )


# ==================================================
# MODAL — INFORMAÇÕES
# ==================================================

class InformacoesModal(discord.ui.Modal):

    def __init__(self):
        super().__init__(
            title="📖 Informações"
        )

        self.nome = discord.ui.TextInput(
            label="Nome",
            placeholder="Nome do personagem",
            required=True,
            max_length=100
        )

        self.idade = discord.ui.TextInput(
            label="Idade",
            required=False,
            max_length=30
        )

        self.sexualidade = discord.ui.TextInput(
            label="Sexualidade",
            required=False,
            max_length=50
        )

        self.altura = discord.ui.TextInput(
            label="Altura",
            required=False,
            max_length=30
        )

        self.peso = discord.ui.TextInput(
            label="Peso",
            required=False,
            max_length=30
        )

        self.add_item(self.nome)
        self.add_item(self.idade)
        self.add_item(self.sexualidade)
        self.add_item(self.altura)
        self.add_item(self.peso)

    async def on_submit(self, interaction):
        criar_ficha(interaction.user.id)

        cursor.execute(
            """
            UPDATE fichas
            SET
                nome = ?,
                idade = ?,
                sexualidade = ?,
                altura = ?,
                peso = ?
            WHERE user_id = ?
            """,
            (
                self.nome.value,
                self.idade.value,
                self.sexualidade.value,
                self.altura.value,
                self.peso.value,
                interaction.user.id
            )
        )

        db.commit()

        await mostrar_ficha(interaction)


# ==================================================
# MODAL — LINHAGEM
# ==================================================

class LinhagemModal(discord.ui.Modal):

    def __init__(self):
        super().__init__(
            title="🧬 Linhagem e Objetivos"
        )

        self.descendencia = discord.ui.TextInput(
            label="Descendência",
            required=False,
            max_length=300
        )

        self.linhagem = discord.ui.TextInput(
            label="Linhagem Heroica",
            required=False,
            max_length=300
        )

        self.sub_linhagem = discord.ui.TextInput(
            label="Sub-linhagem",
            required=False,
            max_length=300
        )

        self.objetivo = discord.ui.TextInput(
            label="Objetivo",
            required=False,
            max_length=500
        )

        self.medos = discord.ui.TextInput(
            label="Medos",
            required=False,
            max_length=500
        )

        self.add_item(self.descendencia)
        self.add_item(self.linhagem)
        self.add_item(self.sub_linhagem)
        self.add_item(self.objetivo)
        self.add_item(self.medos)

    async def on_submit(self, interaction):
        criar_ficha(interaction.user.id)

        cursor.execute(
            """
            UPDATE fichas
            SET
                descendencia = ?,
                linhagem_heroica = ?,
                sub_linhagem = ?,
                objetivo = ?,
                medos = ?
            WHERE user_id = ?
            """,
            (
                self.descendencia.value,
                self.linhagem.value,
                self.sub_linhagem.value,
                self.objetivo.value,
                self.medos.value,
                interaction.user.id
            )
        )

        db.commit()

        await mostrar_ficha(interaction)


# ==================================================
# MODAL — PERSONALIDADE
# ==================================================

class PersonalidadeModal(discord.ui.Modal):

    def __init__(self):
        super().__init__(
            title="🧠 Personalidade e História"
        )

        self.personalidade = discord.ui.TextInput(
            label="Personalidade",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=1000
        )

        self.relacoes = discord.ui.TextInput(
            label="Relações",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=1000
        )

        self.historia = discord.ui.TextInput(
            label="História",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=1500
        )

        self.add_item(self.personalidade)
        self.add_item(self.relacoes)
        self.add_item(self.historia)

    async def on_submit(self, interaction):
        criar_ficha(interaction.user.id)

        cursor.execute(
            """
            UPDATE fichas
            SET
                personalidade = ?,
                relacoes = ?,
                historia = ?
            WHERE user_id = ?
            """,
            (
                self.personalidade.value,
                self.relacoes.value,
                self.historia.value,
                interaction.user.id
            )
        )

        db.commit()

        await mostrar_ficha(interaction)


# ==================================================
# VIEW DA FICHA
# ==================================================

class FichaView(discord.ui.View):

    def __init__(self):
        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Informações",
        emoji="📖",
        style=discord.ButtonStyle.primary
    )
    async def informacoes(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            InformacoesModal()
        )

    @discord.ui.button(
        label="Linhagem",
        emoji="🧬",
        style=discord.ButtonStyle.primary
    )
    async def linhagem(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            LinhagemModal()
        )

    @discord.ui.button(
        label="Personalidade",
        emoji="🧠",
        style=discord.ButtonStyle.primary
    )
    async def personalidade(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            PersonalidadeModal()
        )

    @discord.ui.button(
        label="Atualizar",
        emoji="🔄",
        style=discord.ButtonStyle.secondary
    )
    async def atualizar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            embed=criar_embed_ficha(
                buscar_ficha(interaction.user.id)
            ),
            view=FichaView()
        )


# ==================================================
# PERMISSÕES
# ==================================================

def tem_cargo(interaction, cargo_id):
    if not isinstance(
        interaction.user,
        discord.Member
    ):
        return False

    return any(
        cargo.id == cargo_id
        for cargo in interaction.user.roles
    )


def eh_pesquisador(interaction):
    return tem_cargo(
        interaction,
        PESQUISADOR_ROLE_ID
    )


# ==================================================
# NPC / BOSS
# ==================================================

class CriarNPCModal(discord.ui.Modal):

    def __init__(self):
        super().__init__(title="🛡️ Criar NPC / Boss")

        self.nome = discord.ui.TextInput(label="Nome", required=True, max_length=100)
        self.tipo = discord.ui.TextInput(label="Tipo", placeholder="NPC, Boss, Inimigo...", required=True, max_length=30)
        self.vida = discord.ui.TextInput(label="Vida / PV", placeholder="Ex: 100", required=True, max_length=10)
        self.sistema = discord.ui.TextInput(label="Sistema", placeholder="Tavelada, Ordem, D&D, Brutal...", required=False, max_length=30)
        self.notas = discord.ui.TextInput(label="Notas / Atributos extras", style=discord.TextStyle.paragraph, required=False, max_length=1000)

        self.add_item(self.nome)
        self.add_item(self.tipo)
        self.add_item(self.vida)
        self.add_item(self.sistema)
        self.add_item(self.notas)

    async def on_submit(self, interaction):
        if not eh_pesquisador(interaction):
            await interaction.response.send_message("🔒 Apenas Pesquisadores podem criar NPCs.", ephemeral=True)
            return

        try:
            vida = int(self.vida.value)
        except ValueError:
            await interaction.response.send_message("❌ Vida precisa ser um número.", ephemeral=True)
            return

        if vida < 0:
            await interaction.response.send_message("❌ Vida não pode ser negativa.", ephemeral=True)
            return

        # Garante colunas extras
        for col, tipo in [("sistema", "TEXT DEFAULT ''"), ("notas", "TEXT DEFAULT ''")]:
            try:
                cursor.execute(f"ALTER TABLE npcs ADD COLUMN {col} {tipo}")
                db.commit()
            except:
                pass

        cursor.execute("""
            INSERT INTO npcs (nome, tipo, vida, fisico, pericias, sistema, notas)
            VALUES (?, ?, ?, 0, '{}', ?, ?)
        """, (
            self.nome.value,
            self.tipo.value,
            vida,
            self.sistema.value or "Geral",
            self.notas.value or ""
        ))
        db.commit()

        await interaction.response.send_message(
            f"🛡️ **{self.nome.value}** criado!\n\n"
            f"❤️ Vida: **{vida}**\n"
            f"📜 Sistema: **{self.sistema.value or 'Geral'}**\n"
            f"📝 Notas: {self.notas.value or '—'}",
            ephemeral=True
        )


# ==================================================
# LISTAR NPCS
# ==================================================

async def listar_npcs(interaction):
    try:
        cursor.execute("SELECT id, nome, tipo, vida, sistema, notas FROM npcs ORDER BY id")
    except:
        cursor.execute("SELECT id, nome, tipo, vida, fisico FROM npcs ORDER BY id")
        npcs = cursor.fetchall()
        if not npcs:
            await interaction.response.send_message("🛡️ Nenhum NPC/Boss criado ainda.", ephemeral=True)
            return
        texto = ""
        for row in npcs:
            texto += f"**#{row[0]} — {row[1]}**\n{row[2]} • ❤️ {row[3]}\n\n"
        embed = discord.Embed(title="🛡️ NPCs / BOSSES", description=texto[:4096], color=discord.Color.dark_red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    npcs = cursor.fetchall()

    if not npcs:
        await interaction.response.send_message("🛡️ Nenhum NPC/Boss criado ainda.", ephemeral=True)
        return

    texto = ""
    for row in npcs:
        npc_id, nome, tipo, vida, sistema, notas = row
        texto += f"**#{npc_id} — {nome}**\n"
        texto += f"{tipo} • ❤️ {vida}"
        if sistema:
            texto += f" • 📜 {sistema}"
        texto += "\n"
        if notas:
            texto += f"📝 {notas[:80]}{'...' if len(notas) > 80 else ''}\n"
        texto += "\n"

    embed = discord.Embed(title="🛡️ NPCs / BOSSES", description=texto[:4096], color=discord.Color.dark_red())
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ==================================================
# COMBATE
# ==================================================

def combate_ativo():
    cursor.execute(
        """
        SELECT ativo
        FROM combate
        WHERE id = 1
        """
    )

    resultado = cursor.fetchone()

    if resultado is None:
        return False

    return resultado[0] == 1


def ja_esta_no_combate(tipo, referencia_id):
    cursor.execute(
        """
        SELECT id
        FROM combatentes
        WHERE tipo = ? AND referencia_id = ?
        """,
        (
            tipo,
            referencia_id
        )
    )

    return cursor.fetchone() is not None


def adicionar_jogador_combate(user_id):
    if not combate_ativo():
        return "combate_inativo"

    if ja_esta_no_combate(
        "jogador",
        user_id
    ):
        return "duplicado"

    ficha = buscar_ficha_dict(user_id)

    if ficha is None:
        return "erro"

    nome = ficha["nome"] or "Jogador"

    fisico = int(
        ficha.get("fisico") or 0
    )

    try:
        pericias = json.loads(
            ficha.get("pericias") or "{}"
        )

        if not isinstance(pericias, dict):
            pericias = criar_pericias()

    except (json.JSONDecodeError, TypeError):
        pericias = criar_pericias()

    atletismo = int(
        pericias.get(
            "Físico:Atletismo",
            0
        ) or 0
    )

    dado = random.randint(1, 7)

    iniciativa = (
        dado +
        fisico +
        atletismo
    )

    cursor.execute(
        """
        INSERT INTO combatentes (
            nome,
            tipo,
            referencia_id,
            iniciativa,
            dado,
            fisico,
            atletismo,
            vida
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            nome,
            "jogador",
            user_id,
            iniciativa,
            dado,
            fisico,
            atletismo,
            0
        )
    )

    db.commit()

    return "sucesso"


def adicionar_npc_combate(npc_id):
    if not combate_ativo():
        return "combate_inativo"

    if ja_esta_no_combate(
        "npc",
        npc_id
    ):
        return "duplicado"

    cursor.execute(
        """
        SELECT
            id,
            nome,
            vida,
            fisico,
            pericias
        FROM npcs
        WHERE id = ?
        """,
        (npc_id,)
    )

    npc = cursor.fetchone()

    if npc is None:
        return "nao_encontrado"

    (
        id_npc,
        nome,
        vida,
        fisico,
        pericias_json
    ) = npc

    try:
        pericias = json.loads(
            pericias_json or "{}"
        )

        if not isinstance(pericias, dict):
            pericias = criar_pericias()

    except (json.JSONDecodeError, TypeError):
        pericias = criar_pericias()

    atletismo = int(
        pericias.get(
            "Físico:Atletismo",
            0
        ) or 0
    )

    dado = random.randint(1, 7)

    iniciativa = (
        dado +
        int(fisico or 0) +
        atletismo
    )

    cursor.execute(
        """
        INSERT INTO combatentes (
            nome,
            tipo,
            referencia_id,
            iniciativa,
            dado,
            fisico,
            atletismo,
            vida
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            nome,
            "npc",
            id_npc,
            iniciativa,
            dado,
            int(fisico or 0),
            atletismo,
            int(vida or 0)
        )
    )

    db.commit()

    return "sucesso"


def criar_embed_combate():
    if not combate_ativo():
        return discord.Embed(
            title="⚔️ COMBATE",
            description="Nenhum combate ativo no momento.",
            color=discord.Color.red()
        )

    cursor.execute(
        """
        SELECT rodada, turno
        FROM combate
        WHERE id = 1
        """
    )

    combate = cursor.fetchone()

    if combate is None:
        return discord.Embed(
            title="⚔️ COMBATE",
            description="Nenhum combate configurado.",
            color=discord.Color.red()
        )

    rodada, turno = combate

    cursor.execute(
        """
        SELECT
            id,
            nome,
            tipo,
            iniciativa,
            dado,
            fisico,
            atletismo,
            vida
        FROM combatentes
        ORDER BY iniciativa DESC, id ASC
        """
    )

    combatentes = cursor.fetchall()

    embed = discord.Embed(
        title="⚔️ COMBATE",
        description=f"**Rodada:** {rodada}",
        color=discord.Color.orange()
    )

    if not combatentes:
        embed.add_field(
            name="Combatentes",
            value="Nenhum combatente adicionado ainda.",
            inline=False
        )

        return embed

    texto = ""

    for posicao, combatente in enumerate(
        combatentes,
        start=1
    ):
        (
            cid,
            nome,
            tipo,
            iniciativa,
            dado,
            fisico,
            atletismo,
            vida
        ) = combatente

        prefixo = (
            "▶️"
            if posicao - 1 == turno
            else f"**{posicao}.**"
        )

        icone = (
            "🛡️"
            if tipo == "npc"
            else "👤"
        )

        texto += (
            f"{prefixo} {icone} **{nome}** — "
            f"⚔️ `{iniciativa}`"
        )

        if tipo == "npc":
            texto += f" • ❤️ `{vida}`"

        texto += "\n"

    embed.add_field(
        name="Ordem de Iniciativa",
        value=texto[:1024],
        inline=False
    )

    turno_seguro = min(
        max(turno, 0),
        len(combatentes) - 1
    )

    atual = combatentes[turno_seguro]

    embed.add_field(
        name="▶️ Turno Atual",
        value=f"**{atual[1]}**",
        inline=False
    )

    return embed


def iniciar_combate():
    cursor.execute(
        "DELETE FROM combatentes"
    )

    cursor.execute(
        """
        INSERT OR REPLACE INTO combate (
            id,
            rodada,
            turno,
            ativo
        )
        VALUES (1, 1, 0, 1)
        """
    )

    db.commit()


def proximo_turno():
    if not combate_ativo():
        return False

    cursor.execute(
        """
        SELECT rodada, turno
        FROM combate
        WHERE id = 1
        """
    )

    combate = cursor.fetchone()

    if combate is None:
        return False

    rodada, turno = combate

    cursor.execute(
        "SELECT COUNT(*) FROM combatentes"
    )

    quantidade = cursor.fetchone()[0]

    if quantidade == 0:
        return False

    turno += 1

    if turno >= quantidade:
        turno = 0
        rodada += 1

    cursor.execute(
        """
        UPDATE combate
        SET rodada = ?, turno = ?
        WHERE id = 1
        """,
        (
            rodada,
            turno
        )
    )

    db.commit()

    return True


# ==================================================
# HISTÓRICO
# ==================================================

def registrar_rolagem(
    user_id,
    nome_usuario,
    tipo,
    resultado,
    dado
):
    cursor.execute(
        """
        INSERT INTO historico_rolagens (
            user_id,
            nome_usuario,
            tipo,
            resultado,
            dado
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            nome_usuario,
            tipo,
            resultado,
            dado
        )
    )

    db.commit()


# ==================================================
# VIEW DO COMBATE
# ==================================================

class CombateView(discord.ui.View):

    def __init__(self):
        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Atualizar",
        emoji="🔄",
        style=discord.ButtonStyle.secondary
    )
    async def atualizar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            embed=criar_embed_combate(),
            view=CombateView()
        )


# ==================================================
# VIEW DO MESTRE NO COMBATE
# ==================================================

class CombateMestreView(discord.ui.View):

    def __init__(self):
        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Adicionar NPC",
        emoji="🛡️",
        style=discord.ButtonStyle.danger
    )
    async def adicionar_npc(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if not eh_pesquisador(interaction):
            await interaction.response.send_message(
                "🔒 Apenas Pesquisadores podem fazer isso.",
                ephemeral=True
            )
            return

        cursor.execute(
            """
            SELECT id, nome, tipo
            FROM npcs
            ORDER BY id
            """
        )

        npcs = cursor.fetchall()

        if not npcs:
            await interaction.response.send_message(
                "❌ Você ainda não criou nenhum NPC/Boss.",
                ephemeral=True
            )
            return

        opcoes = []

        for npc_id, nome, tipo in npcs[:25]:
            opcoes.append(
                discord.SelectOption(
                    label=f"{nome} — {tipo}"[:100],
                    value=str(npc_id)
                )
            )

        view = discord.ui.View(
            timeout=60
        )

        view.add_item(
            NPCSelect(opcoes)
        )

        await interaction.response.send_message(
            "🛡️ Escolha o NPC/Boss:",
            view=view,
            ephemeral=True
        )

    @discord.ui.button(
        label="Próximo Turno",
        emoji="⏭️",
        style=discord.ButtonStyle.success
    )
    async def proximo(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if not eh_pesquisador(interaction):
            await interaction.response.send_message(
                "🔒 Apenas Pesquisadores controlam o combate.",
                ephemeral=True
            )
            return

        sucesso = proximo_turno()

        if not sucesso:
            await interaction.response.send_message(
                "❌ Não existem combatentes suficientes.",
                ephemeral=True
            )
            return

        await interaction.response.edit_message(
            embed=criar_embed_combate(),
            view=CombateMestreView()
        )

    @discord.ui.button(
        label="Atualizar",
        emoji="🔄",
        style=discord.ButtonStyle.secondary
    )
    async def atualizar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            embed=criar_embed_combate(),
            view=CombateMestreView()
        )

    @discord.ui.button(
        label="Encerrar",
        emoji="🛑",
        style=discord.ButtonStyle.danger
    )
    async def encerrar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if not eh_pesquisador(interaction):
            await interaction.response.send_message(
                "🔒 Apenas Pesquisadores podem encerrar.",
                ephemeral=True
            )
            return

        cursor.execute(
            "DELETE FROM combatentes"
        )

        cursor.execute(
            """
            UPDATE combate
            SET
                ativo = 0,
                rodada = 1,
                turno = 0
            WHERE id = 1
            """
        )

        db.commit()

        await interaction.response.edit_message(
            content="🛑 **Combate encerrado.**",
            embed=None,
            view=None
        )


# ==================================================
# SELECT NPC
# ==================================================

class NPCSelect(discord.ui.Select):

    def __init__(self, opcoes):
        super().__init__(
            placeholder="Escolha um NPC/Boss...",
            options=opcoes
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):
        if not eh_pesquisador(interaction):
            await interaction.response.send_message(
                "🔒 Apenas Pesquisadores podem adicionar NPCs.",
                ephemeral=True
            )
            return

        npc_id = int(
            self.values[0]
        )

        resultado = adicionar_npc_combate(
            npc_id
        )

        if resultado == "duplicado":
            mensagem = (
                "⚠️ Esse NPC já está no combate."
            )

        elif resultado == "combate_inativo":
            mensagem = (
                "❌ Nenhum combate está ativo."
            )

        elif resultado == "nao_encontrado":
            mensagem = (
                "❌ NPC não encontrado."
            )

        else:
            mensagem = (
                "✅ NPC adicionado ao combate!"
            )

        await interaction.response.send_message(
            mensagem,
            ephemeral=True
        )


# ==================================================
# ESCUDO DO MESTRE
# ==================================================

class EscudoMestre(discord.ui.View):

    def __init__(self):
        super().__init__(
            timeout=None
        )

    @discord.ui.button(
        label="NPCs / Bosses",
        emoji="🛡️",
        style=discord.ButtonStyle.danger
    )
    async def npcs(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if not eh_pesquisador(interaction):
            await interaction.response.send_message(
                "🔒 Apenas Pesquisadores possuem acesso.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🛡️ MODO BOSS",
            description=(
                "Área secreta dos Pesquisadores.\n\n"
                "Aqui você administra NPCs e Bosses."
            ),
            color=discord.Color.dark_red()
        )

        await interaction.response.send_message(
            embed=embed,
            view=BossView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Iniciar Combate",
        emoji="⚔️",
        style=discord.ButtonStyle.success
    )
    async def combate(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if not eh_pesquisador(interaction):
            await interaction.response.send_message(
                "🔒 Apenas Pesquisadores podem iniciar combates.",
                ephemeral=True
            )
            return

        iniciar_combate()

        await interaction.response.send_message(
            embed=criar_embed_combate(),
            view=CombateMestreView(),
            ephemeral=True
        )


# ==================================================
# MODO BOSS
# ==================================================

class BossView(discord.ui.View):

    def __init__(self):
        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Criar NPC / Boss",
        emoji="➕",
        style=discord.ButtonStyle.danger
    )
    async def criar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if not eh_pesquisador(interaction):
            await interaction.response.send_message(
                "🔒 Apenas Pesquisadores podem criar NPCs.",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            CriarNPCModal()
        )

    @discord.ui.button(
        label="Meus NPCs",
        emoji="📋",
        style=discord.ButtonStyle.primary
    )
    async def listar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if not eh_pesquisador(interaction):
            await interaction.response.send_message(
                "🔒 Apenas Pesquisadores podem ver NPCs.",
                ephemeral=True
            )
            return

        await listar_npcs(
            interaction
        )


# ==================================================
# BRUTAL (Slasher)
# ==================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS fichas_brutal (
    user_id INTEGER PRIMARY KEY,
    nome TEXT DEFAULT '',
    pronomes TEXT DEFAULT '',
    interprete TEXT DEFAULT '',
    arquetipo TEXT DEFAULT '',
    agilidade INTEGER DEFAULT 0,
    astucia INTEGER DEFAULT 0,
    forca INTEGER DEFAULT 0,
    carisma INTEGER DEFAULT 0,
    vigor INTEGER DEFAULT 0,
    pilha_dados INTEGER DEFAULT 0,
    pilha_fuga INTEGER DEFAULT 0,
    feridas INTEGER DEFAULT 0,
    sequelas TEXT DEFAULT '',
    habilidades TEXT DEFAULT '',
    aparencia TEXT DEFAULT '',
    vantagens_gerais TEXT DEFAULT '',
    vantagens_especialidade TEXT DEFAULT ''
)
""")
db.commit()


def criar_ficha_brutal(user_id):
    cursor.execute("""
        INSERT OR IGNORE INTO fichas_brutal (user_id) VALUES (?)
    """, (user_id,))
    db.commit()


def garantir_ficha_brutal(user_id):
    criar_ficha_brutal(user_id)
    cursor.execute("SELECT * FROM fichas_brutal WHERE user_id = ?", (user_id,))
    linha = cursor.fetchone()
    colunas = [d[0] for d in cursor.description]
    return dict(zip(colunas, linha))


def criar_embed_ficha_brutal(ficha):
    embed = discord.Embed(
        title="🔪 FICHA — BRUTAL",
        description=f"**{ficha['nome'] or 'Sem nome'}**",
        color=discord.Color.dark_red()
    )

    embed.add_field(
        name="📋 Informações",
        value=(
            f"**Pronomes:** {ficha['pronomes'] or '—'}\n"
            f"**Intérprete:** {ficha['interprete'] or '—'}\n"
            f"**Arquétipo:** {ficha['arquetipo'] or '—'}"
        ),
        inline=False
    )

    embed.add_field(
        name="🩸 Atributos",
        value=(
            f"**Agilidade:** `{ficha['agilidade']}`\n"
            f"**Astúcia:** `{ficha['astucia']}`\n"
            f"**Força:** `{ficha['forca']}`\n"
            f"**Carisma:** `{ficha['carisma']}`\n"
            f"**Vigor:** `{ficha['vigor']}`"
        ),
        inline=True
    )

    embed.add_field(
        name="📦 Pilhas & Feridas",
        value=(
            f"**Pilha de Dados:** `{ficha['pilha_dados']}`\n"
            f"**Pilha de Fuga:** `{ficha['pilha_fuga']}`\n"
            f"**Feridas:** `{ficha['feridas']}`\n"
            f"**Sequelas:** {ficha['sequelas'] or '—'}"
        ),
        inline=True
    )

    if ficha.get("habilidades"):
        embed.add_field(name="🎯 Habilidades", value=ficha["habilidades"][:1024], inline=False)

    if ficha.get("vantagens_gerais"):
        embed.add_field(name="⭐ Vantagens Gerais", value=ficha["vantagens_gerais"][:1024], inline=False)

    if ficha.get("vantagens_especialidade"):
        embed.add_field(name="💎 Vantagens de Especialidade", value=ficha["vantagens_especialidade"][:1024], inline=False)

    if ficha.get("aparencia"):
        embed.add_field(name="🖼️ Aparência", value=ficha["aparencia"][:1024], inline=False)

    embed.set_footer(text="Brutal • Sobreviva... se conseguir")
    return embed


# ==================================================
# KIDS ON BIKES
# ==================================================

KIDS_ATRIBUTOS = {
    "Fear": "d4",
    "Fight": "d6",
    "Flight": "d8",
    "Charm": "d10",
    "Grit": "d12",
    "Brains": "d20",
    "Brawn": "d4"
}

# Mapeamento de dado por idade aproximada (simplificado)
KIDS_DADOS = ["d4", "d6", "d8", "d10", "d12", "d20"]

cursor.execute("""
CREATE TABLE IF NOT EXISTS fichas_kids (
    user_id INTEGER PRIMARY KEY,
    nome TEXT DEFAULT '',
    idade INTEGER DEFAULT 12,
    fear TEXT DEFAULT 'd6',
    fight TEXT DEFAULT 'd6',
    flight TEXT DEFAULT 'd6',
    charm TEXT DEFAULT 'd6',
    grit TEXT DEFAULT 'd6',
    brains TEXT DEFAULT 'd6',
    brawn TEXT DEFAULT 'd6',
    motivacao TEXT DEFAULT '',
    medo TEXT DEFAULT '',
    trope TEXT DEFAULT ''
)
""")
db.commit()


def criar_ficha_kids(user_id):
    cursor.execute("""
        INSERT OR IGNORE INTO fichas_kids (user_id) VALUES (?)
    """, (user_id,))
    db.commit()


def garantir_ficha_kids(user_id):
    criar_ficha_kids(user_id)
    cursor.execute("SELECT * FROM fichas_kids WHERE user_id = ?", (user_id,))
    linha = cursor.fetchone()
    colunas = [d[0] for d in cursor.description]
    return dict(zip(colunas, linha))


def criar_embed_ficha_kids(ficha):
    embed = discord.Embed(
        title="🚲 FICHA — KIDS ON BIKES",
        description=f"**{ficha['nome'] or 'Sem nome'}**",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="📋 Informações",
        value=(
            f"**Idade:** `{ficha['idade']}`\n"
            f"**Motivação:** {ficha['motivacao'] or '—'}\n"
            f"**Medo:** {ficha['medo'] or '—'}\n"
            f"**Trope:** {ficha['trope'] or '—'}"
        ),
        inline=False
    )
    embed.add_field(
        name="🎲 Atributos (dados)",
        value=(
            f"**Fear:** `{ficha['fear']}`\n"
            f"**Fight:** `{ficha['fight']}`\n"
            f"**Flight:** `{ficha['flight']}`\n"
            f"**Charm:** `{ficha['charm']}`\n"
            f"**Grit:** `{ficha['grit']}`\n"
            f"**Brains:** `{ficha['brains']}`\n"
            f"**Brawn:** `{ficha['brawn']}`"
        ),
        inline=False
    )
    embed.set_footer(text="Kids on Bikes • Aventuras e mistérios")
    return embed


# ==================================================
# UI — BRUTAL
# ==================================================

class BrutalInfoModal(discord.ui.Modal):
    def __init__(self, ficha=None):
        super().__init__(title="🔪 Informações — Brutal")
        f = ficha or {}
        self.nome = discord.ui.TextInput(label="Nome", required=False, max_length=100, default=f.get("nome", ""))
        self.pronomes = discord.ui.TextInput(label="Pronomes", required=False, max_length=50, default=f.get("pronomes", ""))
        self.interprete = discord.ui.TextInput(label="Intérprete", required=False, max_length=100, default=f.get("interprete", ""))
        self.arquetipo = discord.ui.TextInput(label="Arquétipo", required=False, max_length=100, default=f.get("arquetipo", ""))
        for item in [self.nome, self.pronomes, self.interprete, self.arquetipo]:
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        garantir_ficha_brutal(interaction.user.id)
        cursor.execute("""
            UPDATE fichas_brutal SET nome=?, pronomes=?, interprete=?, arquetipo=? WHERE user_id=?
        """, (self.nome.value, self.pronomes.value, self.interprete.value, self.arquetipo.value, interaction.user.id))
        db.commit()
        ficha = garantir_ficha_brutal(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_brutal(ficha), view=BrutalFichaView())


class BrutalAtributosModal(discord.ui.Modal):
    def __init__(self, ficha=None):
        super().__init__(title="🩸 Atributos — Brutal")
        f = ficha or {}
        self.agilidade = discord.ui.TextInput(label="Agilidade", required=True, default=str(f.get("agilidade", 0)))
        self.astucia = discord.ui.TextInput(label="Astúcia", required=True, default=str(f.get("astucia", 0)))
        self.forca = discord.ui.TextInput(label="Força", required=True, default=str(f.get("forca", 0)))
        self.carisma = discord.ui.TextInput(label="Carisma", required=True, default=str(f.get("carisma", 0)))
        self.vigor = discord.ui.TextInput(label="Vigor", required=True, default=str(f.get("vigor", 0)))
        for item in [self.agilidade, self.astucia, self.forca, self.carisma, self.vigor]:
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            vals = [int(x.value) for x in [self.agilidade, self.astucia, self.forca, self.carisma, self.vigor]]
        except ValueError:
            await interaction.response.send_message("❌ Atributos precisam ser números.", ephemeral=True)
            return
        garantir_ficha_brutal(interaction.user.id)
        cursor.execute("""
            UPDATE fichas_brutal SET agilidade=?, astucia=?, forca=?, carisma=?, vigor=? WHERE user_id=?
        """, (*vals, interaction.user.id))
        db.commit()
        ficha = garantir_ficha_brutal(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_brutal(ficha), view=BrutalFichaView())


class BrutalEstadoModal(discord.ui.Modal):
    def __init__(self, ficha=None):
        super().__init__(title="📦 Pilhas & Feridas — Brutal")
        f = ficha or {}
        self.pilha_dados = discord.ui.TextInput(label="Pilha de Dados", required=True, default=str(f.get("pilha_dados", 0)))
        self.pilha_fuga = discord.ui.TextInput(label="Pilha de Fuga", required=True, default=str(f.get("pilha_fuga", 0)))
        self.feridas = discord.ui.TextInput(label="Feridas", required=True, default=str(f.get("feridas", 0)))
        self.sequelas = discord.ui.TextInput(label="Sequelas", required=False, max_length=200, default=f.get("sequelas", ""))
        for item in [self.pilha_dados, self.pilha_fuga, self.feridas, self.sequelas]:
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            pd = int(self.pilha_dados.value)
            pf = int(self.pilha_fuga.value)
            fe = int(self.feridas.value)
        except ValueError:
            await interaction.response.send_message("❌ Pilhas e Feridas precisam ser números.", ephemeral=True)
            return
        garantir_ficha_brutal(interaction.user.id)
        cursor.execute("""
            UPDATE fichas_brutal SET pilha_dados=?, pilha_fuga=?, feridas=?, sequelas=? WHERE user_id=?
        """, (pd, pf, fe, self.sequelas.value, interaction.user.id))
        db.commit()
        ficha = garantir_ficha_brutal(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_brutal(ficha), view=BrutalFichaView())


class BrutalTextoModal(discord.ui.Modal):
    def __init__(self, campo, titulo, ficha=None):
        super().__init__(title=titulo)
        self.campo = campo
        f = ficha or {}
        self.texto = discord.ui.TextInput(
            label=titulo,
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=1000,
            default=f.get(campo, "")
        )
        self.add_item(self.texto)

    async def on_submit(self, interaction: discord.Interaction):
        garantir_ficha_brutal(interaction.user.id)
        cursor.execute(f"UPDATE fichas_brutal SET {self.campo}=? WHERE user_id=?",
                       (self.texto.value, interaction.user.id))
        db.commit()
        ficha = garantir_ficha_brutal(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_brutal(ficha), view=BrutalFichaView())


class BrutalFichaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Informações", emoji="📋", style=discord.ButtonStyle.primary)
    async def informacoes(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_brutal(interaction.user.id)
        await interaction.response.send_modal(BrutalInfoModal(ficha))

    @discord.ui.button(label="Atributos", emoji="🩸", style=discord.ButtonStyle.primary)
    async def atributos(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_brutal(interaction.user.id)
        await interaction.response.send_modal(BrutalAtributosModal(ficha))

    @discord.ui.button(label="Estado", emoji="📦", style=discord.ButtonStyle.primary)
    async def estado(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_brutal(interaction.user.id)
        await interaction.response.send_modal(BrutalEstadoModal(ficha))

    @discord.ui.button(label="Habilidades", emoji="🎯", style=discord.ButtonStyle.secondary)
    async def habilidades(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_brutal(interaction.user.id)
        await interaction.response.send_modal(BrutalTextoModal("habilidades", "🎯 Habilidades", ficha))

    @discord.ui.button(label="Vantagens", emoji="⭐", style=discord.ButtonStyle.secondary)
    async def vantagens(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_brutal(interaction.user.id)
        await interaction.response.send_modal(BrutalTextoModal("vantagens_gerais", "⭐ Vantagens Gerais", ficha))

    @discord.ui.button(label="Especialidade", emoji="💎", style=discord.ButtonStyle.secondary)
    async def especialidade(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_brutal(interaction.user.id)
        await interaction.response.send_modal(BrutalTextoModal("vantagens_especialidade", "💎 Vantagens de Especialidade", ficha))

    @discord.ui.button(label="Aparência", emoji="🖼️", style=discord.ButtonStyle.secondary)
    async def aparencia(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_brutal(interaction.user.id)
        await interaction.response.send_modal(BrutalTextoModal("aparencia", "🖼️ Aparência", ficha))

    @discord.ui.button(label="Atualizar", emoji="🔄", style=discord.ButtonStyle.success)
    async def atualizar(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_brutal(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_brutal(ficha), view=BrutalFichaView())

    @discord.ui.button(label="Voltar", emoji="↩️", style=discord.ButtonStyle.secondary)
    async def voltar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=criar_embed_sistemas(), view=SistemasView())


class BrutalSistemaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Minha Ficha", emoji="📖", style=discord.ButtonStyle.primary)
    async def ficha(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_brutal(interaction.user.id)
        await interaction.response.send_message(embed=criar_embed_ficha_brutal(ficha), view=BrutalFichaView(), ephemeral=True)

    @discord.ui.button(label="Rolar 2d6", emoji="🎲", style=discord.ButtonStyle.success)
    async def rolar(self, interaction: discord.Interaction, button: discord.ui.Button):
        d1, d2 = random.randint(1, 6), random.randint(1, 6)
        total = d1 + d2
        registrar_rolagem(interaction.user.id, interaction.user.display_name, "Brutal 2d6", total, 6)
        embed = discord.Embed(title="🎲 ROLAGEM — BRUTAL", color=discord.Color.dark_red())
        embed.add_field(name="Dados", value=f"`{d1}` + `{d2}`", inline=True)
        embed.add_field(name="Total", value=f"**{total}**", inline=True)
        await interaction.response.edit_message(embed=embed, view=BrutalSistemaView())

    @discord.ui.button(label="Voltar", emoji="↩️", style=discord.ButtonStyle.secondary)
    async def voltar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=criar_embed_sistemas(), view=SistemasView())


# ==================================================
# UI — KIDS ON BIKES
# ==================================================

class KidsInfoModal(discord.ui.Modal):
    def __init__(self, ficha=None):
        super().__init__(title="🚲 Informações — Kids on Bikes")
        f = ficha or {}
        self.nome = discord.ui.TextInput(label="Nome", required=False, max_length=100, default=f.get("nome", ""))
        self.idade = discord.ui.TextInput(label="Idade", required=False, default=str(f.get("idade", 12)))
        self.motivacao = discord.ui.TextInput(label="Motivação", required=False, max_length=150, default=f.get("motivacao", ""))
        self.medo = discord.ui.TextInput(label="Medo", required=False, max_length=150, default=f.get("medo", ""))
        self.trope = discord.ui.TextInput(label="Trope", required=False, max_length=100, default=f.get("trope", ""))
        for item in [self.nome, self.idade, self.motivacao, self.medo, self.trope]:
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            idade = int(self.idade.value or 12)
        except:
            idade = 12
        garantir_ficha_kids(interaction.user.id)
        cursor.execute("""
            UPDATE fichas_kids SET nome=?, idade=?, motivacao=?, medo=?, trope=? WHERE user_id=?
        """, (self.nome.value, idade, self.motivacao.value, self.medo.value, self.trope.value, interaction.user.id))
        db.commit()
        ficha = garantir_ficha_kids(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_kids(ficha), view=KidsFichaView())


class KidsAtributosModal1(discord.ui.Modal):
    def __init__(self, ficha=None):
        super().__init__(title="🎲 Atributos 1/2 — Kids")
        f = ficha or {}
        self.fear = discord.ui.TextInput(label="Fear (ex: d6)", required=True, default=f.get("fear", "d6"))
        self.fight = discord.ui.TextInput(label="Fight", required=True, default=f.get("fight", "d6"))
        self.flight = discord.ui.TextInput(label="Flight", required=True, default=f.get("flight", "d6"))
        self.charm = discord.ui.TextInput(label="Charm", required=True, default=f.get("charm", "d6"))
        for item in [self.fear, self.fight, self.flight, self.charm]:
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        garantir_ficha_kids(interaction.user.id)
        cursor.execute("""
            UPDATE fichas_kids SET fear=?, fight=?, flight=?, charm=? WHERE user_id=?
        """, (self.fear.value, self.fight.value, self.flight.value, self.charm.value, interaction.user.id))
        db.commit()
        ficha = garantir_ficha_kids(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_kids(ficha), view=KidsFichaView())


class KidsAtributosModal2(discord.ui.Modal):
    def __init__(self, ficha=None):
        super().__init__(title="🎲 Atributos 2/2 — Kids")
        f = ficha or {}
        self.grit = discord.ui.TextInput(label="Grit", required=True, default=f.get("grit", "d6"))
        self.brains = discord.ui.TextInput(label="Brains", required=True, default=f.get("brains", "d6"))
        self.brawn = discord.ui.TextInput(label="Brawn", required=True, default=f.get("brawn", "d6"))
        for item in [self.grit, self.brains, self.brawn]:
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        garantir_ficha_kids(interaction.user.id)
        cursor.execute("""
            UPDATE fichas_kids SET grit=?, brains=?, brawn=? WHERE user_id=?
        """, (self.grit.value, self.brains.value, self.brawn.value, interaction.user.id))
        db.commit()
        ficha = garantir_ficha_kids(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_kids(ficha), view=KidsFichaView())


class KidsFichaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Informações", emoji="📋", style=discord.ButtonStyle.primary)
    async def informacoes(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_kids(interaction.user.id)
        await interaction.response.send_modal(KidsInfoModal(ficha))

    @discord.ui.button(label="Atributos 1/2", emoji="🎲", style=discord.ButtonStyle.primary)
    async def atributos1(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_kids(interaction.user.id)
        await interaction.response.send_modal(KidsAtributosModal1(ficha))

    @discord.ui.button(label="Atributos 2/2", emoji="🎲", style=discord.ButtonStyle.primary)
    async def atributos2(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_kids(interaction.user.id)
        await interaction.response.send_modal(KidsAtributosModal2(ficha))

    @discord.ui.button(label="Atualizar", emoji="🔄", style=discord.ButtonStyle.success)
    async def atualizar(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_kids(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_kids(ficha), view=KidsFichaView())

    @discord.ui.button(label="Voltar", emoji="↩️", style=discord.ButtonStyle.secondary)
    async def voltar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=criar_embed_sistemas(), view=SistemasView())


class KidsSistemaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Minha Ficha", emoji="📖", style=discord.ButtonStyle.primary)
    async def ficha(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_kids(interaction.user.id)
        await interaction.response.send_message(embed=criar_embed_ficha_kids(ficha), view=KidsFichaView(), ephemeral=True)

    @discord.ui.button(label="Rolar Atributo", emoji="🎲", style=discord.ButtonStyle.success)
    async def rolar(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Select simples de atributo
        view = discord.ui.View(timeout=60)
        opcoes = [
            discord.SelectOption(label="Fear", value="fear"),
            discord.SelectOption(label="Fight", value="fight"),
            discord.SelectOption(label="Flight", value="flight"),
            discord.SelectOption(label="Charm", value="charm"),
            discord.SelectOption(label="Grit", value="grit"),
            discord.SelectOption(label="Brains", value="brains"),
            discord.SelectOption(label="Brawn", value="brawn"),
        ]
        select = discord.ui.Select(placeholder="Escolha o atributo", options=opcoes)

        async def callback(inter: discord.Interaction):
            atr = select.values[0]
            ficha = garantir_ficha_kids(inter.user.id)
            dado_str = ficha.get(atr, "d6")
            try:
                lados = int(dado_str.lower().replace("d", ""))
            except:
                lados = 6
            resultado = random.randint(1, lados)
            registrar_rolagem(inter.user.id, inter.user.display_name, f"Kids {atr}", resultado, lados)
            embed = discord.Embed(title="🎲 ROLAGEM — KIDS ON BIKES", color=discord.Color.blue())
            embed.add_field(name="Atributo", value=atr.capitalize(), inline=True)
            embed.add_field(name="Dado", value=dado_str, inline=True)
            embed.add_field(name="Resultado", value=f"**{resultado}**", inline=True)
            await inter.response.edit_message(embed=embed, view=KidsSistemaView())

        select.callback = callback
        view.add_item(select)
        await interaction.response.edit_message(content="Escolha o atributo para rolar:", embed=None, view=view)

    @discord.ui.button(label="Voltar", emoji="↩️", style=discord.ButtonStyle.secondary)
    async def voltar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=criar_embed_sistemas(), view=SistemasView())


# ==================================================
# UI — ORDEM PARANORMAL
# ==================================================

class OrdemInfoModal(discord.ui.Modal):
    def __init__(self, ficha=None):
        super().__init__(title="👁️ Informações — Ordem")
        self.nome = discord.ui.TextInput(label="Nome", required=False, max_length=100, default=(ficha or {}).get("nome", ""))
        self.jogador = discord.ui.TextInput(label="Jogador", required=False, max_length=100, default=(ficha or {}).get("jogador", ""))
        self.origem = discord.ui.TextInput(label="Origem", required=False, max_length=100, default=(ficha or {}).get("origem", ""))
        self.classe = discord.ui.TextInput(label="Classe", required=False, max_length=100, default=(ficha or {}).get("classe", ""))
        self.trilha = discord.ui.TextInput(label="Trilha", required=False, max_length=100, default=(ficha or {}).get("trilha", ""))
        for item in [self.nome, self.jogador, self.origem, self.classe, self.trilha]:
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        garantir_ficha_ordem(interaction.user.id)
        cursor.execute("""
            UPDATE fichas_ordem SET nome=?, jogador=?, origem=?, classe=?, trilha=?
            WHERE user_id=?
        """, (self.nome.value, self.jogador.value, self.origem.value, self.classe.value, self.trilha.value, interaction.user.id))
        db.commit()
        ficha = garantir_ficha_ordem(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_ordem(ficha), view=OrdemFichaView())


class OrdemAtributosModal(discord.ui.Modal):
    def __init__(self, ficha=None):
        super().__init__(title="🧠 Atributos — Ordem")
        f = ficha or {}
        self.agilidade = discord.ui.TextInput(label="Agilidade", required=True, default=str(f.get("agilidade", 1)))
        self.forca = discord.ui.TextInput(label="Força", required=True, default=str(f.get("forca", 1)))
        self.intelecto = discord.ui.TextInput(label="Intelecto", required=True, default=str(f.get("intelecto", 1)))
        self.presenca = discord.ui.TextInput(label="Presença", required=True, default=str(f.get("presenca", 1)))
        self.vigor = discord.ui.TextInput(label="Vigor", required=True, default=str(f.get("vigor", 1)))
        for item in [self.agilidade, self.forca, self.intelecto, self.presenca, self.vigor]:
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            vals = [int(self.agilidade.value), int(self.forca.value), int(self.intelecto.value),
                    int(self.presenca.value), int(self.vigor.value)]
            # Atributos podem ser 0 ou negativos (conforme regra da mesa)
            pass
        except ValueError:
            await interaction.response.send_message("❌ Atributos precisam ser números inteiros.", ephemeral=True)
            return

        garantir_ficha_ordem(interaction.user.id)
        cursor.execute("SELECT nex FROM fichas_ordem WHERE user_id=?", (interaction.user.id,))
        nex = cursor.fetchone()[0]

        max_pontos = pontos_atributo_ordem(nex)
        total = sum(vals)

        if total > max_pontos:
            await interaction.response.send_message(
                f"❌ Você só tem **{max_pontos}** pontos de atributo no NEX {nex}%.\n"
                f"Você tentou usar **{total}** pontos.\n\n"
                f"Pontos ganhos em: 20%, 50%, 80% e 90%.",
                ephemeral=True
            )
            return

        cursor.execute("""
            UPDATE fichas_ordem SET agilidade=?, forca=?, intelecto=?, presenca=?, vigor=?
            WHERE user_id=?
        """, (*vals, interaction.user.id))

        pv_max, pe_max, san_max = calcular_recursos_ordem(nex, vals[4], vals[3])
        cursor.execute("""
            UPDATE fichas_ordem SET
                pv_max=?, pv=MIN(pv, ?),
                pe_max=?, pe=MIN(pe, ?),
                san_max=?, san=MIN(san, ?)
            WHERE user_id=?
        """, (pv_max, pv_max, pe_max, pe_max, san_max, san_max, interaction.user.id))
        db.commit()
        ficha = garantir_ficha_ordem(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_ordem(ficha), view=OrdemFichaView())


class OrdemBonusPericiaModal(discord.ui.Modal):
    def __init__(self, pericia):
        super().__init__(title=f"🎯 {pericia}")
        self.pericia = pericia
        self.bonus = discord.ui.TextInput(label="Bônus da perícia", placeholder="0", required=True)
        self.add_item(self.bonus)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            bonus = int(self.bonus.value)
        except ValueError:
            await interaction.response.send_message("❌ O bônus precisa ser um número.", ephemeral=True)
            return
        ficha = garantir_ficha_ordem(interaction.user.id)
        ficha["pericias"][self.pericia] = bonus
        cursor.execute("UPDATE fichas_ordem SET pericias=? WHERE user_id=?",
                       (json.dumps(ficha["pericias"], ensure_ascii=False), interaction.user.id))
        db.commit()
        ficha = garantir_ficha_ordem(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_ordem(ficha), view=OrdemFichaView())


class OrdemPericiaSelect(discord.ui.Select):
    def __init__(self, page=0):
        self.page = page
        start = page * 25
        end = start + 25
        opcoes = [discord.SelectOption(label=p, value=p) for p in ORDEM_PERICIAS[start:end]]
        super().__init__(placeholder=f"🎯 Perícias (página {page+1})", options=opcoes)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(OrdemBonusPericiaModal(self.values[0]))


class OrdemPericiasView(discord.ui.View):
    def __init__(self, page=0):
        super().__init__(timeout=180)
        self.page = page
        self.add_item(OrdemPericiaSelect(page))
        if page > 0:
            self.add_item(OrdemPericiaPageButton("⬅️ Anterior", page - 1))
        if (page + 1) * 25 < len(ORDEM_PERICIAS):
            self.add_item(OrdemPericiaPageButton("Próxima ➡️", page + 1))


class OrdemPericiaPageButton(discord.ui.Button):
    def __init__(self, label, page):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.page = page

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=OrdemPericiasView(self.page))


class OrdemRolarSelect(discord.ui.Select):
    def __init__(self, page=0):
        self.page = page
        start = page * 25
        end = start + 25
        opcoes = [discord.SelectOption(label=p, value=p) for p in ORDEM_PERICIAS[start:end]]
        super().__init__(placeholder=f"🎲 Rolar perícia (pág. {page+1})", options=opcoes)

    async def callback(self, interaction: discord.Interaction):
        pericia = self.values[0]
        ficha = garantir_ficha_ordem(interaction.user.id)
        atributo_nome = ORDEM_PERICIA_ATRIBUTO[pericia]
        atributo = ficha[atributo_nome]
        bonus = ficha["pericias"].get(pericia, 0)
        d20 = random.randint(1, 20)
        resultado = d20 + atributo + bonus
        registrar_rolagem(interaction.user.id, interaction.user.display_name, f"Ordem: {pericia}", resultado, d20)
        embed = discord.Embed(title="🎲 ROLAGEM — ORDEM PARANORMAL", color=discord.Color.dark_red())
        embed.add_field(name="Perícia", value=pericia, inline=True)
        embed.add_field(name="D20", value=str(d20), inline=True)
        embed.add_field(name="Resultado", value=f"**{resultado}**", inline=True)
        embed.add_field(name="Cálculo", value=f"`{d20} + {atributo} (atr) + {bonus} (per) = {resultado}`", inline=False)
        await interaction.response.edit_message(embed=embed, view=OrdemSistemaView())


class OrdemRolagemView(discord.ui.View):
    def __init__(self, page=0):
        super().__init__(timeout=180)
        self.add_item(OrdemRolarSelect(page))
        if page > 0:
            self.add_item(OrdemRolarPageButton("⬅️", page - 1))
        if (page + 1) * 25 < len(ORDEM_PERICIAS):
            self.add_item(OrdemRolarPageButton("➡️", page + 1))


class OrdemRolarPageButton(discord.ui.Button):
    def __init__(self, label, page):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.page = page

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=OrdemRolagemView(self.page))


class OrdemNexModal(discord.ui.Modal):
    def __init__(self, ficha=None):
        super().__init__(title="📈 NEX — Ordem")
        f = ficha or {}
        self.nex = discord.ui.TextInput(
            label="NEX (%)",
            placeholder="Ex: 5, 20, 50, 80, 90...",
            required=True,
            default=str(f.get("nex", 5))
        )
        self.add_item(self.nex)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            nex = int(self.nex.value)
            if nex < 5 or nex > 99:
                raise ValueError
        except ValueError:
            await interaction.response.send_message("❌ NEX precisa ser um número entre 5 e 99.", ephemeral=True)
            return

        garantir_ficha_ordem(interaction.user.id)
        cursor.execute("UPDATE fichas_ordem SET nex=? WHERE user_id=?", (nex, interaction.user.id))

        # Recalcular recursos
        cursor.execute("SELECT vigor, presenca FROM fichas_ordem WHERE user_id=?", (interaction.user.id,))
        vigor, presenca = cursor.fetchone()
        pv_max, pe_max, san_max = calcular_recursos_ordem(nex, vigor, presenca)
        cursor.execute("""
            UPDATE fichas_ordem SET
                pv_max=?, pv=MIN(pv, ?),
                pe_max=?, pe=MIN(pe, ?),
                san_max=?, san=MIN(san, ?)
            WHERE user_id=?
        """, (pv_max, pv_max, pe_max, pe_max, san_max, san_max, interaction.user.id))
        db.commit()

        ficha = garantir_ficha_ordem(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_ordem(ficha), view=OrdemFichaView())


class OrdemFichaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Informações", emoji="📋", style=discord.ButtonStyle.primary)
    async def informacoes(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_ordem(interaction.user.id)
        await interaction.response.send_modal(OrdemInfoModal(ficha))

    @discord.ui.button(label="Atributos", emoji="🧠", style=discord.ButtonStyle.primary)
    async def atributos(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_ordem(interaction.user.id)
        await interaction.response.send_modal(OrdemAtributosModal(ficha))

    @discord.ui.button(label="NEX", emoji="📈", style=discord.ButtonStyle.primary)
    async def nex(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_ordem(interaction.user.id)
        await interaction.response.send_modal(OrdemNexModal(ficha))

    @discord.ui.button(label="Perícias", emoji="🎯", style=discord.ButtonStyle.secondary)
    async def pericias(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Escolha a perícia:", embed=None, view=OrdemPericiasView())

    @discord.ui.button(label="Atualizar", emoji="🔄", style=discord.ButtonStyle.success)
    async def atualizar(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_ordem(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_ordem(ficha), view=OrdemFichaView())

    @discord.ui.button(label="Voltar", emoji="↩️", style=discord.ButtonStyle.secondary)
    async def voltar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=criar_embed_sistemas(), view=SistemasView())


class OrdemSistemaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Minha Ficha", emoji="📖", style=discord.ButtonStyle.primary)
    async def ficha(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_ordem(interaction.user.id)
        await interaction.response.send_message(embed=criar_embed_ficha_ordem(ficha), view=OrdemFichaView(), ephemeral=True)

    @discord.ui.button(label="Rolar Perícia", emoji="🎲", style=discord.ButtonStyle.success)
    async def rolar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="🎯 Escolha uma perícia:", embed=None, view=OrdemRolagemView())

    @discord.ui.button(label="Voltar", emoji="↩️", style=discord.ButtonStyle.secondary)
    async def voltar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=criar_embed_sistemas(), view=SistemasView())


# ==================================================
# UI — D&D
# ==================================================

class DndInfoModal(discord.ui.Modal):
    def __init__(self, ficha=None):
        super().__init__(title="🐉 Informações — D&D")
        f = ficha or {}
        self.nome = discord.ui.TextInput(label="Nome", required=False, max_length=100, default=f.get("nome", ""))
        self.classe = discord.ui.TextInput(label="Classe", required=False, max_length=100, default=f.get("classe", ""))
        self.raca = discord.ui.TextInput(label="Raça", required=False, max_length=100, default=f.get("raca", ""))
        self.nivel = discord.ui.TextInput(label="Nível", required=False, default=str(f.get("nivel", 1)))
        for item in [self.nome, self.classe, self.raca, self.nivel]:
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            nivel = int(self.nivel.value or 1)
        except:
            nivel = 1
        garantir_ficha_dnd(interaction.user.id)
        cursor.execute("""
            UPDATE fichas_dnd SET nome=?, classe=?, raca=?, nivel=? WHERE user_id=?
        """, (self.nome.value, self.classe.value, self.raca.value, nivel, interaction.user.id))
        db.commit()
        ficha = garantir_ficha_dnd(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_dnd(ficha), view=DndFichaView())


class DndAtributosModal(discord.ui.Modal):
    def __init__(self, ficha=None):
        super().__init__(title="🧠 Atributos — D&D")
        f = ficha or {}
        self.str_ = discord.ui.TextInput(label="Strength", required=True, default=str(f.get("strength", 10)))
        self.dex = discord.ui.TextInput(label="Dexterity", required=True, default=str(f.get("dexterity", 10)))
        self.con = discord.ui.TextInput(label="Constitution", required=True, default=str(f.get("constitution", 10)))
        self.int_ = discord.ui.TextInput(label="Intelligence", required=True, default=str(f.get("intelligence", 10)))
        self.wis = discord.ui.TextInput(label="Wisdom", required=True, default=str(f.get("wisdom", 10)))
        self.cha = discord.ui.TextInput(label="Charisma", required=True, default=str(f.get("charisma", 10)))
        for item in [self.str_, self.dex, self.con, self.int_, self.wis, self.cha]:
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            vals = [int(x.value) for x in [self.str_, self.dex, self.con, self.int_, self.wis, self.cha]]
        except ValueError:
            await interaction.response.send_message("❌ Atributos precisam ser números.", ephemeral=True)
            return
        garantir_ficha_dnd(interaction.user.id)
        cursor.execute("""
            UPDATE fichas_dnd SET strength=?, dexterity=?, constitution=?, intelligence=?, wisdom=?, charisma=?
            WHERE user_id=?
        """, (*vals, interaction.user.id))
        db.commit()
        ficha = garantir_ficha_dnd(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_dnd(ficha), view=DndFichaView())


class DndSkillSelect(discord.ui.Select):
    def __init__(self):
        opcoes = [discord.SelectOption(label=s, value=s) for s in list(DND_SKILLS.keys())[:25]]
        super().__init__(placeholder="🎯 Escolha uma skill", options=opcoes)

    async def callback(self, interaction: discord.Interaction):
        skill = self.values[0]
        ficha = garantir_ficha_dnd(interaction.user.id)
        atual = ficha["skills"].get(skill, 0)
        ficha["skills"][skill] = 0 if atual else 1
        cursor.execute("UPDATE fichas_dnd SET skills=? WHERE user_id=?",
                       (json.dumps(ficha["skills"], ensure_ascii=False), interaction.user.id))
        db.commit()
        ficha = garantir_ficha_dnd(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_dnd(ficha), view=DndFichaView())


class DndSkillsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(DndSkillSelect())


class DndRolarSelect(discord.ui.Select):
    def __init__(self):
        opcoes = [discord.SelectOption(label=s, value=s) for s in list(DND_SKILLS.keys())[:25]]
        super().__init__(placeholder="🎲 Rolar skill", options=opcoes)

    async def callback(self, interaction: discord.Interaction):
        skill = self.values[0]
        ficha = garantir_ficha_dnd(interaction.user.id)
        atr_nome = DND_SKILLS[skill]
        atr = ficha[atr_nome]
        mod = mod_atributo(atr)
        trained = ficha["skills"].get(skill, 0)
        prof = ficha["proficiency"] if trained else 0
        d20 = random.randint(1, 20)
        resultado = d20 + mod + prof
        registrar_rolagem(interaction.user.id, interaction.user.display_name, f"D&D: {skill}", resultado, d20)
        embed = discord.Embed(title="🎲 ROLAGEM — D&D 5e", color=discord.Color.dark_green())
        embed.add_field(name="Skill", value=skill, inline=True)
        embed.add_field(name="D20", value=str(d20), inline=True)
        embed.add_field(name="Resultado", value=f"**{resultado}**", inline=True)
        embed.add_field(name="Cálculo", value=f"`{d20} + {mod} (mod) + {prof} (prof) = {resultado}`", inline=False)
        await interaction.response.edit_message(embed=embed, view=DndSistemaView())


class DndRolagemView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(DndRolarSelect())


class DndFichaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Informações", emoji="📋", style=discord.ButtonStyle.primary)
    async def informacoes(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_dnd(interaction.user.id)
        await interaction.response.send_modal(DndInfoModal(ficha))

    @discord.ui.button(label="Atributos", emoji="🧠", style=discord.ButtonStyle.primary)
    async def atributos(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_dnd(interaction.user.id)
        await interaction.response.send_modal(DndAtributosModal(ficha))

    @discord.ui.button(label="Skills", emoji="🎯", style=discord.ButtonStyle.secondary)
    async def skills(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Clique na skill para marcar/desmarcar como treinada:", embed=None, view=DndSkillsView())

    @discord.ui.button(label="Atualizar", emoji="🔄", style=discord.ButtonStyle.success)
    async def atualizar(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_dnd(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_dnd(ficha), view=DndFichaView())

    @discord.ui.button(label="Voltar", emoji="↩️", style=discord.ButtonStyle.secondary)
    async def voltar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=criar_embed_sistemas(), view=SistemasView())


class DndSistemaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Minha Ficha", emoji="📖", style=discord.ButtonStyle.primary)
    async def ficha(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_dnd(interaction.user.id)
        await interaction.response.send_message(embed=criar_embed_ficha_dnd(ficha), view=DndFichaView(), ephemeral=True)

    @discord.ui.button(label="Rolar Skill", emoji="🎲", style=discord.ButtonStyle.success)
    async def rolar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="🎲 Escolha uma skill:", embed=None, view=DndRolagemView())

    @discord.ui.button(label="Voltar", emoji="↩️", style=discord.ButtonStyle.secondary)
    async def voltar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=criar_embed_sistemas(), view=SistemasView())


# ==================================================
# UI — PATHFINDER
# ==================================================

class PfInfoModal(discord.ui.Modal):
    def __init__(self, ficha=None):
        super().__init__(title="⚔️ Informações — Pathfinder")
        f = ficha or {}
        self.nome = discord.ui.TextInput(label="Nome", required=False, max_length=100, default=f.get("nome", ""))
        self.classe = discord.ui.TextInput(label="Classe", required=False, max_length=100, default=f.get("classe", ""))
        self.ancestria = discord.ui.TextInput(label="Ancestria", required=False, max_length=100, default=f.get("ancestria", ""))
        self.nivel = discord.ui.TextInput(label="Nível", required=False, default=str(f.get("nivel", 1)))
        for item in [self.nome, self.classe, self.ancestria, self.nivel]:
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            nivel = int(self.nivel.value or 1)
        except:
            nivel = 1
        garantir_ficha_pathfinder(interaction.user.id)
        cursor.execute("""
            UPDATE fichas_pathfinder SET nome=?, classe=?, ancestria=?, nivel=? WHERE user_id=?
        """, (self.nome.value, self.classe.value, self.ancestria.value, nivel, interaction.user.id))
        db.commit()
        ficha = garantir_ficha_pathfinder(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_pathfinder(ficha), view=PfFichaView())


class PfAtributosModal(discord.ui.Modal):
    def __init__(self, ficha=None):
        super().__init__(title="🧠 Atributos — Pathfinder")
        f = ficha or {}
        self.str_ = discord.ui.TextInput(label="Strength", required=True, default=str(f.get("strength", 10)))
        self.dex = discord.ui.TextInput(label="Dexterity", required=True, default=str(f.get("dexterity", 10)))
        self.con = discord.ui.TextInput(label="Constitution", required=True, default=str(f.get("constitution", 10)))
        self.int_ = discord.ui.TextInput(label="Intelligence", required=True, default=str(f.get("intelligence", 10)))
        self.wis = discord.ui.TextInput(label="Wisdom", required=True, default=str(f.get("wisdom", 10)))
        self.cha = discord.ui.TextInput(label="Charisma", required=True, default=str(f.get("charisma", 10)))
        for item in [self.str_, self.dex, self.con, self.int_, self.wis, self.cha]:
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            vals = [int(x.value) for x in [self.str_, self.dex, self.con, self.int_, self.wis, self.cha]]
        except ValueError:
            await interaction.response.send_message("❌ Atributos precisam ser números.", ephemeral=True)
            return
        garantir_ficha_pathfinder(interaction.user.id)
        cursor.execute("""
            UPDATE fichas_pathfinder SET strength=?, dexterity=?, constitution=?, intelligence=?, wisdom=?, charisma=?
            WHERE user_id=?
        """, (*vals, interaction.user.id))
        db.commit()
        ficha = garantir_ficha_pathfinder(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_pathfinder(ficha), view=PfFichaView())


class PfSkillSelect(discord.ui.Select):
    def __init__(self):
        opcoes = [discord.SelectOption(label=s, value=s) for s in PF_SKILLS]
        super().__init__(placeholder="🎯 Escolha uma skill", options=opcoes)

    async def callback(self, interaction: discord.Interaction):
        skill = self.values[0]
        ficha = garantir_ficha_pathfinder(interaction.user.id)
        atual = ficha["skills"].get(skill, 0)
        ficha["skills"][skill] = 0 if atual else 1
        cursor.execute("UPDATE fichas_pathfinder SET skills=? WHERE user_id=?",
                       (json.dumps(ficha["skills"], ensure_ascii=False), interaction.user.id))
        db.commit()
        ficha = garantir_ficha_pathfinder(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_pathfinder(ficha), view=PfFichaView())


class PfSkillsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(PfSkillSelect())


class PfRolarSelect(discord.ui.Select):
    def __init__(self):
        opcoes = [discord.SelectOption(label=s, value=s) for s in PF_SKILLS]
        super().__init__(placeholder="🎲 Rolar skill", options=opcoes)

    async def callback(self, interaction: discord.Interaction):
        skill = self.values[0]
        ficha = garantir_ficha_pathfinder(interaction.user.id)
        # Pathfinder simplificado: usa o modificador do atributo mais próximo + proficiência se trained
        # Mapeamento simples
        atr_map = {
            "Acrobatics": "dexterity", "Athletics": "strength", "Stealth": "dexterity",
            "Thievery": "dexterity", "Arcana": "intelligence", "Crafting": "intelligence",
            "Occultism": "intelligence", "Society": "intelligence", "Nature": "wisdom",
            "Medicine": "wisdom", "Religion": "wisdom", "Survival": "wisdom",
            "Deception": "charisma", "Diplomacy": "charisma", "Intimidation": "charisma",
            "Performance": "charisma"
        }
        atr_nome = atr_map.get(skill, "intelligence")
        atr = ficha[atr_nome]
        mod = mod_atributo(atr)
        trained = ficha["skills"].get(skill, 0)
        prof = ficha["proficiency"] if trained else 0
        d20 = random.randint(1, 20)
        resultado = d20 + mod + prof
        registrar_rolagem(interaction.user.id, interaction.user.display_name, f"PF: {skill}", resultado, d20)
        embed = discord.Embed(title="🎲 ROLAGEM — PATHFINDER", color=discord.Color.dark_gold())
        embed.add_field(name="Skill", value=skill, inline=True)
        embed.add_field(name="D20", value=str(d20), inline=True)
        embed.add_field(name="Resultado", value=f"**{resultado}**", inline=True)
        embed.add_field(name="Cálculo", value=f"`{d20} + {mod} (mod) + {prof} (prof) = {resultado}`", inline=False)
        await interaction.response.edit_message(embed=embed, view=PfSistemaView())


class PfRolagemView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(PfRolarSelect())


class PfFichaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Informações", emoji="📋", style=discord.ButtonStyle.primary)
    async def informacoes(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_pathfinder(interaction.user.id)
        await interaction.response.send_modal(PfInfoModal(ficha))

    @discord.ui.button(label="Atributos", emoji="🧠", style=discord.ButtonStyle.primary)
    async def atributos(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_pathfinder(interaction.user.id)
        await interaction.response.send_modal(PfAtributosModal(ficha))

    @discord.ui.button(label="Skills", emoji="🎯", style=discord.ButtonStyle.secondary)
    async def skills(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Clique na skill para marcar/desmarcar:", embed=None, view=PfSkillsView())

    @discord.ui.button(label="Atualizar", emoji="🔄", style=discord.ButtonStyle.success)
    async def atualizar(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_pathfinder(interaction.user.id)
        await interaction.response.edit_message(embed=criar_embed_ficha_pathfinder(ficha), view=PfFichaView())

    @discord.ui.button(label="Voltar", emoji="↩️", style=discord.ButtonStyle.secondary)
    async def voltar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=criar_embed_sistemas(), view=SistemasView())


class PfSistemaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Minha Ficha", emoji="📖", style=discord.ButtonStyle.primary)
    async def ficha(self, interaction: discord.Interaction, button: discord.ui.Button):
        ficha = garantir_ficha_pathfinder(interaction.user.id)
        await interaction.response.send_message(embed=criar_embed_ficha_pathfinder(ficha), view=PfFichaView(), ephemeral=True)

    @discord.ui.button(label="Rolar Skill", emoji="🎲", style=discord.ButtonStyle.success)
    async def rolar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="🎲 Escolha uma skill:", embed=None, view=PfRolagemView())

    @discord.ui.button(label="Voltar", emoji="↩️", style=discord.ButtonStyle.secondary)
    async def voltar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=criar_embed_sistemas(), view=SistemasView())


# ==================================================
# SISTEMAS
# ==================================================

class SistemasView(discord.ui.View):

    def __init__(self):
        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Tavelada",
        emoji="📜",
        style=discord.ButtonStyle.primary
    )
    async def tavelada(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        embed = discord.Embed(
            title="📜 TAVELADA",
            description=(
                "Sistema próprio da mesa.\n\n"
                "Escolha uma ferramenta do sistema."
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="🎲 Sistema",
            value="D7 + atributos + perícias.",
            inline=False
        )

        embed.add_field(
            name="⚔️ Combate",
            value="Iniciativa, turnos e NPCs.",
            inline=False
        )

        await interaction.response.edit_message(
            embed=embed,
            view=TaveladaSistemaView()
        )

    @discord.ui.button(
        label="Ordem Paranormal",
        emoji="👁️",
        style=discord.ButtonStyle.danger
    )
    async def ordem(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="👁️ ORDEM PARANORMAL",
                description=(
                    "Sistema de investigação paranormal.\n\n"
                    "Use os botões abaixo para acessar sua ficha "
                    "e realizar testes."
                ),
                color=discord.Color.dark_red()
            ),
            view=OrdemSistemaView()
        )

    @discord.ui.button(
        label="D&D",
        emoji="🐉",
        style=discord.ButtonStyle.success
    )
    async def dnd(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="🐉 D&D 5e",
                description=(
                    "Sistema de fantasia clássica.\n\n"
                    "Acesse sua ficha e faça rolagens de skill."
                ),
                color=discord.Color.dark_green()
            ),
            view=DndSistemaView()
        )

    @discord.ui.button(
        label="Pathfinder",
        emoji="⚔️",
        style=discord.ButtonStyle.primary
    )
    async def pathfinder(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="⚔️ PATHFINDER",
                description=(
                    "Sistema de fantasia tática.\n\n"
                    "Acesse sua ficha e faça rolagens de skill."
                ),
                color=discord.Color.dark_gold()
            ),
            view=PfSistemaView()
        )

    @discord.ui.button(
        label="Brutal",
        emoji="🔪",
        style=discord.ButtonStyle.danger
    )
    async def brutal(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="🔪 BRUTAL",
                description="Sistema de slasher.\n\nSobreviva a monstros e assassinos.",
                color=discord.Color.dark_red()
            ),
            view=BrutalSistemaView()
        )

    @discord.ui.button(
        label="Kids on Bikes",
        emoji="🚲",
        style=discord.ButtonStyle.primary
    )
    async def kids(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="🚲 KIDS ON BIKES",
                description="Aventuras e mistérios com crianças e adolescentes.",
                color=discord.Color.blue()
            ),
            view=KidsSistemaView()
        )

    @discord.ui.button(
        label="Voltar",
        emoji="↩️",
        style=discord.ButtonStyle.secondary
    )
    async def voltar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            embed=criar_embed_painel_principal(),
            view=PainelPrincipal()
        )


# ==================================================
# SISTEMA TAVELADA
# ==================================================

class TaveladaSistemaView(discord.ui.View):

    def __init__(self):
        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Minha Ficha",
        emoji="👤",
        style=discord.ButtonStyle.primary
    )
    async def ficha(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await mostrar_ficha(
            interaction
        )

    @discord.ui.button(
        label="Iniciativa",
        emoji="⚔️",
        style=discord.ButtonStyle.success
    )
    async def iniciativa(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if eh_pesquisador(interaction):
            view = CombateMestreView()
        else:
            view = CombateView()

        await interaction.response.send_message(
            embed=criar_embed_combate(),
            view=view,
            ephemeral=True
        )

    @discord.ui.button(
        label="Rolar D7",
        emoji="🎲",
        style=discord.ButtonStyle.secondary
    )
    async def rolar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        resultado = random.randint(1, 7)

        registrar_rolagem(
            interaction.user.id,
            interaction.user.display_name,
            "D7",
            resultado,
            7
        )

        await interaction.response.send_message(
            f"🎲 **{interaction.user.display_name}** rolou um D7!\n\n"
            f"Resultado: **{resultado}**"
        )

    @discord.ui.button(
        label="Voltar",
        emoji="↩️",
        style=discord.ButtonStyle.secondary
    )
    async def voltar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            embed=criar_embed_sistemas(),
            view=SistemasView()
        )


# ==================================================
# FICHAS — SELEÇÃO DE SISTEMA
# ==================================================

class FichasView(discord.ui.View):

    def __init__(self):
        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Tavelada",
        emoji="📜",
        style=discord.ButtonStyle.primary
    )
    async def tavelada(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await mostrar_ficha(
            interaction
        )

    @discord.ui.button(
        label="Ordem Paranormal",
        emoji="👁️",
        style=discord.ButtonStyle.danger
    )
    async def ordem(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        ficha = garantir_ficha_ordem(interaction.user.id)
        await interaction.response.send_message(
            embed=criar_embed_ficha_ordem(ficha),
            view=OrdemFichaView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="D&D",
        emoji="🐉",
        style=discord.ButtonStyle.success
    )
    async def dnd(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        ficha = garantir_ficha_dnd(interaction.user.id)
        await interaction.response.send_message(
            embed=criar_embed_ficha_dnd(ficha),
            view=DndFichaView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Pathfinder",
        emoji="⚔️",
        style=discord.ButtonStyle.primary
    )
    async def pathfinder(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        ficha = garantir_ficha_pathfinder(interaction.user.id)
        await interaction.response.send_message(
            embed=criar_embed_ficha_pathfinder(ficha),
            view=PfFichaView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Brutal",
        emoji="🔪",
        style=discord.ButtonStyle.danger
    )
    async def brutal(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        ficha = garantir_ficha_brutal(interaction.user.id)
        await interaction.response.send_message(
            embed=criar_embed_ficha_brutal(ficha),
            view=BrutalFichaView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Kids on Bikes",
        emoji="🚲",
        style=discord.ButtonStyle.primary
    )
    async def kids(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        ficha = garantir_ficha_kids(interaction.user.id)
        await interaction.response.send_message(
            embed=criar_embed_ficha_kids(ficha),
            view=KidsFichaView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Voltar",
        emoji="↩️",
        style=discord.ButtonStyle.secondary
    )
    async def voltar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            embed=criar_embed_painel_principal(),
            view=PainelPrincipal()
        )


# ==================================================
# ROLAGENS
# ==================================================

class RolagensView(discord.ui.View):

    def __init__(self):
        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Rolar D7",
        emoji="🎲",
        style=discord.ButtonStyle.primary
    )
    async def d7(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        resultado = random.randint(1, 7)

        registrar_rolagem(
            interaction.user.id,
            interaction.user.display_name,
            "D7",
            resultado,
            7
        )

        await interaction.response.send_message(
            f"🎲 **{interaction.user.display_name}** rolou D7!\n\n"
            f"Resultado: **{resultado}**"
        )

    @discord.ui.button(
        label="Histórico",
        emoji="📜",
        style=discord.ButtonStyle.secondary
    )
    async def historico(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        cursor.execute(
            """
            SELECT tipo, resultado, dado, data
            FROM historico_rolagens
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 15
            """,
            (interaction.user.id,)
        )

        rolagens = cursor.fetchall()

        if not rolagens:
            await interaction.response.send_message(
                "📜 Você ainda não possui rolagens no histórico.",
                ephemeral=True
            )
            return

        texto = ""

        for tipo, resultado, dado, data in rolagens:
            texto += (
                f"🎲 **{tipo}** → `{resultado}` "
                f"(D{dado})\n"
            )

        embed = discord.Embed(
            title="📜 HISTÓRICO DE ROLAGENS",
            description=texto,
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    @discord.ui.button(
        label="Voltar",
        emoji="↩️",
        style=discord.ButtonStyle.secondary
    )
    async def voltar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            embed=criar_embed_painel_principal(),
            view=PainelPrincipal()
        )


# ==================================================
# VIEWS DE DESENVOLVIMENTO
# ==================================================

def criar_embed_sistema_desenvolvimento(
    titulo,
    descricao
):
    return discord.Embed(
        title=titulo,
        description=(
            f"{descricao}\n\n"
            "🛠️ O sistema será integrado futuramente "
            "sem afetar as ferramentas já existentes."
        ),
        color=discord.Color.dark_grey()
    )


class SistemaEmDesenvolvimentoView(discord.ui.View):

    def __init__(self):
        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Voltar aos Sistemas",
        emoji="↩️",
        style=discord.ButtonStyle.primary
    )
    async def voltar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            embed=criar_embed_sistemas(),
            view=SistemasView()
        )


class FichaEmDesenvolvimentoView(discord.ui.View):

    def __init__(self):
        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Voltar às Fichas",
        emoji="↩️",
        style=discord.ButtonStyle.primary
    )
    async def voltar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            embed=criar_embed_fichas(),
            view=FichasView()
        )


# ==================================================
# EMBEDS DO PAINEL
# ==================================================

def criar_embed_painel_principal():
    embed = discord.Embed(
        title="🎲 TAVELADA RPG",
        description=(
            "Central de ferramentas da mesa.\n\n"
            "Escolha uma categoria:"
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="📚 Sistemas",
        value=(
            "Escolha e acesse os sistemas "
            "disponíveis no Tavelada."
        ),
        inline=False
    )

    embed.add_field(
        name="📖 Fichas",
        value=(
            "Crie e gerencie fichas "
            "de personagem."
        ),
        inline=False
    )

    embed.add_field(
        name="⚔️ Combate",
        value=(
            "Veja a iniciativa e o "
            "combate atual."
        ),
        inline=False
    )

    embed.add_field(
        name="🎲 Rolagens",
        value=(
            "Faça rolagens e consulte "
            "seu histórico."
        ),
        inline=False
    )

    embed.add_field(
        name="🛡️ Mestre",
        value=(
            "Ferramentas exclusivas "
            "dos Pesquisadores."
        ),
        inline=False
    )

    embed.set_footer(
        text="Tavelada RPG • Painel Principal"
    )

    return embed


def criar_embed_sistemas():
    embed = discord.Embed(
        title="📚 SISTEMAS",
        description=(
            "Escolha o sistema que deseja acessar."
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="📜 Tavelada",
        value="Sistema próprio da mesa.",
        inline=False
    )

    embed.add_field(
        name="👁️ Ordem Paranormal",
        value="Integração em desenvolvimento.",
        inline=False
    )

    embed.add_field(
        name="🐉 D&D",
        value="Integração em desenvolvimento.",
        inline=False
    )

    embed.add_field(
        name="⚔️ Pathfinder",
        value="Integração em desenvolvimento.",
        inline=False
    )

    return embed


def criar_embed_fichas():
    return discord.Embed(
        title="📖 FICHAS",
        description=(
            "Escolha o sistema da ficha que deseja acessar."
        ),
        color=discord.Color.blurple()
    )


# ==================================================
# PAINEL PRINCIPAL NOVO
# ==================================================

class PainelPrincipal(discord.ui.View):

    def __init__(self):
        super().__init__(
            timeout=None
        )

    @discord.ui.button(
        label="Sistemas",
        emoji="📚",
        style=discord.ButtonStyle.primary
    )
    async def sistemas(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            embed=criar_embed_sistemas(),
            view=SistemasView()
        )

    @discord.ui.button(
        label="Fichas",
        emoji="📖",
        style=discord.ButtonStyle.primary
    )
    async def fichas(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            embed=criar_embed_fichas(),
            view=FichasView()
        )

    @discord.ui.button(
        label="Combate",
        emoji="⚔️",
        style=discord.ButtonStyle.success
    )
    async def combate(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if eh_pesquisador(interaction):
            view = CombateMestreView()
        else:
            view = CombateView()

        await interaction.response.send_message(
            embed=criar_embed_combate(),
            view=view,
            ephemeral=True
        )

    @discord.ui.button(
        label="Rolagens",
        emoji="🎲",
        style=discord.ButtonStyle.secondary
    )
    async def rolagens(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        embed = discord.Embed(
            title="🎲 ROLAGENS",
            description=(
                "Escolha uma ferramenta de rolagem."
            ),
            color=discord.Color.blurple()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=RolagensView()
        )

    @discord.ui.button(
        label="Mestre",
        emoji="🛡️",
        style=discord.ButtonStyle.danger
    )
    async def mestre(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if not eh_pesquisador(interaction):
            await interaction.response.send_message(
                "🔒 **Acesso negado.**\n"
                "Somente Pesquisadores podem utilizar "
                "o Escudo do Mestre.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🛡️ ESCUDO DO MESTRE",
            description=(
                "Área privada dos Pesquisadores.\n\n"
                "Aqui ficam as ferramentas da mesa."
            ),
            color=discord.Color.dark_red()
        )

        await interaction.response.send_message(
            embed=embed,
            view=EscudoMestre(),
            ephemeral=True
        )


# ==================================================
# /PAINEL
# ==================================================

@tree.command(
    name="painel",
    description="Abre o painel do Tavelada.",
    guild=GUILD
)
async def painel(interaction: discord.Interaction):
    try:
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send(
            embed=criar_embed_painel_principal(),
            view=PainelPrincipal()
        )
    except Exception as e:
        try:
            await interaction.followup.send(
                f"❌ Erro ao abrir o painel: {e}",
                ephemeral=True
            )
        except:
            print(f"Erro no /painel: {e}")


# ==================================================
# /MESTRE
# ==================================================

@tree.command(
    name="mestre",
    description="Abre o Escudo do Mestre.",
    guild=GUILD
)
async def mestre(
    interaction: discord.Interaction
):
    if not eh_pesquisador(interaction):
        await interaction.response.send_message(
            "🔒 **Acesso negado.**\n"
            "Somente Pesquisadores podem utilizar "
            "o Escudo do Mestre.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="🛡️ ESCUDO DO MESTRE",
        description=(
            "Área privada dos Pesquisadores.\n\n"
            "Aqui ficam as ferramentas da mesa."
        ),
        color=discord.Color.dark_red()
    )

    await interaction.response.send_message(
        embed=embed,
        view=EscudoMestre(),
        ephemeral=True
    )


# ==================================================
# /D7
# ==================================================

@tree.command(
    name="d7",
    description="Rola um dado de 7 lados.",
    guild=GUILD
)
async def d7(
    interaction: discord.Interaction
):
    resultado = random.randint(1, 7)

    registrar_rolagem(
        interaction.user.id,
        interaction.user.display_name,
        "D7",
        resultado,
        7
    )

    await interaction.response.send_message(
        f"🎲 **{interaction.user.display_name}** rolou D7!\n"
        f"Resultado: **{resultado}**"
    )


# ==================================================
# /HISTORICO
# ==================================================

@tree.command(
    name="historico",
    description="Mostra seu histórico de rolagens.",
    guild=GUILD
)
async def historico(
    interaction: discord.Interaction
):
    cursor.execute(
        """
        SELECT tipo, resultado, dado, data
        FROM historico_rolagens
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 15
        """,
        (interaction.user.id,)
    )

    rolagens = cursor.fetchall()

    if not rolagens:
        await interaction.response.send_message(
            "📜 Você ainda não possui rolagens no histórico.",
            ephemeral=True
        )
        return

    texto = ""

    for tipo, resultado, dado, data in rolagens:
        texto += (
            f"🎲 **{tipo}** → `{resultado}` "
            f"(D{dado})\n"
        )

    embed = discord.Embed(
        title="📜 HISTÓRICO DE ROLAGENS",
        description=texto,
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )


# ==================================================
# /DARXP
# ==================================================

@tree.command(
    name="darxp",
    description="Dá XP para um jogador.",
    guild=GUILD
)
@app_commands.describe(
    jogador="Jogador que receberá XP",
    quantidade="Quantidade de XP"
)
async def darxp(
    interaction: discord.Interaction,
    jogador: discord.Member,
    quantidade: int
):
    if not eh_pesquisador(interaction):
        await interaction.response.send_message(
            "🔒 Apenas Pesquisadores podem dar XP.",
            ephemeral=True
        )
        return

    if quantidade <= 0:
        await interaction.response.send_message(
            "❌ A quantidade de XP precisa ser maior que zero.",
            ephemeral=True
        )
        return

    (
        nivel,
        nivel_antigo,
        subiu
    ) = adicionar_xp(
        jogador.id,
        quantidade
    )

    ficha_depois = buscar_ficha_dict(
        jogador.id
    )

    xp_atual = ficha_depois["xp"]

    mensagem = (
        f"⭐ **XP concedido!**\n\n"
        f"👤 Jogador: **{jogador.display_name}**\n"
        f"✨ XP recebido: **+{quantidade}**\n"
        f"📈 Nível: **{nivel}**\n"
        f"⭐ XP atual: "
        f"`{xp_atual}/{xp_para_nivel(nivel)}`"
    )

    if subiu:
        mensagem += (
            f"\n\n🎉 **SUBIU DE NÍVEL!**\n"
            f"⭐ Nível anterior: **{nivel_antigo}**"
        )

    await interaction.response.send_message(
        mensagem,
        ephemeral=True
    )


# ==================================================
# /NIVEL
# ==================================================

@tree.command(
    name="nivel",
    description="Mostra seu nível e XP.",
    guild=GUILD
)
async def nivel(
    interaction: discord.Interaction
):
    ficha = buscar_ficha_dict(
        interaction.user.id
    )

    nivel_atual = int(
        ficha["nivel"] or 1
    )

    xp_atual = int(
        ficha["xp"] or 0
    )

    embed = discord.Embed(
        title=(
            f"⭐ PROGRESSÃO — "
            f"{interaction.user.display_name}"
        ),
        color=discord.Color.gold()
    )

    embed.add_field(
        name="📈 Nível",
        value=f"`{nivel_atual}`",
        inline=True
    )

    embed.add_field(
        name="✨ XP",
        value=(
            f"`{xp_atual}/"
            f"{xp_para_nivel(nivel_atual)}`"
        ),
        inline=True
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )


# ==================================================
# /RESETARNIVEL
# ==================================================

@tree.command(
    name="resetarnivel",
    description="Reseta o nível e XP de um jogador.",
    guild=GUILD
)
@app_commands.describe(
    jogador="Jogador que terá o nível resetado"
)
async def resetarnivel(
    interaction: discord.Interaction,
    jogador: discord.Member
):
    if not eh_pesquisador(interaction):
        await interaction.response.send_message(
            "🔒 Apenas Pesquisadores podem resetar níveis.",
            ephemeral=True
        )
        return

    resetar_nivel_jogador(
        jogador.id
    )

    await interaction.response.send_message(
        f"🔄 **Progressão resetada!**\n\n"
        f"👤 Jogador: **{jogador.display_name}**\n"
        f"📈 Nível: **1**\n"
        f"✨ XP: **0/{xp_para_nivel(1)}**",
        ephemeral=True
    )


# ==================================================
# /ADICIONAR_JOGADOR
# ==================================================

@tree.command(
    name="adicionar_jogador",
    description="Adiciona um jogador ao combate.",
    guild=GUILD
)
@app_commands.describe(
    jogador="Jogador que participará do combate"
)
async def adicionar_jogador(
    interaction: discord.Interaction,
    jogador: discord.Member
):
    if not eh_pesquisador(interaction):
        await interaction.response.send_message(
            "🔒 Apenas Pesquisadores podem adicionar jogadores.",
            ephemeral=True
        )
        return

    resultado = adicionar_jogador_combate(
        jogador.id
    )

    if resultado == "combate_inativo":
        mensagem = (
            "❌ Nenhum combate está ativo.\n"
            "Use `/mestre` e inicie um combate primeiro."
        )

    elif resultado == "duplicado":
        mensagem = (
            "⚠️ Esse jogador já está no combate."
        )

    elif resultado != "sucesso":
        mensagem = (
            "❌ Não foi possível adicionar o jogador."
        )

    else:
        mensagem = (
            f"👤 **{jogador.display_name}** entrou no combate!\n\n"
            "🎲 A iniciativa foi rolada automaticamente."
        )

    await interaction.response.send_message(
        mensagem,
        ephemeral=True
    )


# ==================================================
# BOT ONLINE
# ==================================================

@client.event
async def on_ready():
    print(
        f"🤖 Bot conectado como {client.user}"
    )

    try:
        synced = await tree.sync(
            guild=GUILD
        )

        print(
            f"✅ {len(synced)} comandos sincronizados no servidor!"
        )

        print(
            "📋 Comandos:"
        )

        for comando in synced:
            print(
                f"   /{comando.name}"
            )

    except Exception as erro:
        print(
            f"❌ Erro ao sincronizar comandos: {erro}"
        )


# ==================================================
# INICIAR BOT
# ==================================================

if not TOKEN:
    print(
        "❌ A variável DISCORD_TOKEN não foi encontrada."
    )
else:
    client.run(TOKEN)