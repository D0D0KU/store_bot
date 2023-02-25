from mysql.connector import connect, Error
from config import mysql_name, mysql_pw


def start_db():
    global connection
    connection = connect(
            host="localhost",
            user=mysql_name,
            password=mysql_pw,
            database="store_bot"
    )
    if connection:
        print('Database connect OK!')


def add_group(group):
    """
    Функция заполняет таблицу по переданному имени.
    :param group: переменная для заполнения.
    """
    try:
        insert_into_table_name = f'''INSERT INTO product_group (group_name) 
                                     VALUES ("{group}")
        '''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            connection.commit()
    except Error as e:
        print(e)


def add_product(lst):
    """
        Функция заполняет таблицу products.
        :param lst: список для заполнения.
        """
    try:
        insert_into_table_name = f'''INSERT INTO products (name, group_id, amount, price, image) 
                                     VALUES (%s, %s, %s, %s, %s)
        '''
        with connection.cursor() as cursor:
            cursor.executemany(insert_into_table_name, lst)
            connection.commit()
    except Error as e:
        print(e)


def add_amount(num, product):
    try:
        insert_into_table_name = f'''UPDATE products
        SET amount = amount + {num}
        WHERE name = "{product}"
        '''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            connection.commit()
    except Error as e:
        print(e)


def delete_group(group):
    try:
        insert_into_table_name = f'''
        DELETE FROM products 
        WHERE id IN (SELECT products.id
        FROM (SELECT * FROM products) products INNER JOIN product_group ON products.group_id = product_group.id
        WHERE product_group.group_name = "{group}");
            
        DELETE FROM product_group
        WHERE group_name = "{group}"
        '''

        with connection.cursor() as cursor:
            for result in cursor.execute(insert_into_table_name, multi=True):
                if result.with_rows:
                    print(result.fetchall())
            connection.commit()
    except Error as e:
        print(e)


def delete_product(product):
    try:
        insert_into_table_name = f'''DELETE FROM products
        WHERE name = "{product}"
        '''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            connection.commit()
    except Error as e:
        print(e)


def get_group_id(group):
    try:
        insert_into_table_name = f'''SELECT id
        FROM product_group
        WHERE group_name = "{group}"
        '''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            result = cursor.fetchall()
            for row in result:
                return row
    except Error as e:
        print(e)


def get_all_group_name():
    try:
        insert_into_table_name = f'''SELECT group_name
        FROM product_group'''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            result = cursor.fetchall()
            return result
    except Error as e:
        print(e)


def get_name_product_from_group(group):
    try:
        insert_into_table_name = f'''SELECT products.name
        FROM products
        WHERE group_id = (SELECT id FROM product_group WHERE group_name = "{group}")'''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            result = cursor.fetchall()
            return result
    except Error as e:
        print(e)


def get_all_product_name():
    try:
        insert_into_table_name = f'''SELECT name
        FROM products'''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            result = cursor.fetchall()
            return result
    except Error as e:
        print(e)


def get_product(product):
    try:
        insert_into_table_name = f'''SELECT name, amount, price, image
        FROM products
        WHERE name = "{product}"'''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            result = cursor.fetchall()
            return result
    except Error as e:
        print(e)


def add_user(lst):
    try:
        insert_into_table_name = f'''INSERT INTO users (user_id, first_name, last_name, user_name) 
                                     VALUES (%s, %s, %s, %s)
        '''
        with connection.cursor() as cursor:
            cursor.executemany(insert_into_table_name, lst)
            connection.commit()
    except Error as e:
        print(e)


def take_away_quantity(num, product):
    try:
        insert_into_table_name = f'''UPDATE products
        SET amount = amount - {num}
        WHERE name = "{product}"
        '''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            connection.commit()
    except Error as e:
        print(e)


def add_user_basket(lst):
    try:
        insert_into_table_name = f'''INSERT INTO basket (user_id, product, amount) 
                                     VALUES (%s, %s, %s)
            '''
        with connection.cursor() as cursor:
            cursor.executemany(insert_into_table_name, lst)
            connection.commit()
    except Error as e:
        print(e)


def get_basket(user_id):
    try:
        insert_into_table_name = f'''SELECT product, amount
        FROM basket
        WHERE user_id = "{user_id}"'''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            result = cursor.fetchall()
            return result
    except Error as e:
        print(e)


def delete_in_basket(user_id, product):
    try:
        insert_into_table_name = f'''DELETE FROM basket
        WHERE product = "{product}" AND user_id = "{user_id}"
        '''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            connection.commit()
    except Error as e:
        print(e)


