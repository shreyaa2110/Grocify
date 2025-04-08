import tkinter as tk
from tkinter import messagebox, ttk
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
from datetime import datetime


categories = {
    "Food Items": {
        "Milk (1L)": 30,
        "Eggs (6 pcs)": 40,
        "Butter (100g)": 55,
        "Cheese (200g)": 90,
        "Bread (loaf)": 25,
        "Biscuits (pack)": 20,
        "Maggi Noodles": 15,
        "Tea (250g)": 75,
        "Coffee (100g)": 110,
        "Juice (1L)": 50
    },
    "Groceries": {
        "Rice (1kg)": 60,
        "Wheat Flour (1kg)": 45,
        "Sugar (1kg)": 42,
        "Salt (1kg)": 20,
        "Cooking Oil (1L)": 140
    },
    "Other House Requirements": {
        "Toothpaste": 50,
        "Shampoo (100ml)": 70,
        "Soap (bar)": 35,
        "Detergent (500g)": 65,
        "Handwash": 60
    }
}

cart = {}
customer_name = ""
customer_phone = ""

# Launch popup for quantity input
def prompt_quantity(product_name, price):
    qty_window = tk.Toplevel(root)
    qty_window.title("Enter Quantity")
    qty_window.geometry("250x130")
    qty_window.grab_set()

    tk.Label(qty_window, text=f"Enter quantity for\n{product_name}", font=("Arial", 11)).pack(pady=10)
    qty_entry = tk.Entry(qty_window, justify="center")
    qty_entry.pack()

    def add_and_close():
        try:
            qty = int(qty_entry.get())
            if qty <= 0:
                raise ValueError
            add_to_cart(product_name, price, qty)
            qty_window.destroy()
        except:
            messagebox.showerror("Invalid Input", "Please enter a valid quantity.")

    tk.Button(qty_window, text="Add", bg="#4CAF50", fg="white", command=add_and_close).pack(pady=8)


def add_to_cart(item, price, qty):
    if item in cart:
        cart[item]['qty'] += qty
        cart[item]['total'] = cart[item]['qty'] * cart[item]['price']
    else:
        cart[item] = {'price': price, 'qty': qty, 'total': price * qty}
    update_cart_display()


def update_cart_display():
    cart_list.delete(*cart_list.get_children())
    total = 0
    for i, (item, details) in enumerate(cart.items(), start=1):
        amount = details['qty'] * details['price']
        total += amount
        cart_list.insert('', 'end', values=(
            i,
            item,
            details['qty'],
            f"₹{details['price']:.2f}",
            f"₹{amount:.2f}"
        ))
    total_label.config(text=f"Total: ₹{total:.2f}")

def remove_selected():
    selected = cart_list.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select an item to remove.")
        return
    item_index = int(cart_list.item(selected[0])['values'][0]) - 1
    item_name = list(cart.keys())[item_index]
    del cart[item_name]
    update_cart_display()


