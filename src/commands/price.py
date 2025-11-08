from datetime import datetime
from discord.ext import commands

from src.steam import search_steam_game, get_game_price

class Price(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="price")
    async def price(self, ctx, *, game_name: str):
        """Verifica o preço de um ou mais jogos na Steam

        Uso: !price jogo1, jogo2, jogo3
        """
        game_names = [name.strip() for name in game_name.split(',') if name.strip()]
        if not game_names:
            return await ctx.send("⚠️ Informe ao menos um nome de jogo. Ex: `!price Celeste, Hades`")

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
                continue
            found_games.append({"info": info, "price_data": price_data})

        if not found_games:
            return await ctx.send("Não encontrei nenhum desses jogos na Steam. Tente outros nomes.")

        now = datetime.now().strftime("%d/%m/%Y - %H:%M")
        for game in found_games:
            info = game["info"]
            price_data = game["price_data"]
            print(game)
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
    await bot.add_cog(Price(bot))