def minus_in_basket(user_id, product, amount):
    try:
        insert_into_table_name = f'''UPDATE basket
        SET amount = amount - {amount}
        WHERE product = "{product}" AND user_id = "{user_id}"
        '''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            connection.commit()
    except Error as e:
        print(e)


def plus_in_basket(u, p, a):
    try:
        with connection.cursor() as cursor:
            cursor.callproc('insert_basket', (u, p, a))
            connection.commit()
    except Error as e:
        print(e)


def check_basket(user_id):
    try:
        insert_into_table_name = f'''SELECT EXISTS(SELECT 2 FROM basket WHERE user_id = {user_id})
        '''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            result = cursor.fetchall()
            return result
    except Error as e:
        print(e)


def add_order(lst):
    try:
        insert_into_table_name = f'''INSERT INTO orders (id, user_id, name, price) 
                                     VALUES (%s, %s, %s, %s)
        '''
        with connection.cursor() as cursor:
            cursor.executemany(insert_into_table_name, lst)
            connection.commit()
    except Error as e:
        print(e)


def get_id_for_order(user_id):
    try:
        insert_into_table_name = f'''SELECT id
        FROM basket
        WHERE user_id = {user_id}
        '''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            result = cursor.fetchall()
            return result[0][0]
    except Error as e:
        print(e)


def get_first_name(user_id):
    try:
        insert_into_table_name = f'''SELECT first_name
        FROM users
        WHERE user_id = {user_id}
        '''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            result = cursor.fetchall()
            return result[0][0]
    except Error as e:
        print(e)


def get_price_for_order(user_id):
    try:
        insert_into_table_name = f'''select SUM(price*basket.amount)
        from basket inner join products on basket.product = products.name
        WHERE user_id = {user_id}
        '''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            result = cursor.fetchall()
            return result[0][0]
    except Error as e:
        print(e)


def clear_basket(user_id):
    try:
        insert_into_table_name = f'''DELETE FROM basket
        WHERE user_id = "{user_id}"
        '''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            connection.commit()
    except Error as e:
        print(e)


def get_all_basket():
    try:
        insert_into_table_name = f'''SELECT user_id, product, amount
        FROM basket
        '''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            result = cursor.fetchall()
            return result
    except Error as e:
        print(e)


def clear_all_basket():
    try:
        insert_into_table_name = f'''DELETE FROM basket
        '''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            connection.commit()
    except Error as e:
        print(e)


def get_all_orders():
    try:
        insert_into_table_name = f'''SELECT id, name, price
        FROM orders
        '''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            result = cursor.fetchall()
            return result
    except Error as e:
        print(e)


def insert_product_for_order(lst):
    try:
        insert_into_table_name = f'''INSERT INTO products_for_order (id, product, amount) 
                                     VALUES (%s, %s, %s)
            '''
        with connection.cursor() as cursor:
            cursor.executemany(insert_into_table_name, lst)
            connection.commit()
    except Error as e:
        print(e)


def del_order(order_id):
    try:
        insert_into_table_name = f'''
        DELETE FROM orders
        WHERE id = {order_id}
        '''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            connection.commit()
    except Error as e:
        print(e)


def del_products_for_order(order_id):
    try:
        insert_into_table_name = f'''
        DELETE FROM products_for_order
        WHERE id = {order_id}
        '''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            connection.commit()
    except Error as e:
        print(e)


def get_product_from_order(order_id):
    try:
        insert_into_table_name = f'''SELECT amount, product
        FROM products_for_order
        WHERE id = {order_id}
        '''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            result = cursor.fetchall()
            return result
    except Error as e:
        print(e)


def check_user(user_id):
    try:
        insert_into_table_name = f'''SELECT EXISTS(SELECT 2 FROM users WHERE user_id = {user_id})
        '''
        with connection.cursor() as cursor:
            cursor.execute(insert_into_table_name)
            result = cursor.fetchall()
            return result
    except Error as e:
        print(e)
# add_product([['oz', 26, 1, 1, 't']])
# add_group("no beer")
# delete_group('no beer')
# delete_product('r')
# print(get_group_id("no beer"))
# print(get_all_group_name())
# print(get_product_from_group("пиво"))
# print([i for i in get_product_from_group('пиво')])
# print(get_all_product_name())
# print(get_product("q")[0])
# add_user([[1, "Dav", "Davidson", "Tot"]])
# add_user_basket([[1, "beer", 3]])
# take_away_quantity(1, "beer")
# print(get_basket(1))
# add_products_for_order([[1, 'tyt', 1, 1]])
# add_order([[0, 0, 'служебный', 0]])
# print(get_id_for_order())
# update_order_id()

