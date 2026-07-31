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
STRATZ_TOKEN = os.getenv("STRATZ_TOKEN")

intents = nextcord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

generator_channel_id = None
heroes_dict = {}
items_dict = {}

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
    return mejores[:3]

async def obtener_items_stratz(heroe_id, enemigos_ids):
    if not STRATZ_TOKEN:
        return None
    
    url = f"https://api.stratz.com/api/v1/Hero/{heroe_id}/matchups"
    
    headers = {
        "Authorization": f"Bearer {STRATZ_TOKEN}"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    items_early = {}
                    items_mid = {}
                    items_late = {}
                    
                    for matchup in data.get('matchups', []):
                        if matchup['heroId'] in enemigos_ids:
                            for item in matchup.get('earlyGameItems', []):
                                item_id = item['itemId']
                                popularity = item.get('popularity', 0)
                                items_early[item_id] = items_early.get(item_id, 0) + popularity
                            
                            for item in matchup.get('midGameItems', []):
                                item_id = item['itemId']
                                popularity = item.get('popularity', 0)
                                items_mid[item_id] = items_mid.get(item_id, 0) + popularity
                            
                            for item in matchup.get('lateGameItems', []):
                                item_id = item['itemId']
                                popularity = item.get('popularity', 0)
                                items_late[item_id] = items_late.get(item_id, 0) + popularity
                    
                    early = sorted(items_early.items(), key=lambda x: x[1], reverse=True)[:4]
                    mid = sorted(items_mid.items(), key=lambda x: x[1], reverse=True)[:4]
                    late = sorted(items_late.items(), key=lambda x: x[1], reverse=True)[:4]
                    
                    return {
                        'early': early,
                        'mid': mid,
                        'late': late
                    }
    except Exception as e:
        print(f"Error en Stratz API: {e}")
    
    return None

async def obtener_items_opendota(heroe_id):
    try:
        url = f"https://api.opendota.com/api/heroes/{heroe_id}/itemPopularity"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    early = sorted(data.get('early_game', {}).items(), key=lambda x: x[1], reverse=True)[:4]
                    mid = sorted(data.get('mid_game', {}).items(), key=lambda x: x[1], reverse=True)[:4]
                    late = sorted(data.get('late_game', {}).items(), key=lambda x: x[1], reverse=True)[:4]
                    
                    return {
                        'early': [(int(item_id), popularity * 100) for item_id, popularity in early],
                        'mid': [(int(item_id), popularity * 100) for item_id, popularity in mid],
                        'late': [(int(item_id), popularity * 100) for item_id, popularity in late]
                    }
    except Exception as e:
        print(f"Error en OpenDota items: {e}")
    
    return None

def nombre_a_id(nombre_texto):
    global heroes_dict
    nombre = nombre_texto.strip().lower()
    
    for hero_id, hero in heroes_dict.items():
        api = hero["localized_name"].strip().lower()
        if api == nombre:
            return hero_id
    
    return None

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

async def manejar_autocompletado(interaction: Interaction, texto_actual: str):
    try:
        sugerencias = await autocompletar_heroes(interaction, texto_actual)
        await interaction.response.send_autocomplete(sugerencias)
    except Exception:
        pass

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

# ============================================
# COMANDO COUNTER - DEFINITIVO (SIN EMBED DE 5 HÉROES)
# ============================================

@bot.slash_command(name="counter", description="Muestra contrapicks y guía de items para counterear")
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
    try:
        await interaction.response.defer()
    except Exception:
        pass
    
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
        
        enemigos_ids = []
        enemigos_nombres = []
        
        for nombre in heroes_input:
            hero_id = nombre_a_id(nombre)
            if hero_id:
                enemigos_ids.append(hero_id)
                enemigos_nombres.append(nombre)
            else:
                await interaction.followup.send(f"❌ No se encontró el héroe: **{nombre}**")
                return
        
        if not enemigos_ids:
            await interaction.followup.send("❌ No se encontraron héroes válidos.")
            return
        
        # Obtener contrapicks (solo 3)
        contrapicks = await obtener_contrapicks(enemigos_ids)
        
        if not contrapicks:
            await interaction.followup.send("❌ No se encontraron contrapicks para estos héroes")
            return
        
        # === 1. ENVIAR IMAGEN DE ENEMIGOS ===
        imagen_enemigos = await generar_imagen_enemigos(enemigos_ids)
        file_enemigos = nextcord.File(imagen_enemigos, filename="enemigos.png")
        embed_enemigos = nextcord.Embed(color=0xff0000)
        embed_enemigos.set_image(url="attachment://enemigos.png")
        await interaction.followup.send(embed=embed_enemigos, file=file_enemigos)
        
        # === 2. ENVIAR 3 EMBEDS DE CONTRAPICKS ===
        for idx, (hero_id, winrate) in enumerate(contrapicks[:3]):
            hero = heroes_dict.get(hero_id)
            if not hero:
                continue
            
            # Obtener items (Stratz o OpenDota)
            items_guia = await obtener_items_stratz(hero_id, enemigos_ids)
            if not items_guia:
                items_guia = await obtener_items_opendota(hero_id)
            
            embed = nextcord.Embed(
                title=f"🛡️ {hero['localized_name']}",
                color=0x00ff00
            )
            
            embed.add_field(name="📊 Winrate", value=f"{winrate:.1f}%", inline=False)
            
            if items_guia:
                early_text = ""
                for item_id, popularity in items_guia['early']:
                    if isinstance(item_id, int):
                        item_name = items_dict.get(item_id, f"Item {item_id}")
                    else:
                        item_name = items_dict.get(int(item_id), f"Item {item_id}")
                    early_text += f"• **{item_name}** ({popularity:.1f}%)\n"
                if early_text:
                    embed.add_field(name="🌱 Early Game", value=early_text, inline=True)
                
                mid_text = ""
                for item_id, popularity in items_guia['mid']:
                    if isinstance(item_id, int):
                        item_name = items_dict.get(item_id, f"Item {item_id}")
                    else:
                        item_name = items_dict.get(int(item_id), f"Item {item_id}")
                    mid_text += f"• **{item_name}** ({popularity:.1f}%)\n"
                if mid_text:
                    embed.add_field(name="⚔️ Mid Game", value=mid_text, inline=True)
                
                late_text = ""
                for item_id, popularity in items_guia['late']:
                    if isinstance(item_id, int):
                        item_name = items_dict.get(item_id, f"Item {item_id}")
                    else:
                        item_name = items_dict.get(int(item_id), f"Item {item_id}")
                    late_text += f"• **{item_name}** ({popularity:.1f}%)\n"
                if late_text:
                    embed.add_field(name="🔥 Late Game", value=late_text, inline=True)
            
            # Descargar imagen del héroe como thumbnail
            async with aiohttp.ClientSession() as session:
                img, _ = await descargar_imagen_heroe(session, hero['name'])
                img_bytes = BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                file = nextcord.File(img_bytes, filename=f"hero_{idx}.png")
                embed.set_thumbnail(url=f"attachment://hero_{idx}.png")
                
                await interaction.followup.send(embed=embed, file=file)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}")

