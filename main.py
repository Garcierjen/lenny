import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import subprocess
import io

load_dotenv()
token = os.getenv('token')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

@bot.command()
async def obf(ctx):
    if not ctx.message.attachments:
        await ctx.send("lua file pls")
        return

    attachment = ctx.message.attachments[0]
    file_bytes = await attachment.read()
    
    input_filename = f"temp_{ctx.author.id}.lua"
    output_filename = f"obf_{ctx.author.id}.lua"
    with open(input_filename, "wb") as f:
        f.write(file_bytes)

    try:
        result = subprocess.run(
            ["prometheus-lua", "--preset", "Strong", input_filename, "--o", output_filename],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or "Unknown error"
            await ctx.send(f"failed:\n```rs\n{error_msg[:1900]}```")
            return
        if os.path.exists(output_filename) and os.path.getsize(output_filename) > 0:
            with open(output_filename, "rb") as f:
                output_bytes = f.read()
        elif result.stdout:
            output_bytes = result.stdout.encode('utf-8')
        else:
            await ctx.send("Obfuscation completed, but no output data was generated.")
            return

        file_data = io.BytesIO(output_bytes)
        output_file =discord.File(fp=file_data, filename=f"obf_{attachment.filename}")

        await ctx.send("Here is your shi:", file=output_file)

    except Exception as e:
        await ctx.send(f"An error occurred: `{e}`")

    finally:
        for filename in [input_filename, output_filename]:
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except OSError:
                    pass

bot.run(token, log_handler=handler, log_level=logging.DEBUG)