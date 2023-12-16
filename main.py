from aiogram import Bot, executor, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.deep_linking import get_start_link, decode_payload
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import TOKEN

cancelMarkup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("Отменить отправку❌", callback_data="cancel")]])

class States(StatesGroup):
    message = State()

bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

async def get_id(call: CallbackQuery, state: FSMContext):
    id = int(call.data.split("_")[1])
    await call.message.answer("_😙 Отправь анонимное сообщение пользователю_\n\n*Напиши cюда всё, что угодно в одном сообщении и пользователь сразу его получит, но не будет знать от кого оно.*\n\n_📝 Ты можешь отправить фото, видео, голосовое сообщение, текст_", parse_mode='markdown', reply_markup=cancelMarkup)
    await States.message.set()
    async with state.proxy() as data:
        data['id'] = id

@dp.message_handler(commands="start", state="*")
async def cmd_start(message: Message, state: FSMContext):
    await state.finish()
    args = message.get_args()
    if args == "" or args is None:
        link = await get_start_link(message.from_user.id, encode=True)
        await message.answer(f"😀 Чтобы получить много <b>анонимных сообщений</b> мы рекомендуем тебе разместить твою персональную ссылку в описании профиля телеграм.\n\n🔗Твоя персональная ссылка: {link}", parse_mode='html')
    else:
        id = decode_payload(args)
        if int(id) != message.from_user.id:
            await message.answer("_😙 Отправь анонимное сообщение пользователю_\n\n*Напиши cюда всё, что угодно в одном сообщении и пользователь сразу его получит, но не будет знать от кого оно.*\n\n_📝 Ты можешь отправить фото, видео, голосовое сообщение, текст_", parse_mode='markdown',
                                 reply_markup=cancelMarkup)
            await States.message.set()
            async with state.proxy() as data:
                data["id"] = id
        else:
            markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("🔗Получить ссылку", callback_data="get_link")]])
            await message.answer("*🤦‍♀️ Писать самому себе - глупо.*\n\nЛучше размести ссылку в сториз или у себя в профиле *Instagram/Telegram/VK/TikTok*, и сообщения не заставят себя долго ждать 😉", parse_mode='markdown', reply_markup=markup)

@dp.message_handler(state=States.message, content_types=['animation', 'audio', 'contact', 'dice', 'document', 'location', 'photo', 'poll', 'sticker', 'text', 'venue', 'video', 'video_note', 'voice'])
async def send_handler(message: Message, state: FSMContext):
    async with state.proxy() as data:
        id = data["id"]
    markup = InlineKeyboardMarkup(1)
    sendButton = InlineKeyboardButton("Отправить ещё одно🔁", callback_data=f"send_{id}")
    markup.add(sendButton)
    get_markup = InlineKeyboardMarkup(1)
    answerButton = InlineKeyboardButton("✉️Ответить", callback_data=f"answer_{message.from_user.id}")
    get_markup.add(answerButton)
    await bot.send_message(id, f"*💬Вам пришло новое анонимное сообщение от пользователя* #{message.from_user.id}", parse_mode="markdown")
    await bot.copy_message(id, message.from_user.id, message.message_id, reply_markup=get_markup)
    await message.answer("*💬Анонимное сообщение отправлено*\n\n_Хотите отправить еще одно для этого пользователя?_", parse_mode="markdown", reply_markup=markup)
    await state.finish()

@dp.callback_query_handler(text_contains="send_")
async def cb_send_again(call: CallbackQuery, state: FSMContext):
    await get_id(call, state)

@dp.callback_query_handler(text_contains="answer_")
async def cb_answer(call: CallbackQuery, state: FSMContext):
    await get_id(call, state)
        
@dp.callback_query_handler(text="cancel", state="*")
async def cb_cancel(call: CallbackQuery, state: FSMContext):
   await call.message.delete()
   await state.finish()

@dp.callback_query_handler(text="get_link", state="*")
async def cb_get_link(call: CallbackQuery, state: FSMContext):
    link = await get_start_link(call.from_user.id, encode=True)
    await call.message.answer(f"😀 Чтобы получить много <b>анонимных сообщений</b> мы рекомендуем тебе разместить твою персональную ссылку в описании профиля телеграм.\n\n🔗Твоя персональная ссылка: {link}", parse_mode='html')

@dp.message_handler(lambda msg: True)
async def echo(message: Message, state: FSMContext):
    await cmd_start(message, state)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

