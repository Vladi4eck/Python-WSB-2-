## Ten projekt to system zarządzania sklepem internetowym z bazą danych PostgreSQL i interfejsem w Pythonie.
###  System obejmuje:
 -  Uwierzytelnianie użytkowników (rejestracja i logowanie)
 -  Zarządzanie produktami
 -  Składanie zamówień
 -  Zarządzanie płatnościami
 -  Funkcje administracyjne
### SQL Struktura bazy danych 
####  **Users** - przechowuje informacje o użytkownikach:
 - id (SERIAL PRIMARY KEY)
 - name (VARCHAR)
 - password (VARCHAR)
 - email (VARCHAR, UNIQUE)
 - role (ENUM: 'administrator' lub 'client') 
 - created_at (TIMESTAMP)
#### **Products** - zawiera dane o produktach:
 - id (SERIAL PRIMARY KEY)
 - name (VARCHAR)
 - description (TEXT)
 - price (DECIMAL)
 - stock (INTEGER)
#### **Orders** - informacje o zamówieniach:
- id (SERIAL PRIMARY KEY)
- user_id (FOREIGN KEY do users)
- created_at (TIMESTAMP)
- status (ENUM: 'new', 'processing', 'shipped', 'delivered', 'cancelled')
#### **Order_items** - produkty w zamówieniach:
- order_id (FOREIGN KEY do orders)
- product_id (FOREIGN KEY do products)
- quantity (INTEGER)
- price (DECIMAL)
####  **Payments** - dane o płatnościach:
- id (SERIAL PRIMARY KEY)
- order_id (FOREIGN KEY do orders)
- payment_method (VARCHAR)
- amount (DECIMAL)
- status (ENUM: 'pending', 'paid', 'error')

### Triggers

1. **decrease_stock** - automatycznie zmniejsza ilość produktu w magazynie po dodaniu do zamówienia

2. **update_order_status_after_payment** - aktualizuje status zamówienia na 'processing' po udanej płatności
## Python Interfejs 
### Klasy
 **DatabaseConnection** - implementuje wzorzec Singleton do zarządzania połączeniem z bazą danych
### Główne funkcje
#### **Uwierzytelnianie**:
hash_password - haszuje hasło za pomocą bcrypt 
register_user - rejestruje nowego użytkownika
login_user - loguje użytkownika
#### **Funkcje użytkownika**:
list_products - wyświetla dostępne produkty 
list_user_orders - pokazuje zamówienia użytkownika 
buy_products - składa nowe zamówienie
#### Funkcje administracyjne:
list_tables - wyświetla listę tabel w bazie danych
delete_table - usuwa wskazaną tabelę
## Bezpicieństwo 
- Hasła przechowywane są w postaci zahaszowanej przy użyciu bcrypt
- Zaimplementowana weryfikacja ról w celu ograniczenia dostępu
- Codziennie o godzinie 2:00 tworzona jest kopia zapasowa kodu SQL projektu na moim komputerze