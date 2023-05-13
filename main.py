import wws
import discord
import pandas as pd
from discord.ext.commands import Bot

intents = discord.Intents.default()
intents.message_content = True
bot = Bot("!", intents=intents)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.command()
async def whowouldsay(ctx, *, msg):
    print("whowouldsay called")
    async with ctx.typing():
        test = wws.predict(msg)

        print(test[0])
        await ctx.reply(test[0])


@bot.command()
async def retrain(ctx, recent=None):
    print("retrain called")
    if ctx.author.id == ctx.guild.owner.id or \
            ctx.author.id == 123524026923614208:
        await ctx.channel.send('Training started, this may take a while...')
        async with ctx.typing():
            max_msgs = None
            if recent == "recent":
                max_msgs = 4000
                await ctx.channel.send('Recent Only')

            maindf = pd.DataFrame(columns=["user", "msg"])
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
                        maindf = pd.concat([maindf, msg_df])
                    else:
                        print("channel too small")
                    print("done with " + chnl.name)
        print("collected all messages")
        wws.savetraindata(maindf)
        print("SAVED")
        wws.refit()
        print("model fit")
        await ctx.channel.send("Retrained on " + str(maindf.size) + " messages from " + str(chnl_count) + " channels!")
    else:
        await ctx.channel.send("Unauthorised >:(")
        print("Unauthorised (" + ctx.author.name + ")")


@bot.command()
async def wouldsay(ctx, user, *, msg):
    if ctx.author.id == 123524026923614208:
        print("wouldsay called")
        async with ctx.typing():
            test = wws.wouldsay(user, msg)

            print(test[0])
            await ctx.reply(test[0])


bot.run("")  # BOT TOKEN HERE
