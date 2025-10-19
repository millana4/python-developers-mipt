
class Product:
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock

    def update_stock(self, quantity):
        quantity = int(quantity)
        if self.stock + quantity >= 0:
            self.stock += quantity
        else:
            raise ValueError('Количество товара не может быть отрицательным')

class Order:
    def __init__(self):
        self.positions = {}

    def add_product(self, product, quantity):
        """Добавляет товар в заказ"""
        if quantity <= product.stock:
            self.positions[product] = quantity
            product.stock -= quantity
        else:
            raise Exception(f"Недостаточно товара '{product.name}' на складе. Доступно: {product.stock}")

    def calculate_total(self):
        """Рассчитывает стоимость заказа"""
        total = 0
        for product, quantity in self.positions.items():
            total += product.price * quantity
        return total

class Store:
    def __init__(self):
        self.products = []

    def add_product(self, product):
        """Добавляет товар в магазин"""
        self.products.append(product)

    def list_products(self):
        """Показывает все товары в магазине"""
        print(f"Наименование товара ----- Цена -------- Количество")
        for product in self.products:
            print(f"{product.name} ----- {product.price} ----- {product.stock}")

    def create_order(self):
        """Создает новый заказ"""
        return Order()

# Задача: Модель магазина

# Создаем магазин
store = Store()

# Создаем товары
product1 = Product("Ноутбук", 1000, 5)
product2 = Product("Смартфон", 500, 10)

# Добавляем товары в магазин
store.add_product(product1)
store.add_product(product2)

# Список всех товаров
store.list_products()

# Создаем заказ
order = store.create_order()

# Добавляем товары в заказ
order.add_product(product1, 2)
order.add_product(product2, 3)

# Выводим общую стоимость заказа
total = order.calculate_total()
print(f"Общая стоимость заказа: {total}")

# Проверяем остатки на складе после заказа
store.list_products()

