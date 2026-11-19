import tkinter as tk
from tkinter import ttk, messagebox


class CoffeeShopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MyКофейня — Учёт заказов")
        self.root.geometry("850x550")

        self.menu_prices = {
            "Эспрессо": 150,
            "Американо": 180,
            "Капучино": 220,
            "Латте": 240,
            "Раф": 270,
            "Матча Латте": 260,
            "Какао": 200
        }

        self.orders = []
        self.next_id = 1

        self.setup_ui()

    def setup_ui(self):
        form_frame = ttk.LabelFrame(self.root, text="Данные заказа", padding=10)
        form_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(form_frame, text="Номер заказа:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.id_var = tk.StringVar(value="Авто")
        self.id_entry = ttk.Entry(form_frame, textvariable=self.id_var, state="readonly", width=10)
        self.id_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form_frame, text="Напиток:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.drink_var = tk.StringVar(value="Капучино")
        self.drink_combo = ttk.Combobox(
            form_frame, textvariable=self.drink_var, values=list(self.menu_prices.keys()), state="readonly", width=18
        )
        self.drink_combo.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        self.drink_combo.bind("<<ComboboxSelected>>", self.calculate_total)

        ttk.Label(form_frame, text="Количество:").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.qty_var = tk.StringVar(value="1")
        self.qty_entry = ttk.Entry(form_frame, textvariable=self.qty_var, width=8)
        self.qty_entry.grid(row=0, column=5, sticky="w", padx=5, pady=5)
        self.qty_entry.bind("<KeyRelease>", self.calculate_total)

        ttk.Label(form_frame, text="Итого (₽):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.total_var = tk.StringVar(value="220")
        self.total_entry = ttk.Entry(form_frame, textvariable=self.total_var, state="readonly", width=10)
        self.total_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form_frame, text="Комментарий / добавки:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.comment_var = tk.StringVar()
        self.comment_entry = ttk.Entry(form_frame, textvariable=self.comment_var, width=25)
        self.comment_entry.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        ttk.Label(form_frame, text="Статус:").grid(row=1, column=4, sticky="w", padx=5, pady=5)
        self.status_var = tk.StringVar(value="Готовится")
        self.status_combo = ttk.Combobox(
            form_frame, textvariable=self.status_var, values=["Готовится", "Выдан"], state="readonly", width=12
        )
        self.status_combo.grid(row=1, column=5, sticky="w", padx=5, pady=5)

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=6, pady=10, sticky="w")

        ttk.Button(btn_frame, text="Создать заказ", command=self.add_order).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Сохранить изменения", command=self.update_order).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Отметить «Выдан»", command=self.mark_issued).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Удалить заказ", command=self.delete_order).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Очистить форму", command=self.clear_form).pack(side="left", padx=5)

        filter_frame = ttk.LabelFrame(self.root, text="Поиск и фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Поиск по номеру:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.search_var, width=15).pack(side="left", padx=5)
        ttk.Button(filter_frame, text="Найти", command=self.refresh_table).pack(side="left", padx=5)

        ttk.Label(filter_frame, text="Фильтр по статусу:").pack(side="left", padx=15)
        self.filter_status_var = tk.StringVar(value="Все")
        filter_combo = ttk.Combobox(
            filter_frame, textvariable=self.filter_status_var, values=["Все", "Готовится", "Выдан"], state="readonly", width=15
        )
        filter_combo.pack(side="left", padx=5)
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        ttk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters).pack(side="left", padx=10)

        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "drink", "qty", "total", "comment", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("id", text="№")
        self.tree.heading("drink", text="Напиток")
        self.tree.heading("qty", text="Кол-во")
        self.tree.heading("total", text="Сумма (₽)")
        self.tree.heading("comment", text="Состав / Комментарий")
        self.tree.heading("status", text="Статус")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("drink", width=140)
        self.tree.column("qty", width=70, anchor="center")
        self.tree.column("total", width=90, anchor="center")
        self.tree.column("comment", width=260)
        self.tree.column("status", width=110, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_select_order)

    def calculate_total(self, event=None):
        drink = self.drink_var.get()
        price = self.menu_prices.get(drink, 0)
        try:
            qty = int(self.qty_var.get())
            if qty < 1:
                raise ValueError
            self.total_var.set(str(price * qty))
        except ValueError:
            self.total_var.set("Ошибка")

    def validate_input(self):
        drink = self.drink_var.get().strip()
        if not drink or drink not in self.menu_prices:
            messagebox.showerror("Ошибка ввода", "Выберите напиток из списка.")
            return None
        try:
            qty = int(self.qty_var.get().strip())
            if qty <= 0 or qty > 100:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Количество должно быть целым числом от 1 до 100.")
            return None
        total = self.menu_prices[drink] * qty
        comment = self.comment_var.get().strip()
        status = self.status_var.get()
        return drink, qty, total, comment, status

    def add_order(self):
        data = self.validate_input()
        if not data:
            return
        drink, qty, total, comment, _ = data
        order = {
            "id": self.next_id,
            "drink": drink,
            "qty": qty,
            "total": total,
            "comment": comment,
            "status": "Готовится"
        }
        self.orders.append(order)
        self.next_id += 1
        self.clear_form()
        self.refresh_table()

    def on_select_order(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item_values = self.tree.item(selected[0], "values")
        order_id = int(item_values[0])
        for order in self.orders:
            if order["id"] == order_id:
                self.id_var.set(str(order["id"]))
                self.drink_var.set(order["drink"])
                self.qty_var.set(str(order["qty"]))
                self.total_var.set(str(order["total"]))
                self.comment_var.set(order["comment"])
                self.status_var.set(order["status"])
                break

    def update_order(self):
        if self.id_var.get() == "Авто":
            messagebox.showwarning("Внимание", "Сначала выберите заказ из списка для изменения.")
            return
        data = self.validate_input()
        if not data:
            return
        order_id = int(self.id_var.get())
        drink, qty, total, comment, new_status = data
        for order in self.orders:
            if order["id"] == order_id:
                if order["status"] == "Выдан" and new_status == "Готовится":
                    messagebox.showerror("Ошибка статуса", "Нельзя вернуть выданный заказ обратно в работу.")
                    return
                order["drink"] = drink
                order["qty"] = qty
                order["total"] = total
                order["comment"] = comment
                order["status"] = new_status
                break
        self.refresh_table()
        messagebox.showinfo("Успех", f"Заказ №{order_id} обновлён.")

    def mark_issued(self):
        if self.id_var.get() == "Авто":
            messagebox.showwarning("Внимание", "Выберите заказ из списка.")
            return
        order_id = int(self.id_var.get())
        for order in self.orders:
            if order["id"] == order_id:
                if order["status"] == "Выдан":
                    messagebox.showinfo("Информация", "Заказ уже имеет статус «Выдан».")
                    return
                order["status"] = "Выдан"
                self.status_var.set("Выдан")
                break
        self.refresh_table()

    def delete_order(self):
        if self.id_var.get() == "Авто":
            messagebox.showwarning("Внимание", "Выберите заказ из списка для удаления.")
            return
        order_id = int(self.id_var.get())
        confirm = messagebox.askyesno("Подтверждение удаления", f"Вы уверены, что хотите удалить заказ №{order_id}?")
        if confirm:
            self.orders = [o for o in self.orders if o["id"] != order_id]
            self.clear_form()
            self.refresh_table()

    def clear_form(self):
        self.id_var.set("Авто")
        self.drink_var.set("Капучино")
        self.qty_var.set("1")
        self.total_var.set("220")
        self.comment_var.set("")
        self.status_var.set("Готовится")
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def reset_filters(self):
        self.search_var.set("")
        self.filter_status_var.set("Все")
        self.refresh_table()

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        search_query = self.search_var.get().strip()
        status_filter = self.filter_status_var.get()

        for order in self.orders:
            if search_query and str(order["id"]) != search_query:
                continue
            if status_filter != "Все" and order["status"] != status_filter:
                continue
            self.tree.insert("", "end", values=(
                order["id"], order["drink"], order["qty"], order["total"], order["comment"], order["status"]
            ))


if __name__ == "__main__":
    root = tk.Tk()
    app = CoffeeShopApp(root)
    root.mainloop()
