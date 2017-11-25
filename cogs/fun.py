import hashlib
import math
import random
from string import ascii_lowercase

from discord.ext import commands

ascii_digit = '0123456789'
wrongs = [
    'Oof',
    'Nope',
    'Not quite',
    'Almost',
    'Not a chance',
    'Are you even trying?',
    'Way off',
    'So close',
]

def number(arg: str) -> complex:
    arg = arg.replace('i', 'j')
    return complex(arg)

def factor(x):
    fs = set()
    for i in range(1, int(math.ceil(math.sqrt(x)))):
        if x%i == 0:
            fs.add(x//i)
            fs.add(i)
    return fs

def p_factor(x):
    factors = set()
    i = 2
    while x > i:
        if x % i == 0:
            factors.add(i)
            x //= i
        else:
            i += 1

    return factors

class Fun:

    def __init__(self, bot):
        import os
        self.bot = bot
        self.wangernumb = False
        if os.path.exists('./lastwang'):
            self.lastwang = open('./lastwang').readline()
        else:
            self.lastwang = self.hash(1)
            open('./lastwang', 'w').write(self.lastwang)

    @staticmethod
    def hash(object):
        return hashlib.sha512(bytes(repr(object), 'utf8')).hexdigest()

    @staticmethod
    def int(string: str) -> int:
        try: return int(string)
        except ValueError: return 1

    def check_numberwang(self, num):
        r = num
        i = type(num)
        rstr = ''.join(c for c in self.hash(r) if c in ascii_lowercase)
        istr = self.int(''.join(c for c in self.hash(i) if c in ascii_digit))
        rstr = self.int(''.join(c for c in self.hash(rstr) if c in ascii_digit))
        lw = self.int(''.join(c for c in self.lastwang if c in ascii_digit))

        lw, istr = int(str(lw)[-int(str(istr)[0])//2-5:]), int(str(istr)[-int(str(lw)[0])//2-5:])
        lw = self.int(''.join(c for c in self.hash(factor(lw) ^ factor(istr)) if c in ascii_digit))
        lw, rstr = int(str(lw)[-int(str(rstr)[0]) // 2 - 5:]), int(str(rstr)[-int(str(lw)[0]) // 2 - 5:])
        final =  p_factor(lw) & p_factor(rstr)
        return len(final) > 0, len(final) > 1

    @commands.group(invoke_without_command=True)
    async def numberwang(self, ctx, *, num):
        '''
        See if a number is numberwang.
        '''
        async with ctx.typing():
            is_numberwang, wangernumb = self.check_numberwang(num)


        if is_numberwang:
            self.lastwang = self.hash(self.lastwang + str(num))
            open('./lastwang', 'w').write(self.lastwang)
            if not self.wangernumb:
                await ctx.send(f'{ctx.author.mention} That\'s numberwang!')
                if wangernumb:
                    self.wangernumb = True
                    await ctx.send('Let\'s rotate the board!')

            else:
                await ctx.send('That\'s WangerNumb!')
                self.wangernumb = False

        else:
            if not self.wangernumb:
                await ctx.send(f'I\'m sorry {ctx.author.mention}, but that is not numberwang.')
                self.lastwang = self.hash(self.lastwang + str(num))
                open('./lastwang', 'w').write(self.lastwang)
            else:
                await ctx.send(random.choice(wrongs))


def setup(bot):
    bot.add_cog(Fun(bot))