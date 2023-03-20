from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import exceptions as exc
from whale_checker_bot.create_bot import bot
from keyboards import kb_client, urlkb, wlistkb
from data import sqlite_db
from ether import ether_cl
import emoji
import asyncio


wallet_for_check = '' # Global string variable to record the wallet to be checked


class FSMUser(StatesGroup):
    '''State module'''
    wallet = State()
    description = State()
    balance_wallet = State()
    token_address = State()


async def commands_start(message : types.Message):
    '''Command "/start" function'''
    try:
        await bot.send_message(message.from_user.id, 'Greetings my dear friend!\n'
                                                     'I will help you track transactions from whale wallets and other important bumps in web3.)\n'
                                                     "Let's get started!",
                                                     reply_markup=kb_client)
        await message.delete()
    except:
        await message.reply("Communication with the bot is only possible via private messages!\n"
                            "Write to him to continue:\nhttps://t.me/marketmakers_stalker_bot")


async def send_notifications_transactions(callback_query: types.CallbackQuery):
    '''Notifications about new transactions on wallets'''
    await bot.send_message(callback_query.from_user.id, "Stalker mode has started...")
    while True:
        try:
            wallets = await sqlite_db.sql_for_transactions(callback_query.from_user.id)
            print(ether_cl.subscriptions)
            for wallet in wallets:
                current_latest_tx = ether_cl.get_latest_tx(ether_cl.transactions(wallet[0]))
            
                if callback_query.from_user.id in ether_cl.subscriptions.keys()\
                        and wallet[0] in ether_cl.subscriptions[callback_query.from_user.id]\
                        and int(current_latest_tx['timestamp']) > int(ether_cl.subscriptions[callback_query.from_user.id][wallet[0]]['timestamp']):
                    await bot.send_message(callback_query.from_user.id, f'New transactions occured for {wallet[1]}!')
                    await bot.send_message(callback_query.from_user.id, ether_cl.format_tx(current_latest_tx))

                ether_cl.update_subscriptions(callback_query.from_user.id, wallet[0])
        except:
            print('Somrthing wrong')
        await asyncio.sleep(20)
        

async def get_wallet_balance(message: types.Message):
    ''' Start checking wallet balance'''
    await FSMUser.balance_wallet.set()
    await message.reply('Send me the wallet address.')


async def show_wallet_balance(message: types.Message, state: FSMContext):
    '''Check wallet balance'''
    try:
        global wallet_for_check
        wallet_for_check = message.text
        await message.reply(ether_cl.get_wallet_balance(wallet_for_check), \
                            reply_markup=InlineKeyboardMarkup().\
                            add(InlineKeyboardButton(f'{emoji.emojize("➕")}Add token contract{emoji.emojize("➕")}', callback_data=f'Contract {wallet_for_check}')))
        await state.finish()
    except (TypeError, AssertionError) as ex:
        await message.reply('This address does not exist on the ETH network(')
        await state.finish()


async def add_token_address(callback_query: types.CallbackQuery):
    '''Start adding token's contract address to check token balance on wallet'''
    await FSMUser.token_address.set()
    await callback_query.message.answer('Send me the token address.')
    await callback_query.answer()


async def show_token_balance(message: types.Message, state: FSMContext):
    '''Add token's contract address to check token balance on wallet'''
    try:
        token_address = message.text
        await message.reply(ether_cl.get_balance_with_token(wallet_for_check, token_address))
        await state.finish()
    except (TypeError, AssertionError) as ex:
        await message.reply('This address does not exist on the ERC-20 network(')
        await state.finish()


async def cm_start(callback_query: types.CallbackQuery):
    '''Start adding new wallet into watchlist'''
    await FSMUser.wallet.set()
    await callback_query.message.answer('Send me the wallet address.')
    await callback_query.answer()


async def load_wallet(message: types.Message, state: FSMContext):
    '''Add user_id and wallet into database'''
    async with state.proxy() as data:
        data['user_id'] = message.from_user.id
        data['wallet'] = message.text
    await FSMUser.next()
    await message.reply('Add a description to this wallet.\n(20 characters max)')


