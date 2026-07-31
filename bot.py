import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption, ChannelType, ButtonStyle, PermissionOverwrite, PartialEmoji
import os
from dotenv import load_dotenv
import asyncio
from nextcord.ui import View, Button
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import math
import re

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = nextcord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

generator_channel_id = None
heroes_dict = {}

# ============================================
# TODOS LOS HÉROES GUARDADOS EN EL CÓDIGO
# ============================================

NOMBRES_HEROES = [
    "Anti-Mage", "Axe", "Bane", "Bloodseeker", "Crystal Maiden", "Drow Ranger",
    "Earthshaker", "Juggernaut", "Mirana", "Morphling", "Shadow Fiend", "Phantom Lancer",
    "Puck", "Pudge", "Razor", "Sand King", "Storm Spirit", "Sven", "Tiny",
    "Vengeful Spirit", "Windranger", "Zeus", "Kunkka", "Lina", "Lion",
    "Shadow Shaman", "Slardar", "Tidehunter", "Witch Doctor", "Chaos Knight",
    "Queen of Pain", "Venomancer", "Faceless Void", "Wraith King", "Death Prophet",
    "Phantom Assassin", "Pugna", "Templar Assassin", "Viper", "Luna",
    "Dragon Knight", "Dazzle", "Clockwerk", "Leshrac", "Natures Prophet",
    "Lifestealer", "Dark Seer", "Clinkz", "Omniknight", "Enchantress",
    "Huskar", "Night Stalker", "Broodmother", "Bounty Hunter", "Weaver",
    "Jakiro", "Batrider", "Chen", "Spectre", "Ancient Apparition",
    "Doom", "Ursa", "Spirit Breaker", "Gyrocopter", "Alchemist",
    "Invoker", "Silencer", "Outworld Destroyer", "Lycan", "Brewmaster",
    "Shadow Demon", "Lone Druid", "Skeleton King", "Naga Siren", "Keeper of the Light",
    "Io", "Treant Protector", "Ogre Magi", "Undying", "Rubick",
    "Disruptor", "Nyx Assassin", "Necrophos", "Warlock", "Medusa",
    "Troll Warlord", "Centaur Warrunner", "Magnus", "Timbersaw", "Bristleback",
    "Tusk", "Skywrath Mage", "Abaddon", "Elder Titan", "Legion Commander",
    "Ember Spirit", "Earth Spirit", "Underlord", "Terrorblade", "Phoenix",
    "Oracle", "Techies", "Winter Wyvern", "Arc Warden", "Monkey King",
    "Dark Willow", "Pangolier", "Grimstroke", "Mars", "Snapfire",
    "Void Spirit", "Hoodwink", "Dawnbreaker", "Marci", "Primal Beast",
    "Muerta", "Kez", "Ringmaster"
]

# ALIASES PARA NOMBRES CORTOS
ALIASES = {
    "am": "Anti-Mage", "pa": "Phantom Assassin", "sf": "Shadow Fiend",
    "pl": "Phantom Lancer", "pudge": "Pudge", "legion": "Legion Commander",
    "lc": "Legion Commander", "sven": "Sven", "abaddon": "Abaddon",
    "puck": "Puck", "axe": "Axe", "jugg": "Juggernaut",
    "void": "Faceless Void", "wk": "Wraith King", "spec": "Spectre",
    "es": "Earthshaker", "sk": "Sand King", "tide": "Tidehunter",
    "bb": "Bristleback", "qop": "Queen of Pain", "lina": "Lina",
    "lion": "Lion", "cm": "Crystal Maiden", "wd": "Witch Doctor",
    "dk": "Dragon Knight", "bs": "Bloodseeker", "od": "Outworld Destroyer",
    "kotl": "Keeper of the Light", "io": "Io", "wisp": "Io",
    "ember": "Ember Spirit", "storm": "Storm Spirit", "marci": "Marci",
    "invoker": "Invoker", "sniper": "Sniper", "zeus": "Zeus",
    "rubick": "Rubick", "oracle": "Oracle", "dazzle": "Dazzle",
    "lich": "Lich", "enigma": "Enigma", "beastmaster": "Beastmaster",
    "bm": "Beastmaster", "lycan": "Lycan", "slark": "Slark",
    "riki": "Riki", "weaver": "Weaver", "wind": "Windranger",
    "wr": "Windranger", "drow": "Drow Ranger", "medusa": "Medusa",
    "gyro": "Gyrocopter", "luna": "Luna", "ta": "Templar Assassin",
    "viper": "Viper", "veno": "Venomancer", "jakiro": "Jakiro",
    "ogre": "Ogre Magi", "treant": "Treant Protector", "tree": "Treant Protector",
    "bristle": "Bristleback", "centaur": "Centaur Warrunner", "cw": "Centaur Warrunner",
    "mars": "Mars", "snapfire": "Snapfire", "snap": "Snapfire",
    "hood": "Hoodwink", "hoodwink": "Hoodwink", "grim": "Grimstroke",
    "grimstroke": "Grimstroke", "earth": "Earth Spirit", "faceless": "Faceless Void",
    "bane": "Bane", "necrophos": "Necrophos", "necro": "Necrophos",
    "pugna": "Pugna", "leshrac": "Leshrac", "lesh": "Leshrac",
    "kunkka": "Kunkka", "alch": "Alchemist", "alchemist": "Alchemist",
    "clinkz": "Clinkz", "spectre": "Spectre", "troll": "Troll Warlord",
    "magnus": "Magnus", "brew": "Brewmaster", "brewmaster": "Brewmaster",
    "shaman": "Shadow Shaman", "ss": "Shadow Shaman"
}

