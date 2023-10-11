import discord
from discord.ext import commands, tasks
import sqlite3

class Autodb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_conn = sqlite3.connect('automod.db')
        self.create_tables()
        self.update_guilds.start()

    def create_tables(self):
        cursor = self.db_conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS server_settings (
                            server_id INTEGER PRIMARY KEY,
                            swear_filter_enabled INTEGER DEFAULT 0
                          )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS caps_filter_settings (
                            server_id INTEGER PRIMARY KEY,
                            enabled INTEGER DEFAULT 0,
                            caps_limit INTEGER DEFAULT 10
                          )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS char_spam_settings (
                            server_id INTEGER PRIMARY KEY,
                            enabled INTEGER DEFAULT 0,
                            char_limit INTEGER DEFAULT 5
                          )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS emoji_spam_settings (
                            server_id INTEGER PRIMARY KEY,
                            enabled INTEGER DEFAULT 0,
                            emoji_limit INTEGER DEFAULT 5
                          )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS image_attachment_settings (
                            server_id INTEGER PRIMARY KEY,
                            enabled INTEGER DEFAULT 0,
                            image_limit INTEGER DEFAULT 3
                          )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS discord_link_settings (
                            server_id INTEGER PRIMARY KEY,
                            enabled INTEGER DEFAULT 0
                          )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS link_filter_settings (
                            server_id INTEGER PRIMARY KEY,
                            enabled INTEGER DEFAULT 0
                          )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS max_char_settings (
                            server_id INTEGER PRIMARY KEY,
                            enabled INTEGER DEFAULT 0,
                            max_chars INTEGER DEFAULT 500
                          )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS mention_filter_settings (
                            server_id INTEGER PRIMARY KEY,
                            enabled INTEGER DEFAULT 0,
                            max_mentions INTEGER DEFAULT 2
                          )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS spam_settings (
                            server_id INTEGER PRIMARY KEY,
                            enabled INTEGER DEFAULT 0,
                            spam_threshold INTEGER DEFAULT 3,
                            spam_time_interval INTEGER DEFAULT 1
                          )""")
        self.db_conn.commit()

    @tasks.loop(minutes=1)
    async def update_guilds(self):
        cursor = self.db_conn.cursor()
        guilds = self.bot.guilds
        for guild in guilds:
            cursor.execute("SELECT * FROM server_settings WHERE server_id = ?", (guild.id,))
            result = cursor.fetchone()
            if not result:
                cursor.execute("INSERT INTO server_settings (server_id, swear_filter_enabled) VALUES (?, ?)", (guild.id, 0))
                cursor.execute("INSERT INTO caps_filter_settings (server_id, enabled, caps_limit) VALUES (?, ?, ?)", (guild.id, 0, 10))
                cursor.execute("INSERT INTO char_spam_settings (server_id, enabled, char_limit) VALUES (?, ?, ?)", (guild.id, 0, 5))
                cursor.execute("INSERT INTO emoji_spam_settings (server_id, enabled, emoji_limit) VALUES (?, ?, ?)", (guild.id, 0, 5))
                cursor.execute("INSERT INTO image_attachment_settings (server_id, enabled, image_limit) VALUES (?, ?, ?)", (guild.id, 0, 3))
                cursor.execute("INSERT INTO discord_link_settings (server_id, enabled) VALUES (?, ?)", (guild.id, 0))
                cursor.execute("INSERT INTO link_filter_settings (server_id, enabled) VALUES (?, ?)", (guild.id, 0))
                cursor.execute("INSERT INTO max_char_settings (server_id, enabled, max_chars) VALUES (?, ?, ?)", (guild.id, 0, 500))
                cursor.execute("INSERT INTO mention_filter_settings (server_id, enabled, max_mentions) VALUES (?, ?, ?)", (guild.id, 0, 2))
                cursor.execute("INSERT INTO spam_settings (server_id, enabled, spam_threshold, spam_time_interval) VALUES (?, ?, ?, ?)", (guild.id, 0, 3, 1))
                self.db_conn.commit()
                print(f"Added {guild.name} ({guild.id}) to the database")



    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT * FROM server_settings WHERE server_id = ?", (guild.id,))
        result = cursor.fetchone()
        if not result:
            cursor.execute("INSERT INTO server_settings (server_id, swear_filter_enabled) VALUES (?, ?)", (guild.id, 0))
            cursor.execute("INSERT INTO caps_filter_settings (server_id, enabled, caps_limit) VALUES (?, ?, ?)", (guild.id, 0, 10))
            cursor.execute("INSERT INTO char_spam_settings (server_id, enabled, char_limit) VALUES (?, ?, ?)", (guild.id, 0, 5))
            cursor.execute("INSERT INTO emoji_spam_settings (server_id, enabled, emoji_limit) VALUES (?, ?, ?)", (guild.id, 0, 5))
            cursor.execute("INSERT INTO image_attachment_settings (server_id, enabled, image_limit) VALUES (?, ?, ?)", (guild.id, 0, 3))
            cursor.execute("INSERT INTO discord_link_settings (server_id, enabled) VALUES (?, ?)", (guild.id, 0))
            cursor.execute("INSERT INTO link_filter_settings (server_id, enabled) VALUES (?, ?)", (guild.id, 0))
            cursor.execute("INSERT INTO max_char_settings (server_id, enabled, max_chars) VALUES (?, ?, ?)", (guild.id, 0, 500))
            cursor.execute("INSERT INTO mention_filter_settings (server_id, enabled, max_mentions) VALUES (?, ?, ?)", (guild.id, 0, 2))
            cursor.execute("INSERT INTO spam_settings (server_id, enabled, spam_threshold, spam_time_interval) VALUES (?, ?, ?, ?)", (guild.id, 0, 3, 1))
            self.db_conn.commit()
            print(f"Added {guild.name} ({guild.id}) to the database")

                            

async def setup(bot):
   await bot.add_cog(Autodb(bot))
