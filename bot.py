import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption, ChannelType, PermissionOverwrite, ButtonStyle
from nextcord.ui import View, Button, Select
from nextcord import SelectOption
import os
import json
from dotenv import load_dotenv
import asyncio
import aiohttp

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = nextcord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ARCHIVO_GENERADORES = "/data/generadores.json"

def cargar_generadores():
    if os.path.exists(ARCHIVO_GENERADORES):
        try:
            with open(ARCHIVO_GENERADORES, "r") as f:
                data = json.load(f)
                return {int(k): int(v) for k, v in data.items()}
        except Exception as e:
            print(f"Error al cargar generadores: {e}")
    return {}

def guardar_generadores(generadores):
    try:
        os.makedirs(os.path.dirname(ARCHIVO_GENERADORES), exist_ok=True)
        with open(ARCHIVO_GENERADORES, "w") as f:
            json.dump({str(k): str(v) for k, v in generadores.items()}, f, indent=2)
    except Exception as e:
        print(f"Error al guardar generadores: {e}")

generadores = cargar_generadores()

MEDALLAS = [
    "Heraldo",
    "Guardián",
    "Cruzado",
    "Arconte",
    "Leyenda",
    "Ancestro",
    "Divino",
    "Inmortal",
]

ESTRELLAS = [
    "⭐",
    "⭐⭐",
    "⭐⭐⭐",
    "⭐⭐⭐⭐",
    "⭐⭐⭐⭐⭐",
]

ROLES_MEDALLA = MEDALLAS
ROLES_ESTRELLA = ESTRELLAS
ROLES_DOTA = ROLES_MEDALLA + ROLES_ESTRELLA

POSICIONES = [
    "Safe Lane",
    "Mid Lane",
    "Off Lane",
    "Support 4",
    "Support 5",
]

def obtener_texto_rango(rank_tier):
    if not rank_tier:
        return "Unranked"
    medallas = MEDALLAS
    estrellas = ["", "I", "II", "III", "IV", "V"]
    nivel = rank_tier // 10
    estrellas_num = rank_tier % 10
    if not (1 <= nivel <= 8):
        return "Unranked"
    nombre_medalla = medallas[nivel - 1]
    if nivel == 8:
        return "Inmortal"
    if estrellas_num < 1 or estrellas_num > 5:
        return nombre_medalla
    return f"{nombre_medalla} {estrellas[estrellas_num]}"