def generate_bill():
    if not cart:
        messagebox.showwarning("Cart Empty", "Please add items to the cart.")
        return

    filename = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    c = pdf_canvas.Canvas(filename)


    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    c.setFont("DejaVuSans", 16)

    c.drawString(180, 800, "Grocify Grocery Store")
    c.setFont("DejaVuSans", 12)
    c.drawString(50, 780, f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    c.drawString(50, 765, f"Customer: {customer_name}")
    c.drawString(50, 750, f"Phone: {customer_phone}")
    c.drawString(50, 735, "-"*80)
    c.drawString(50, 715, "Item")
    c.drawString(250, 715, "Qty")
    c.drawString(300, 715, "Rate")
    c.drawString(370, 715, "Total")
    c.drawString(50, 700, "-"*80)

    y = 685
    total = 0
    for item, detail in cart.items():
        line_total = detail['qty'] * detail['price']
        c.drawString(50, y, item)
        c.drawString(250, y, str(detail['qty']))
        c.drawString(300, y, f"₹ {detail['price']:.2f}")
        c.drawString(370, y, f"₹ {line_total:.2f}")
        y -= 20
        total += line_total

    c.setFont("DejaVuSans", 12)
    c.drawString(50, y - 10, "-"*80)
    c.drawString(50, y - 30, f"Total Amount: ₹ {total:.2f}")
    c.drawString(50, y - 50, "Thank you for shopping with us!")
    c.save()

    messagebox.showinfo("Receipt Generated", f"Receipt saved as {filename}")
    cart.clear()
    update_cart_display()
    messagebox.showinfo("Thank You", "Thank you for shopping with Grocify!\nWe hope to see you again!")


def show_main_window():
    global root, cart_list, total_label

    popup.destroy()
    root = tk.Tk()
    root.title("Grocify – Fast. Fresh. Affordable.")
    root.geometry("900x650")
    root.config(bg="#f7f7f7")

    tk.Label(root, text="🛒  Grocify – Fast. Fresh. Affordable.", font=("Arial", 20, "bold"),
             bg="#4CAF50", fg="white", pady=10).pack(fill=tk.X)

    category_frame = tk.Frame(root, bg="white")
    category_frame.place(x=20, y=60, width=370, height=480)

    def show_products(cat_name):
        for widget in category_frame.winfo_children():
            widget.destroy()

        tk.Button(category_frame, text="⬅ Back", font=("Arial", 10),
                  command=load_categories, bg="#ddd").pack(anchor="w", pady=5, padx=5)

        prod_canvas = tk.Canvas(category_frame, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(category_frame, orient="vertical", command=prod_canvas.yview)
        scroll_frame = tk.Frame(prod_canvas, bg="white")
        scroll_frame.bind("<Configure>", lambda e: prod_canvas.configure(scrollregion=prod_canvas.bbox("all")))
        prod_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        prod_canvas.configure(yscrollcommand=scrollbar.set)
        prod_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for name, price in categories[cat_name].items():
            btn = tk.Button(scroll_frame, text=f"{name} - ₹{price:.2f}", font=("Arial", 10),
                            bg="#e0f7fa", anchor="w", relief="ridge", width=35,
                            command=lambda n=name, p=price: prompt_quantity(n, p))
            btn.pack(padx=5, pady=2, anchor="w")

    def load_categories():
        for widget in category_frame.winfo_children():
            widget.destroy()

        tk.Label(category_frame, text="📂 Categories", font=("Arial", 14, "bold"), bg="white", anchor="w").pack(pady=10)

        for cat in categories:
            tk.Button(category_frame, text=cat, font=("Arial", 12),
                      width=30, height=2, bg="#f0f0f0",
                      command=lambda c=cat: show_products(c)).pack(pady=5)

    load_categories()


    cart_frame = tk.LabelFrame(root, text="Your Cart", bg="white", font=("Arial", 12))
    cart_frame.place(x=410, y=60, width=470, height=460)

    columns = ("#", "Item", "Qty", "Rate", "Amount")
    cart_list = ttk.Treeview(cart_frame, columns=columns, show="headings", height=18)
    for col in columns:
        cart_list.heading(col, text=col)
        cart_list.column(col, anchor="center", width=90)
    cart_list.pack(fill=tk.BOTH, expand=True)

    total_label = tk.Label(root, text="Total: ₹ 0.00", font=("Arial", 14, "bold"), bg="white", fg="#333")
    total_label.place(x=730, y=530)

    tk.Button(root, text="🗑 Remove Item", font=("Arial", 12), bg="#f44336", fg="white", command=remove_selected).place(x=420, y=570)
    tk.Button(root, text="🧾 Generate Bill", font=("Arial", 12), bg="#4CAF50", fg="white", command=generate_bill).place(x=600, y=570)

    root.mainloop()


popup = tk.Tk()
popup.title("Enter Customer Info")
popup.geometry("1000x600")
popup.resizable(False, False)

tk.Label(popup, text="Welcome to Grocify!", font=("Arial", 14, "bold"), fg="green").pack(pady=20)

tk.Label(popup, text="Customer Name:").pack()
name_input = tk.Entry(popup, width=30)
name_input.pack(pady=2)

tk.Label(popup, text="Phone Number:").pack()
phone_input = tk.Entry(popup, width=30)
phone_input.pack(pady=2)

def validate_and_start():
    global customer_name, customer_phone
    name = name_input.get().strip()
    phone = phone_input.get().strip()

    if not name:
        messagebox.showerror("Input Error", "Please enter a valid name.")
        return
    if not phone.isdigit() or len(phone) != 10:
        messagebox.showerror("Input Error", "Please enter a valid 10-digit phone number.")
        return

    customer_name = name
    customer_phone = phone
    show_main_window()

tk.Button(popup, text="Continue", font=("Arial", 12), bg="#4CAF50", fg="white", command=validate_and_start).pack(pady=10)
popup.mainloop()