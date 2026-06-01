import os
from datetime import datetime
import pandas as pd  # Import pandas for advanced CSV handling

# --- FILE PATH CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PRODUCT_FILE = os.path.join(BASE_DIR, "products.csv")
CUSTOMER_FILE = os.path.join(BASE_DIR, "customers.csv")


# ---------------- FILE HANDLING ---------------- #

def load_products():
    products = {}
    try:
        df = pd.read_csv(PRODUCT_FILE, encoding='utf-8')
        df['product_id'] = df['product_id'].astype(str)
        products = df.set_index('product_id').to_dict(orient='index')
    except Exception as e:
        print("Product csv file not found. Starting with an empty inventory.")
    return products


def save_products(products):
    if not products:
        df = pd.DataFrame(columns=["product_id", "name", "price", "quantity"])
        df.to_csv(PRODUCT_FILE, index=False, encoding='utf-8')
        return
        
    try:
        df = pd.DataFrame.from_dict(products, orient='index')
        df.index.name = 'product_id'
        df = df.reset_index()
        df.to_csv(PRODUCT_FILE, index=False, encoding='utf-8')
    except Exception as e:
        print(f"Error saving products: {e}")


def load_customers():
    customers = []
    try:
        df = pd.read_csv(CUSTOMER_FILE, encoding='utf-8')
        customers = df.to_dict(orient='records')
    except FileNotFoundError:
        print("Customer file not found. Starting fresh.")
    except Exception as e:
        print(f"Error loading customers: {e}")
    return customers


def save_customers(customers):
    try:
        df = pd.DataFrame(customers)
        if df.empty:
            df = pd.DataFrame(columns=["customer_id", "items", "total", "datetime"])
        df.to_csv(CUSTOMER_FILE, index=False, encoding='utf-8')
    except Exception as e:
        print(f"Error saving customers: {e}")


# ---------------- BILL FUNCTIONS ---------------- #

def scan_items(products, bill):
    while True:
        pid = input("Enter product ID (or 'q' to stop): ").strip()
        if pid == 'q':
            break

        if pid not in products:
            print("Invalid product ID.")
            continue

        if products[pid]["quantity"] <= 0:
            print(f"Out of stock! {products[pid]['name']} is completely unavailable.")
            continue

        products[pid]["quantity"] -= 1
        bill.append(pid)
        print(f"Added {products[pid]['name']} to bill. (Remaining stock: {products[pid]['quantity']})")


def show_bill(products, bill):
    total = 0
    print("\n--- Current Bill ---")
    for i, pid in enumerate(bill):
        product = products[pid]
        print(f"{i+1}. {product['name']} - {product['price']:.2f} DKK")
        total += product['price']
    print(f"Total: {total:.2f} DKK") 


def remove_item(products, bill):
    if not bill:
        print("Bill is empty!")
        return

    show_bill(products, bill)
    try:
        index = int(input("Enter item number to remove: ")) - 1
        if 0 <= index < len(bill):
            removed = bill.pop(index)
            products[removed]["quantity"] += 1
            print(f"Removed: {products[removed]['name']}. (Stock restored to: {products[removed]['quantity']})")
        else:
            print("Invalid index.")
    except ValueError:
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

        if pid in item_summary:
            item_summary[pid]["qty"] += 1
        else:
            item_summary[pid] = {
                "name": product["name"],
                "qty": 1
            }

    items_str = ", ".join([f"{v['name']} x{v['qty']}" for v in item_summary.values()])
    customer_id = max([int(c["customer_id"]) for c in customers], default=0) + 1
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    formatted_total = f"{total:.2f}"

    customers.append({
        "customer_id": customer_id,
        "items": items_str,
        "total": formatted_total,  
        "datetime": now
    })

    print("\n--- FINAL BILL ---")
    print("Customer ID:", customer_id)
    print("Items:", items_str)
    print(f"Total: {total:.2f} DKK")  
    print("Date:", now)
    
    save_products(products)
    save_customers(customers)


# ---------------- DATABASE MANAGEMENT ---------------- #

def manage_products(products):
    while True:
        print("\n1. Show Products\n2. Add Product\n3. Remove Product\n4. Back")
        choice = input("Choice: ")

        if choice == '1':
            if not products:
                print("Inventory database is empty.")
            else:
                # Print headers with clean fixed formatting widths
                print(f"\n{'ID':<10} {'Name':<20} {'Price':<15} {'Quantity':<10}")
                print("-" * 60)
                
                # FIX: Instead of printing the raw dictionary element 'p', 
                # we print the explicit subkeys cleanly formatted into columns
                for pid, p in products.items():
                    price_display = f"{p['price']:.2f} DKK"
                    print(f"{pid:<10} {str(p['name']).strip():<20} {price_display:<15} {p['quantity']:<10}")    

        elif choice == '2':
            try:
                pid = input("ID: ").strip()
                name = input("Name: ").strip()
                price = float(input("Price: "))
                qty = int(input("Quantity: "))
                products[pid] = {"name": name, "price": price, "quantity": qty}
                print(f"Product '{name}' updated successfully.")
            except ValueError:
                print("Invalid numeric value provided for Price or Quantity.")

        elif choice == '3':
            pid = input("Enter ID to remove: ").strip()
            if products.pop(pid, None) is not None:
                print(f"Product ID '{pid}' removed.")
            else:
                print("Product ID not found.")

        elif choice == '4':
            break


def manage_customers(customers):
    while True:
        print("\n1. Show Customers\n2. Remove Customer\n3. Back")
        choice = input("Choice: ")

        if choice == '1':
            if not customers:
                print("Customer database ledger is empty.")
            else:
                for c in customers:
                    print(c)

        elif choice == '2':
            cid = input("Enter customer ID: ").strip()
            initial_count = len(customers)
            customers[:] = [c for c in customers if str(c["customer_id"]) != cid]
            
            if len(customers) < initial_count:
                print(f"Customer log history '{cid}' dropped out of system stack.")
            else:
                print("Customer ID reference index missing.")

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
                print("\n1. Scan Items\n2. Show Bill\n3. Remove Item\n4. Finalize and add customer to the customer database\n5. Cancel")
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
                    for pid in bill:
                        products[pid]["quantity"] += 1
                    print("Bill cancelled. Items returned to inventory.")
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