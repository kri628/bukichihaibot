import discord
from discord.ext import commands
import bukichi
import json

bot = commands.Bot(command_prefix='/', help_command=None, intents=discord.Intents.all())  # prompt
prev_result = []

color_m = 0x82d745
color_w = 0xe8e82a

f = open('../../discordSettings/BukichihaiBot.txt', 'r')
token = f.readline()

config = {}


class CommandError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class MemberNumError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def init_server(server):
    global config

    config[str(server[0])] = {"server_name": server[1],
                              "owner": server[2],
                              "allowed_grp": [],
                              "min-inked": False,
                              "non-dup": False
                              }

    save_setting()


def save_setting():
    global config

    with open('./config.json', 'w') as f:
        json.dump(config, f, indent=4)
    f.close()

    print("settings saved.")


def isAllowed(server_id, user):
    global config

    if user.guild_permissions.administrator:
        return True

    if user.id == 1020740857856524288:
        return True

    allowed_roles_id = config.get(str(server_id)).get('allowed_grp')

    if not allowed_roles_id:
        return False

    user_roles_id = [role.id for role in user.roles]

    # print(user_roles_id)

    for allowed_role_id in allowed_roles_id:
        for user_role_id in user_roles_id:
            if allowed_role_id == user_role_id:
                return True
    return False


@bot.event
async def on_ready():
    global config

    print(f'Login bot: {bot.user}')

    with open("./config.json", "r") as f:
        config = json.load(f)
    f.close()

    # print(config)


@bot.command(name='help')
async def response_help(ctx):
    embed = discord.Embed(title="Help", description="ランダムで武器を選びます。\n", color=color_m)
    embed.add_field(name="`/bukichi op [人数]`", value="オープンの1チームの武器を選びます。（２〜４人）", inline=False)
    embed.add_field(name="`/bukichi pr [人数]`", value="プラベの両チームの武器を選びます。（２〜８人）\n*偶数のみ可能\n", inline=False)

    embed.add_field(name="`/chmod status`", value="サーバーの現在の設定が見れます。", inline=False)
    embed.add_field(name="`/chmod min-inked [on/off]`", value="チームメンバー全体の最小限の塗り性能を保障します。"
                                                              "\nこの機能を on/off することができます。"
                                                              "\n*サーバーの所有者と指定された管理メンバーのみ使用できます。\n", inline=False)
    embed.add_field(name="`/chmod non-dup [on/off]`", value="チーム内の武器が重複しないようにします。"
                                                            "\nこの機能を on/off することができます。"
                                                            "\n*サーバーの所有者と指定された管理メンバーのみ使用できます。\n",  inline=False)

    embed.add_field(name="`/chgrp add [@ロール]`"
                         "\n`/chgrp del [@ロール]`", value="ロールに管理権限を付与または取り消します。"
                                                        "\nこの権限を持つメンバーは、ブキチ杯の設定を変更することができます。"
                                                        "\n*サーバーの所有者のみ使用できます。", inline=False)
    embed.set_footer(text="made by リリ")
    await ctx.send(embed=embed)


@bot.command(name='bukichi')
async def random_weapon(ctx, *, text=''):
    global prev_result, config

    server_id = ctx.guild.id

    if config.get(str(server_id)) is None:
        init_server([server_id, ctx.guild.name, ctx.guild.owner.name])

    settings = config.get(str(server_id))

    try:
        words = text.split()
        mode = words[0]
        num = int(words[1])

        if mode == 'op':
            if num > 4 or num < 2:
                raise MemberNumError('Open member must be 2~4.')

            weapon, result = bukichi.getOpResult(num, prev_result, settings)

            prev_result = result

            str_t = '\n'.join(weapon)

            embed = discord.Embed(title="オープン", description="ランダムで武器を選びます。", color=color_m)
            embed.add_field(name="武器", value=str_t, inline=True)

        elif mode == 'pr':
            if num > 8 or num < 2:
                raise MemberNumError('Private member must be 2~8.')

            if num % 2 == 1:
                raise MemberNumError('Member must be even.')

            n = num // 2
            weapon_b, weapon_y = bukichi.getPrResult(n, settings)

            str_b = '\n'.join(weapon_b)
            str_y = '\n'.join(weapon_y)

            embed = discord.Embed(title="プラベ", description="ランダムで武器を選びます。", color=color_m)
            embed.add_field(name="\U0001F49B Yellow", value='>>> {}'.format(str_b), inline=True)
            embed.add_field(name="\U0001F499 Blue", value='>>> {}'.format(str_y), inline=True)

        else:
            raise CommandError("Mode must be 'op' or 'pr'.")

        await ctx.send(embed=embed)

    except MemberNumError as MNE:
        # print('Member error', MNE)
        embed = discord.Embed(
            description="人数が正しくありません。 詳細は`/help`で確認できます。\n>>> **オープン** : ２〜４人\n**プラベ** : ２〜８人の偶数",
            color=color_w)
        await ctx.send(embed=embed)

    except (CommandError, IndexError) as CE:
        print('Command error', CE)
        print(text, end='\n')

        embed = discord.Embed(description="コマンドを正しく入力してください。 詳細は`/help`で確認できます。", color=color_w)
        embed.add_field(name="`/bukichi op [人数]`", value="オープンの1チームの武器を選びます。（２〜４人）", inline=False)
        embed.add_field(name="`/bukichi pr [人数]`", value="プラベの両チームの武器を選びます。（２〜８人）\n*偶数のみ可能", inline=False)
        await ctx.send(embed=embed)

    # except Exception as e:
    #     print('error', e)


