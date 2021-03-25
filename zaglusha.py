from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
import yaml
with open("config.yaml") as f:
    yamldata = yaml.load(f,Loader=yaml.FullLoader)

bot = Bot(token=yamldata['zag_token'])
dp = Dispatcher(bot)

@dp.message_handler()
async def main(msg:types.Message):
    await msg.reply("Бот находиться на технических работах ¯\_(ツ)_/¯")
    #print(msg['from']['username'])

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
