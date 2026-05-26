#!/usr/bin/env python3
"""
Калькулятор с графическим интерфейсом
Создан с использованием tkinter
"""

import tkinter as tk
from tkinter import ttk
import math


class Calculator:
    """Основной класс калькулятора"""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Калькулятор")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        # Переменные состояния
        self.current_input: str = "0"
        self.previous_value: float | None = None
        self.operator: str | None = None
        self.waiting_for_new_number: bool = False
        self.last_result: float | None = None
        self.last_operator: str | None = None
        self.last_operand: float | None = None
        self.error_after_id: str | None = None

        self._setup_styles()
        self._create_widgets()
        self._bind_keyboard()

        # Центрируем окно
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_reqwidth() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_reqheight() // 2)
        self.root.geometry(f"+{x}+{y}")

    def _setup_styles(self) -> None:
        """Настройка стилей"""
        style = ttk.Style()
        style.theme_use("clam")

        # Цветовая схема (Catppuccin Mocha)
        self.colors = {
            "bg": "#1e1e2e",
            "display_bg": "#181825",
            "button_num": "#313244",
            "button_num_hover": "#45475a",
            "button_op": "#f38ba8",
            "button_op_hover": "#f5a0b8",
            "button_eq": "#89b4fa",
            "button_eq_hover": "#a6c8ff",
            "button_func": "#585b70",
            "button_func_hover": "#6c7086",
            "button_clear": "#f38ba8",
            "button_clear_hover": "#f5a0b8",
            "text_primary": "#cdd6f4",
            "text_secondary": "#a6adc8",
            "text_display": "#cdd6f4",
        }

    def _create_widgets(self) -> None:
        """Создание виджетов интерфейса"""
        # Фрейм для дисплея
        display_frame = tk.Frame(
            self.root,
            bg=self.colors["display_bg"],
            highlightbackground="#313244",
            highlightthickness=1,
        )
        display_frame.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=(10, 5))

        # Метка для истории/предыдущего значения
        self.history_label = tk.Label(
            display_frame,
            text="",
            font=("Segoe UI", 12),
            bg=self.colors["display_bg"],
            fg=self.colors["text_secondary"],
            anchor="e",
            height=1,
        )
        self.history_label.pack(fill="x", padx=12, pady=(8, 0))

        # Основной дисплей
        self.display_var = tk.StringVar(value="0")
        self.display_label = tk.Label(
            display_frame,
            textvariable=self.display_var,
            font=("Segoe UI", 36, "bold"),
            bg=self.colors["display_bg"],
            fg=self.colors["text_display"],
            anchor="e",
            height=1,
        )
        self.display_label.pack(fill="x", padx=12, pady=(0, 8))

        # Фрейм для кнопок
        buttons_frame = tk.Frame(self.root, bg=self.colors["bg"])
        buttons_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=(5, 10))

        # Определяем кнопки
        buttons = [
            # (текст, row, col, colspan, тип)
            ("C", 0, 0, 1, "clear"),
            ("±", 0, 1, 1, "func"),
            ("%", 0, 2, 1, "func"),
            ("÷", 0, 3, 1, "operator"),
            ("7", 1, 0, 1, "number"),
            ("8", 1, 1, 1, "number"),
            ("9", 1, 2, 1, "number"),
            ("×", 1, 3, 1, "operator"),
            ("4", 2, 0, 1, "number"),
            ("5", 2, 1, 1, "number"),
            ("6", 2, 2, 1, "number"),
            ("−", 2, 3, 1, "operator"),
            ("1", 3, 0, 1, "number"),
            ("2", 3, 1, 1, "number"),
            ("3", 3, 2, 1, "number"),
            ("+", 3, 3, 1, "operator"),
            ("0", 4, 0, 2, "number"),
            (",", 4, 2, 1, "func"),
            ("=", 4, 3, 1, "equal"),
        ]

        self.button_widgets: dict[str, tk.Button] = {}

        for text, row, col, colspan, btn_type in buttons:
            btn = self._create_button(buttons_frame, text, btn_type)
            btn.grid(
                row=row,
                column=col,
                columnspan=colspan,
                sticky="nsew",
                padx=3,
                pady=3,
                ipadx=0,
                ipady=0,
            )
            self.button_widgets[text] = btn

        # Настройка веса колонок и строк для равномерного распределения
        for i in range(4):
            buttons_frame.columnconfigure(i, weight=1)
        for i in range(5):
            buttons_frame.rowconfigure(i, weight=1)

    def _create_button(self, parent: tk.Frame, text: str, btn_type: str) -> tk.Button:
        """Создание кнопки с нужным стилем"""
        if btn_type == "number":
            bg = self.colors["button_num"]
            hover_bg = self.colors["button_num_hover"]
            fg = self.colors["text_primary"]
            width = 5
        elif btn_type == "operator":
            bg = self.colors["button_op"]
            hover_bg = self.colors["button_op_hover"]
            fg = "#1e1e2e"
            width = 5
        elif btn_type == "equal":
            bg = self.colors["button_eq"]
            hover_bg = self.colors["button_eq_hover"]
            fg = "#1e1e2e"
            width = 5
        elif btn_type == "clear":
            bg = self.colors["button_clear"]
            hover_bg = self.colors["button_clear_hover"]
            fg = "#1e1e2e"
            width = 5
        else:  # func
            bg = self.colors["button_func"]
            hover_bg = self.colors["button_func_hover"]
            fg = self.colors["text_primary"]
            width = 5

        btn = tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 16, "bold"),
            bg=bg,
            fg=fg,
            width=width,
            height=1,
            bd=0,
            activebackground=hover_bg,
            activeforeground=fg,
            cursor="hand2",
            relief="flat",
        )

        # Привязываем обработчики
        if text == "C":
            btn.config(command=self._clear)
        elif text == "=":
            btn.config(command=self._calculate_result)
        elif text == "±":
            btn.config(command=self._negate)
        elif text == "%":
            btn.config(command=self._percent)
        elif text == ",":
            btn.config(command=self._add_decimal)
        elif text in ("+", "−", "×", "÷"):
            btn.config(command=lambda op=text: self._set_operator(op))
        else:
            btn.config(command=lambda num=text: self._add_digit(num))

        # Эффекты наведения
        btn.bind("<Enter>", lambda e, b=btn, h=hover_bg: b.config(bg=h))
        btn.bind("<Leave>", lambda e, b=btn, bg=bg: b.config(bg=bg))

        return btn

    def _bind_keyboard(self) -> None:
        """Привязка клавиатуры"""
        key_map = {
            "0": "0", "1": "1", "2": "2", "3": "3", "4": "4",
            "5": "5", "6": "6", "7": "7", "8": "8", "9": "9",
            "period": ",",
            "comma": ",",
            "plus": "+", "minus": "−",
            "asterisk": "×", "slash": "÷",
            "Return": "=", "KP_Enter": "=",
            "BackSpace": "backspace",
            "Escape": "C",
            "percent": "%",
        }

        for key, action in key_map.items():
            self.root.bind(f"<Key-{key}>", lambda e, a=action: self._handle_key(a))

    def _handle_key(self, action: str) -> None:
        """Обработка нажатия клавиш"""
        if action in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
            self._add_digit(action)
        elif action == ",":
            self._add_decimal()
        elif action in ("+", "−", "×", "÷"):
            self._set_operator(action)
        elif action == "=":
            self._calculate_result()
        elif action == "C":
            self._clear()
        elif action == "backspace":
            self._backspace()
        elif action == "%":
            self._percent()

    def _add_digit(self, digit: str) -> None:
        """Добавление цифры"""
        if self.waiting_for_new_number or self.current_input == "0":
            self.current_input = digit
            self.waiting_for_new_number = False
        else:
            self.current_input += digit

        self._cancel_error_clear()
        self._update_display()

    def _add_decimal(self) -> None:
        """Добавление десятичной точки"""
        if self.waiting_for_new_number:
            self.current_input = "0,"
            self.waiting_for_new_number = False
        elif "," not in self.current_input:
            self.current_input += ","

        self._cancel_error_clear()
        self._update_display()

    def _set_operator(self, op: str) -> None:
        """Установка оператора"""
        if self.operator is not None and not self.waiting_for_new_number:
            self._calculate_result()

        try:
            self.previous_value = self._parse_number(self.current_input)
        except ValueError:
            self._show_error("Ошибка")
            return

        self.operator = op
        self.waiting_for_new_number = True
        self._update_history()

    def _calculate_result(self) -> None:
        """Вычисление результата"""
        # Если оператор не задан, но есть последняя операция — повторяем её
        if self.operator is None:
            if (self.last_operator is not None
                    and self.last_result is not None
                    and self.last_operand is not None):
                self.previous_value = self.last_result
                self.operator = self.last_operator
                self.current_input = self._format_result(self.last_operand)
                self.waiting_for_new_number = False
            else:
                return

        try:
            current_value = self._parse_number(self.current_input)
            if self.previous_value is None:
                return

            op_map = {
                "+": lambda a, b: a + b,
                "−": lambda a, b: a - b,
                "×": lambda a, b: a * b,
                "÷": lambda a, b: a / b if b != 0 else float("inf"),
            }

            operation = op_map.get(self.operator)
            if operation is None:
                return

            result = operation(self.previous_value, current_value)

            if math.isinf(result):
                self._show_error("На ноль делить нельзя")
                return

            if math.isnan(result):
                self._show_error("Ошибка")
                return

            self.last_operator = self.operator
            self.last_result = result
            self.last_operand = current_value

            # Форматирование результата
            self.current_input = self._format_result(result)

            self._update_display()
            self._update_history()

            # Сброс для следующего ввода
            self.previous_value = result
            self.operator = None
            self.waiting_for_new_number = True

        except (ValueError, ZeroDivisionError):
            self._show_error("Ошибка")

    def _negate(self) -> None:
        """Смена знака числа"""
        if self.current_input == "0":
            return

        if self.current_input.startswith("−"):
            self.current_input = self.current_input[1:]
        else:
            self.current_input = "−" + self.current_input

        self._update_display()

    def _percent(self) -> None:
        """Вычисление процента"""
        try:
            value = self._parse_number(self.current_input)
            if self.previous_value is not None:
                result = self.previous_value * (value / 100)
            else:
                result = value / 100

            self.current_input = self._format_result(result)

            self._update_display()
            self.waiting_for_new_number = True

        except ValueError:
            self._show_error("Ошибка")

    def _clear(self) -> None:
        """Очистка всего"""
        self.current_input = "0"
        self.previous_value = None
        self.operator = None
        self.waiting_for_new_number = False
        self.last_result = None
        self.last_operator = None
        self.last_operand = None
        self._cancel_error_clear()
        self._update_display()
        self._update_history()

    def _parse_number(self, text: str) -> float:
        """Преобразование строки в число"""
        normalized = text.replace("−", "-").replace(",", ".")
        return float(normalized)

    def _format_result(self, value: float) -> str:
        """Форматирование числа-результата в строку"""
        if value == int(value) and abs(value) < 1e15:
            return str(int(value))
        else:
            return f"{value:.10f}".rstrip("0").rstrip(".")

    def _format_number(self, text: str) -> str:
        """Форматирование числа с запятой"""
        if text.startswith("−"):
            sign = "−"
            num = text[1:]
        else:
            sign = ""
            num = text

        # Замена точки на запятую для отображения
        num = num.replace(".", ",")
        return sign + num

    def _update_display(self) -> None:
        """Обновление дисплея"""
        formatted = self._format_number(self.current_input)
        self.display_var.set(formatted)

    def _update_history(self) -> None:
        """Обновление строки истории"""
        if self.previous_value is not None and self.operator is not None:
            prev = self._format_number(str(self.previous_value).replace(".", ","))
            op_symbols = {"+": "+", "−": "−", "×": "×", "÷": "÷"}
            op = op_symbols.get(self.operator, self.operator)
            self.history_label.config(text=f"{prev} {op}")
        else:
            self.history_label.config(text="")

    def _backspace(self) -> None:
        """Удаление последнего символа"""
        if self.waiting_for_new_number or self.current_input in ("0", "−0"):
            return
        if len(self.current_input) == 1 or (len(self.current_input) == 2 and self.current_input.startswith("−")):
            self.current_input = "0"
        else:
            self.current_input = self.current_input[:-1]
        self._cancel_error_clear()
        self._update_display()

    def _cancel_error_clear(self) -> None:
        """Отмена запланированной очистки после ошибки"""
        if self.error_after_id is not None:
            self.root.after_cancel(self.error_after_id)
            self.error_after_id = None

    def _show_error(self, message: str) -> None:
        """Показать ошибку на дисплее"""
        self._cancel_error_clear()
        self.display_var.set(message)
        self.error_after_id = self.root.after(1000, self._clear)


def main() -> None:
    """Точка входа"""
    root = tk.Tk()
    app = Calculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
