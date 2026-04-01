import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

RANKS = [
    (0, 1000, "F"),
    (1000, 10000, "E"),
    (10000, 20000, "D"),
    (20000, 50000, "C"),
    (50000, 100000, "B"),
    (100000, 500000, "A"),
    (500000, 1000000, "S"),
    (1000000, 5000000, "National"),
    (5000000, 10000000, "Low Monarch"),
    (10000000, 50000000, "High Monarch"),
    (50000000, float('inf'), "Shadow Monarch")
]

user_xp = {}

def get_rank(xp):
    for low, high, rank in RANKS:
        if low <= xp < high:
            return rank
    return "F"

def xp_bar(xp, current_rank, bar_length=20):
    low, high, _ = next((low, high, r) for low, high, r in RANKS if r == current_rank)
    filled_length = int((xp - low) / (high - low) * bar_length)
    return "█" * filled_length + "░" * (bar_length - filled_length)

def create_xp_image(player_name, xp_gained, current_rank, avatar_url, total_xp):
    background = Image.open("background_horizontal.png").convert("RGBA")
    width, height = background.size
    response = requests.get(avatar_url)
    avatar = Image.open(BytesIO(response.content)).convert("RGBA")
    avatar = avatar.resize((100, 100))
    avatar_x = (width - 100)//2
    avatar_y = 150
    background.paste(avatar, (avatar_x, avatar_y), avatar)
    draw = ImageDraw.Draw(background)
    font_name = ImageFont.truetype("arialbd.ttf", 50)
    font_bar = ImageFont.truetype("arialbd.ttf", 35)
    font_msg = ImageFont.truetype("arialbd.ttf", 45)
    name_text = player_name
    name_w, name_h = draw.textsize(name_text, font=font_name)
    draw.text(((width - name_w)//2, 40), name_text, font=font_name, fill=(255, 215, 0))
    bar_text = xp_bar(total_xp, current_rank)
    bar_w, bar_h = draw.textsize(bar_text, font=font_bar)
    draw.text(((width - bar_w)//2, avatar_y + 110), f"XP BAR: {bar_text}", font=font_bar, fill=(255, 255, 255))
    msg_text = f"XP GAINED: +{xp_gained} | CURRENT RANK: {current_rank}"
    msg_w, msg_h = draw.textsize(msg_text, font=font_msg)
    draw.text(((width - msg_w)//2, height//2 - msg_h//2), msg_text, font=font_msg, fill=(255, 215, 0))
    path = f"{player_name}_xp.png"
    background.save(path)
    return path

@bot.command()
async def addxp(ctx, amount: int):
    uid = ctx.author.id
    user_xp[uid] = user_xp.get(uid, 0) + amount
    rank = get_rank(user_xp[uid])
    image_path = create_xp_image(str(ctx.author), amount, rank, ctx.author.avatar.url, user_xp[uid])
    await ctx.send(file=discord.File(image_path))

bot.run(TOKEN)
