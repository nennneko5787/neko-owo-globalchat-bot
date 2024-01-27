# Server Invite URL
# https://discord.com/api/oauth2/authorize?client_id=1051683005472702465&permissions=8&scope=bot
import os
import discord
from discord import Interaction, Message
from server import keep_alive
from discord.ext import tasks
import asyncio
from supabase import create_client, Client
import datetime
import time
from collections import defaultdict

fuck = time.time()-8

spamtaisaku = defaultdict(lambda: fuck)

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)
data = supabase.auth.sign_in_with_password({"email": os.environ.get("SUPABASE_EMAIL"), "password": os.environ.get("SUPABASE_PASS")})

last_commit_dt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
last_commit_date = last_commit_dt.strftime('%Y/%m/%d %H:%M:%S')

global_channel_name = "neko-global-chat"  # 設定したいチャンネル名を入力
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True
intents.members = True

client = discord.Client(intents=intents)  # 接続に必要なオブジェクトを生成
tree = discord.app_commands.CommandTree(client) #←ココ

@client.event
async def on_guild_join(guild):
	channel = await guild.create_text_channel("neko-global-chat")
	embed = discord.Embed(title="neko's global chat Botを導入していただきありがとうございます。",description="早速このチャンネルで挨拶をしてみましょう！",color=0xda70d6)
	await channel.send("",embed=embed)

