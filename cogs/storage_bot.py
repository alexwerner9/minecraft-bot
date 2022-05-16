import os

from dotenv import load_dotenv
import mysql.connector
from discord.ext import commands

class StorageBot(commands.Cog):
    def __init__(self, bot, mysql_user=None, mysql_pass=None):
        print('Starting Storage Bot')
        self.db = self._connect_to_mysql(mysql_user, mysql_pass)
        self.cursor = self.db.cursor(buffered=True)
        self._create_databases()


    def _connect_to_mysql(self, mysql_user, mysql_pass):
        print(f'User {mysql_user}, Pass {mysql_pass}')
        database = mysql.connector.connect(
            host="localhost",
            user=mysql_user,
            password=mysql_pass,
            port=3306,
            database="main"
        )
        return database


    def _store_data(self, table, columns, values):
        columns_string = ""
        for column in columns:
            columns_string += f'{column}, '
        columns_string = columns_string[:-2]
        for i in range(len(values)):
            if i%len(columns) == 0:
                value_string = ""
                for f in range(len(columns)):
                    value_string += f'\'{values[i]}\', '
                    i += 1
                value_string = value_string[:-2]
                query = f'INSERT INTO {table} ({columns_string}) VALUES ({value_string})'
                print(query)
                self.cursor.execute(query)
                self.db.commit()


    def _create_databases(self):
        table_name = 'var_storage'
        table_schema = 'id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), value VARCHAR(255)'
        self.cursor.execute(f'SHOW TABLES LIKE \"{table_name}\"')
        table_already_exists = False
        for x in self.cursor:
            table_already_exists = True
            break
        if table_already_exists:
            print(f'Table {table_name} already exists!')
        else:
            query = f"""CREATE TABLE {table_name} ({table_schema})"""
            self.cursor.execute(query)


    def _retrieve_data(self, name):
        query = f'SELECT value FROM var_storage WHERE name=\"{name}\"'
        self.cursor.execute(query)


    @commands.command(
        name='store'
    )
    async def store(self, ctx, *command_args):
        value = ""
        for arg in command_args[1:]:
            value += f'{arg} '
        value = value[:-1]
        name = command_args[0]
        self._store_data('var_storage', ['name', 'value'], [name, value])
        channel = ctx.message.channel
        await channel.send(f'Stored \"{name}\"')


    @commands.command(
        name='retrieve'
    )
    async def retrieve(self, ctx, name):
        self._retrieve_data(name)
        user = ctx.message.author
        channel = ctx.message.channel
        response = ''
        for x in self.cursor:
            result = x[0]
            response += f'{name}: {result}\n'
        if len(response) < 1:
            await channel.send(f'No results for \"{name}\"')
            return
        await channel.send(f'```{response}```')
        

    @commands.command(
        name='delete',
        pass_context=True
    )
    async def delete(self, ctx, name):
        query = f'DELETE FROM var_storage WHERE name=\"{name}\"'
        self.cursor.execute(query)
        self.db.commit()
        channel = ctx.message.channel
        await channel.send(f"Deleted \"{name}\"")


    @commands.command(
        name='listall',
        pass_context=True
    )
    async def list_all(self, context):
        query = "SELECT name, value FROM var_storage"
        self.cursor.execute(query)
        response = 'All available data:\n```'
        for res in self.cursor:
            x = res[0]
            y = res[1]
            response += f'{x}: {y}\n'
        response = f'{response[:-2]}```'
        channel = context.message.channel
        await channel.send(response)


def setup(bot):
    load_dotenv()
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_PASS = os.getenv('MYSQL_PASS')
    bot.add_cog(StorageBot(bot, MYSQL_USER, MYSQL_PASS))