async def load_description(message: types.Message, state: FSMContext):
    '''Add wallet's description into database'''
    async with state.proxy() as data:
        data['description'] = message.text
    await bot.send_message(message.from_user.id, 'Wallet has been added')
    await sqlite_db.sql_add_command(state)
    await state.finish()


async def cancel_handler(message: types.Message, state: FSMContext):
    '''Useless "/cancel" function. Can be used if you wanna cancel adding wallet to watchlist'''
    current_state = await state.get_state()
    if current_state is None:
        return    
    await message.reply('Ok')
    await state.finish()


async def check_watchlist(message: types.Message, state: FSMContext):
    '''Check watchlist'''
    try:
        read = await sqlite_db.sql_read(message)
        res = ''
        for wal in read:
            res += f'{wal[1]} : {wal[2]}\n'
        await message.answer(res, reply_markup=wlistkb)
        await state.finish()
    except exc.MessageTextIsEmpty as ex:
        await message.reply('Your watchlist is empty', reply_markup=wlistkb)


async def delete_item(callback_query: types.CallbackQuery, state: FSMContext):
    '''Start deleting wallet from watchlist'''
    read = await sqlite_db.sql_read_for_del(callback_query)
    for wal in read:
        await callback_query.message.answer(f'{wal[1]} : {wal[2]}',\
                                            reply_markup=InlineKeyboardMarkup().\
                                            add(InlineKeyboardButton(f'Delete', callback_data=f'del {wal[2]}')))
    await callback_query.answer()
    await state.finish()


async def del_callback_run(callback_query: types.CallbackQuery):
    '''Delete wallet from watchlist'''
    try:
        await sqlite_db.sql_delete_command(callback_query.data.replace('del ', ''), callback_query.from_user.id)
        await callback_query.answer(text='Wallet has been deleted', show_alert=True)
    except exc.MessageError as ex:
        await callback_query.answer(text='Wallet already deleted', show_alert=True)


async def pay_respect_command(message: types.Message, state: FSMContext):
    '''Press "F" To Pay Respect'''
    await message.answer('Socials:', reply_markup=urlkb)
    await state.finish()


async def empty(message: types.Message):
    '''Check if message from user isn't include any commands'''
    await message.answer('Bruh...')
    await message.delete()


def register_handlers_client(dp : Dispatcher):
    '''Registration for all bot's handlers'''
    dp.register_message_handler(commands_start, commands=['start', 'help'])
    dp.register_message_handler(cancel_handler, commands='cancel', state='*')
    dp.register_message_handler(cancel_handler, lambda message: message.text == 'cancel', state='*')
    dp.register_message_handler(check_watchlist, lambda message: message.text == f'{emoji.emojize("📄")}My watchlist{emoji.emojize("📄")}', state='*')
    dp.register_callback_query_handler(delete_item, lambda query: query.data and query.data.startswith('Delete'), state='*')
    dp.register_callback_query_handler(del_callback_run, lambda query: query.data and query.data.startswith('del '))
    dp.register_callback_query_handler(send_notifications_transactions, lambda query: query.data and query.data.startswith('Start'), state='*')
    dp.register_message_handler(pay_respect_command, lambda message: message.text == f'{emoji.emojize("👍🏿")}Pay respect{emoji.emojize("👍🏿")}', state='*')
    dp.register_message_handler(get_wallet_balance, lambda message: message.text == f'{emoji.emojize("💲")}Check wallet balance{emoji.emojize("💲")}', state='*')
    dp.register_message_handler(show_wallet_balance, state=FSMUser.balance_wallet)
    dp.register_callback_query_handler(add_token_address, lambda query: query.data and query.data.startswith('Contract '), state='*')
    dp.register_message_handler(show_token_balance, state=FSMUser.token_address)
    dp.register_callback_query_handler(cm_start, lambda query: query.data and query.data.startswith('Add'), state=None)
    dp.register_message_handler(load_wallet, state=FSMUser.wallet)
    dp.register_message_handler(load_description, state=FSMUser.description)
    dp.register_message_handler(empty)