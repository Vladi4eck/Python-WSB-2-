from itertools import product

import psycopg2
import bcrypt
from typing import Optional

#Singleton for more optimised connection
class DatabaseConnection:
    _instance: Optional[psycopg2.extensions.connection] = None

    @classmethod
    def get_connection(cls) :
        if cls._instance is None or cls._instance.closed:
            cls._instance = psycopg2.connect(
            dbname = "wsb", #Name of Database
            user = "postgres", #User in postgres
            password = "Gamer323*", #Password for Database et.g
            host = "localhost",
            port = "5432",
            )
        return cls._instance

    @classmethod
    def close_connection(cls):  #Closing connection
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None

#Function to hash passwords
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt() #Salt for hashing
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

#Function to register users
def register_user(name: str, email: str, password: str, role: str = 'client'):
    hashed_pw = hash_password(password)
    conn = DatabaseConnection.get_connection() #Connection to database's data
    cursor = conn.cursor()

    #Adding registered user to table Users
    insert_query = """ 
    INSERT INTO users (name, email, password, role) 
    VALUES (%s, %s, %s, %s)
    RETURNING id;
    """
    cursor.execute(insert_query, (name, email, hashed_pw, role))
    user_id = cursor.fetchone()[0]

    conn.commit()
    print(f"User successfully registered (id = {user_id})")

    # cursor.close()
    # conn.close()

def check_password(plain_password: str, hashed_password: str) -> bool: #Comparing passwords
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def login_user(email: str,password: str):
    conn = DatabaseConnection.get_connection() #Connection in order to compare data
    cursor = conn.cursor()


    select_query = """ 
        SELECT id, name, email, password, role 
        FROM users
        WHERE email = %s;
        """
    cursor.execute(select_query, (email,))
    user = cursor.fetchone()
    cursor.close()

    if not user: #Incorrect email
        print("User not found.")
        return

    user_id, name, email, hashed_pw, role = user

    if not check_password(password, hashed_pw): #Incorrect password
        print("Incorrect password.")
        return

    print(f"Login successful: {name} (id={user_id}, role={role})")

    if role == "administrator":
        print("Access to administrative functions activated")
        admin_options()
    else:
        print("Regular user")
        user_options(user_id)

def admin_options():
    print("== Welcome! What would you like to do? ==")
    while True:
        action = input("1 - Show tables | 2 - Delete tables | 0 - Log out ")
        if action == "1":
            list_tables()
        elif action == "2":
            list_tables()
            delete_table()
        elif action == "0":
            break
        else:
            print("Error") #Unrecognisable symbol
def user_options(user_id: int):
    print("== Welcome! What would you like to do? ==")
    while True:
        action = input("1 - Check product list | 2 - My orders | 3 - Buy a product | 0 - Cancel ")
        if action == "1": #Checking table products
            list_products()
        elif action == "2": #Checking table orders
            list_user_orders(user_id)
        elif action == "3":
            buy_product(user_id)
        elif action == "0":
            break
        else:
            print("Print only numbers")

#def table_manipulation():
#print("== What would you like to do with the tables? ==")
#action = input("1 - Delete | 2 - Check")
#if action == 1:
def list_products():
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id,name,price, stock FROM products;")
        products = cursor.fetchall()
        if not products:
            print("No products in stock")
        else:
            print("Available products:")
            for pid,name,price, stock in products:
                print(f"ID: {pid},Name: {name},Price: {price} zł,In stock: {stock}")
    except Exception as e:
        print(f"Error:{e}")
    finally: cursor.close()

def list_user_orders(user_id: int):
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT o.id, o.status, o.created_at, p.amount, p.status
            FROM orders o
            LEFT JOIN payments p ON o.id = p.order_id
            WHERE o.user_id = %s;
        """, (user_id,))
        orders = cursor.fetchall()
        if not orders:
            print("You have no orders yet")
        else:
            print("Your orders: ")
            for oid, status, created, amount, pay_status in orders:
                print(f" Order ID: {oid}, Status: {status}, Price: {amount} zł, Payment Method: {pay_status}, Date: {created}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

def list_tables():
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
        """)
        tables = cursor.fetchall()

        if not tables:
            print("No tables in sc 'public'.")
            return

        print("List of tables in data base:")
        for table in tables:
            print(f"• {table[0]}")


    except Exception as e:
        print(f"Error while retrieving the list of tables: {e}")
    finally:
        cursor.close()

def delete_table():
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()

    table_name = input("Enter the name of the table you want to delete: ").strip()

    confirm = input(f"Are you sure about deleting this table '{table_name}'? (yes/no): ").lower().strip()
    if confirm != "yes":
        print("Canceled")
        return

    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        conn.commit()
        print(f"The table '{table_name}' has been deleted")
    except Exception as e:
        print(f"During the process occurred an error: {e}")
    finally:
        cursor.close()

def buy_product(user_id: int):
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()

    try: #Show available products
        cursor.execute("SELECT id, name, price, stock FROM products;")
        products = cursor.fetchall()
        if not products:
            print("No products available")
            return

        print("Available products: ")
        for prod in products:
            print(f"ID: {prod[0]} | {prod[1]} | Price: {prod[2]} | In stock: {prod[3]}")

        #Product choosing
        product_id = int(input("Enter product's ID: "))
        quantity = int(input("Quantity: "))

        #Check if available
        cursor.execute("SELECT price, stock FROM products WHERE id = %s;", (product_id,))
        result = cursor.fetchone()
        if not result:
            print("Product not found")
            return

        price, stock = result
        if quantity > stock:
            print("Not enough goods in stock.")
            return

        total_price = price * quantity

        #Creating an order
        cursor.execute(
            "INSERT INTO orders(user_id,status) VALUES (%s, 'new') RETURNING id;",
            (user_id,)
        )
        order_id = cursor.fetchone()[0]
        #Adding product to the order
        cursor.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s);",
            (order_id, product_id, quantity, price)
        )
        # #Lowering quantity
        # cursor.execute(
        #     "UPDATE products SET stock = stock - %s WHERE id = %s;",
        #     (quantity, product_id)
        # )
        #Creating payment
        cursor.execute(
            "INSERT INTO payments (order_id, payment_method, amount, status) VALUES (%s, 'card', %s, 'pending');",
            (order_id, total_price)
        )
        conn.commit()
        print(f" Order №{order_id} successfully placed for the amount of {total_price:.2f} PLN.")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close
#Пример запуска

def main():
    while 1==1:
        action = input("1 - Sign up | 2 - Log in | 0 - Exit: " ).lower().strip()
        if action == "1":
            print("=== Registration ===")
            name = input("Name: ")
            email = input("Email: ")
            password = input("Password: ")
            role = input('Your role: administrator/client? ')
            register_user(name, email, password, role)
        elif action == "2":
            print("=== Authorisation ===")
            email = input("Email: ")
            password = input("Password: ")
            login_user(email,password)
        elif action == "0":
            break
        else:
            print("Type only numbers")
#Todo возможность делать покупки при входе за обычного юзера
main()

DatabaseConnection.close_connection()