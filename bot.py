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

# Cargo de Mestre / Pesquisador
PESQUISADOR_ROLE_ID = 1535729779087515678

# Cargo de jogador / Cobaia
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

        db.commit()

        print(
            f"✅ Coluna '{coluna}' adicionada à tabela '{tabela}'."
        )


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
        "Intuição"
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


ATRIBUTOS = [
    "Físico",
    "Conhecimento",
    "Social",
    "Vontade"
]


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

        pontos_atributo INTEGER DEFAULT 10,

        pericias TEXT DEFAULT '{}',

        pontos_pericia INTEGER DEFAULT 20,

        vida_max INTEGER DEFAULT 20,

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

    "pontos_atributo": "INTEGER DEFAULT 10",

    "pericias": "TEXT DEFAULT '{}'",

    "pontos_pericia": "INTEGER DEFAULT 20",

    "vida_max": "INTEGER DEFAULT 20",

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

        vida INTEGER DEFAULT 20,

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

        vida INTEGER DEFAULT 0,

        vida_max INTEGER DEFAULT 0
    )
    """
)


# ==================================================
# MIGRAÇÃO COMBATENTES
# ==================================================

adicionar_coluna_se_nao_existir(
    "combatentes",
    "vida_max",
    "INTEGER DEFAULT 0"
)


# ==================================================
# HISTÓRICO
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
# CRIAR FICHA
# ==================================================

def criar_ficha(user_id):

    cursor.execute(
        """
        SELECT user_id
        FROM fichas
        WHERE user_id = ?
        """,
        (user_id,)
    )

    existe = cursor.fetchone()

    if existe is None:

        cursor.execute(
            """
            INSERT INTO fichas (

                user_id,

                pericias,

                pontos_atributo,

                pontos_pericia,

                vida_max,

                xp,

                nivel
            )

            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (

                user_id,

                json.dumps(
                    criar_pericias(),
                    ensure_ascii=False
                ),

                10,

                20,

                20,

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
        """
        SELECT *
        FROM fichas
        WHERE user_id = ?
        """,
        (user_id,)
    )

    return cursor.fetchone()


# ==================================================
# BUSCAR FICHA DICT
# ==================================================

def buscar_ficha_dict(user_id):

    criar_ficha(user_id)

    cursor.execute(
        """
        SELECT *
        FROM fichas
        WHERE user_id = ?
        """,
        (user_id,)
    )

    ficha = cursor.fetchone()

    if ficha is None:
        return None

    colunas = [
        descricao[0]
        for descricao in cursor.description
    ]

    return dict(
        zip(colunas, ficha)
    )


# ==================================================
# PERÍCIAS DO JOGADOR
# ==================================================

def pegar_pericias(ficha):

    try:

        pericias = json.loads(
            ficha.get("pericias") or "{}"
        )

        if not isinstance(pericias, dict):
            return criar_pericias()

        return pericias

    except:

        return criar_pericias()


# ==================================================
# XP
# ==================================================

def xp_para_nivel(nivel):

    return max(1, nivel) * 100


