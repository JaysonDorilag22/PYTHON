class Product:
    def __init__(self, name, quantity, price):
        self.name = name
        self.quantity = quantity
        self.price = price

    def __str__(self):
        return f"Product(name={self.name}, quantity={self.quantity}, price={self.price})"

class Inventory:
    def __init__(self):
        self.products = []

    def add_product(self, product):
        self.products.append(product)

    def remove_product(self, product_name):
        self.products = [product for product in self.products if product.name != product_name]

    def update_product(self, product_name, quantity=None, price=None):
        for product in self.products:
            if product.name == product_name:
                if quantity is not None:
                    product.quantity = quantity
                if price is not None:
                    product.price = price

    def list_products(self):
        for product in self.products:
            print(product)

def main():
    inventory = Inventory()

    while True:
        print("\nInventory Management System")
        print("1. Add Product")
        print("2. Remove Product")
        print("3. Update Product")
        print("4. List Products")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter product name: ")
            quantity = int(input("Enter product quantity: "))
            price = float(input("Enter product price: "))
            product = Product(name, quantity, price)
            inventory.add_product(product)
        elif choice == '2':
            name = input("Enter product name to remove: ")
            inventory.remove_product(name)
        elif choice == '3':
            name = input("Enter product name to update: ")
            quantity = input("Enter new quantity (leave blank to keep current): ")
            price = input("Enter new price (leave blank to keep current): ")
            quantity = int(quantity) if quantity else None
            price = float(price) if price else None
            inventory.update_product(name, quantity, price)
        elif choice == '4':
            inventory.list_products()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()