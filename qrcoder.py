import discord
from discord import app_commands
from discord.ext import commands
import os
import random
import re
import asyncio
import unicodedata
import qrcode
from PIL import Image, ImageDraw
import io

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

def create_dotted_qr(data: str, dot_size: int = 24, spacing: int = 12) -> Image.Image:
    """データからドットスタイルのQRコードImageオブジェクトを生成する"""
    # 💡 Discordに特化した、シンプルでパフォーマンスの良い設定
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H, # 高いエラー訂正レベル
        box_size=1,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    qr_matrix = qr.get_matrix()
    matrix_size = len(qr_matrix)
    
    # 画像サイズを計算
    img_width = matrix_size * spacing
    img_height = matrix_size * spacing
    
    # 画像を作成
    img = Image.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(img)
    
    # QRコードの各モジュールを点として描画
    for y in range(matrix_size):
        for x in range(matrix_size):
            if qr_matrix[y][x]:  # 黒いモジュール
                # 円の中心座標
                center_x = x * spacing + spacing // 2
                center_y = y * spacing + spacing // 2
                
                # 円を描画
                left = center_x - dot_size // 2
                top = center_y - dot_size // 2
                right = center_x + dot_size // 2
                bottom = center_y + dot_size // 2
                
                draw.ellipse([left, top, right, bottom], fill='black')
                
    return img



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
        if q_type.lower() == "dot":
            # 💡 Botが自分で定義した関数を呼び出し、Dotスタイルを描かせる！
            img = create_dotted_qr(link, dot_size=8, spacing=14)
        else:
            # 💡 デフォルトのSquareスタイル
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data(link)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
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