@bot.command(name='chmod')
async def chSetting(ctx, *, text=''):
    global config

    server_id = ctx.guild.id
    # print(server_id)

    # print(ctx.guild.roles)

    if not str(server_id) in config:
        init_server([server_id, ctx.guild.name, ctx.guild.owner.name])

    try:
        words = text.split()
        mode = words[0]

        if mode == 'min-inked' or mode == 'non-dup':
            if not isAllowed(server_id, ctx.message.author):
                embed = discord.Embed(title="設定変更", description="このコマンドはサーバーの所有者と指定された管理メンバーのみ使用できます。",
                                      color=color_w)
                await ctx.send(embed=embed)
                return

            value = words[1]

            if value == 'on':
                config[str(server_id)][mode] = True

                save_setting()

                embed = discord.Embed(title="設定変更", description="設定が変更されました。", color=color_m)
                embed.set_footer(text=f"{mode}: on")
                await ctx.send(embed=embed)

            elif value == 'off':
                config[str(server_id)][mode] = False

                save_setting()

                embed = discord.Embed(title="設定変更", description="設定が変更されました。", color=color_m)
                embed.set_footer(text=f"{mode}: off")
                await ctx.send(embed=embed)

            else:
                raise CommandError("min-inked mode must be 'on'/'off'.")

        elif mode == 'status':
            min_inked = config.get(str(server_id)).get('min-inked')
            non_dup = config.get(str(server_id)).get('non-dup')
            min_inked_s = 'on' if min_inked else 'off'
            non_dup_s = 'on' if non_dup else 'off'

            allowed_roles_id = config.get(str(server_id)).get('allowed_grp')

            owner = ctx.guild.owner
            if owner.nick:
                member_name = {owner.nick}
            elif owner.global_name:
                member_name = {owner.global_name}
            else:
                member_name = {owner.name}

            if allowed_roles_id:
                for role_id in allowed_roles_id:
                    members = ctx.guild.get_role(role_id).members
                    # print(members)
                    for member in members:
                        if member.nick:
                            name = member.nick
                        elif member.global_name:
                            name = member.global_name
                        else:
                            name = member.name
                        member_name.add(name)

            # print(member_name)
            str_m = '\n'.join(member_name)

            embed = discord.Embed(title="設定", description="このサーバーの現在の設定です。"
                                                            "\nこの設定は、サーバー所有者と指定された管理メンバーのみ変更できます。",
                                  color=color_m)
            embed.add_field(name="塗り性能の保障", value="`min-inked` : " + min_inked_s, inline=False)
            embed.add_field(name="武器重複の防止", value="`non-dup` : " + non_dup_s, inline=False)
            embed.add_field(name="管理メンバー", value='>>> {}'.format(str_m), inline=False)
            await ctx.send(embed=embed)

    except (CommandError, IndexError) as CE:
        # print('Command error', CE)
        embed = discord.Embed(description="コマンドを正しく入力してください。 詳細は`/help`で確認できます。", color=color_w)
        embed.add_field(name="`/chmod status`", value="サーバーの現在の設定が見れます。", inline=False)
        embed.add_field(name="`/chmod min-inked [on/off]`", value="チームメンバー全体の最小限の塗り性能を保障します。", inline=False)
        embed.add_field(name="`/chmod non-dup [on/off]`", value="チーム内の武器が重複しないようにします。", inline=False)
        embed.set_footer(text="*サーバーの所有者と指定された管理メンバーのみ使用できます。\n")
        await ctx.send(embed=embed)

    # except Exception as e:
    #     print(e)


@bot.command(name='chgrp')
async def chPermission(ctx, text='', *, role: discord.Role):
    global config

    server_id = ctx.guild.id

    if not str(server_id) in config:
        init_server([server_id, ctx.guild.name, ctx.guild.owner.name])

    if ctx.guild:
        if not (ctx.message.author.guild_permissions.administrator or ctx.message.author.id == 1020740857856524288):
            embed = discord.Embed(title="権限変更", description="このコマンドはサーバーの所有者のみが使用できます。", color=color_w)
            await ctx.send(embed=embed)
            return

    try:
        words = text.split()
        # print(role.name, role.id)
        # print(words)
        mode = words[0]

        if mode == 'add':
            if role.id in config[str(server_id)]['allowed_grp']:
                embed = discord.Embed(title="権限変更", description=f"{role}はすでに管理メンバーです。", color=color_w)
                await ctx.send(embed=embed)
                return

            config[str(server_id)]['allowed_grp'].append(role.id)

            save_setting()

            embed = discord.Embed(title="権限変更", description=f"権限が変更されました。 {role.mention}に管理権限を与えます。",
                                  color=color_m)
            await ctx.send(embed=embed)

        elif mode == 'del':
            config[str(server_id)]['allowed_grp'].remove(role.id)

            save_setting()

            embed = discord.Embed(title="権限変更", description=f"権限が変更されました。 {role.mention}を管理メンバーから除外します。",
                                  color=color_m)
            await ctx.send(embed=embed)

        else:
            raise CommandError("mode must be 'add' or 'del'.")

    except ValueError:
        embed = discord.Embed(title="権限変更", description=f"{role}は管理メンバーではありません。", color=color_w)
        await ctx.send(embed=embed)

    except (CommandError, IndexError) as CE:
        # print('Command error', CE)
        embed = discord.Embed(description="コマンドを正しく入力してください。 詳細は`/help`で確認できます。", color=color_w)
        embed.add_field(name="`/chgrp add [@ロール]`"
                             "\n`/chgrp del [@ロール]`", value="ロールに管理権限を付与または取り消します。", inline=False)
        embed.set_footer(text="*サーバーの所有者のみ使用できます。\n")
        await ctx.send(embed=embed)


bot.run(token)