async def descargar_imagen_heroe(session, hero_name_api):
    hero_key = hero_name_api.replace('npc_dota_hero_', '')
    url = f"https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/{hero_key}.png"
    
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.read()
                img = Image.open(BytesIO(data))
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                return img, True
    except Exception:
        pass
    
    width, height = 180, 100
    img = Image.new('RGBA', (width, height), color=(40, 40, 50, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([5, 5, width-5, height-5], fill=(60, 60, 80, 255))
    
    iniciales = hero_key[:2].upper()
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), iniciales, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    draw.text((x, y), iniciales, fill=(200, 200, 200, 255), font=font)
    
    return img, False

async def generar_imagen_contrapicks(contrapicks):
    img_width = 280
    img_height = 160
    padding = 20
    
    cols = 5
    total_width = cols * (img_width + padding) + padding
    total_height = img_height + padding + 75
    
    mosaic = Image.new('RGBA', (total_width, total_height), color=(30, 30, 40, 255))
    draw = ImageDraw.Draw(mosaic)
    
    try:
        font_titulo = ImageFont.truetype("arial.ttf", 28)
        font_winrate = ImageFont.truetype("arial.ttf", 24)
    except:
        font_titulo = ImageFont.load_default()
        font_winrate = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), "⚔️ MEJORES CONTRAPICKS", font=font_titulo)
    text_width = bbox[2] - bbox[0]
    text_x = (total_width - text_width) // 2
    draw.text((text_x, 10), "⚔️ MEJORES CONTRAPICKS", fill=(255, 215, 0, 255), font=font_titulo)
    
    async with aiohttp.ClientSession() as session:
        for idx, (hero_id, winrate) in enumerate(contrapicks):
            hero = heroes_dict.get(hero_id)
            if not hero:
                continue
            
            x = padding + idx * (img_width + padding)
            y = 50
            
            img, _ = await descargar_imagen_heroe(session, hero['name'])
            img = img.resize((img_width, img_height), Image.Resampling.LANCZOS)
            mosaic.paste(img, (x, y), img)
            
            draw.rectangle([x, y, x + img_width, y + img_height], 
                          outline=(255, 215, 0, 255), width=4)
            
            winrate_text = f"{winrate:.1f}%"
            bbox = draw.textbbox((0, 0), winrate_text, font=font_winrate)
            text_width = bbox[2] - bbox[0]
            text_x = x + (img_width - text_width) // 2
            text_y = y + img_height + 12
            draw.text((text_x, text_y), winrate_text, fill=(255, 215, 0, 255), font=font_winrate)
    
    output = BytesIO()
    mosaic_rgb = Image.new('RGB', mosaic.size, (30, 30, 40))
    mosaic_rgb.paste(mosaic, mask=mosaic.split()[3] if mosaic.mode == 'RGBA' else None)
    mosaic_rgb.save(output, "PNG", compress_level=1, optimize=False)
    output.seek(0)
    
    return output