@bot.slash_command(name="generador", description="Asignar canal generador de salas temporales")
async def generador(
    interaction: Interaction,
    generator: nextcord.VoiceChannel = SlashOption(
        name="generator",
        description="Canal de voz generador",
        channel_types=[ChannelType.voice]
    )
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("No tienes permisos.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    guild_id = interaction.guild.id
    nuevo_id = generator.id
    old_id = generadores.get(guild_id)
    generadores[guild_id] = nuevo_id
    guardar_generadores(generadores)
    mensaje = f"Canal generador asignado: <#{nuevo_id}>"
    if old_id and old_id != nuevo_id:
        mensaje = f"Canal actualizado: <#{old_id}> ➔ <#{nuevo_id}>"
    await interaction.followup.send(mensaje, ephemeral=True)

@bot.event
async def on_voice_state_update(member, before, after):
    if not after.channel:
        return
    guild_id = member.guild.id
    generator_id = generadores.get(guild_id)
    if generator_id is None:
        return
    if after.channel.id != generator_id:
        return
    guild = member.guild
    new_category = await guild.create_category(name=f"# {member.display_name}")
    overwrites_voice = {
        guild.default_role: PermissionOverwrite(connect=True),
        member: PermissionOverwrite(manage_channels=True)
    }
    voice_channel = await guild.create_voice_channel(
        name=f"AUDIO",
        overwrites=overwrites_voice,
        category=new_category,
        user_limit=11
    )
    await member.edit(voice_channel=voice_channel)
    overwrites_text = {
        guild.default_role: PermissionOverwrite(read_messages=True, send_messages=True)
    }
    text_channel = await guild.create_text_channel(
        name=f"CHAT",
        overwrites=overwrites_text,
        category=new_category
    )
    async def eliminar_canales_si_vacio():
        while True:
            await asyncio.sleep(1)
            if len(voice_channel.members) == 0:
                try:
                    await voice_channel.delete()
                    await text_channel.delete()
                    await new_category.delete()
                except:
                    pass
                break
    bot.loop.create_task(eliminar_canales_si_vacio())

class UnirseAlCreadorView(View):
    def __init__(self, creador_id, timeout=600):
        super().__init__(timeout=timeout)
        self.creador_id = creador_id

    @nextcord.ui.button(label="Unirse a la partida", style=ButtonStyle.success, emoji="🎮")
    async def unirse(self, button: Button, interaction: Interaction):
        guild = interaction.guild
        creador = guild.get_member(self.creador_id)
        if not creador:
            await interaction.response.send_message(
                "El creador ya no está en el servidor.",
                ephemeral=True
            )
            return
        if not creador.voice or not creador.voice.channel:
            await interaction.response.send_message(
                "El creador no está en un canal de voz en este momento.",
                ephemeral=True
            )
            return
        canal_voz_creador = creador.voice.channel
        member = interaction.user
        if member.voice and member.voice.channel and member.voice.channel.id == canal_voz_creador.id:
            await interaction.response.send_message(
                "Ya estás en la partida del creador.",
                ephemeral=True
            )
            return
        if member.voice and member.voice.channel:
            try:
                await member.move_to(canal_voz_creador)
                await interaction.response.send_message(
                    f"Te uniste a la partida en <#{canal_voz_creador.id}>.",
                    ephemeral=True
                )
                return
            except Exception as e:
                print(f"Error al mover: {e}")
        enlace = f"https://discord.com/channels/{guild.id}/{canal_voz_creador.id}"
        await interaction.response.send_message(
            f"🎮 **Únete a la partida aquí:**\n{enlace}",
            ephemeral=True
        )

@bot.slash_command(name="buscarpartida", description="Publica tu perfil para buscar partida")
async def buscarpartida(
    interaction: Interaction,
    id_jugador: int = SlashOption(
        name="id",
        description="Steam32 Account ID (ej: 1568537464)",
        required=True
    )
):
    await interaction.response.defer()
    url = f"https://api.opendota.com/api/players/{id_jugador}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    await interaction.followup.send("No se pudo encontrar al jugador. Verifica el ID.")
                    return
                data = await response.json()
    except Exception as e:
        await interaction.followup.send(f"Error al consultar la API: {e}")
        return
    perfil = data.get('profile', {})
    nombre = perfil.get('personaname', 'Desconocido')
    avatar = perfil.get('avatarfull')
    rank_tier = data.get('rank_tier')
    print(f"[DEBUG] ID={id_jugador} | rank_tier crudo={rank_tier}")
    medalla_texto = obtener_texto_rango(rank_tier)
    embed = nextcord.Embed(
        title=f"🎮 Buscando partida - {nombre}",
        description=f"**Rango:** {medalla_texto}\n**ID:** {id_jugador}",
        color=0x00FF00
    )
    if avatar:
        embed.set_thumbnail(url=avatar)
    embed.set_footer(text="Haz clic en el botón para unirte a la partida del creador")
    view = UnirseAlCreadorView(interaction.user.id)
    await interaction.followup.send(embed=embed, view=view)

async def asegurar_roles(guild: nextcord.Guild):
    roles_existentes = {r.name: r for r in guild.roles}
    for nombre in ROLES_DOTA:
        if nombre not in roles_existentes:
            try:
                await guild.create_role(
                    name=nombre,
                    reason="Auto-creación de roles de Dota 2 (/rangos)"
                )
                print(f"[ROLES] Creado: {nombre}")
            except Exception as e:
                print(f"[ROLES] Error creando {nombre}: {e}")

seleccion_temporal = {}

async def aplicar_roles(interaction: Interaction):
    user_id = interaction.user.id
    member = interaction.user
    guild = interaction.guild

    datos = seleccion_temporal.get(user_id, {})
    medalla = datos.get("medalla")
    estrella = datos.get("estrella")

    if not medalla or not estrella:
        return

    roles_existentes = {r.name: r for r in guild.roles}

    roles_a_quitar = []
    for nombre in ROLES_DOTA:
        rol = roles_existentes.get(nombre)
        if rol and rol in member.roles:
            roles_a_quitar.append(rol)

    if roles_a_quitar:
        try:
            await member.remove_roles(*roles_a_quitar, reason="Cambio de rango Dota 2")
        except Exception as e:
            print(f"Error quitando roles: {e}")

    rol_medalla = roles_existentes.get(medalla)
    rol_estrella = roles_existentes.get(estrella)

    if rol_medalla is None or rol_estrella is None:
        return

    try:
        await member.add_roles(rol_medalla, rol_estrella, reason="Auto-asignación de rango Dota 2")
    except Exception as e:
        print(f"Error asignando roles: {e}")

class SelectMedalla(Select):
    def __init__(self, guild: nextcord.Guild):
        opciones = [SelectOption(label=m, value=m) for m in MEDALLAS]
        super().__init__(
            placeholder="Elige tu medalla...",
            options=opciones,
            min_values=1,
            max_values=1,
            row=0
        )

    async def callback(self, interaction: Interaction):
        seleccion_temporal.setdefault(interaction.user.id, {})["medalla"] = self.values[0]
        await interaction.response.defer()
        await aplicar_roles(interaction)

class SelectEstrella(Select):
    def __init__(self, guild: nextcord.Guild):
        opciones = [SelectOption(label=e, value=e) for e in ESTRELLAS]
        super().__init__(
            placeholder="Elige tus estrellas...",
            options=opciones,
            min_values=1,
            max_values=1,
            row=1
        )

    async def callback(self, interaction: Interaction):
        seleccion_temporal.setdefault(interaction.user.id, {})["estrella"] = self.values[0]
        await interaction.response.defer()
        await aplicar_roles(interaction)

class VistaRangos(View):
    def __init__(self, guild: nextcord.Guild, timeout=None):
        super().__init__(timeout=timeout)
        self.add_item(SelectMedalla(guild))
        self.add_item(SelectEstrella(guild))

@bot.slash_command(name="rangos", description="Despliega el panel de rangos de Dota 2 (solo admins)")
async def rangos(interaction: Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "Solo los administradores pueden usar este comando.",
            ephemeral=True
        )
        return
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild

    me = guild.me
    if not me.guild_permissions.manage_roles:
        await interaction.followup.send(
            "⚠️ El bot no tiene el permiso **Gestionar roles**. No podrá asignar ni quitar roles.",
            ephemeral=True
        )
        return

    await asegurar_roles(guild)

    embed = nextcord.Embed(
        title="Selecciona tu rango de Dota 2",
        description=(
            "**Paso 1:** Elige tu medalla en el primer menú.\n"
            "**Paso 2:** Elige tus estrellas en el segundo menú.\n\n"
            "Al completar ambos, el bot te quitará tu rango anterior y te pondrá los nuevos roles."
        ),
        color=0x00FF00
    )
    embed.set_footer(text="Solo puedes tener una medalla y una estrella a la vez.")

    view = VistaRangos(guild)
    await interaction.channel.send(embed=embed, view=view)
    await interaction.followup.send("Panel desplegado.", ephemeral=True)

async def asegurar_roles_posiciones(guild: nextcord.Guild):
    roles_existentes = {r.name: r for r in guild.roles}
    for nombre in POSICIONES:
        if nombre not in roles_existentes:
            try:
                await guild.create_role(
                    name=nombre,
                    reason="Auto-creación de roles de posición Dota 2 (/roles)"
                )
                print(f"[ROLES-POS] Creado: {nombre}")
            except Exception as e:
                print(f"[ROLES-POS] Error creando {nombre}: {e}")

class SelectPosiciones(Select):
    def __init__(self, guild: nextcord.Guild):
        opciones = [SelectOption(label=p, value=p) for p in POSICIONES]
        super().__init__(
            placeholder="Elige tus posiciones...",
            options=opciones,
            min_values=0,
            max_values=len(POSICIONES),
            row=0
        )

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()
        member = interaction.user
        guild = interaction.guild

        seleccionadas = list(self.values)

        roles_existentes = {r.name: r for r in guild.roles}

        roles_a_quitar = []
        for nombre in POSICIONES:
            rol = roles_existentes.get(nombre)
            if rol and rol in member.roles:
                roles_a_quitar.append(rol)

        if roles_a_quitar:
            try:
                await member.remove_roles(*roles_a_quitar, reason="Cambio de posiciones Dota 2")
            except Exception as e:
                print(f"Error quitando posiciones: {e}")

        roles_a_poner = []
        for nombre in seleccionadas:
            rol = roles_existentes.get(nombre)
            if rol:
                roles_a_poner.append(rol)

        if roles_a_poner:
            try:
                await member.add_roles(*roles_a_poner, reason="Auto-asignación de posiciones Dota 2")
            except Exception as e:
                print(f"Error asignando posiciones: {e}")

class VistaRolesPosiciones(View):
    def __init__(self, guild: nextcord.Guild, timeout=None):
        super().__init__(timeout=timeout)
        self.add_item(SelectPosiciones(guild))

@bot.slash_command(name="roles", description="Panel para elegir tus posiciones de Dota 2 (solo admins)")
async def roles(interaction: Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "Solo los administradores pueden usar este comando.",
            ephemeral=True
        )
        return
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild

    me = guild.me
    if not me.guild_permissions.manage_roles:
        await interaction.followup.send(
            "⚠️ El bot no tiene el permiso **Gestionar roles**. No podrá asignar ni quitar roles.",
            ephemeral=True
        )
        return

    await asegurar_roles_posiciones(guild)

    embed = nextcord.Embed(
        title="Selecciona tus posiciones de Dota 2",
        description=(
            "Marca en el menú todas las posiciones que juegas.\n"
            "Puedes elegir varias a la vez.\n"
            "Para quitarte una posición, simplemente desmárcala.\n\n"
            "Los cambios se aplican automáticamente."
        ),
        color=0x00FF00
    )
    embed.set_footer(text="Puedes tener varias posiciones a la vez.")

    view = VistaRolesPosiciones(guild)
    await interaction.channel.send(embed=embed, view=view)
    await interaction.followup.send("Panel desplegado.", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    print(f"Generadores cargados: {generadores}")
    try:
        await bot.sync_all_application_commands()
        print("Comandos slash sincronizados globalmente")
        for guild in bot.guilds:
            await bot.sync_application_commands(guild_id=guild.id)
            print(f"Comandos sincronizados en: {guild.name}")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")

if __name__ == "__main__":
    bot.run(TOKEN)
