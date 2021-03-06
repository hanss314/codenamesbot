import discord
import datetime
import time
import urllib
import os
import random

from discord.ext import commands

IMAGE_PREFIX = "bot_data/images/"

class Misc:
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def format_args(cmd):
        params = list(cmd.clean_params.items())
        p_str = ''
        for p in params:
            print(p[1], p[1].default, p[1].empty)
            if p[1].default == p[1].empty:
                p_str += f' <{p[0]}>'
            else:
                p_str += f' [{p[0]}]'

        return p_str

    def format_commands(self, prefix, cmd, name=None):
        cmd_args = self.format_args(cmd)
        if not name: name = cmd.name
        name = name.replace('  ', ' ')
        d = f'`{prefix}{name}{cmd_args}`\n'

        if type(cmd) == commands.core.Group:
            cmds = sorted(list(cmd.commands), key=lambda x: x.name)
            for subcmd in cmds:
                d += self.format_commands(prefix, subcmd, name=f'{name} {subcmd.name}')

        return d

    def get_help(self, ctx, cmd, name=None):
        d = f'Help for command `{cmd.name}`:\n'
        d += '\n**Usage:**\n'

        d += self.format_commands(ctx.prefix, cmd, name=name)

        d += '\n**Description:**\n'
        d += '{}\n'.format('None' if cmd.help is None else cmd.help.strip())

        if cmd.aliases:
            d += '\n**Aliases:**'
            for alias in cmd.aliases:
                d += f'\n`{ctx.prefix}{alias}`'

            d += '\n'

        return d

    @commands.command()
    @commands.guild_only()
    async def me(self, ctx, member: discord.Member=None):
        """Get info about yourself."""
        if not member: member = ctx.author
        now = datetime.datetime.utcnow()
        joined_days = now - member.joined_at
        created_days = now - member.created_at
        avatar = member.avatar_url

        embed = discord.Embed(colour=member.colour)
        embed.add_field(name='Nickname', value=member.display_name)
        embed.add_field(name='User ID', value=member.id)
        embed.add_field(name='Avatar', value='[Click here to show]({})'.format(avatar))

        embed.add_field(name='Created',
                        value=member.created_at.strftime('%x %X') + '\n{} days ago'.format(max(0, created_days.days)))
        embed.add_field(name='Joined',
                        value=member.joined_at.strftime('%x %X') + '\n{} days ago'.format(max(0, joined_days.days)))
        roles = '\n'.join(
            [r.mention for r in sorted(member.roles, key=lambda x: x.position, reverse=True) if r.name != '@everyone'])
        if roles == '': roles = '\@everyone'
        embed.add_field(name='Roles', value=roles)

        embed.set_author(name=member, icon_url=avatar)

        try:
            await ctx.channel.send(embed=embed)
        except discord.Forbidden:
            pass

    @commands.command()
    async def invite(self, ctx):
        """Invite me to your server!"""
        await ctx.send(
            '*Invite me to your server:* ' +
            f'<https://discordapp.com/oauth2/authorize?client_id={ctx.bot.user.id}&scope=bot>'
        )

    @commands.command(aliases=['ping'])
    async def latency(self, ctx):
        """View websocket and message send latency."""

        rtt_before = time.monotonic()
        message = await ctx.send('Ping...')
        rtt_after = time.monotonic()
        rtt_latency = round((rtt_after - rtt_before) * 1000)

        await message.edit(content=f'WS: **{ctx.bot.latency*1000:.0f} ms**\nRTT: **{rtt_latency} ms**')

    @commands.command(aliases=['g'])
    async def google(self, ctx, *, query: str):
        """Google for a query"""
        op = urllib.parse.urlencode({'q': query})
        await ctx.send(f'https://google.com/search?{op}&safe=active')

    @commands.command()
    async def about(self, ctx):
        """About the bot"""
        d = 'This bot was made by *hanss314#0128*\n' \
            'Source code can be found at <https://github.com/hanss314/Okuu>\n' \
            f'Use {ctx.prefix}help for help'

        await ctx.send(d)

    @commands.command()
    async def dab(self, ctx):
        """Dab at the haters"""
        await ctx.send('<:nueDab:404506021114150922>')

    @commands.command(aliases=['i', 'img'])
    async def image(self, ctx, image):
        """Get an image"""
        directory = IMAGE_PREFIX + image
        if os.path.isdir(directory) or os.path.islink(directory):
            f = os.listdir(directory)
            if not f: return await ctx.send('Unyu? I can\'t find that image.')
            f = random.choice()
            f = os.path.join(directory, f)
            await ctx.send(file=discord.File(f))
        else:
            images = [i for i in os.listdir(IMAGE_PREFIX) if i.endswith('.png') or i.endswith('.jpg')]
            images = [i for i in images if image in i.split('.')[0]]
            if not images: return await ctx.send('Unyu? I can\'t find that image.')
            for i in images:
                if image == i.split('.')[0]:
                    f = os.path.join(IMAGE_PREFIX, i)
                    return await ctx.send(file=discord.File(f))

            f = os.path.join(IMAGE_PREFIX, random.choice(images))
            await ctx.send(file=discord.File(f))

    @commands.command()
    async def asakura(self, ctx):
        """A Sakura"""
        await ctx.send(file=discord.File('bot_data/images/sakura.png'))

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def hackban(self, ctx, user_id: int, *, reason=''):
        """Ban a user by ID"""
        user = discord.Object(user_id)
        try:
            await ctx.guild.ban(user, reason=reason)
            await ctx.send(f'Banned <@{user_id}>')
        except discord.Forbidden:
            await ctx.send('I do not have permissions.')
        except discord.HTTPException:
            await ctx.send('Banning failed, did you type the id correctly?')

    @commands.command(aliases=['tatsukete_eirin', 'eirin', 'tatsukete'])
    async def help(self, ctx, *args):
        """This help message"""
        if len(args) == 0:
            cats = [cog for cog in self.bot.cogs]
            cats.sort()
            width = max([len(cat) for cat in cats]) + 2
            d = '**Categories:**\n'
            for cat in zip(cats[0::2], cats[1::2]):
                d += '**`{}`**{}**`{}`**\n'.format(cat[0], ' ' * int(2.3 * (width-len(cat[0]))), cat[1])
            if len(cats) % 2 == 1:
                d += '**`{}`**\n'.format(cats[-1])

            d += '\nUse `{0}help <category>` to list commands in a category.\n'.format(ctx.prefix)
            d += 'Use `{0}help <command>` to get in depth help for a command.\n'.format(ctx.prefix)

        elif len(args) == 1:
            cats = {cog.lower(): cog for cog in self.bot.cogs}
            if args[0].lower() in cats:
                cog_name = cats[args[0].lower()]
                d = 'Commands in category **`{}`**:\n'.format(cog_name)
                cmds = self.bot.get_cog_commands(cog_name)
                for cmd in sorted(list(cmds), key=lambda x: x.name):
                    d += '\n  `{}{}`'.format(ctx.prefix, cmd.name)

                    brief = cmd.brief
                    if brief is None and cmd.help is not None:
                        brief = cmd.help.split('\n')[0]

                    if brief is not None:
                        d += ' - {}'.format(brief)
                d += '\n'
            else:
                if args[0] not in ctx.bot.all_commands:
                    d = 'Unyu?'
                else:
                    cmd = ctx.bot.all_commands[args[0]]
                    d = self.get_help(ctx, cmd)
        else:
            d = ''
            cmd = ctx.bot
            cmd_name = ''
            for i in args:
                i = i.replace('@', '@\u200b')
                if cmd == ctx.bot and i in cmd.all_commands:
                    cmd = cmd.all_commands[i]
                    cmd_name += cmd.name + ' '
                elif type(cmd) == commands.Group and i in cmd.all_commands:
                    cmd = cmd.all_commands[i]
                    cmd_name += cmd.name + ' '
                else:
                    d += 'Unyu?'
                    break

            else:
                d = self.get_help(ctx, cmd, name=cmd_name)

        # d += '\n*Made by hanss314#0128*'
        return await ctx.send(d)


def setup(bot):
    bot.add_cog(Misc(bot))
