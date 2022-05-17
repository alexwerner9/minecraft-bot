import json
import os
import fnmatch
import math
from dotenv import load_dotenv

from discord.ext import commands

load_dotenv()
RECIPES_PATH = os.getenv('RECIPES_PATH')

class ResourcesBot(commands.Cog):
    def __init__(self):
        print('Starting Resources Bot')
        self.calculating = False

    @commands.command(
        name='calculate'
    )
    async def calculate(self, ctx, *items):
        self.calculating = True
        self.totals = {}
        if len(items) > 0:
            await self._main_calculate(ctx, *items)
            await self._stop_calculating(ctx)
            return
        await ctx.message.channel.send('Ready to calculate. Enter resources like this: `!c 21 anvil`, and then press enter. When finished, use `!stop`')


    @commands.command(
        name='c'
    )
    async def c(self, ctx, *resources):
        await self._main_calculate(ctx, *resources)


    async def _main_calculate(self, ctx, *resources):
        if not self.calculating:
            await ctx.message.channel.send(f'Please enable calculating with `!calculate`')
            return
        if len(resources) > 2 and resources[2] == 'override':
            self.totals[f'minecraft:{resources[1]}'] = int(resources[0])
            await self._confirm_message(ctx.message)
            return
        resources_dict = self._parse_resources(resources)
        for wanted_item in resources_dict:
            files = self._check_item_path(wanted_item)
            valid_item = await self._check_files(files, ctx, wanted_item, resources_dict)
            if not valid_item:
                continue
            recipe_json = self._load_recipe_json(wanted_item)
            wanted_item_count = int(resources_dict[wanted_item])
            self._calculate_resource(wanted_item_count, recipe_json)

            await self._confirm_message(ctx.message)


    async def _check_files(self, files, ctx, wanted_item, resources_dict):
        if len(files) == 0:
            self.override_item = [wanted_item, resources_dict[wanted_item]]
            if wanted_item[-1] == 's':
                response = f'No crafting recipes for {wanted_item}. I see there\'s an \"s\" at the end - try making it singular.\nTo add to your list anyways, use `!override`'
            else:
                response = f'No crafting recipes for {wanted_item}. Too add to your list anyways, use `!override`'
            await ctx.message.channel.send(response)
            return False
        if len(files) > 1:
            file_str = ''
            for file in files:
                file_str += f'{file}\n'
            await ctx.message.channel.send(f'**Multiple results for {wanted_item}:**\n```{file_str}```')
            return False
        return True


    async def _confirm_message(self, message):
        emoji = '\N{THUMBS UP SIGN}'
        await message.add_reaction(emoji)


    @commands.command(
        name='override'
    )
    async def override(self, ctx):
        item = f'minecraft:{self.override_item[0]}'
        count = int(self.override_item[1])
        if item not in self.totals:
            self.totals[item] = count
        else:
            self.totals[item] += count
        await ctx.message.channel.send(f'**Added {self.override_item[0]} anyways.**')


    @commands.command(
        name='search'
    )
    async def search_for_resource(self, ctx, item):
        result = []
        pattern = f'*{item}*'
        for root, dirs, files in os.walk(RECIPES_PATH):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    result.append(name[:-5])
        if len(result) == 0:
            response = '**No items match your search**'
        else:
            result_str = ''
            for file in result:
                result_str += f'{file}\n'
            response = f'**Matching items:**```\n{result_str}```'
        await ctx.message.channel.send(response)


    @commands.command(
        name='stop'
    )
    async def stop_calculating(self, ctx):
        await self._stop_calculating(ctx)


    async def _stop_calculating(self, ctx):
        result_str = ''
        for key in self.totals:
            key_str = key[10:]
            value = int(math.ceil(self.totals[key]))
            if value == 0:
                continue
            stacks = int(math.floor(value / 64))
            remainder = value % 64
            if stacks == 0:
                result_str += f'{key_str}: {remainder} individual\n'
            else:
                result_str += f'{key_str}: {stacks} stacks, {remainder} individual ({value} total)\n'
        await ctx.message.channel.send(f'**Resources needed:**\n```{result_str}```')
        self.calculating = False


    def _check_item_path(self, item):
        result = []
        pattern = f'*{item}*'
        for root, dirs, files in os.walk(RECIPES_PATH):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    result.append(name[:-5])
                    if name[:-5] == item:
                        return [name]
        if len(result) == 1 and result[0] is not item:
            return []
        return result


    def _parse_resources(self, resources):
        res = {}
        for i in range(1, len(resources)):
            if i%2 == 0:
                continue
            mat = resources[i]
            num = resources[i-1]
            res[mat] = num

        return res

    
    def _calculate_resource(self, number, recipe_json):
        if recipe_json['type'] == 'minecraft:crafting_shaped':
            pattern = recipe_json['pattern']
            key_map = {}
            for key, needed_item in recipe_json['key'].items():
                try:
                    key_map[key] = needed_item['item']
                except Exception:
                    key_map[key] = needed_item['tag']
            for key in key_map:
                item_name = key_map[key]
                if item_name not in self.totals:
                    self.totals[item_name] = 0
                for row in pattern:
                    self.totals[item_name] += row.count(key) * number
                try:
                    count = recipe_json['result']['count']
                except Exception:
                    count = 1
                self.totals[item_name] /= count

        if recipe_json['type'] == 'minecraft:crafting_shapeless':
            ing = ''
            it = ''
            try:
                i = recipe_json['ingredients']
                ing = 'ingredients'
            except Exception:
                ing = 'ingredient'
            try:
                j = recipe_json[ing]
                i = recipe_json[ing][0]['tag']
                it = 'tag'
            except Exception:
                it = 'item'
            for item in recipe_json[ing]:
                length = len(recipe_json[ing])
                n = recipe_json[ing][0][it]
                if item[it] not in self.totals:
                    self.totals[item[it]] = 1 * number
                else:
                    self.totals[item[it]] += 1 * number
                try:
                    count = recipe_json['result']['count']
                except Exception:
                    count = 1
                self.totals[item[it]] /= count

        if recipe_json['type'] == 'minecraft:smelting':
            try:
                self.totals[recipe_json['ingredient']['tag']] = 1 * number
            except Exception:
                self.totals[recipe_json['ingredient']['item']] = 1 * number


    def _load_recipe_json(self, item):
        path = f'{RECIPES_PATH}{item}.json'
        file = open(path)
        recipe_json = json.load(file)
        return recipe_json

def setup(bot):
    bot.add_cog(ResourcesBot())