def adicionar_xp(user_id, quantidade):

    ficha = buscar_ficha_dict(user_id)

    nivel = int(
        ficha.get("nivel") or 1
    )

    xp = int(
        ficha.get("xp") or 0
    )

    xp += quantidade

    nivel_antigo = nivel

    subiu = False

    while xp >= xp_para_nivel(nivel):

        xp -= xp_para_nivel(nivel)

        nivel += 1

        subiu = True

    cursor.execute(
        """
        UPDATE fichas

        SET
            xp = ?,
            nivel = ?

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
# EMBED DA FICHA
# ==================================================

def criar_embed_ficha(ficha):

    if ficha is None:

        return discord.Embed(
            title="❌ Ficha não encontrada",
            color=discord.Color.red()
        )

    dados = {
        "user_id": ficha[0],
        "nome": ficha[1],
        "idade": ficha[2],
        "sexualidade": ficha[3],
        "altura": ficha[4],
        "peso": ficha[5],
        "descendencia": ficha[6],
        "linhagem": ficha[7],
        "sub_linhagem": ficha[8],
        "objetivo": ficha[9],
        "medos": ficha[10],
        "personalidade": ficha[11],
        "relacoes": ficha[12],
        "historia": ficha[13],
        "fisico": ficha[14],
        "conhecimento": ficha[15],
        "social": ficha[16],
        "vontade": ficha[17]
    }

    ficha_dict = buscar_ficha_dict(
        dados["user_id"]
    )

    pericias = pegar_pericias(
        ficha_dict
    )

    xp = ficha_dict["xp"]
    nivel = ficha_dict["nivel"]

    pontos_atributo = ficha_dict[
        "pontos_atributo"
    ]

    pontos_pericia = ficha_dict[
        "pontos_pericia"
    ]

    vida_max = ficha_dict[
        "vida_max"
    ]

    embed = discord.Embed(

        title=(
            f"👤 FICHA — "
            f"{dados['nome'] or 'Sem nome'}"
        ),

        description="🔒 Esta ficha é privada.",

        color=discord.Color.blurple()
    )

    embed.add_field(

        name="📖 Informações",

        value=(
            f"**Nome:** {dados['nome'] or '—'}\n"
            f"**Idade:** {dados['idade'] or '—'}\n"
            f"**Sexualidade:** {dados['sexualidade'] or '—'}\n"
            f"**Altura:** {dados['altura'] or '—'}\n"
            f"**Peso:** {dados['peso'] or '—'}"
        ),

        inline=False
    )

    embed.add_field(

        name="🧬 Linhagem",

        value=(
            f"**Descendência:** {dados['descendencia'] or '—'}\n"
            f"**Linhagem Heroica:** {dados['linhagem'] or '—'}\n"
            f"**Sub-linhagem:** {dados['sub_linhagem'] or '—'}"
        ),

        inline=False
    )

    embed.add_field(

        name="⚔️ Atributos",

        value=(
            f"💪 **Físico:** `{dados['fisico']}`\n"
            f"🧠 **Conhecimento:** `{dados['conhecimento']}`\n"
            f"🗣️ **Social:** `{dados['social']}`\n"
            f"🔥 **Vontade:** `{dados['vontade']}`"
        ),

        inline=False
    )

    embed.add_field(

        name="❤️ Status",

        value=(
            f"❤️ **Vida Máxima:** `{vida_max}`\n"
            f"⭐ **Nível:** `{nivel}`\n"
            f"✨ **XP:** `{xp}/{xp_para_nivel(nivel)}`"
        ),

        inline=False
    )

    embed.add_field(

        name="📊 Pontos",

        value=(
            f"⚔️ Pontos de Atributo: `{pontos_atributo}`\n"
            f"📚 Pontos de Perícia: `{pontos_pericia}`"
        ),

        inline=False
    )

    embed.add_field(

        name="🎯 Objetivo",

        value=dados["objetivo"] or "—",

        inline=False
    )

    embed.add_field(

        name="😨 Medos",

        value=dados["medos"] or "—",

        inline=False
    )

    for categoria, lista in PERICIAS.items():

        texto = ""

        for pericia in lista:

            chave = f"{categoria}:{pericia}"

            valor = pericias.get(
                chave,
                0
            )

            texto += (
                f"**{pericia}:** `{valor}`\n"
            )

        embed.add_field(

            name=f"📋 {categoria}",

            value=texto[:1024],

            inline=True
        )

    embed.set_footer(
        text="Tavelada RPG"
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
# MODAL INFORMAÇÕES
# ==================================================

class InformacoesModal(discord.ui.Modal):

    def __init__(self):

        super().__init__(
            title="📖 Informações"
        )

        self.nome = discord.ui.TextInput(
            label="Nome",
            required=True
        )

        self.idade = discord.ui.TextInput(
            label="Idade",
            required=False
        )

        self.sexualidade = discord.ui.TextInput(
            label="Sexualidade",
            required=False
        )

        self.altura = discord.ui.TextInput(
            label="Altura",
            required=False
        )

        self.peso = discord.ui.TextInput(
            label="Peso",
            required=False
        )

        self.add_item(self.nome)
        self.add_item(self.idade)
        self.add_item(self.sexualidade)
        self.add_item(self.altura)
        self.add_item(self.peso)

    async def on_submit(self, interaction):

        criar_ficha(
            interaction.user.id
        )

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

        await interaction.response.send_message(
            "✅ Informações salvas!",
            ephemeral=True
        )


# ==================================================
# MODAL LINHAGEM
# ==================================================

class LinhagemModal(discord.ui.Modal):

    def __init__(self):

        super().__init__(
            title="🧬 Linhagem"
        )

        self.descendencia = discord.ui.TextInput(
            label="Descendência",
            required=False
        )

        self.linhagem = discord.ui.TextInput(
            label="Linhagem Heroica",
            required=False
        )

        self.sub_linhagem = discord.ui.TextInput(
            label="Sub-linhagem",
            required=False
        )

        self.objetivo = discord.ui.TextInput(
            label="Objetivo",
            required=False
        )

        self.medos = discord.ui.TextInput(
            label="Medos",
            required=False
        )

        self.add_item(self.descendencia)
        self.add_item(self.linhagem)
        self.add_item(self.sub_linhagem)
        self.add_item(self.objetivo)
        self.add_item(self.medos)

    async def on_submit(self, interaction):

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

        await interaction.response.send_message(
            "✅ Linhagem salva!",
            ephemeral=True
        )


# ==================================================
# MODAL PERSONALIDADE
# ==================================================

class PersonalidadeModal(discord.ui.Modal):

    def __init__(self):

        super().__init__(
            title="🧠 Personalidade"
        )

        self.personalidade = discord.ui.TextInput(
            label="Personalidade",
            style=discord.TextStyle.paragraph,
            required=False
        )

        self.relacoes = discord.ui.TextInput(
            label="Relações",
            style=discord.TextStyle.paragraph,
            required=False
        )

        self.historia = discord.ui.TextInput(
            label="História",
            style=discord.TextStyle.paragraph,
            required=False
        )

        self.add_item(self.personalidade)
        self.add_item(self.relacoes)
        self.add_item(self.historia)

    async def on_submit(self, interaction):

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

        await interaction.response.send_message(
            "✅ Personalidade salva!",
            ephemeral=True
        )


# ==================================================
# VIEW ATRIBUTOS
# ==================================================

class AtributosView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=300
        )

    async def aumentar(
        self,
        interaction,
        atributo
    ):

        ficha = buscar_ficha_dict(
            interaction.user.id
        )

        pontos = int(
            ficha["pontos_atributo"]
        )

        if pontos <= 0:

            await interaction.response.send_message(
                "❌ Você não possui mais pontos de atributo.",
                ephemeral=True
            )

            return

        coluna = atributo.lower()

        cursor.execute(
            f"""
            UPDATE fichas

            SET
                {coluna} = {coluna} + 1,
                pontos_atributo = pontos_atributo - 1

            WHERE user_id = ?
            """,
            (interaction.user.id,)
        )

        db.commit()

        await interaction.response.edit_message(
            content=(
                f"✅ **{atributo} aumentado!**\n"
                "Reabra sua ficha para ver os valores."
            ),
            embed=None,
            view=None
        )

    @discord.ui.button(
        label="Físico +1",
        emoji="💪",
        style=discord.ButtonStyle.primary
    )
    async def fisico(self, interaction, button):

        await self.aumentar(
            interaction,
            "Físico"
        )

    @discord.ui.button(
        label="Conhecimento +1",
        emoji="🧠",
        style=discord.ButtonStyle.primary
    )
    async def conhecimento(self, interaction, button):

        await self.aumentar(
            interaction,
            "Conhecimento"
        )

    @discord.ui.button(
        label="Social +1",
        emoji="🗣️",
        style=discord.ButtonStyle.primary
    )
    async def social(self, interaction, button):

        await self.aumentar(
            interaction,
            "Social"
        )

    @discord.ui.button(
        label="Vontade +1",
        emoji="🔥",
        style=discord.ButtonStyle.primary
    )
    async def vontade(self, interaction, button):

        await self.aumentar(
            interaction,
            "Vontade"
        )


# ==================================================
# SELECT DE PERÍCIAS
# ==================================================

class PericiaSelect(discord.ui.Select):

    def __init__(self, opcoes):

        super().__init__(
            placeholder="Escolha uma perícia...",
            options=opcoes
        )

    async def callback(self, interaction):

        ficha = buscar_ficha_dict(
            interaction.user.id
        )

        pontos = int(
            ficha["pontos_pericia"]
        )

        if pontos <= 0:

            await interaction.response.send_message(
                "❌ Você não possui pontos de perícia.",
                ephemeral=True
            )

            return

        pericias = pegar_pericias(
            ficha
        )

        chave = self.values[0]

        pericias[chave] = (
            int(pericias.get(chave, 0)) + 1
        )

        cursor.execute(
            """
            UPDATE fichas

            SET
                pericias = ?,
                pontos_pericia = pontos_pericia - 1

            WHERE user_id = ?
            """,
            (
                json.dumps(
                    pericias,
                    ensure_ascii=False
                ),
                interaction.user.id
            )
        )

        db.commit()

        await interaction.response.send_message(
            (
                f"✅ **{chave.split(':')[1]}** "
                "aumentada em +1!"
            ),
            ephemeral=True
        )


# ==================================================
# VIEW FICHA
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
        interaction,
        button
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
        interaction,
        button
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
        interaction,
        button
    ):

        await interaction.response.send_modal(
            PersonalidadeModal()
        )

    @discord.ui.button(
        label="Atributos",
        emoji="⚔️",
        style=discord.ButtonStyle.success
    )
    async def atributos(
        self,
        interaction,
        button
    ):

        ficha = buscar_ficha_dict(
            interaction.user.id
        )

        pontos = ficha["pontos_atributo"]

        await interaction.response.send_message(

            f"📊 Você possui **{pontos} pontos** de atributo.",

            view=AtributosView(),

            ephemeral=True
        )

    @discord.ui.button(
        label="Perícias",
        emoji="📚",
        style=discord.ButtonStyle.success
    )
    async def pericias(
        self,
        interaction,
        button
    ):

        opcoes = []

        for categoria, lista in PERICIAS.items():

            for pericia in lista:

                chave = f"{categoria}:{pericia}"

                opcoes.append(

                    discord.SelectOption(

                        label=pericia,

                        description=categoria,

                        value=chave
                    )
                )

        view = discord.ui.View(
            timeout=300
        )

        view.add_item(
            PericiaSelect(opcoes[:25])
        )

        await interaction.response.send_message(

            "📚 Escolha uma perícia para aumentar.",

            view=view,

            ephemeral=True
        )

    @discord.ui.button(
        label="Atualizar",
        emoji="🔄",
        style=discord.ButtonStyle.secondary
    )
    async def atualizar(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(

            embed=criar_embed_ficha(
                buscar_ficha(
                    interaction.user.id
                )
            ),

            view=FichaView()
        )


# ==================================================
# TESTES
# ==================================================

def atributo_da_pericia(categoria):

    if categoria == "Conhecimento":
        return "conhecimento"

    if categoria == "Percepção":
        return "vontade"

    if categoria == "Social":
        return "social"

    if categoria == "Físico":
        return "fisico"

    if categoria == "Combate":
        return "fisico"

    return "vontade"


class TestePericiaSelect(discord.ui.Select):

    def __init__(self):

        opcoes = []

        for categoria, lista in PERICIAS.items():

            for pericia in lista:

                chave = f"{categoria}:{pericia}"

                opcoes.append(

                    discord.SelectOption(

                        label=pericia,

                        description=categoria,

                        value=chave
                    )
                )

        super().__init__(

            placeholder="Escolha a perícia...",

            options=opcoes[:25]
        )

    async def callback(self, interaction):

        ficha = buscar_ficha_dict(
            interaction.user.id
        )

        pericias = pegar_pericias(
            ficha
        )

        chave = self.values[0]

        categoria, nome_pericia = chave.split(
            ":",
            1
        )

        atributo_nome = atributo_da_pericia(
            categoria
        )

        atributo = int(
            ficha.get(
                atributo_nome,
                0
            )
        )

        valor_pericia = int(
            pericias.get(
                chave,
                0
            )
        )

        dado = random.randint(1, 7)

        resultado = (
            dado +
            atributo +
            valor_pericia
        )

        registrar_rolagem(

            interaction.user.id,

            interaction.user.display_name,

            f"Teste: {nome_pericia}",

            resultado,

            7
        )

        embed = discord.Embed(

            title="🎲 TESTE",

            color=discord.Color.gold()
        )

        embed.add_field(
            name="📋 Perícia",
            value=f"**{nome_pericia}**",
            inline=False
        )

        embed.add_field(
            name="🎲 D7",
            value=f"`{dado}`",
            inline=True
        )

        embed.add_field(
            name="⚔️ Atributo",
            value=f"`+{atributo}`",
            inline=True
        )

        embed.add_field(
            name="📚 Perícia",
            value=f"`+{valor_pericia}`",
            inline=True
        )

        embed.add_field(
            name="🏆 RESULTADO FINAL",
            value=f"# {resultado}",
            inline=False
        )

        await interaction.response.send_message(
            embed=embed
        )


class TesteView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=300
        )

        self.add_item(
            TestePericiaSelect()
        )


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

    return (
        resultado is not None
        and resultado[0] == 1
    )


def ja_esta_no_combate(tipo, referencia_id):

    cursor.execute(
        """
        SELECT id
        FROM combatentes

        WHERE
            tipo = ?
            AND referencia_id = ?
        """,
        (
            tipo,
            referencia_id
        )
    )

    return cursor.fetchone() is not None


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


def adicionar_jogador_combate(user_id):

    if not combate_ativo():
        return "combate_inativo"

    if ja_esta_no_combate(
        "jogador",
        user_id
    ):
        return "duplicado"

    ficha = buscar_ficha_dict(
        user_id
    )

    nome = ficha["nome"] or "Jogador"

    fisico = int(
        ficha["fisico"] or 0
    )

    vida = int(
        ficha["vida_max"] or 20
    )

    pericias = pegar_pericias(
        ficha
    )

    atletismo = int(
        pericias.get(
            "Físico:Atletismo",
            0
        )
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
            vida,
            vida_max

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            nome,
            "jogador",
            user_id,
            iniciativa,
            dado,
            fisico,
            atletismo,
            vida,
            vida
        )
    )

    db.commit()

    return "sucesso"


def criar_embed_combate():

    if not combate_ativo():

        return discord.Embed(

            title="⚔️ COMBATE",

            description=(
                "Nenhum combate ativo no momento."
            ),

            color=discord.Color.red()
        )

    cursor.execute(
        """
        SELECT rodada, turno
        FROM combate
        WHERE id = 1
        """
    )

    rodada, turno = cursor.fetchone()

    cursor.execute(
        """
        SELECT

            id,
            nome,
            tipo,
            referencia_id,
            iniciativa,
            vida,
            vida_max

        FROM combatentes

        ORDER BY iniciativa DESC, id ASC
        """
    )

    combatentes = cursor.fetchall()

    embed = discord.Embed(

        title="⚔️ COMBATE",

        description=f"🔥 **Rodada {rodada}**",

        color=discord.Color.orange()
    )

    if not combatentes:

        embed.add_field(

            name="Combatentes",

            value="Nenhum combatente entrou ainda.",

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
            referencia_id,
            iniciativa,
            vida,
            vida_max
        ) = combatente

        marcador = (
            "▶️"
            if posicao - 1 == turno
            else f"**{posicao}.**"
        )

        icone = (
            "👤"
            if tipo == "jogador"
            else "🛡️"
        )

        texto += (
            f"{marcador} {icone} **{nome}**\n"
            f"⚡ Iniciativa: `{iniciativa}` "
            f"• ❤️ `{vida}/{vida_max}`\n\n"
        )

    embed.add_field(

        name="📜 Ordem de Iniciativa",

        value=texto[:1024],

        inline=False
    )

    return embed


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

    rodada, turno = cursor.fetchone()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM combatentes
        """
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

        SET
            rodada = ?,
            turno = ?

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
# VIEW COMBATE
# ==================================================

class CombateView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Entrar no Combate",
        emoji="⚔️",
        style=discord.ButtonStyle.success
    )
    async def entrar(
        self,
        interaction,
        button
    ):

        resultado = adicionar_jogador_combate(
            interaction.user.id
        )

        mensagens = {

            "sucesso":
                "✅ Você entrou no combate!",

            "duplicado":
                "⚠️ Você já está no combate!",

            "combate_inativo":
                "❌ Não existe combate ativo."
        }

        await interaction.response.send_message(

            mensagens.get(
                resultado,
                "❌ Erro."
            ),

            ephemeral=True
        )

    @discord.ui.button(
        label="Atualizar",
        emoji="🔄",
        style=discord.ButtonStyle.secondary
    )
    async def atualizar(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(

            embed=criar_embed_combate(),

            view=CombateView()
        )


# ==================================================
# VIEW MESTRE COMBATE
# ==================================================

class CombateMestreView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Próximo Turno",
        emoji="⏭️",
        style=discord.ButtonStyle.success
    )
    async def proximo(
        self,
        interaction,
        button
    ):

        if not eh_pesquisador(interaction):

            await interaction.response.send_message(
                "🔒 Apenas Pesquisadores.",
                ephemeral=True
            )

            return

        proximo_turno()

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
        interaction,
        button
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
        interaction,
        button
    ):

        if not eh_pesquisador(interaction):

            await interaction.response.send_message(
                "🔒 Apenas Pesquisadores.",
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
        interaction,
        button
    ):

        await mostrar_ficha(
            interaction
        )

    @discord.ui.button(
        label="Fazer Teste",
        emoji="🎲",
        style=discord.ButtonStyle.success
    )
    async def teste(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(

            "🎲 Escolha a perícia do teste:",

            view=TesteView(),

            ephemeral=True
        )

    @discord.ui.button(
        label="Combate",
        emoji="⚔️",
        style=discord.ButtonStyle.danger
    )
    async def combate(
        self,
        interaction,
        button
    ):

        view = (
            CombateMestreView()
            if eh_pesquisador(interaction)
            else CombateView()
        )

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
    async def d7(
        self,
        interaction,
        button
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
            f"🎲 Resultado: **{resultado}**"
        )


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
        interaction,
        button
    ):

        embed = discord.Embed(

            title="📜 TAVELADA",

            description=(
                "Sistema oficial da mesa.\n\n"
                "🎲 D7 + Atributo + Perícia"
            ),

            color=discord.Color.blurple()
        )

        await interaction.response.edit_message(

            embed=embed,

            view=TaveladaSistemaView()
        )

    @discord.ui.button(
        label="Voltar",
        emoji="↩️",
        style=discord.ButtonStyle.secondary
    )
    async def voltar(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(

            embed=criar_embed_painel_principal(),

            view=PainelPrincipal()
        )


# ==================================================
# EMBEDS
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
        value="Acesse os sistemas.",
        inline=False
    )

    embed.add_field(
        name="📖 Fichas",
        value="Gerencie seu personagem.",
        inline=False
    )

    embed.add_field(
        name="⚔️ Combate",
        value="Combate e iniciativa.",
        inline=False
    )

    embed.add_field(
        name="🎲 Rolagens",
        value="Role dados e faça testes.",
        inline=False
    )

    return embed


