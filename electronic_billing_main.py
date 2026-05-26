import os
from datetime import datetime
import pandas as pd  # Import pandas for advanced CSV handling

# --- FILE PATH CONFIGURATION ---
# Dynamically locate the script's directory so it works on any computer
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#Reading the product csv file and customer csv file from the same directory as the script\
PRODUCT_FILE = os.path.join(BASE_DIR, "products.csv")
CUSTOMER_FILE = os.path.join(BASE_DIR, "customers.csv")



# ---------------- FILE HANDLING VIA PANDAS ---------------- #

# ---------------- FILE HANDLING ---------------- #

def load_products():
    products = {}
    try:
        # Load CSV data into a Pandas DataFrame
        df = pd.read_csv(PRODUCT_FILE, encoding='utf-8')
        
        # Ensure the product_id column reads as strings so lookups work cleanly
        df['product_id'] = df['product_id'].astype(str)
        
        # Convert DataFrame rows into a nested Python dictionary indexed by product_id
        products = df.set_index('product_id').to_dict(orient='index')
        

    except Exception as e:
        print("Product csv file not found. Please ensure 'products.csv' exists in the same directory as this script. Starting with an empty inventory.")
    return products


def save_products(products):
    if not products:
        # If the memory dictionary is completely empty, create an empty structured CSV file
        df = pd.DataFrame(columns=["product_id", "name", "price", "quantity"])
        df.to_csv(PRODUCT_FILE, index=False, encoding='utf-8')
        return
        
    try:
        # Turn the memory dictionary back into a Pandas DataFrame
        df = pd.DataFrame.from_dict(products, orient='index')
        
        # Move the index ('product_id') back into its own structural column
        df.index.name = 'product_id'
        df = df.reset_index()
        
        # Write rows cleanly back down to the disk file
        df.to_csv(PRODUCT_FILE, index=False, encoding='utf-8')
    except Exception as e:
        print(f"Error saving products: {e}")


def load_customers():
    customers = []
    try:
        # Load the CSV transactions ledger sheet directly into a DataFrame
        df = pd.read_csv(CUSTOMER_FILE, encoding='utf-8')
        
        # Convert the structural DataFrame cleanly into a list of row dictionaries
        customers = df.to_dict(orient='records')
    except FileNotFoundError:
        print("Customer file not found. Starting fresh.")
    except Exception as e:
        print(f"Error loading customers: {e}")
    return customers


def save_customers(customers):
    try:
        # Generate a structural DataFrame matching our list records array
        df = pd.DataFrame(customers)
        
        # If the list array was empty, make sure headers are structurally retained on disk
        if df.empty:
            df = pd.DataFrame(columns=["customer_id", "items", "total", "datetime"])
            
        # Write rows cleanly back down to the disk file
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
    if not bill:
        print("Bill is empty!")
        return

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
            if not products:
                print("Inventory database is empty.")
            else:
                for pid, p in products.items():
                    print(pid, p)

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
        print("\n1. Show Customers\n2. Remove Customer\n3. Add customer \n4. Back")
        choice = input("Choice: ")

        if choice == '1':
            for c in customers:
                print(c)

        elif choice == '2':
            cid = input("Enter customer ID: ")
            customers[:] = [c for c in customers if c["customer_id"] != cid]

        elif choice == '3':
            cid = input("Customer ID: ")
            items = input("Items (format: name xqty, ...): ")
            total = float(input("Total: "))
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            customers.append({
                "customer_id": cid,
                "items": items,
                "total": total,
                "datetime": now
            })

        elif choice == '4':
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
