#Server Invite URL
#https://discord.com/api/oauth2/authorize?client_id=1051683005472702465&permissions=8&scope=bot
import os
import discord

token = os.getenv('DISCORD_TOKEN')  #Your TOKEN
global_channel_name = "neko-global-chat"  #設定したいチャンネル名を入力

client = discord.Client(intents=discord.Intents.default())  #接続に必要なオブジェクトを生成


@client.event
async def on_message(message):
  if message.channel.name == global_channel_name:  #グローバルチャットにメッセージが来たとき
    #メッセージ受信部
    if message.author.bot:  #BOTの場合は何もせず終了
      return
    #メッセージ送信部
    for channel in client.get_all_channels():  #BOTが所属する全てのチャンネルをループ
      if channel.name == global_channel_name:  #グローバルチャット用のチャンネルが見つかったとき
        if channel == message.channel:  #発言したチャンネルには送らない
          continue

        embed = discord.Embed(
          description=message.content,
          color=0x9B95C9)  #埋め込みの説明に、メッセージを挿入し、埋め込みのカラーを紫`#9B95C9`に設定        
          embed.set_author(name=message.author.name,icon_url="https://media.discordapp.net  /avatars/{}/{}.png?size=1024".format(message.author.id, message.author.avatar))

        await channel.send(embed=embed)

    await message.add_reaction('✅')


client.run(TOKEN)
