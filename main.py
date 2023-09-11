import discord
from discord.ext import commands
import bukichi
import json

bot = commands.Bot(command_prefix='/', help_command=None, intents=discord.Intents.all())  # prompt
prev_result = []

color_m = 0x82d745
color_w = 0xe8e82a

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


def init_server(server_id):
    global config

    config[str(server_id)] = {"allowed_grp": [],
                              "min_inked": False
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

    print(config)


@bot.command(name='help')
async def response_help(ctx):
    embed = discord.Embed(title="Help", description="ランダムで武器を選びます。\n", color=color_m)
    embed.add_field(name="`/bukichi op [人数]`", value="オープンの1チームの武器を選びます。（２〜４人）", inline=False)
    embed.add_field(name="`/bukichi pr [人数]`", value="プラベの両チームの武器を選びます。（２〜８人）\n*偶数のみ可能\n", inline=False)

    embed.add_field(name="`/chmod status`", value="サーバーの現在の設定が見れます。", inline=False)
    embed.add_field(name="`/chmod min-inked [on/off]`", value="チームメンバー全体の最小限の塗り性能を保障します。"
                                                              "\nこの機能を on/off することができます。"
                                                              "\n*サーバーの所有者と指定された管理メンバーのみ使用できます。\n", inline=False)

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
    min_inked = config.get(str(server_id)).get('min_inked')
    # print(min_inked)

    if min_inked is None:
        init_server(server_id)

    try:
        words = text.split()
        mode = words[0]
        num = int(words[1])

        if mode == 'op':
            if num > 4 or num < 2:
                raise MemberNumError('Open member must be 2~4.')

            weapon, result = bukichi.getOpResult(num, prev_result, min_inked)

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
            weapon_b, weapon_y = bukichi.getPrResult(n, min_inked)

            str_b = '\n'.join(weapon_b)
            str_y = '\n'.join(weapon_y)

            embed = discord.Embed(title="プラベ", description="ランダムで武器を選びます。", color=color_m)
            embed.add_field(name="Blue", value='>>> {}'.format(str_b), inline=True)
            embed.add_field(name="Yellow", value='>>> {}'.format(str_y), inline=True)

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
        # print('Command error', CE)
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
        init_server(server_id)

    try:
        words = text.split()
        mode = words[0]

        if mode == 'min-inked':
            if not isAllowed(server_id, ctx.message.author):
                embed = discord.Embed(title="設定変更", description="このコマンドは管理者と指定された管理メンバーのみ使用できます。",
                                      color=color_w)
                await ctx.send(embed=embed)
                return

            # if not (ctx.message.author.guild_permissions.administrator or ctx.message.author.id == 1020740857856524288):
            #     embed = discord.Embed(title="設定変更", description="このコマンドは管理者と指定された管理メンバーのみ使用できます。",
            #                           color=color_w)
            #     await ctx.send(embed=embed)
            #     return

            value = words[1]

            if value == 'on':
                config[str(server_id)]['min_inked'] = True

                save_setting()

                embed = discord.Embed(title="設定変更", description="設定が変更されました。", color=color_m)
                embed.set_footer(text="min-inked: on")
                await ctx.send(embed=embed)

            elif value == 'off':
                config[str(server_id)]['min_inked'] = False

                save_setting()

                embed = discord.Embed(title="設定変更", description="設定が変更されました。", color=color_m)
                embed.set_footer(text="min-inked: off")
                await ctx.send(embed=embed)

            else:
                raise CommandError("min-inked mode must be 'on'/'off'.")

        elif mode == 'status':
            min_inked = config.get(str(server_id)).get('min_inked')
            value = 'on' if min_inked else 'off'

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

            print(member_name)
            str_m = '\n'.join(member_name)

            embed = discord.Embed(title="設定", description="このサーバーの現在の設定です。"
                                                            "\nこの設定は、サーバー所有者と指定された管理メンバーのみ変更できます。",
                                  color=color_m)
            embed.add_field(name="塗り性能保障", value="`min-inked` : " + value, inline=False)
            embed.add_field(name="管理メンバー", value='>>> {}'.format(str_m), inline=False)
            await ctx.send(embed=embed)

    except (CommandError, IndexError) as CE:
        # print('Command error', CE)
        embed = discord.Embed(description="コマンドを正しく入力してください。 詳細は`/help`で確認できます。", color=color_w)
        embed.add_field(name="`/chmod status`", value="サーバーの現在の設定が見れます。", inline=False)
        embed.add_field(name="`/chmod min-inked [on/off]`", value="チームメンバー全体の最小限の塗り性能を保障します。"
                                                                  "\n*管理者と指定された管理メンバーのみ使用できます。", inline=False)
        await ctx.send(embed=embed)

    # except Exception as e:
    #     print(e)


@bot.command(name='chgrp')
async def chPermission(ctx, text='', *, role: discord.Role):
    global config

    server_id = ctx.guild.id

    if not str(server_id) in config:
        init_server(server_id)

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
        await ctx.send(embed=embed)


bot.run('MTE0OTc1NDM3NDcwMTE5NTI5NQ.Gyh0_i.DkpCz45PVKJkeOF54VM9mXXxnWl7X2Kj8hiwys')
