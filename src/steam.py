import os
import aiohttp

GGDEALS_API_KEY = os.getenv("GGDEALS_API_KEY")

async def search_steam_game(query: str):
    url = "https://store.steampowered.com/api/storesearch/"
    params = {"term": query, "l": "portuguese", "cc": "BR"}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get("items", [])
                    if items:
                        return {
                            "id": items[0].get("id"),
                            "name": items[0].get("name"),
                            "type": items[0].get("type"),
                        }
        except Exception:
            return None
    return None

async def get_game_price(app_id: int):
    url = f"https://api.gg.deals/v1/prices/by-steam-app-id/"
    params = {"ids": app_id, "key": GGDEALS_API_KEY, "region": "br"}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and str(app_id) in data.get("data", {}):
                        return data["data"][str(app_id)]
        except Exception:
            return None
    return None
