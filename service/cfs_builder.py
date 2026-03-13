'''
script for build CFS (Cash Flow Statement) 
'''
import asyncio
import pandas as pd
import csv


# create class CFS 
class CFS:

    JOURNAL_PATH = 'telegram/content/journal.csv'
    CFS_PATH = 'telegram/content/cfs.csv'  

    async def load_journal(self):
        try:
            return await asyncio.to_thread(pd.read_csv, self.JOURNAL_PATH)
        except:
            return pd.DataFrame()

    async def build(self):
        # load journal
        df = await self.load_journal()
        if df.empty:
            return

        # group by category
        grouped = df.groupby('category')['sum'].sum().to_dict()

        # load CFS (cfs.csv)
        template_lines = []
        with open(self.CFS_PATH, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                template_lines.append(row)

        # update sum
        updated_lines = []
        for row in template_lines:
            if len(row) >= 2:
                category_name = row[0].strip()
                if category_name in grouped:
                    value = grouped[category_name]
                    # add minus if it need
                    if value < 0:
                        value_str = f'({abs(value):,.0f})'
                    else:
                        value_str = f'{value:,.0f}'
                    updated_lines.append([category_name, value_str])
                else:
                    updated_lines.append(row)
            else:
                updated_lines.append(row)

        # save cfs.csv
        with open(self.CFS_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(updated_lines)