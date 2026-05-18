import csv
from datetime import datetime

PRODUCT_FILE = r"C:\Users\nilov\ReDi School\Retail Electronic Billing project\electronic billing-project details\electronic billing\products_large.csv"
CUSTOMER_FILE = r"C:\Users\nilov\ReDi School\Retail Electronic Billing project\electronic billing-project details\electronic billing\customers_large.csv"


# ---------------- FILE HANDLING ---------------- #
def load_products():
    products = {}
    try:
        with open(PRODUCT_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                products[row['product_id']] = {
                    "name": row['name'],
                    "price": float(row['price']),
                    "quantity": int(row['quantity'])
                }
    except FileNotFoundError:
        print("Product file not found. Starting with empty database.")
    return products


def save_products(products):
    with open(PRODUCT_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["product_id", "name", "price", "quantity"])
        for pid, details in products.items():
            writer.writerow([pid, details["name"], details["price"], details["quantity"]])


def load_customers():
    customers = []
    try:
        with open(CUSTOMER_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                customers.append(row)
    except FileNotFoundError:
        print("Customer file not found. Starting fresh.")
    return customers


def save_customers(customers):
    with open(CUSTOMER_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["customer_id", "items", "total", "datetime"])
        for c in customers:
            writer.writerow([c["customer_id"], c["items"], c["total"], c["datetime"]])


# ---------------- BILL FUNCTIONS ---------------- #
def scan_items(products, bill):
    while True:
        pid = input("Enter product ID (or 'q' to stop): ")
        if pid == 'q':
            break

        if pid not in products:
            print("Invalid product ID.")
            continue

        if products[pid]["quantity"] <= 0:
            print("Out of stock!")
            continue

        bill.append(pid)
        print(f"Added {products[pid]['name']} to bill.")


def show_bill(products, bill):
    total = 0
    print("\n--- Current Bill ---")
    for i, pid in enumerate(bill):
        product = products[pid]
        print(f"{i+1}. {product['name']} - {product['price']}")
        total += product['price']
    print("Total:", total)


def remove_item(products, bill):
    show_bill(products, bill)
    try:
        index = int(input("Enter item number to remove: ")) - 1
        if 0 <= index < len(bill):
            removed = bill.pop(index)
            print("Removed:", products[removed]["name"])
        else:
            print("Invalid index.")
    except:
        print("Invalid input.")


def generate_bill(products, customers, bill):
    if not bill:
        print("Bill is empty!")
        return

    total = 0
    item_summary = {}

    for pid in bill:
        product = products[pid]
        total += product["price"]
        products[pid]["quantity"] -= 1

        if pid in item_summary:
            item_summary[pid]["qty"] += 1
        else:
            item_summary[pid] = {
                "name": product["name"],
                "qty": 1
            }

    items_str = ", ".join([f"{v['name']} x{v['qty']}" for v in item_summary.values()])
    customer_id = len(customers) + 1
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    customers.append({
        "customer_id": customer_id,
        "items": items_str,
        "total": total,
        "datetime": now
    })

    print("\n--- FINAL BILL ---")
    print("Customer ID:", customer_id)
    print("Items:", items_str)
    print("Total:", total)
    print("Date:", now)


# ---------------- DATABASE MANAGEMENT ---------------- #
def manage_products(products):
    while True:
        print("\n1. Show Products\n2. Add Product\n3. Remove Product\n4. Back")
        choice = input("Choice: ")

        if choice == '1':
            for pid, p in products.items():
                print(pid, p)

        elif choice == '2':
            pid = input("ID: ")
            name = input("Name: ")
            price = float(input("Price: "))
            qty = int(input("Quantity: "))
            products[pid] = {"name": name, "price": price, "quantity": qty}

        elif choice == '3':
            pid = input("Enter ID to remove: ")
            products.pop(pid, None)

        elif choice == '4':
            break


def manage_customers(customers):
    while True:
        print("\n1. Show Customers\n2. Remove Customer\n3. Back")
        choice = input("Choice: ")

        if choice == '1':
            for c in customers:
                print(c)

        elif choice == '2':
            cid = input("Enter customer ID: ")
            customers[:] = [c for c in customers if c["customer_id"] != cid]

        elif choice == '3':
            break


# ---------------- MAIN MENU ---------------- #
def main():
    products = load_products()
    customers = load_customers()

    while True:
        print("\n==== BILLING SYSTEM ====")
        print("1. New Bill")
        print("2. Manage Products")
        print("3. Manage Customers")
        print("4. Exit")

        choice = input("Select option: ")

        if choice == '1':
            bill = []
            while True:
                print("\n1. Scan Items\n2. Show Bill\n3. Remove Item\n4. Finalize\n5. Cancel")
                sub = input("Choice: ")

                if sub == '1':
                    scan_items(products, bill)
                elif sub == '2':
                    show_bill(products, bill)
                elif sub == '3':
                    remove_item(products, bill)
                elif sub == '4':
                    generate_bill(products, customers, bill)
                    break
                elif sub == '5':
                    break

        elif choice == '2':
            manage_products(products)

        elif choice == '3':
            manage_customers(customers)

        elif choice == '4':
            save_products(products)
            save_customers(customers)
            print("Data saved. Exiting...")
            break


if __name__ == "__main__":
    main()