@tree.context_menu(name="ユーザー情報を取得")
async def user(interaction: Interaction, message: Message):
	await interaction.response.defer()
	if message.channel.name == "neko-global-chat":
		# カーソルをオープンします
		response = supabase.table('message').select("*").eq('message', message.id).execute()
		query_result = response.data[0]
		channel = client.get_channel(int(query_result["raw_channel"]))
		msg = await channel.fetch_message(int(query_result["raw_message"]))
		user = msg.author
		embed = discord.Embed(title="",description="",color=user.color)
		embed.set_author(name=f"{user.name}の情報",icon_url=user.display_avatar.url)
		embed.add_field(name="参加中のサーバー",value=user.guild.name)
		embed.add_field(name="このサーバーに参加した日時",value=user.joined_at.astimezone(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y/%m/%d %H:%M:%S.%f'))
		embed.add_field(name="Discordに登録した日時",value=user.created_at.astimezone(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y/%m/%d %H:%M:%S.%f'))
		await interaction.followup.send("",embed=embed,ephemeral=True)
	else:
		await interaction.followup.send("そこは グローバルチャットの チャンネルでは ない！")


@tree.context_menu(name="サーバー情報を取得")
async def user(interaction: Interaction, message: Message):
	await interaction.response.defer()
	if message.channel.name == "neko-global-chat":
		response = supabase.table('message').select("*").eq('message', message.id).execute()
		query_result = response.data[0]
		channel = client.get_channel(int(query_result["raw_channel"]))
		msg = await channel.fetch_message(int(query_result["raw_message"]))
		guild = msg.guild
		embed = discord.Embed(title="",description="",color=0xda70d6)
		embed.set_author(name=f"{guild.name}の情報",icon_url=guild.icon.url)
		embed.add_field(name="参加人数",value=guild.member_count)
		true_member_count = len([m for m in guild.members if not m.bot])
		embed.add_field(name="Botを除いた人数",value=true_member_count)
		embed.add_field(name="サーバーの説明",value=guild.description)
		embed.add_field(name="サーバーの作成日時",value=guild.created_at.astimezone(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y/%m/%d %H:%M:%S.%f'))
		await interaction.followup.send("",embed=embed,ephemeral=True)
	else:
		await interaction.followup.send("そこは グローバルチャットの チャンネルでは ない！")

@tree.context_menu(name="メッセージを削除(管理用)")
async def user(interaction: Interaction, message: Message):
	await interaction.response.defer()
	if interaction.user.id == 1048448686914551879:
		if message.channel.name == "neko-global-chat":
			response = supabase.table('message').select("*").eq('message', message.id).execute()
			query_result = response.data[0]

			response = supabase.table('message').select("*").eq('raw_message', query_result["raw_message"]).execute()
			query_result = response.data[0]

			msgid = message.id

			for dic in query_result:
				if int(dic["message"]) != msgid:
					channel = client.get_channel(int(dic["channel"]))
					msg = await channel.fetch_message(int(dic["message"]))
					await msg.delete()
			await message.delete()
			await interaction.followup.send("削除しました。")
		else:
			await interaction.followup.send("そこは グローバルチャットの チャンネルでは ない！")
	else:
		await interaction.followup.send("You don't have permission!",ephemeral=True)

@client.event
async def on_message_delete(message):
	if message.channel.name == "neko-global-chat":
		response = supabase.table('message').select("*").eq('message', message.id).execute()
		query_result = response.data[0]

		response = supabase.table('message').select("*").eq('raw_message', query_result["raw_message"]).execute()
		query_result = response.data[0]

		for dic in query_result:
			if int(dic["message"]) != message.id:
				channel = client.get_channel(int(dic["channel"]))
				msg = await channel.fetch_message(int(dic["message"]))
				await msg.delete()

@tree.command(name="servers",description="get servers list")
async def test_command(interaction: discord.Interaction):
	if interaction.user.id != 1048448686914551879:
		await interaction.response.send_message("You don't have permission!",ephemeral=True)
		return
	
	await interaction.response.defer()
	embed = discord.Embed(title="servers list",description="",color=0xda70d6)
	for guild in client.guilds:
		true_member_count = len([m for m in guild.members if not m.bot])
		embed.add_field(name=f"{guild.name}({true_member_count} / {guild.member_count})",value=guild.owner.name)
	await interaction.followup.send("",embed=embed,ephemeral=True)


@tree.command(name="generate",description="Loop all guilds, If #neko-global-chat channel is not found, then create #neko-global-chat channel.")
async def test_command(interaction: discord.Interaction):
	if interaction.user.id != 1048448686914551879:
		await interaction.response.send_message("You don't have permission!",ephemeral=True)
		return
	
	await interaction.response.defer()
	count = 0
	for guild in client.guilds:
		await interaction.channel.send(f"確認中: {guild.name}({guild.id})")
		cnl = discord.utils.get(guild.text_channels, name="neko-global-chat")
		if cnl == None:
			await interaction.channel.send(f"お: {guild.name}({guild.id})")
			try:
				channel = await guild.create_text_channel("neko-global-chat")
				embed = discord.Embed(title="neko's global chat Botを導入していただきありがとうございます。",description="早速このチャンネルで挨拶をしてみましょう！",color=0xda70d6)
				await channel.send("",embed=embed)
				count += 1
				await interaction.channel.send(f"できた: {guild.name}({guild.id})")
			except Exception as e:
				await interaction.channel.send(f"Error(おそらく権限が足りない): {guild.name}({guild.id})")
				if guild.id != 861590137116819486:
					await guild.owner.create_dm()
					embed = discord.Embed(title="neko's global chat botについて",description="こんにちは。あなたのサーバーで、neko's global chat botが正しく導入されていないことが確認されました。\nですので、Discordサーバーにて`neko-global-chat`という名前のテキストチャンネルを作成していただければなと思います。\nこの件についてのお問い合わせは、このDMではなく、**nennneko5787**のDMまでどうぞ。",color=0xda70d6)
					embed.add_field(name="正しく導入されていないことが確認できたサーバー",value=guild.name)
					embed.set_author(name="nennneko5787",icon_url="https://i.imgur.com/zJ094I4.png")
					await guild.owner.dm_channel.send("",embed=embed)
					await interaction.channel.send(f"DMおくった: {guild.name}({guild.id})")
				else:
					await interaction.channel.send(f"ディス速のBot置き場でした: {guild.name}({guild.id})")
		else:
			await interaction.channel.send(f"作る必要なかった: {guild.name}({guild.id})")
	await interaction.followup.send(f"OK, {count}")


@client.event
async def on_message(message):
	if message.author.id == client.user.id:
		return
	if message.channel.name == global_channel_name:  # グローバルチャットにメッセージが来たとき
		# メッセージ受信部
		if message.author.bot:  # BOTの場合は何もせず終了
			return
		if message.guild.id == 1136234915663466496:
			return
		if message.content.find("discord.gg") != -1 or message.content.find("discord.com/invite/") != -1 or message.content.find("dsc.gg") != -1:
			await message.author.create_dm()
			embed = discord.Embed(title="エラーが発生しました。",description="禁止ワードが含まれています",color=discord.Colour.red())
			await message.author.dm_channel.send("",embed=embed)
			return
		if (time.time() - spamtaisaku[f"{message.author.id}"]) <= 8:
			await message.author.create_dm()
			otintin = (time.time() - spamtaisaku[f"{message.author.id}"])
			embed = discord.Embed(title="エラーが発生しました。",description=f"スパムは禁止です。あと{8 - otintin}秒待ってからもう一度メッセージを送信してさい。",color=discord.Colour.red())
			await message.author.dm_channel.send("",embed=embed)
			return
		spamtaisaku[f"{message.author.id}"] = time.time()
		datas = {
			"message": message.id,
			"channel": message.channel.id,
			"guild": message.guild.id,
			"raw_message": message.id,
			"raw_channel": message.channel.id,
			"raw_guild": message.guild.id,
		}
		data, count = supabase.table('message').insert(datas).execute()
		# メッセージ送信部
		for channel in client.get_all_channels():  # BOTが所属する全てのチャンネルをループ
			try:
				if channel.name == global_channel_name:  # グローバルチャット用のチャンネルが見つかったとき
					if channel != message.channel:  # 発言したチャンネルには送らない
						await channel.typing()
						embed = discord.Embed(
							description=message.content,
							color=message.author.colour,
							url="https://owo-neko-globalchat-bot.onrender.com/?message={}&channel={}&guild={}".format(
								message.id,
								message.channel.id,
								message.guild.id
							),
						)  # 埋め込みの説明に、メッセージを挿入し、埋め込みのカラーを紫`#9B95C9`に設定
						if (message.author.id == 1048448686914551879) or (
							message.author.id == 1026050624556638208
						):
							isAdmin = "🛠️"
						else:
							isAdmin = ""
						if message.author.discriminator != "0":
							name = "{}#{}".format(
								message.author.name, message.author.discriminator
							)
						else:
							name = "{}".format(message.author.name)

						if message.author.display_name is not name:
							embed.set_author(
								name="{}({}) {}".format(
									message.author.display_name, name, isAdmin
								),
								icon_url=message.author.display_avatar.url,
							)
						else:
							embed.set_author(
								name="{} {}".format(name, isAdmin),
								icon_url=message.author.display_avatar.url,
							)

						jst_datetime = message.created_at.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
						embed.set_footer(
							text="{} | {}".format(
								message.guild.name,
								jst_datetime.strftime("%Y/%m/%d %H:%M:%S")
							),
							icon_url=message.guild.icon,
						)

						if message.reference:  # 返信メッセージであるとき
							reference_msg = await message.channel.fetch_message(
								message.reference.message_id
							)  # メッセージIDから、元のメッセージを取得
							if (
								reference_msg.embeds and reference_msg.author == client.user
							):  # 返信の元のメッセージが、埋め込みメッセージかつ、このBOTが送信したメッセージのとき→グローバルチャットの他のサーバーからのメッセージと判断
								reference_message_content = reference_msg.embeds[
									0
								].description  # メッセージの内容を埋め込みから取得
								reference_message_author = reference_msg.embeds[
									0
								].author.name  # メッセージのユーザーを埋め込みから取得
							elif (
								reference_msg.author != client.user
							):  # 返信の元のメッセージが、このBOTが送信したメッセージでは無い時→同じチャンネルのメッセージと判断
								reference_message_content = (
									reference_msg.content
								)  # メッセージの内容を取得
								reference_message_author = (
									reference_msg.author.name
									+ "#"
									+ reference_msg.author.discriminator
								)  # メッセージのユーザーを取得
							reference_content = ""
							for (
								string
							) in (
								reference_message_content.splitlines()
							):  # 埋め込みのメッセージを行で分割してループ
								reference_content += (
									"> " + string + "\n"
								)  # 各行の先頭に`> `をつけて結合
							reference_value = "**@{}**\n{}".format(
								reference_message_author, reference_content
							)  # 返信メッセージを生成
							embed.add_field(
								name="返信しました", value=reference_value, inline=True
							)  # 埋め込みに返信メッセージを追加
						embeds = []
						embeds.append(embed)
						if message.attachments != []:  # 添付ファイルが存在するとき
							for tenpura in message.attachments:  # 全ての添付ファイルをループ
								embed2 = discord.Embed(
									url="https://owo-neko-globalchat-bot.onrender.com/?message={}&channel={}&guild={}".format(
										message.id,
										message.channel.id,
										message.guild.id
									),
								)  # 埋め込みの説明
								embed2.set_image(url=tenpura)
								embeds.append(embed2)
								embed.add_field(
									name="📎添付ファイル", value=tenpura.url, inline=True
								)  # 埋め込みに添付ファイルのリンクを追加
						if message.stickers != []:  # スタンプが存在するとき
							for tenpura in message.stickers:  # 全てのスタンプをループ
								embed2 = discord.Embed(
									url="https://owo-neko-globalchat-bot.onrender.com/?message={}&channel={}&guild={}".format(
										message.id,
										message.channel.id,
										message.guild.id
									),
								)  # 埋め込みの説明
								embed2.set_image(url=tenpura.url)
								embeds.append(embed2)
								embed.add_field(
									name="🖍️スタンプ", value=tenpura.url, inline=True
								)  # 埋め込みにスタンプのリンクを追加
						if (
							channel.permissions_for(channel.guild.me).send_messages
							is True
						):
							newmsg = await channel.send(embeds=embeds)  # メッセージを送信

						datas = {
							"message": newmsg.id,
							"channel": newmsg.channel.id,
							"guild": newmsg.guild.id,
							"raw_message": message.id,
							"raw_channel": message.channel.id,
							"raw_guild": message.guild.id,
						}
						data, count = supabase.table('message').insert(datas).execute()
			except Exception as e:  # work on python 3.x
				print(
					"サーバーID[{}]({})にて{}エラーが発生したため、処理をスキップします。".format(
						channel.id, channel.guild.name, str(e)
					)
				)
				continue

		await message.add_reaction("✅")
		await asyncio.sleep(5)
		await message.remove_reaction("✅", client.user)

@client.event
async def on_reaction_add(reaction, user):
	if user != reaction.message.guild.me:
		response = supabase.table('message').select("*").eq('message', reaction.message.id).execute()
		query_result = response.data[0]

		response = supabase.table('message').select("*").eq('raw_message', query_result["raw_message"]).execute()
		query_result = response.data

		for dic in query_result:
			if int(dic["message"]) != reaction.message.id:
				channel = client.get_channel(int(dic["channel"]))
				msg = await channel.fetch_message(int(dic["message"]))
				await msg.add_reaction(reaction.emoji)

@client.event
async def on_reaction_remove(reaction, user):
	if user != reaction.message.guild.me:
		if reaction.count <= 0:
			response = supabase.table('message').select("*").eq('message', reaction.message.id).execute()
			query_result = response.data[0]

			if reaction.message.id == query_result["raw_message"]:
				response = supabase.table('message').select("*").eq('raw_message', query_result["raw_message"]).execute()
				query_result = response.data

				for dic in query_result:
					if int(dic["message"]) != reaction.message.id:
						channel = client.get_channel(int(dic["channel"]))
						msg = await channel.fetch_message(int(dic["message"]))
						await msg.remove_reaction(reaction.emoji,msg.guild.me)

# 起動時に動作する処理
@client.event
async def on_ready():
	await tree.sync()
	reloadPresence.start()


@tasks.loop(seconds=20)
async def reloadPresence():
	await client.change_presence(
		activity=discord.Game(
			name="#neko-global-chat | {} Servers | deployed: {}".format(
				len(client.guilds),
				last_commit_date
			)
		)
	)

keep_alive()
token = os.getenv("DISCORD_TOKEN_NEKOGLOBALCHAT")  # Your TOKEN
client.run(token)