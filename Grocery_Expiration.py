from datetime import datetime,timedelta
import sqlite3

conn = sqlite3.connect('grocerydb.sqlite')
cur = conn.cursor()

today = datetime.today()
delta = timedelta(days=60)
two_months_ago = str(today - delta)[:10]

def clear_really_old_foods():
    cur.execute('SELECT Expiration FROM Expiration_Dates')
    data = cur.fetchall()
    if data != []:
        for tup in data:
            if tup[0] <= two_months_ago:
                cur.execute('DELETE FROM Expiration_Dates WHERE Expiration = (?)',(tup[0],))

def is_word(string):
    for character in string:
        if character.isdigit(): return(True)
    return(False)

def date_format_checker(date):
    if '-' not in date:
        return(True)
    components = date.split('-')
    if len(components[0]) != 4 or len(components[1]) != 2 or len(components[2]) != 2:
        return(True)
    for component in components:
        for character in component:
            if character.isalpha():
                return(True)
        return(False)

def expiring_soon(lst):
    new_lst = []
    base = datetime.today()
    date_list = [str(base - timedelta(days=x))[:10] for x in range(-8,0)]
    for tup in lst:
        if tup[1] in date_list:
            new_lst.append(tup)
    return(new_lst)

def expired_foods(lst):
    new_lst = []
    for tup in lst:
        if tup[1] < str(datetime.today()):
            new_lst.append(tup)
    return(new_lst)

cur.executescript('''
CREATE TABLE IF NOT EXISTS Expiration_Dates (Item TEXT, Expiration TEXT);
''')

clear_really_old_foods()

while True:
    print('''
________________________________________
        ╭━━━╮
        ┃╭━━╯
        ┃╰━━┳╮╭┳━━┳┳━┳━━╮
        ┃╭━━┻╋╋┫╭╮┣┫╭┫╭╮┃
        ┃╰━━┳╋╋┫╰╯┃┃┃┃╰╯┃
        ╰━━━┻╯╰┫╭━┻┻╯╰━━╯
        ╱╱╱╱╱╱╱┃┃   By Preston Cook
        ╱╱╱╱╱╱╱╰╯
________________________________________''')

    print('''
To Add an Entry: Select 1
To View Upcoming Expired Goods: Select 2
To View Expired Goods: Select 3
To Delete an Entry: Select 4
To Exit Program: Select 5
________________________________________\n''')

    user_selection = input('Enter Selection: ')
    print('________________________________________\n')

    while user_selection not in ['1','2','3','4','5']:
        print('Error: Invalid Selection')
        user_selection = input('Enter Selection: ')

    if user_selection == '1':
        print('Enter your product name and its expiration date. Enter STOP when done:\n')
        while True:
            product = input('Input your Product: ')
            if product.lower() == 'stop': break
            while is_word(product) and product.lower() != 'stop':
                print('ERROR: Invalid Input')
                product = input('Input your Product: ')
            expiration_date = input('Enter the Expiration Date (YYYY-MM-DD): ')
            if expiration_date.lower() == 'stop': break
            while date_format_checker(expiration_date) and expiration_date.lower() != 'stop' and product.lower() != 'stop':
                print('ERROR: Invalid Input')
                expiration_date = input('Enter the Expiration Date (YYYY-MM-DD): ')
            if product.lower() != 'stop' and expiration_date.lower() != 'stop':
                cur.execute('INSERT INTO Expiration_Dates (Item,Expiration) VALUES (?,?)',(product.lower(),expiration_date))
                conn.commit()
    
    elif user_selection == '2':
        cur.execute('SELECT * FROM Expiration_Dates')
        row = cur.fetchone()
        if row is None:
            print('ERROR: There is No Data')
        else:
            cur.execute('SELECT * FROM Expiration_Dates ORDER BY Expiration')
            data = cur.fetchall()
            expiring_foods = expiring_soon(data)
            for tup in expiring_foods:
                print(f'{tup[0]}   {tup[1]}')
    
    elif user_selection == '3':
        cur.execute('SELECT * FROM Expiration_Dates')
        row = cur.fetchone()
        if row is None:
            print('ERROR: There is No Data')
        else:
            cur.execute('SELECT * FROM Expiration_Dates ORDER BY Expiration')
            data = cur.fetchall()
            gross_foods = expired_foods(data)
            for tup in gross_foods:
                print(f'{tup[0].capitalize()}   {tup[1]}')
    
    elif user_selection == '4':
        cur.execute('SELECT * FROM Expiration_Dates')
        data = cur.fetchall()
        for tup in data:
            print(f'{tup[0].capitalize()}   {tup[1]}')
        user_input = input('Enter the name of the food you would like to remove: ').lower()
        cur.execute('SELECT Item FROM Expiration_Dates WHERE Item = (?)',(user_input,))
        row = cur.fetchone()
        if row is None:
            print('ERROR: Food not in databse')
        else:
            user_confirmation = input(f'Are you sure you want to delete {user_input.capitalize()}? (Y/N): ').lower()
            if user_confirmation == 'y':
                cur.execute('DELETE FROM Expiration_Dates WHERE Item = (?)',(user_input,))
                print(f"'{user_input.capitalize()}' successfully deleted from database.")
    elif user_selection == '5': quit()