def criar_embed_sistemas():

    return discord.Embed(

        title="📚 SISTEMAS",

        description=(
            "Escolha um sistema."
        ),

        color=discord.Color.blurple()
    )


# ==================================================
# PAINEL PRINCIPAL
# ==================================================

class PainelPrincipal(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Sistemas",
        emoji="📚",
        style=discord.ButtonStyle.primary
    )
    async def sistemas(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(

            embed=criar_embed_sistemas(),

            view=SistemasView()
        )

    @discord.ui.button(
        label="Ficha",
        emoji="👤",
        style=discord.ButtonStyle.primary
    )
    async def ficha(
        self,
        interaction,
        button
    ):

        await mostrar_ficha(
            interaction
        )

    @discord.ui.button(
        label="Combate",
        emoji="⚔️",
        style=discord.ButtonStyle.success
    )
    async def combate(
        self,
        interaction,
        button
    ):

        view = (
            CombateMestreView()
            if eh_pesquisador(interaction)
            else CombateView()
        )

        await interaction.response.send_message(

            embed=criar_embed_combate(),

            view=view,

            ephemeral=True
        )

    @discord.ui.button(
        label="Teste",
        emoji="🎲",
        style=discord.ButtonStyle.secondary
    )
    async def teste(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(

            "🎲 Escolha uma perícia:",

            view=TesteView(),

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
async def painel(interaction):

    await interaction.response.send_message(

        embed=criar_embed_painel_principal(),

        view=PainelPrincipal()
    )


# ==================================================
# /D7
# ==================================================

@tree.command(
    name="d7",
    description="Rola um D7.",
    guild=GUILD
)
async def d7(interaction):

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


# ==================================================
# /TESTE
# ==================================================

@tree.command(
    name="teste",
    description="Faz um teste usando uma perícia.",
    guild=GUILD
)
async def teste(interaction):

    await interaction.response.send_message(

        "🎲 Escolha a perícia:",

        view=TesteView(),

        ephemeral=True
    )


# ==================================================
# /INICIAR_COMBATE
# ==================================================

@tree.command(
    name="iniciar_combate",
    description="Inicia um combate.",
    guild=GUILD
)
async def iniciar_combate_comando(interaction):

    if not eh_pesquisador(interaction):

        await interaction.response.send_message(

            "🔒 Apenas Pesquisadores podem iniciar combates.",

            ephemeral=True
        )

        return

    iniciar_combate()

    await interaction.response.send_message(

        "⚔️ **COMBATE INICIADO!**",

        embed=criar_embed_combate(),

        view=CombateMestreView()
    )


# ==================================================
# /ENTRAR_COMBATE
# ==================================================

@tree.command(
    name="entrar_combate",
    description="Entra no combate ativo.",
    guild=GUILD
)
async def entrar_combate(interaction):

    resultado = adicionar_jogador_combate(
        interaction.user.id
    )

    mensagens = {

        "sucesso":
            "⚔️ Você entrou no combate!",

        "duplicado":
            "⚠️ Você já está no combate.",

        "combate_inativo":
            "❌ Não existe combate ativo."
    }

    await interaction.response.send_message(

        mensagens.get(
            resultado,
            "❌ Erro."
        ),

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
    jogador="Jogador",
    quantidade="Quantidade de XP"
)
async def darxp(
    interaction,
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

            "❌ O XP precisa ser maior que zero.",

            ephemeral=True
        )

        return

    nivel, antigo, subiu = adicionar_xp(

        jogador.id,

        quantidade
    )

    mensagem = (
        f"⭐ **XP concedido!**\n\n"
        f"👤 {jogador.display_name}\n"
        f"✨ +{quantidade} XP\n"
        f"📈 Nível: {nivel}"
    )

    if subiu:

        mensagem += (
            "\n\n🎉 **SUBIU DE NÍVEL!**"
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
            f"✅ {len(synced)} comandos sincronizados!"
        )

        for comando in synced:

            print(
                f"   /{comando.name}"
            )

    except Exception as erro:

        print(
            f"❌ Erro: {erro}"
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