async def generar_imagen_enemigos(enemigos_ids):
    img_width = 280
    img_height = 160
    padding = 20
    
    cols = len(enemigos_ids)
    total_width = cols * (img_width + padding) + padding
    total_height = img_height + padding + 50
    
    mosaic = Image.new('RGBA', (total_width, total_height), color=(30, 30, 40, 255))
    draw = ImageDraw.Draw(mosaic)
    
    try:
        font_titulo = ImageFont.truetype("arial.ttf", 28)
    except:
        font_titulo = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), "👹 HÉROES ENEMIGOS", font=font_titulo)
    text_width = bbox[2] - bbox[0]
    text_x = (total_width - text_width) // 2
    draw.text((text_x, 10), "👹 HÉROES ENEMIGOS", fill=(255, 100, 100, 255), font=font_titulo)
    
    async with aiohttp.ClientSession() as session:
        for idx, hero_id in enumerate(enemigos_ids):
            hero = heroes_dict.get(hero_id)
            if not hero:
                continue
            
            x = padding + idx * (img_width + padding)
            y = 50
            
            img, _ = await descargar_imagen_heroe(session, hero['name'])
            img = img.resize((img_width, img_height), Image.Resampling.LANCZOS)
            mosaic.paste(img, (x, y), img)
            
            draw.rectangle([x, y, x + img_width, y + img_height], 
                          outline=(255, 0, 0, 255), width=4)
    
    output = BytesIO()
    mosaic_rgb = Image.new('RGB', mosaic.size, (30, 30, 40))
    mosaic_rgb.paste(mosaic, mask=mosaic.split()[3] if mosaic.mode == 'RGBA' else None)
    mosaic_rgb.save(output, "PNG", compress_level=1, optimize=False)
    output.seek(0)
    
    return output

async def obtener_contrapicks(heroe_ids):
    contrapicks_scores = {}
    contrapicks_games = {}
    
    async with aiohttp.ClientSession() as session:
        for heroe_id in heroe_ids:
            try:
                url = f"https://api.opendota.com/api/heroes/{heroe_id}/matchups"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for matchup in data[:30]:
                            hero_contra = matchup['hero_id']
                            
                            if hero_contra not in heroe_ids:
                                wins = matchup.get('wins', 0)
                                games = matchup.get('games_played', 0)
                                
                                if hero_contra not in contrapicks_scores:
                                    contrapicks_scores[hero_contra] = 0
                                    contrapicks_games[hero_contra] = 0
                                
                                contrapicks_scores[hero_contra] += wins
                                contrapicks_games[hero_contra] += games
                                
            except Exception as e:
                continue
    
    winrates = {}
    for hero_id, wins in contrapicks_scores.items():
        games = contrapicks_games.get(hero_id, 0)
        if games > 0:
            winrates[hero_id] = (wins / games) * 100
        else:
            winrates[hero_id] = 0
    
    mejores = sorted(winrates.items(), key=lambda x: x[1], reverse=True)
    return mejores[:5]

def nombre_a_id(nombre_texto):
    global heroes_dict

    print("LEN:", len(heroes_dict))

    nombre = nombre_texto.strip().lower()

    for hero_id, hero in heroes_dict.items():
        api = hero["localized_name"].strip().lower()

        if api == nombre:
            return hero_id

    return None

# ============================================
# AUTOCOMPLETADO GENERICO (SIN ERRORES)
# ============================================

async def autocompletar_heroes(interaction: Interaction, texto_actual: str):
    texto_actual = texto_actual.lower().strip()
    
    if not texto_actual:
        return NOMBRES_HEROES[:25]
    
    sugerencias = []
    for nombre in NOMBRES_HEROES:
        if texto_actual in nombre.lower():
            sugerencias.append(nombre)
            if len(sugerencias) >= 25:
                break
    
    if not sugerencias:
        sugerencias = NOMBRES_HEROES[:25]
    
    return sugerencias

# ============================================
# COMANDO COUNTER CON 5 CAMPOS
# ============================================

