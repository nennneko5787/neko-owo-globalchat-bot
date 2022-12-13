#Server Invite URL
#https://discord.com/api/oauth2/authorize?client_id=1051683005472702465&permissions=8&scope=bot
import os
import discord
try:
	from discordtoken import token
except ImportError:
	token = os.getenv('DISCORD_TOKEN_NEKOGLOBALCHAT')  #Your TOKEN
from server import keep_alive
global_channel_name = "neko-global-chat"  #設定したいチャンネル名を入力
intents=discord.Intents.default()
intents.message_content=True

client = discord.Client(intents=intents)  #接続に必要なオブジェクトを生成

@client.event
async def on_message(message):
    if message.channel.name == global_channel_name: #グローバルチャットにメッセージが来たとき
        #メッセージ受信部
        if message.author.bot: #BOTの場合は何もせず終了
            return
        #メッセージ送信部
        for channel in client.get_all_channels(): #BOTが所属する全てのチャンネルをループ
            if channel.name == global_channel_name: #グローバルチャット用のチャンネルが見つかったとき
                if channel == message.channel: #発言したチャンネルには送らない
                    continue
                    
                embed=discord.Embed(description=message.content, color=0x9B95C9) #埋め込みの説明に、メッセージを挿入し、埋め込みのカラーを紫`#9B95C9`に設定
                embed.set_author(name="{}#{}".format(message.author.name, message.author.discriminator),icon_url=message.author.avatar)
                embed.set_footer(text="{} / mID:{}".format(message.guild.name, message.id),icon_url=message.guild.icon)
                if message.attachments != []: #添付ファイルが存在するとき
                    embed.set_image(url=message.attachments[0].url)

                if message.reference: #返信メッセージであるとき
                    reference_msg = await message.channel.fetch_message(message.reference.message_id) #メッセージIDから、元のメッセージを取得
                    if reference_msg.embeds and reference_msg.author == client.user: #返信の元のメッセージが、埋め込みメッセージかつ、このBOTが送信したメッセージのとき→グローバルチャットの他のサーバーからのメッセージと判断
                        reference_message_content = reference_msg.embeds[0].description #メッセージの内容を埋め込みから取得
                        reference_message_author = reference_msg.embeds[0].author.name #メッセージのユーザーを埋め込みから取得
                    elif reference_msg.author != client.user: #返信の元のメッセージが、このBOTが送信したメッセージでは無い時→同じチャンネルのメッセージと判断
                        reference_message_content = reference_msg.content #メッセージの内容を取得
                        reference_message_author = reference_msg.author.name+'#'+reference_msg.author.discriminator #メッセージのユーザーを取得
                    reference_content = ""
                    for string in reference_message_content.splitlines(): #埋め込みのメッセージを行で分割してループ
                        reference_content += "> " + string + "\n" #各行の先頭に`> `をつけて結合
                    reference_value = "**@{}**\n{}".format(reference_message_author, reference_content) #返信メッセージを生成
                    embed.add_field(name='返信しました', value=reference_value, inline=True) #埋め込みに返信メッセージを追加
                    
                await channel.send(embed=embed) #メッセージを送信
        await message.add_reaction('✅') #リアクションを送信

keep_alive()
client.run(token)