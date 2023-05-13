import os.path

import wws
import discord
import pandas as pd
from discord.ext.commands import Bot

intents = discord.Intents.default()
intents.message_content = True
bot = Bot("!", intents=intents)


@bot.event
async def on_ready():
    print("We have logged in as " + str(bot.user))


@bot.command()
async def whowouldsay(ctx, *, msg):
    print("whowouldsay called")
    if os.path.exists(str(ctx.guild.id) + "-training data.csv"):
        async with ctx.typing():
            prediction = await wws.predict(msg, str(ctx.guild.id) + "-training data.csv")

            print(prediction[0])
            await ctx.reply(prediction[0])
    else:
        await ctx.channel.send("Please use '**!train**' *(uses all server messages, slow)* or '**!train recent**' *(uses up to the last 4000 "
                               "messages of each channel, faster)* before trying to use '**!whowouldsay**'")


@bot.command()
async def train(ctx, recent=None):
    print("train called")
    if ctx.author.guild_permissions.administrator or \
            ctx.author.id == 123524026923614208:
        await ctx.channel.send("Training started, this may take a while...")
        async with ctx.typing():
            max_msgs = None
            if recent == "recent":
                max_msgs = 4000

            main_df = pd.DataFrame(columns=["user", "msg"])
            chnl_count = 0
            for chnl in ctx.message.guild.channels:
                if str(chnl.type) == "text" and \
                        chnl.permissions_for(chnl.guild.me).view_channel:
                    chnl_count += 1
                    msgs = [msg async for msg in chnl.history(limit=max_msgs) if
                            msg.content != "" and
                            msg.content[0] != "!" and
                            not msg.content.startswith("http") and
                            " " in msg.content and
                            not msg.author.bot]
                    msg_list = 0
                    for msg in msgs:
                        if msg_list == 0:
                            msg_list = [[msg.author.name, msg.content]]
                        else:
                            if msg.content != "":
                                msg_list.append([msg.author.name, msg.content])

                    print("adding to main: " + chnl.name)
                    if msg_list != 0 and len(msg_list) > 0:
                        msg_df = pd.DataFrame(msg_list, columns=["user", "msg"])
                        main_df = pd.concat([main_df, msg_df])
                    else:
                        print("channel too small")
                    print("done with " + chnl.name)
        print("collected all messages")
        await wws.savetraindata(main_df, str(ctx.guild.id) + "-training data.csv")
        print("model fit")
        await ctx.channel.send("Retrained on " + str(main_df.size) + " messages from " + str(chnl_count) + " channels!")
    else:
        await ctx.channel.send("Unauthorised, only a server admin can train the bot")
        print("Unauthorised (" + ctx.author.name + ")")


""" In Progress
@bot.command()
async def wouldsay(ctx, user, *, msg):
    if ctx.author.id == 123524026923614208:
        print("wouldsay called")
        async with ctx.typing():
            test = wws.wouldsay(user, msg)
            print(test[0])
            await ctx.reply(test[0])
"""

bot.run("")  # BOT TOKEN HERE
