# Server Invite URL
# https://discord.com/api/oauth2/authorize?client_id=1051683005472702465&permissions=8&scope=bot
import os
import discord
from server import keep_alive
from discord.ext import tasks
import asyncio
import psycopg2
from psycopg2.extras import DictCursor
import datetime

# データベースとのコネクションを確立します。
connection = psycopg2.connect(
	"host={} dbname={} user={} password={}".format(
		os.getenv("db_host"),
		os.getenv("db_name"),
		os.getenv("db_user"),
		os.getenv("db_pass"),
	)
)

last_commit_dt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
last_commit_date = last_commit_dt.strftime('%Y/%m/%d %H:%M:%S.%f')

global_channel_name = "neko-global-chat"  # 設定したいチャンネル名を入力
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True

client = discord.Client(intents=intents)  # 接続に必要なオブジェクトを生成

@client.event
async def on_guild_join(guild):
	await guild.create_text_channel("neko-global-chat")


@client.event
async def on_message(message):
	# カーソルをオープンします
	cursor = connection.cursor()
	if message.channel.name == global_channel_name:  # グローバルチャットにメッセージが来たとき
		# メッセージ受信部
		if message.author.bot:  # BOTの場合は何もせず終了
			return
		if message.guild.id == 1136234915663466496:
			return
		sql = "INSERT INTO message (message, channel, guild, raw_message, raw_channel, raw_guild) VALUES (%s, %s, %s, %s, %s, %s)"
		cursor.execute(sql, (message.id, message.channel.id, message.guild.id, message.id, message.channel.id, message.guild.id))
		connection.commit()
		# メッセージ送信部
		for channel in client.get_all_channels():  # BOTが所属する全てのチャンネルをループ
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
							icon_url=message.author.avatar,
						)
					else:
						embed.set_author(
							name="{} {}".format(name, isAdmin),
							icon_url=message.author.avatar,
						)

					jst_datetime = message.created_at.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
					embed.set_footer(
						text="{} | {} | mID:{} | guildID:{}".format(
							message.guild.name,
							jst_datetime.strftime("%Y/%m/%d %H:%M:%S.%f"),
							message.id,
							message.guild.id,
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
					try:
						if (
							channel.permissions_for(channel.guild.me).send_messages
							is True
						):
							newmsg = await channel.send(embeds=embeds)  # メッセージを送信

						sql = "INSERT INTO message (message, channel, guild, raw_message, raw_channel, raw_guild) VALUES (%s, %s, %s, %s, %s, %s)"
						cursor.execute(sql, (newmsg.id, newmsg.channel.id, newmsg.guild.id, message.id, message.channel.id, message.guild.id))
						connection.commit()
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
		cursor.close()

@client.event
async def on_reaction_add(reaction, user):
	# カーソルをオープンします
	cursor1 = connection.cursor(cursor_factory=DictCursor)
	cursor2 = connection.cursor(cursor_factory=DictCursor)
	if user != reaction.message.guild.me:
		try:
			query = (reaction.message.id,)
			cursor1.execute("SELECT * FROM message WHERE message = %s",query)
			query_result = cursor1.fetchone()
			cursor1.close()

			que = (query_result["raw_message"],)
			cursor2.execute("SELECT * FROM message WHERE raw_message = %s",que)
			query_result = cursor2.fetchall()
			cursor2.close()

			for dic in query_result:
				if int(dic["message"]) != reaction.message.id:
					channel = client.get_channel(int(dic["channel"]))
					msg = await channel.fetch_message(int(dic["message"]))
					await msg.add_reaction(reaction.emoji)

		except Exception as e:  # work on python 3.x
			print(
				"エラー {}".format(
					str(e)
				)
			)

@client.event
async def on_reaction_remove(reaction, user):
	# カーソルをオープンします
	cursor1 = connection.cursor(cursor_factory=DictCursor)
	cursor2 = connection.cursor(cursor_factory=DictCursor)
	if user != reaction.message.guild.me:
		try:
			query = (reaction.message.id,)
			cursor1.execute("SELECT * FROM message WHERE message = %s",query)
			query_result = cursor1.fetchone()
			connection.commit()
			cursor1.close()
			await asyncio.sleep(1)

			que = (query_result["raw_message"],)
			cursor2.execute("SELECT * FROM message WHERE raw_message = %s",que)
			query_result = cursor2.fetchall()
			connection.commit()
			cursor2.close()
			await asyncio.sleep(1)
			
			for dic in query_result:
				if int(dic["message"]) != reaction.message.id:
					channel = client.get_channel(int(dic["channel"]))
					msg = await channel.fetch_message(int(dic["message"]))
					await msg.remove_reaction(reaction.emoji)

		except Exception as e:  # work on python 3.x
			print(
				"エラー {}".format(
					str(e)
				)
			)

# 起動時に動作する処理
@client.event
async def on_ready():
	reloadPresence.start()


@tasks.loop(seconds=20)
async def reloadPresence():
	await client.change_presence(
		activity=discord.Game(
			name="#neko-global-chat | deployed: {} | {} Servers".format(
				last_commit_date,
				len(client.guilds)
			)
		)
	)

keep_alive()
token = os.getenv("DISCORD_TOKEN_NEKOGLOBALCHAT")  # Your TOKEN
client.run(token)