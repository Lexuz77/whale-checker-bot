import sqlite3 as sq


def sql_start():
    '''Connect to database'''
    global base, cur
    base = sq.connect('marketmakers_stalker.db')
    cur = base.cursor()
    if base:
        print('Data base connected OK!')
    base.execute('CREATE TABLE IF NOT EXISTS wallets\
                 (user_id INT,\
                 wallet TEXT,\
                 description TEXT)')
    base.commit()


async def sql_add_command(state):
    '''Add user_id, wallet and description to database'''
    async with state.proxy() as data:
        cur.execute('INSERT INTO wallets VALUES (?, ?, ?)', tuple(data.values()))
        base.commit()


async def sql_read(message):
    '''Retrieve wallets from the database for a particular user'''
    return cur.execute(f"SELECT * FROM wallets WHERE user_id={message.from_user.id}").fetchall()
    

async def sql_read_for_del(callback_query):
    '''Retrieve wallets from the database of a particular user for later deletion'''
    return cur.execute(f"SELECT * FROM wallets WHERE user_id={callback_query.from_user.id}").fetchall()


async def sql_delete_command(callback_query, user_id):
    '''Delete a wallet from the database'''
    cur.execute(f'DELETE FROM wallets WHERE description="{callback_query}" AND user_id={user_id}')
    base.commit()


async def sql_for_transactions(user_id):
    '''Retrieve specific wallets from the database to check for transactions'''
    return cur.execute(f'SELECT wallet, description FROM wallets WHERE user_id={user_id}').fetchall()