@bot.slash_command(name="counter", description="Muestra los 5 mejores contrapicks para hasta 5 héroes")
async def counter(
    interaction: Interaction,
    heroe1: str = SlashOption(
        name="heroe1",
        description="Primer héroe enemigo",
        required=True
    ),
    heroe2: str = SlashOption(
        name="heroe2",
        description="Segundo héroe enemigo (opcional)",
        required=False
    ),
    heroe3: str = SlashOption(
        name="heroe3",
        description="Tercer héroe enemigo (opcional)",
        required=False
    ),
    heroe4: str = SlashOption(
        name="heroe4",
        description="Cuarto héroe enemigo (opcional)",
        required=False
    ),
    heroe5: str = SlashOption(
        name="heroe5",
        description="Quinto héroe enemigo (opcional)",
        required=False
    )
):
    await interaction.response.defer()
    
    try:
        heroes_input = [heroe1]
        if heroe2:
            heroes_input.append(heroe2)
        if heroe3:
            heroes_input.append(heroe3)
        if heroe4:
            heroes_input.append(heroe4)
        if heroe5:
            heroes_input.append(heroe5)
        
        numeros_procesados = []
        nombres_validos = []
        
        for nombre in heroes_input:
            print(f"RECIBIDO: {repr(nombre)}")

            hero_id = nombre_a_id(nombre)

            if hero_id:
                numeros_procesados.append(hero_id)
                nombres_validos.append(nombre)
            else:
                await interaction.followup.send(f"❌ No se encontró el héroe: **{nombre}**")
                return
        
        if not numeros_procesados:
            await interaction.followup.send("❌ No se encontraron héroes válidos.")
            return
        
        if len(numeros_procesados) > 5:
            await interaction.followup.send(f"⚠️ **Máximo 5 héroes.** Tienes {len(numeros_procesados)}.")
            return
        
        await interaction.followup.send("🔄 **Buscando los mejores contrapicks...**")
        mensaje = await interaction.original_message()
        
        contrapicks = await obtener_contrapicks(numeros_procesados)
        
        if not contrapicks:
            await mensaje.edit(content="❌ No se encontraron contrapicks para estos héroes")
            return
        
        imagen_enemigos = await generar_imagen_enemigos(numeros_procesados)
        file_enemigos = nextcord.File(imagen_enemigos, filename="enemigos.png")
        
        embed_enemigos = nextcord.Embed(color=0xff0000)
        embed_enemigos.set_image(url="attachment://enemigos.png")
        
        await mensaje.delete()
        await interaction.followup.send(embed=embed_enemigos, file=file_enemigos)
        
        imagen_contrapicks = await generar_imagen_contrapicks(contrapicks)
        file_contrapicks = nextcord.File(imagen_contrapicks, filename="contrapicks.png")
        
        enemigos_str = ', '.join(nombres_validos)
        
        embed_contrapicks = nextcord.Embed(
            title="⚔️ MEJORES CONTRAPICKS",
            description=f"👹 **Enemigos:** {enemigos_str}",
            color=0x3498db
        )
        embed_contrapicks.set_image(url="attachment://contrapicks.png")
        embed_contrapicks.set_footer(text="Basado en estadísticas de OpenDota | Datos de partidas reales")
        
        await interaction.followup.send(embed=embed_contrapicks, file=file_contrapicks)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}")

# ============================================
# REGISTRAR AUTOCOMPLETADO PARA CADA CAMPO
# ============================================

@counter.on_autocomplete("heroe1")
async def autocompletar_heroe1(interaction: Interaction, texto_actual: str):
    sugerencias = await autocompletar_heroes(interaction, texto_actual)
    await interaction.response.send_autocomplete(sugerencias)

@counter.on_autocomplete("heroe2")
async def autocompletar_heroe2(interaction: Interaction, texto_actual: str):
    sugerencias = await autocompletar_heroes(interaction, texto_actual)
    await interaction.response.send_autocomplete(sugerencias)

@counter.on_autocomplete("heroe3")
async def autocompletar_heroe3(interaction: Interaction, texto_actual: str):
    sugerencias = await autocompletar_heroes(interaction, texto_actual)
    await interaction.response.send_autocomplete(sugerencias)

@counter.on_autocomplete("heroe4")
async def autocompletar_heroe4(interaction: Interaction, texto_actual: str):
    sugerencias = await autocompletar_heroes(interaction, texto_actual)
    await interaction.response.send_autocomplete(sugerencias)

