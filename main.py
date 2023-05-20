import wws
import wws_nn
import os.path
import discord
import pandas as pd
from discord.ext.commands import Bot

MESSAGE_MAX = 50000

intents = discord.Intents.default()
intents.message_content = True
bot = Bot("!", intents=intents)


@bot.event
async def on_ready():
    print("We have logged in as " + str(bot.user))


@bot.command()
async def whowouldsay(ctx, *, msg):
    print("whowouldsay (nn) called")
    if os.path.exists(str(ctx.guild.id) + "-training data.csv"):
        async with ctx.typing():
            prediction = await wws_nn.predict(msg, str(ctx.guild.id) + "-training data.csv")

            if prediction == "NEED_TRAIN":
                await ctx.channel.send("Network not trained yet, training now, this may take a while...")
                await train(str(ctx.guild.id) + "-training data.csv")
                await ctx.channel.send("Training done!")
                prediction = await wws_nn.predict(msg, str(ctx.guild.id) + "-training data.csv")

            print(prediction)
            await ctx.reply(prediction)
    else:
        await ctx.channel.send("Please use '**!refresh**' *(uses all server messages, slow)* or '**!refresh recent**' *(uses up to the last 4000 "
                               "messages of each channel, faster)* before trying to use '**!whowouldsay**'")


async def train(server_csv):
    if os.path.exists(server_csv):
        await wws_nn.train(server_csv)


@bot.command()
async def trainnn(ctx):
    print("trainnn called")
    if ctx.author.id == 123524026923614208:
        if os.path.exists(str(ctx.guild.id) + "-training data.csv"):
            async with ctx.typing():
                await train(str(ctx.guild.id) + "-training data.csv")


@bot.command()
async def refresh(ctx, recent=None):
    print("refresh called")
    if ctx.author.guild_permissions.administrator or \
            ctx.author.id == 123524026923614208:
        await ctx.channel.send("Collecting messages, this may take a while...")
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

                    if main_df.size >= MESSAGE_MAX:
                        break
                    print("done with " + chnl.name)
        print("collected all messages")
        await wws.savetraindata(main_df, str(ctx.guild.id) + "-training data.csv")
        print("model fit")
        await ctx.channel.send("Collected " + str(main_df.size) + " messages from " + str(chnl_count) + " channels!")
        await ctx.channel.send("Retraining, this may take a while...")
        await train(str(ctx.guild.id) + "-training data.csv")
        await ctx.channel.send("Retrained!")
    else:
        await ctx.channel.send("Unauthorised, only a server admin can collect messages")
        print("Unauthorised (" + ctx.author.name + ")")


bot.run("")  # BOT TOKEN HERE

""" Obsolete: old method using N-GRAM and NAIVE BAYES
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
"""
