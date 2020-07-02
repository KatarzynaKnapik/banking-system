import random
import sqlite3


def connect_db():
    return sqlite3.connect('card.s3db')


def create_db(conn):
    cur = conn.cursor()
    # cur.execute('DROP TABLE card')
    cur.execute('CREATE TABLE IF NOT EXISTS card(id integer, number text, pin text, balance integer DEFAULT 0);')
    conn.commit()


def insert_into_db(card_num, password, conn):
    global count
    cur = conn.cursor()

    cur.execute('INSERT INTO card (id, number, pin) values ({}, {}, {})'.format(count, card_num, password))
    count += 1
    conn.commit()


def calculate_checksum(card_number):
    check_card_number = card_number[0:15]
    card_number_nums = [int(num) for num in check_card_number]
    number_new = [num * 2 if index % 2 == 0 else num
                  for index, num in enumerate(card_number_nums)]

    number_final = [num - 9 if num > 9 else num for num in number_new]
    number_sum = sum(number_final)
    checksum = 0

    for i in range(10):
        if (number_sum + i) % 10 == 0:
            checksum = i
            break

    return checksum


def create_card_number(accounts):
    card_number = []
    for i in range(0, 15):
        if i == 0:
            card_number.append('4')
        elif 1 <= i <= 5:
            card_number.append('0')
        else:
            num = random.randint(0, 9)
            card_number.append(str(num))

    card_number = ''.join(card_number)

    for key in accounts:
        if card_number == key[:-1]:
            return create_card_number(accounts)

    checksum = calculate_checksum(card_number)

    credit_card_number = card_number + str(checksum)

    return credit_card_number


def create_password():
    password = []
    for i in range(0, 4):
        num = random.randint(0, 9)
        password.append(str(num))

    return ''.join(password)


def create_account(card_number, password, accounts, conn):
    insert_into_db(card_number, password, conn)
    accounts[card_number] = password
    return accounts


def check_if_account_exist(card_number, password, accounts_dict):
    for key, value in accounts_dict.items():
        if key == card_number and value == password:
            return True

    return False


def show_account_balance(card_number, conn):
    cur = conn.cursor()
    cur.execute('SELECT balance FORM card WHERE number LIKE {}'.format(card_number))

    print('Balance', cur.fetchone()[0], sep=' ')


def check_card_number(card_number):
    checksum = calculate_checksum(card_number)
    return int(card_number[-1]) == checksum


def add_income(card_number, income, conn):
    cur = conn.cursor()
    cur.execute('UPDATE card SET balance = balance + {} WHERE number = {}'.format(income, card_number))
    conn.commit()

def make_money_transfer(user_card_number, destination_card_number, money, conn):
    cur = conn.cursor()
    cur.execute('UPDATE card SET balance = balance + {} WHERE number = {}'.format(money, destination_card_number))
    cur.execute('UPDATE card SET balance = balance - {} WHERE number = {}'.format(money, user_card_number))
    conn.commit()

def get_account(card_number, conn):
    cur = conn.cursor()
    cur.execute('SELECT * FROM card WHERE number LIKE {}'.format(card_number))
    return cur.fetchone()


def check_if_transfer_possible(destination_card_number, conn, user_card_number):
    if not check_card_number(destination_card_number):
        print('Probably you made mistake in the card number. Please try again!')
    elif get_account(destination_card_number, conn) == None:
        print('Such a card does not exist.')
    elif destination_card_number == user_card_number:
        print("You can't transfer money to the same account!")
    else:
        amount_to_transfer = input('Enter how much money you want to transfer:')
        if check_if_enough_money(user_card_number, conn, amount_to_transfer):
            make_money_transfer(user_card_number, destination_card_number, amount_to_transfer, conn)
            print('Success!')
        else:
            print('Not enough money')


def check_if_enough_money(user_card_number, conn, money):
    if get_account(user_card_number, conn)[3] < int(money):
        return False
    return True




def close_account(card_number, conn):
    if get_account(card_number, conn) != None:
        cur = conn.cursor()
        cur.execute('DELETE FROM card where number = {}'.format(card_number))
        conn.commit()


def log_out():
    print('You have successfully logged out!')


# program
enter_possibilities = ['1. Create an account', '2. Log into account', '0. Exit']
accounts = dict()
db_connection = connect_db()
create_db(db_connection)
count = 0

end_action = False

while end_action == False:

    for i in enter_possibilities:
        print(i)

    user_input = input()

    if user_input == '1':
        print()
        print('Your card has been created')
        print('Your card number:')
        card_number = create_card_number(accounts)
        print(card_number)
        print('Your card PIN:')
        password = create_password()
        print(password)
        print()
        create_account(card_number, password, accounts, db_connection)

    elif user_input == '2':
        print()
        print('Enter your card number:')
        card_number = input()
        print('Enter your PIN:')
        password = input()
        if check_if_account_exist(card_number, password, accounts):


            print()
            print('You have successfully logged in!')
            print()

            account_possibilities = ['1. Balance', '2. Add income', '3. Do transfer', '4. Close account', '5. Log out', '0. Exit']

            while True:
                for i in account_possibilities:
                    print(i)

                user_account_choice = input()

                if user_account_choice == '1':
                    print()
                    show_account_balance(card_number, db_connection)
                    print()
                elif user_account_choice == '2':
                    print()
                    income = input('Enter income:')
                    add_income(card_number, income, db_connection)
                    print('Income was added!')
                    print()
                elif user_account_choice == '3':
                    print()
                    print('Transfer')
                    destination_card_number = input('Enter card number:')
                    check_if_transfer_possible(destination_card_number, db_connection, card_number)
                    print()
                elif user_account_choice == '4':
                    close_account(card_number, db_connection)
                elif user_account_choice == '0':
                    print('Bye!')
                    end_action = True
                    break

        else:
            print()
            print('Wrong card number or PIN!')
            print()

    elif user_input == '0':
        print('Bye!')
        end_action = True
        break

