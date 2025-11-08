from datetime import datetime
from discord.ext import commands
import discord
from howlongtobeatpy import HowLongToBeat

from src.steam import search_steam_game, get_game_price

def convert_min_to_hours(time):
    time = float(time)

    if time < 1: 
        minutes = int(time * 60)
        return f"{minutes} min"
    else: 
        return f"{time:.1f}h"

class Info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="info")
    async def info(self, ctx, *, game_name: str):

        game_names = [name.strip() for name in game_name.split(',') if name.strip()]
        if not game_names:
            return await ctx.send("⚠️ Informe ao menos um nome de jogo. Ex: `!info Celeste, Hades`")

        await ctx.send(f"🔍 Procurando **{len(game_names)}** jogo(s) na Steam...")

        found_games = []
        not_found = []

        for name in game_names:
            info = await search_steam_game(name)
            if not info:
                not_found.append(name)
                continue
            price_data = await get_game_price(info["id"]) if info else None
            if not price_data:
                not_found.append(name)
                
            hltb_data = await HowLongToBeat().async_search(name)
            if hltb_data:
                game = hltb_data[0]
                info["main_story"] = game.main_story
                info["main_extra"] = game.main_extra
            found_games.append({"info": info, "price_data": price_data})

        if not found_games:
            return await ctx.send("Não encontrei nenhum desses jogos na Steam. Tente outros nomes.")

        now = datetime.now().strftime("%d/%m/%Y - %H:%M")

        embed = discord.Embed(title="Info dos jogos", color=0x00ff00)

        for game in found_games:
            info = game["info"]
            price_data = game["price_data"]
            app_id = info["id"]
            game_title = info.get("name")

            prices = price_data.get("prices", {})
            current_retail = prices.get("currentRetail", "N/A")
            current_keyshops = prices.get("currentKeyshops", "N/A")

            historical_retail = prices.get("historicalRetail", "N/A")
            historical_keyshops = prices.get("historicalKeyshops", "N/A")

            embed.add_field(name=f"🎮 {game_title}", value="", inline=False)
            
            value_retail = f"🏪 **Preço atual (Lojas oficiais)**\nR$ {current_retail}\n\n"
            value_retail += f"📊 **Menor preço histórico (Lojas oficiais)**\nR$ {historical_retail}"
            embed.add_field(name="\u200b", value=value_retail, inline=True)

            value_keys = f"🔑 **Preço atual (Key Shops)**\nR$ {current_keyshops}\n\n"
            value_keys += f"🔑 **Menor preço histórico (Key Shops)**\nR$ {historical_keyshops}"
            embed.add_field(name="\u200b", value=value_keys, inline=True)

            embed.add_field(name="Tempo de conclusão história principal (HLTB)", value=f"{convert_min_to_hours(info.get('main_story', 0))}", inline=False)
            embed.add_field(name="Tempo de conclusão história principal + extra (HLTB)", value=f"{convert_min_to_hours(info.get('main_extra', 0))}", inline=False)

            gg_deals_url = price_data.get("url", "")
            if gg_deals_url:
                embed.add_field(name="🔗 Veja mais", value=f"[GG.deals]({gg_deals_url}) • [Steam](https://store.steampowered.com/app/{app_id}/)\n\n", inline=False)
            
            embed.add_field(name="\u200b", value="──────────────────────", inline=False)

        embed.set_footer(text=f"Obs: Lojas oficiais: Steam, Epic Games, GOG etc\nEncontrados {len(found_games)} de {len(game_names)} jogos • Atualizado em {now}")
        await ctx.send(embed=embed)

        if not_found:
            not_found_list = ", ".join(f"**{n}**" for n in not_found)
            await ctx.send(f"Não encontrei: {not_found_list}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))
