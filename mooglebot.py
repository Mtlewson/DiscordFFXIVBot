from discord.ext import commands
from dotenv import load_dotenv
import discord
import asyncio
import aiohttp
import pyxivapi
from pyxivapi.models import Filter, Sort

load_dotenv()
TOKEN = ":D"
client = pyxivapi.XIVAPIClient(api_key=":D")
bot = commands.Bot(command_prefix='!')

#parses input
def parseInput(input):
    inputList = []
    wordsToNotCapitalize = ["of"]
    for i in range(len(input)):
        if input[i].lower() in wordsToNotCapitalize:
            inputList.append(input[i].lower())
        else:
            title = input[i].upper()
            if len(title) > 1:
              title = title[0] + title[1:].lower()
            inputList.append(title)
    input = " ".join(inputList)
    return input

#returns item information
async def getItemInfo(input):
    item = await client.index_search(
        name=input,
        indexes=["Item"],
        columns=["ID", "Name"],
        )
    await client.session.close()
    return item['Results']

#returns recipe information
async def getRecipeInfo(input):
    recipe = await client.index_search(
        name=input,
        indexes=["Recipe"],
        columns=["ID", "ItemIngredient0.Name", "AmountIngredient0", "ItemIngredient1.Name", "AmountIngredient1", "ItemIngredient2.Name", "AmountIngredient2", "ItemIngredient3.Name", "AmountIngredient3", "ItemIngredient4.Name", "AmountIngredient4", "ItemIngredient5.Name", "AmountIngredient5", "ItemIngredient6.Name", "AmountIngredient6", "ItemIngredient7.Name", "AmountIngredient7", "ItemIngredient8.Name", "AmountIngredient8", "ItemIngredient9.Name", "AmountIngredient9", "RecipeLevelTable","SecretRecipeBook.Name","Icon","ClassJob.Abbreviation"],
    )
    await client.session.close()
    outputRecipe = ""

    for i in range(0,10):
        info = (str(recipe.get("Results")[0].get("AmountIngredient"+str(i) ))+ "x " + str(recipe.get("Results")[0].get("ItemIngredient"+str(i) ).get("Name")))
        if i == 7:
            outputRecipe += "\n"
        if info[0] != "0":
            outputRecipe += info
            if i < 9:
               outputRecipe += "\n"

    suggestedControl = str(recipe.get("Results")[0].get("RecipeLevelTable").get("SuggestedControl"))
    suggestedCraftsmanship = str(recipe.get("Results")[0].get("RecipeLevelTable").get("SuggestedCraftsmanship"))
    icon = str(recipe.get("Results")[0].get("Icon"))

    classJob = str(recipe.get("Results")[0].get("ClassJob").get("Abbreviation"))
    classJobLevel = str(recipe.get("Results")[0].get("RecipeLevelTable").get("ClassJobLevel"))
    recipeBookName = str(recipe.get("Results")[0].get("SecretRecipeBook").get("Name"))

    levelInfo = classJob + " " + classJobLevel

    return suggestedControl, suggestedCraftsmanship, classJob, classJobLevel, levelInfo, outputRecipe, icon, recipeBookName

#returns recipe materials as two dictionaries, a material dictionary and crystal dictionary
async def getRecipeMaterials(input):
    recipe = await client.index_search(
        name=input,
        indexes=["Recipe"],
        columns=["ID", "ItemIngredient0.Name", "AmountIngredient0", "ItemIngredient1.Name", "AmountIngredient1", "ItemIngredient2.Name", "AmountIngredient2", "ItemIngredient3.Name", "AmountIngredient3", "ItemIngredient4.Name", "AmountIngredient4", "ItemIngredient5.Name", "AmountIngredient5", "ItemIngredient6.Name", "AmountIngredient6", "ItemIngredient7.Name", "AmountIngredient7", "ItemIngredient8.Name", "AmountIngredient8", "ItemIngredient9.Name", "AmountIngredient9", "RecipeLevelTable","SecretRecipeBook.Name","Icon","ClassJob.Abbreviation"],
    )
    outputDict = {}
    crystalDict = {}

    for i in range(0,7):
        if str(recipe.get("Results")[0].get("ItemIngredient"+str(i) ).get("Name")) != "None":
          outputDict[str(recipe.get("Results")[0].get("ItemIngredient"+str(i) ).get("Name"))] = (recipe.get("Results")[0].get("AmountIngredient"+str(i)))

    for i in range(7,10):
        if str(recipe.get("Results")[0].get("ItemIngredient"+str(i) ).get("Name")) != "None":
          crystalDict[str(recipe.get("Results")[0].get("ItemIngredient"+str(i) ).get("Name"))] = (recipe.get("Results")[0].get("AmountIngredient"+str(i)))

    return outputDict, crystalDict

