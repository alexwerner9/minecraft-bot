import json
import os
import fnmatch
import math

from discord.ext import commands

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
        await ctx.message.channel.send('Ready to calculate. Enter resources like this: `!c 21 anvil`, and then press enter. When finished, use `!stop_calculating`')


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
        for resource in resources_dict:
            files = self._check_item_path(resource)
            if len(files) == 0:
                self.override_item = [resource, resources_dict[resource]]
                if resource[-1] == 's':
                    response = f'No crafting recipes for {resource}. I see there\'s an \"s\" at the end - try making it singular.\nTo add to your list anyways, use `!override`'
                else:
                    response = f'No crafting recipes for {resource}. Too add to your list anyways, use `!override`'
                await ctx.message.channel.send(response)
                return
            if len(files) > 1:
                file_str = ''
                for file in files:
                    file_str += f'{file}\n'
                await ctx.message.channel.send(f'**Multiple results for {resource}:**\n```{file_str}```')
                return
            num_resources, block = self._calculate_resource(resource, int(resources_dict[resource]))
            if block:
                remainder = int(resources_dict[resource]) % 9
                if resource not in num_resources and remainder != 0:
                    num_resources[f'minecraft:{resource}'] = int(resources_dict[resource]) % 9
                else:
                    if remainder == 0:
                        num_resources.pop(resource)

            for r in num_resources:
                if r not in self.totals:
                    self.totals[r] = num_resources
                else:
                    self.totals[r] += num_resources[r]
            await self._confirm_message(ctx.message)


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
        for root, dirs, files in os.walk('C:\\Users\\Alex\Desktop\\Coding\\Discord bot\\sigma-bot\\assets\\recipes\\'):
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
                result_str += f'{key_str}: {stacks} stacks, {remainder} individual\n'
        await ctx.message.channel.send(f'**Resources needed:**\n```{result_str}```')
        self.calculating = False


    def _check_item_path(self, item):
        result = []
        pattern = f'*{item}*'
        for root, dirs, files in os.walk('C:\\Users\\Alex\Desktop\\Coding\\Discord bot\\sigma-bot\\assets\\recipes\\'):
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

    
    def _calculate_resource(self, resource, number):
        file_name = f'C:\\Users\\Alex\Desktop\\Coding\\Discord bot\\sigma-bot\\assets\\recipes\\{resource}.json'
        file = open(file_name)
        recipe_json = json.load(file)
        if recipe_json['type'] == 'minecraft:crafting_shaped':
            pattern = recipe_json['pattern']
            items = {}
            items_dict = {}
            for key, value in recipe_json['key'].items():
                try:
                    items_dict[key] = value['item']
                except Exception:
                    items_dict[key] = value['tag']
            for short in items_dict:
                if items_dict[short] not in items:
                    items[items_dict[short]] = 0
                for row in pattern:
                    items[items_dict[short]] += row.count(short) * number
                try:
                    count = recipe_json['result']['count']
                except Exception:
                    count = 1
                block = 'block' in recipe_json['result']['item']
                items[items_dict[short]] /= count
                if block:
                    items[items_dict[short]] = math.floor(items[items_dict[short]])
            
            recur_items = []
            deletion_queue = []
            for item in items:
                print(item)
                item_name = item[10:]
                files = self._check_item_path(item_name)
                if len(files) == 1:
                    r, recur_block = self._calculate_resource(item_name, items[item])
                    if recur_block:
                        items[item] = items[item] % 9
                    else:
                        deletion_queue.append(item)
                    recur_items.append(r)
            for recur_item in recur_items:
                for item in recur_item:
                    if item not in items:
                        items[item] = 0
                    items[item] += recur_item[item]
            for d in deletion_queue:
                items.pop(d)
            return items, block

        if recipe_json['type'] == 'minecraft:crafting_shapeless':
            items = {}
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
                if item[it] not in items:
                    items[item[it]] = 1 * number
                else:
                    items[item[it]] += 1 * number
                try:
                    count = recipe_json['result']['count']
                except Exception:
                    count = 1
                items[item[it]] /= count
            block = 'block' in recipe_json[ing][0]['item']
            if block:
                items[item[it]] = math.floor(items[item[it]])
            return items, block

        if recipe_json['type'] == 'minecraft:smelting':
            items = {}
            try:
                items[recipe_json['ingredient']['tag']] = 1 * number
            except Exception:
                items[recipe_json['ingredient']['item']] = 1 * number
            return items, False


def setup(bot):
    bot.add_cog(ResourcesBot())
