from discord.ext import commands

class HelperBot(commands.Cog):
    def __init__(self):
        print('Starting Helper Bot')

    @commands.command(
        name='help'
    )
    async def help(self, ctx, *commands):
        if len(commands) == 0:
            file_name = 'C:\\Users\Alex\\Desktop\\Coding\\Discord Bot\\sigma-bot\\assets\\help.txt'
        else:
            if commands[0] == 'storage':
                file_name = 'C:\\Users\Alex\\Desktop\\Coding\\Discord Bot\\sigma-bot\\assets\\help_storage.txt'
            else:
                if commands[0] == 'calculate':
                    file_name = 'C:\\Users\Alex\\Desktop\\Coding\\Discord Bot\\sigma-bot\\assets\\help_calculate.txt'
        with open(file_name, 'r') as file:
            data = file.read()
            await ctx.message.channel.send(f'```{data}```')

def setup(bot):
    bot.add_cog(HelperBot())
