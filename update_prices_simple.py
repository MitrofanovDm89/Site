import sqlite3
import os

# Путь к базе данных
db_path = 'db.sqlite3'

# Проверяем, что файл базы данных существует
if not os.path.exists(db_path):
    print(f"Файл базы данных не найден: {db_path}")
    exit(1)

# Подключаемся к базе данных
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Проверяем, есть ли поля price_netto и price_brutto
cursor.execute("PRAGMA table_info(catalog_product)")
columns = cursor.fetchall()
column_names = [col[1] for col in columns]

print("Доступные колонки в таблице catalog_product:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

if 'price_netto' not in column_names or 'price_brutto' not in column_names:
    print("Поля price_netto и price_brutto не найдены в таблице!")
    print("Нужно применить миграцию.")
    conn.close()
    exit(1)

# Получаем список товаров
cursor.execute("SELECT id, title, slug, price_netto, price_brutto FROM catalog_product")
products = cursor.fetchall()

print(f"\nНайдено товаров: {len(products)}")

# Обновляем цены
products_to_update = [
    # Hüpfburgen
    ('huepfburg-zirkus', 83.19, 99.00),
    ('huepfburg-dschungel', 109.24, 130.00),
    ('huepfburg-polizei', 126.05, 150.00),
    ('huepfburg-madagaskar', 126.05, 150.00),
    ('huepfburg-party', 184.87, 220.00),
    ('huepfburg-maxi', 210.08, 250.00),
    
    # Spiele & Unterhaltung
    ('shooting-combo', 252.10, 300.00),
    ('dart-xxl', 83.19, 99.00),
    ('fussball-billiard', 83.19, 99.00),
    
    # Vermietung
    ('event-betreuung', 252.10, 300.00),
    ('fussball-darts', 83.19, 99.00),
    ('kinderbetreuung', 210.08, 250.00),
    ('animation', 184.87, 220.00),
    ('dekorationsservice', 126.05, 150.00),
    ('catering-service', 252.10, 300.00),
    ('fotograf', 210.08, 250.00),
    ('dj-service', 184.87, 220.00),
    ('transport-service', 252.10, 300.00),
]

updated_count = 0
for slug, price_netto, price_brutto in products_to_update:
    cursor.execute(
        "UPDATE catalog_product SET price_netto = ?, price_brutto = ? WHERE slug = ?",
        (price_netto, price_brutto, slug)
    )
    if cursor.rowcount > 0:
        print(f"Обновлен товар: {slug}")
        updated_count += 1
    else:
        print(f"Товар не найден: {slug}")

conn.commit()
conn.close()

print(f"\nУспешно обновлено {updated_count} товаров") 