@counter.on_autocomplete("heroe5")
async def autocompletar_heroe5(interaction: Interaction, texto_actual: str):
    sugerencias = await autocompletar_heroes(interaction, texto_actual)
    await interaction.response.send_autocomplete(sugerencias)

@bot.slash_command(name="generador", description="Asignar canal generador de salas temporales")
async def generador(
    interaction: Interaction,
    generator: nextcord.VoiceChannel = SlashOption(
        name="generator",
        description="Canal de voz generador",
        channel_types=[ChannelType.voice]
    )
):
    global generator_channel_id
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("No tienes permisos.", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    nuevo_id = generator.id
    old_id = generator_channel_id
    generator_channel_id = nuevo_id
    
    mensaje = f"Canal generador asignado: <#{nuevo_id}>"
    if old_id and old_id != nuevo_id:
        mensaje = f"Canal actualizado: <#{old_id}> ➔ <#{nuevo_id}>"
    
    await interaction.followup.send(mensaje, ephemeral=True)

@bot.slash_command(name="rango", description="Panel de selección de rango de Dota 2")
async def rango(interaction: Interaction):
    ranks = {
        "MedallaHeraldo": PartialEmoji(name="MedallaHeraldo", id=1389344036980265101),
        "MedallaGuardian": PartialEmoji(name="MedallaGuardian", id=1389344040150892674),
        "MedallaCruzado": PartialEmoji(name="MedallaCruzado", id=1389344044089348096),
        "MedallaArconte": PartialEmoji(name="MedallaArconte", id=1389344046261993632),
        "MedallaLeyenda": PartialEmoji(name="MedallaLeyenda", id=1389344030793400451),
        "MedallaAncestro": PartialEmoji(name="MedallaAncestro", id=1389344027815579698),
        "MedallaDivino": PartialEmoji(name="MedallaDivino", id=1389344042076213258),
        "MedallaInmortal": PartialEmoji(name="MedallaInmortal", id=1389344033784201356)
    }
    
    view = View(timeout=None)
    items = list(ranks.items())
    
    for i in range(len(items)):
        nombre, emoji = items[i]
        
        async def make_callback(role_name):
            async def callback(interaction_btn: Interaction):
                member = interaction_btn.user
                guild = interaction_btn.guild
                
                for r in ranks:
                    old = nextcord.utils.get(guild.roles, name=r)
                    if old in member.roles:
                        await member.remove_roles(old)
                
                role = nextcord.utils.get(guild.roles, name=role_name)
                if role:
                    await member.add_roles(role)
                
                await interaction_btn.response.defer()
            return callback
        
        button = Button(label=nombre, emoji=emoji, style=ButtonStyle.primary, row=i // 2)
        button.callback = await make_callback(nombre)
        view.add_item(button)
    
    await interaction.response.send_message("Selecciona tu rango:", view=view, ephemeral=False)

@bot.event
async def on_voice_state_update(member, before, after):
    global generator_channel_id
    if after.channel and after.channel.id == generator_channel_id:
        guild = member.guild
        new_category = await guild.create_category(name=f"# {member.display_name}")

        overwrites_voice = {
            guild.default_role: PermissionOverwrite(connect=True),
            member: PermissionOverwrite(manage_channels=True)
        }
        voice_channel = await guild.create_voice_channel(
            name=f"🎤-AUDIO",
            overwrites=overwrites_voice,
            category=new_category,
            user_limit=5
        )
        await member.move_to(voice_channel)

        overwrites_text = {
            guild.default_role: PermissionOverwrite(read_messages=True, send_messages=True)
        }
        text_channel = await guild.create_text_channel(
            name=f"💬-CHAT",
            overwrites=overwrites_text,
            category=new_category
        )

        async def eliminar_canales_si_vacio():
            while True:
                await asyncio.sleep(0.1)
                if len(voice_channel.members) == 0:
                    try:
                        await voice_channel.delete()
                        await text_channel.delete()
                        await new_category.delete()
                    except:
                        pass
                    break

        bot.loop.create_task(eliminar_canales_si_vacio())

@bot.event
async def on_ready():
    global heroes_dict

    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.opendota.com/api/heroes") as response:
            if response.status == 200:
                heroes = await response.json()
                heroes_dict = {h["id"]: h for h in heroes}

if __name__ == "__main__":
    bot.run(TOKEN)