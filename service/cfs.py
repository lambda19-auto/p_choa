'''
script for build CFS (Cash Flow Statement)
'''

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
        """
        delete number
        """
        return re.sub(r'^\d+(\.\d+)*\.\s*', '', text).strip()

    def format_money(self, value: float):
        """
        add format
        """
        abs_value = f"{abs(value):,.2f}".replace(',', ' ').replace('.', ',')

        if value < 0:
            return f"({abs_value})"

        return abs_value

    async def build(self):

        df = await self.load_journal()

        if df.empty:
            return

        # group by category
        grouped = df.groupby('category')['sum'].sum().to_dict() #type: ignore

        template_lines = []

        # read cfs.csv
        with open(self.CFS_PATH, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)

            for row in reader:
                template_lines.append(row)

        updated_lines = []

        for row in template_lines:

            if len(row) >= 2:

                original_name = row[0].strip()
                clean_name = self.normalize_category(original_name)

                if clean_name in grouped:

                    value = grouped[clean_name]

                    value_str = self.format_money(value)

                    updated_lines.append([original_name, value_str])

                else:

                    updated_lines.append([original_name, "0,00"])

            else:
                updated_lines.append(row)

        # rewrite file
        with open(self.CFS_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(updated_lines)