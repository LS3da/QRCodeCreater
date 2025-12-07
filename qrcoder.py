import discord
from discord import app_commands
from discord.ext import commands
import os
import random
import re
import asyncio
import unicodedata
import qrcode
from PIL import Image
import io
from qrcode.image.styles import DotStyle, SquareStyle

# 💡 Botの基本設定: 必要最小限の権限
bot = commands.Bot(command_prefix=' ', intents=discord.Intents.default())

# ======================= Bot起動時のイベント =======================
@bot.event
async def on_ready():
    print(f'Login OK: {bot.user} (ID: {bot.user.id})')
    # 💡 スラッシュコマンドをDiscordに同期させる
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)}個のスラッシュコマンドを同期しました。")
    except Exception as e:
        print(f"スラッシュコマンドの同期に失敗しました: {e}")
# ================================================================

# ======================= ここからがスラッシュコマンドです =======================

# /createqrコマンド：QRコードを生成
@bot.tree.command(name="createqr", description="リンクからQRコードを生成します。")
@app_commands.describe(
    link="QRコードに埋め込むリンクやテキスト（必須）",
    q_type="デザインタイプ（square:四角/dot:点）。デフォルトは四角です。"
)
async def createqr_slash(interaction: discord.Interaction, link: str, q_type: str = "square"):
    
    await interaction.response.defer(thinking=True, ephemeral=False)
    
    try:
        # 1. QRコードジェネレーターの準備
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(link)
        qr.make(fit=True)
        
        # 2. デザインの適用と画像生成
        if q_type.lower() == "dot":
            # 💡 DotStyle クラスを直接使用する
            img = qr.make_image(image_factory=DotStyle)
        else:
            # 💡 SquareStyle クラス（または、そのままの書き方）
            # Botが読み込みミスをしないように、SquareStyleも直接使う形式に修正
            img = qr.make_image(image_factory=SquareStyle, fill_color="black", back_color="white")
            
        # 3. 画像をメモリに保存
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # 4. Discordにアップロード
        file = discord.File(buffer, filename="qrcode.png")
        
        await interaction.followup.send(
            f"✅ **QRコード生成完了！**\n埋め込みリンク: `{link}`",
            file=file
        )
        
    except Exception as e:
        print(f"QRコード生成エラー: {e}")
        await interaction.followup.send("ごめんなさい、QRコードの生成中にエラーが発生しました。", ephemeral=True)

# ============================================================================

# Botの起動
bot.run(os.environ['DISCORD_BOT_TOKEN'])