@counter.on_autocomplete("heroe1")
async def autocompletar_heroe1(interaction: Interaction, texto_actual: str):
    await manejar_autocompletado(interaction, texto_actual)

@counter.on_autocomplete("heroe2")
async def autocompletar_heroe2(interaction: Interaction, texto_actual: str):
    await manejar_autocompletado(interaction, texto_actual)

@counter.on_autocomplete("heroe3")
async def autocompletar_heroe3(interaction: Interaction, texto_actual: str):
    await manejar_autocompletado(interaction, texto_actual)

@counter.on_autocomplete("heroe4")
async def autocompletar_heroe4(interaction: Interaction, texto_actual: str):
    await manejar_autocompletado(interaction, texto_actual)

@counter.on_autocomplete("heroe5")
async def autocompletar_heroe5(interaction: Interaction, texto_actual: str):
    await manejar_autocompletado(interaction, texto_actual)

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
    global heroes_dict, items_dict
    
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.opendota.com/api/heroes") as response:
            if response.status == 200:
                heroes = await response.json()
                heroes_dict = {h["id"]: h for h in heroes}
        
        async with session.get("https://api.opendota.com/api/constants/items") as response:
            if response.status == 200:
                items_data = await response.json()
                items_dict = {}
                for item_id, item_data in items_data.items():
                    try:
                        item_id_int = int(item_id)
                        items_dict[item_id_int] = item_data.get('dname', item_id)
                    except ValueError:
                        items_dict[item_id] = item_data.get('dname', item_id)
    
    print(f"✅ Bot conectado como {bot.user}")
    print(f"✅ {len(heroes_dict)} héroes cargados")
    print(f"✅ {len(items_dict)} items cargados")
    
    try:
        await bot.sync_all_application_commands()
        print("✅ Comandos slash sincronizados")
    except Exception as e:
        print(f"⚠️ Error al sincronizar comandos: {e}")

if __name__ == "__main__":
    bot.run(TOKEN)
