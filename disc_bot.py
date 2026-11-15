import io
import ccxt
import discord
from discord.ext import commands
import matplotlib.pyplot as plt

# Your Bot Token
TOKEN = "MTU3MTQ0NTYwNjg1MjA3NTU1MA.GYybQK.1arlF96ShoZq7CvQCBkpHpL7fYcgSOqxQgOQxs"

# Setup bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize CCXT for Binance
exchange = ccxt.binance({"enableRateLimit": True})


@bot.event
async def on_ready():
  print(f"Logged in successfully as {bot.user.name}!")


@bot.command(name="price", help="Shows live prices for BTC, ETH, and SOL")
async def price(ctx):
  try:
    symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    response_msg = "📊 **Live Crypto Market Prices:**\n"

    for symbol in symbols:
      ticker = exchange.fetch_ticker(symbol)
      price_val = ticker["last"]
      coin_name = symbol.split("/")[0]
      response_msg += f"• **{coin_name}:** `${price_val:,.2f} USD`\n"

    await ctx.send(response_msg)

  except Exception as e:
    await ctx.send(f"⚠️ Error fetching prices: `{str(e)}`")


@bot.command(name="chart", help="Generates a price chart (e.g., !chart BTC)")
async def chart(ctx, coin: str = "BTC"):
  try:
    coin = coin.upper()
    symbol = f"{coin}/USDT"

    # Fetch recent OHLCV (candlestick) history data from Binance
    # fetches up to the last 24 hourly candles
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe="1h", limit=24)

    # Extract timestamps and closing prices
    timestamps = [
        discord.utils.snowflake_time(ctx.message.id)  # placeholder or index
        for _ in ohlcv
    ]
    prices = [candle[4] for candle in ohlcv]  # Close price is at index 4
    hours = [f"{i}h ago" for i in range(len(prices), 0, -1)]

    # Generate the Matplotlib chart
    plt.figure(figsize=(8, 4))
    plt.plot(
        hours,
        prices,
        marker="o",
        color="#2ecc71" if prices[-1] >= prices[0] else "#e74c3c",
        linewidth=2,
    )
    plt.title(f"24-Hour Price Trend for {coin}/USDT", fontsize=12, color="white")
    plt.xlabel("Timeframe", fontsize=10, color="white")
    plt.ylabel("Price (USD)", fontsize=10, color="white")

    # Dark theme styling to match Discord
    plt.gca().set_facecolor("#313338")
    plt.gcf().patch.set_facecolor("#313338")
    plt.xticks(color="white", rotation=45)
    plt.yticks(color="white")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()

    # Save plot to an in-memory bytes buffer (avoids disk space clutter)
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", dpi=100)
    buffer.seek(0)
    plt.close()

    # Send the image file straight into Discord
    file = discord.File(buffer, filename=f"{coin}_chart.png")
    await ctx.send(
        content=f"📈 Here is the latest 24h trend chart for **{coin}**:",
        file=file,
    )

  except Exception as e:
    await ctx.send(
        f"⚠️ Error generating chart for `{coin}`. Make sure it's valid (e.g.,"
        f" `!chart BTC`): `{str(e)}`"
    )


# Run the bot
bot.run(TOKEN)