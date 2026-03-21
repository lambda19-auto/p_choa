import asyncio
import pandas as pd
import csv
import re


class CFS:

    JOURNAL_PATH = 'telegram/content/journal.csv'
    CFS_PATH = 'telegram/content/cfs.csv'

    async def load_journal(self):
        try:
            return await asyncio.to_thread(pd.read_csv, self.JOURNAL_PATH)
        except:
            return pd.DataFrame()

    def normalize_category(self, text: str):
        """Удаляет номера категорий в начале строки"""
        return re.sub(r'^\d+(\.\d+)*\.\s*', '', text).strip()

    def format_money(self, value: float):
        """Форматирует число в строку с пробелами и запятыми, добавляет скобки для отрицательных"""
        abs_value = f"{abs(value):,.2f}".replace(',', ' ').replace('.', ',')
        return f"({abs_value})" if value < 0 else abs_value

    async def build(self):
        df = await self.load_journal()
        if df.empty:
            return

        # агрегируем суммы по категориям из журнала
        grouped = df.groupby('category')['sum'].sum().to_dict()  # type: ignore

        # читаем шаблон cfs.csv
        template_lines = []
        with open(self.CFS_PATH, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                template_lines.append(row)

        updated_lines = []

        # для хранения суммы по текущей группе
        group_sums = {}
        current_group_name = None
        temp_sum = 0

        for row in template_lines:
            if len(row) >= 2:
                original_name = row[0].strip()
                clean_name = self.normalize_category(original_name)

                # проверка — строка это группа или подкатегория
                is_group = re.match(r'^\d+\.\s', original_name) and not re.match(r'^\d+\.\d+', original_name)

                if is_group:
                    # если была предыдущая группа, записываем её сумму
                    if current_group_name is not None:
                        updated_lines.append([current_group_name, self.format_money(temp_sum)])
                    current_group_name = original_name
                    temp_sum = 0
                    continue

                # сумма подкатегории из журнала
                value = grouped.get(clean_name, 0)
                temp_sum += value
                updated_lines.append([original_name, self.format_money(value)])
            else:
                updated_lines.append(row)

        # записываем последнюю группу
        if current_group_name is not None:
            updated_lines.append([current_group_name, self.format_money(temp_sum)])

        # записываем результат в файл
        with open(self.CFS_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(updated_lines)