@bot.command(name='i', help='!i gives the wiki page of the item')
async def inputCommand(ctx, *args):

    input = parseInput(args)
    item = await getItemInfo(input)

    if item == []:
        response = input + " does not exist, kupo!"
    else:
        input = input.replace(" ", "_")
        response = "https://ffxiv.consolegameswiki.com/wiki/"+input

    await ctx.send(response)

@bot.command(name='m', help='!m gives the market values of the item')
async def inputCommand(ctx, *args):
    input = parseInput(args)
    item = await getItemInfo(input)
    if item == []:
        response = input + " does not exist, kupo!"
    else:
        ID = item[0]['ID']
        response = "https://universalis.app/market/"+str(ID)
    await ctx.send(response)

@bot.command(name='r', help='!r item gives the recipe')
async def inputCommand(ctx, *args):

    input = parseInput(args)

    try:
        #grabs recipe information
        suggestedControl, suggestedCraftsmanship, classJob, classJobLevel, levelInfo, outputRecipe, icon, recipeBookName = await getRecipeInfo(input)
        #strings for embed output
        secondColumn = levelInfo + "\n" + "Suggested Craftsmanship: " + suggestedCraftsmanship + "\nSuggested Control: " + suggestedControl + "\nRecipe Book: " + recipeBookName
        #creates discord embed
        embed=discord.Embed(title=input, color=0x109319)
        embed.add_field(name="Components", value=outputRecipe, inline=True)
        embed.add_field(name="Requirements", value=secondColumn, inline=True)
        embed.set_thumbnail(url="https://xivapi.com"+icon)

        await ctx.send(embed=embed)

    except:
        await ctx.send("That recipe doesn't exist, kupo!")

#returns the materials of several recipes as one large list
@bot.command(name='br', help='!br bulk recipes!')
async def inputCommand(ctx, *args):
    input = parseInput(args)
    materialDict = {}
    crystalDict = {}
    for recipe in input.split(","):
        recipeName = recipe.strip()
        try :
            recipeDict, crystalMatDict = await getRecipeMaterials(recipeName)
            for key in recipeDict:
                if key not in materialDict.keys() and key != None:
                    materialDict[key] = recipeDict[key]
                else :
                    materialDict[key] += recipeDict[key]
            for key in crystalMatDict:
                if key not in crystalDict.keys() and key != None:
                    crystalDict[key] = crystalMatDict[key]
                else :
                    crystalDict[key] += crystalMatDict[key]
        except :
            await ctx.send(recipe + " doesn't exist kupo!")

    output = ""

    sortedMaterials = sorted(materialDict.items(), key=lambda x: x[1], reverse=True)
    sortedCrystals = sorted(crystalDict.items(), key=lambda x: x[1], reverse=True)

    for key in sortedMaterials:
        output += key[0] + ": " + str(key[1]) + "\n"

    crystalsOutput = ""
    for key in sortedCrystals:
        crystalsOutput += key[0] + ": " + str(key[1]) + "\n"

    embed=discord.Embed(title=input, color=0x109319)
    embed.add_field(name="Components", value=output, inline=True)
    embed.add_field(name="Crystals", value=crystalsOutput, inline=True)

    await ctx.send(embed=embed)

#returns gathering location
@bot.command(name='gl', help='!gl gives the gathering location of the item')
async def inputCommand(ctx, *args):

    input = parseInput(args)

    item = await getItemInfo(input)

    if item == []:
        response = input + " does not exist, kupo!"
    else:
        input = input.replace(" ", "%20")
        response = "<"+"https://ffxivteamcraft.com/gathering-location?query="+input+">"

    await ctx.send(response)


bot.run(TOKEN)
