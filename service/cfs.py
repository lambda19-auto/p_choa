import asyncio
import csv
from pathlib import Path
import re

import pandas as pd
from pandas import DataFrame

try:
    from .google_sheets import GoogleSheetsStorage
except ImportError:
    from google_sheets import GoogleSheetsStorage


class CFS:

    BASE_DIR = Path(__file__).resolve().parent
    JOURNAL_PATH = BASE_DIR / 'telegram' / 'content' / 'journal.csv'
    CFS_PATH = BASE_DIR / 'telegram' / 'content' / 'cfs.csv'

    REPORT_STRUCTURE = [
        (
            '1. Денежные потоки от операционной деятельности',
            [
                ('1.1. Продажи через торговые точки', 'Продажи через торговые точки', 1),
                ('1.2. Продажи через вендинговые автоматы', 'Продажи через вендинговые автоматы', 1),
                ('1.3. Возвраты от поставщиков', 'Возвраты от поставщиков', 1),
                ('1.4. Закупка товара', 'Закупка товара', -1),
                ('1.5. Транспортные услуги', 'Транспортные услуги', -1),
                ('1.6. Комиссии за эквайринг', 'Комиссии за эквайринг', -1),
                ('1.7. Расчётно-кассовое обслуживание (РКО)', 'Расчётно-кассовое обслуживание (РКО)', -1),
                ('1.8. Налоги (ЕНВД, УСН 6%, транспортный налог)', 'Налоги (ЕНВД, УСН 6%, транспортный налог)', -1),
                ('1.9. Зарплаты и налоги(НДФЛ, ПФР) производственного персонала', 'Зарплаты и налоги(НДФЛ, ПФР) производственного персонала', -1),
                ('1.10. Зарплаты и налоги(НДФЛ, ПФР) коммерческого персонала', 'Зарплаты и налоги(НДФЛ, ПФР) коммерческого персонала', -1),
                ('1.11. Зарплаты и налоги(НДФЛ, ПФР) административного персонала', 'Зарплаты и налоги(НДФЛ, ПФР) административного персонала', -1),
                ('1.12. Обучение персонала', 'Обучение персонала', -1),
                ('1.13. Расходы на персонал', 'Расходы на персонал', -1),
                ('1.14. Командировочные расходы', 'Командировочные расходы', -1),
                ('1.15. Представительские расходы', 'Представительские расходы', -1),
                ('1.16. Поиск и найм персонала', 'Поиск и найм персонала', -1),
                ('1.17. Реклама и маркетинг', 'Реклама и маркетинг', -1),
                ('1.18. Содержание торговых точек и офиса', 'Содержание торговых точек и офиса', -1),
                ('1.19. Аренда офиса и магазинов', 'Аренда офиса и магазинов', -1),
                ('1.20. Покупка наличности', 'Покупка наличности', -1),
                ('1.21. Прочие операционные расходы', 'Прочие операционные расходы', -1),
            ],
            'Итого денежный поток от операционной деятельности',
        ),
        (
            '2. Денежные потоки от инвестиционной деятельности',
            [
                ('2.1. Покупка основных средств (ОС)', 'Покупка основных средств (ОС)', -1),
                ('2.2. Ремонт основных средств', 'Ремонт основных средств', -1),
                ('2.3. Продажа основных средств', 'Продажа основных средств', 1),
                ('2.4. Выдача кредитов и займов', 'Выдача кредитов и займов', -1),
                ('2.5. Возврат кредитов и займов', 'Возврат кредитов и займов', 1),
            ],
            'Итого денежный поток от инвестиционной деятельности',
        ),
        (
            '3. Денежные потоки от финансовой деятельности',
            [
                ('3.1. Получение кредитов и займов', 'Получение кредитов и займов', 1),
                ('3.2. Оплаты по кредитам, займам и овердрафту', 'Оплаты по кредитам, займам и овердрафту', -1),
                ('3.3. Вклады от собственников', 'Вклады от собственников', 1),
                ('3.4. Дивиденды', 'Дивиденды', -1),
                ('3.5. Прочие поступления от финансовых операций', 'Прочие поступления от финансовых операций', 1),
            ],
            'Итого денежный поток от финансовой деятельности',
        ),
        (
            '4. Технические операции',
            [
                ('4.1. Доход — перевод между счетами', 'Перевод между счетами компании', 1),
                ('4.2. Расход — перевод между счетами', 'Перевод между счетами компании', -1),
            ],
            'Итого по техническим операциям',
        ),
    ]

    CATEGORY_ALIASES = {
        'Расчётно-кассовое обслуживание (РКО)': [
            'Расчётно-кассовое обслуживание (РКО)',
            'Расчетно-кассовое обслуживание (РКО)',
            'Комиссии за эквайринг',
        ],
        'Налоги (ЕНВД, УСН 6%, транспортный налог)': [
            'Налоги (ЕНВД, УСН 6%, транспортный налог)',
            'Налоги (ЕНВД, УСН 6%)',
        ],
        'Зарплаты и налоги(НДФЛ, ПФР) производственного персонала': [
            'Зарплаты и налоги(НДФЛ, ПФР) производственного персонала',
            'Зарплаты и налоги(ФОТ) производственного персонала',
        ],
        'Зарплаты и налоги(НДФЛ, ПФР) коммерческого персонала': [
            'Зарплаты и налоги(НДФЛ, ПФР) коммерческого персонала',
            'Зарплаты и налоги(ФОТ) коммерческого персонала',
        ],
        'Зарплаты и налоги(НДФЛ, ПФР) административного персонала': [
            'Зарплаты и налоги(НДФЛ, ПФР) административного персонала',
            'Зарплаты и налоги(ФОТ) административного персонала',
        ],
        'Аренда офиса и магазинов': [
            'Аренда офиса и магазинов',
            'Аренда',
        ],
        'Прочие операционные расходы': [
            'Прочие операционные расходы',
            'Прочие операционные расходы',
        ],
        'Перевод между счетами компании': [
            'Перевод между счетами компании',
            'Доход — Перевод между счетами',
            'Расход — Перевод между счетами',
        ],
    }

    async def load_journal(self, prefer_local: bool = False):
        expected_columns = ['note', 'date', 'sum', 'account', 'counterparty', 'category']

        if not prefer_local:
            # first preference: Google Sheets journal if configured
            try:
                sheets = GoogleSheetsStorage()
                if sheets.is_configured:
                    rows = await asyncio.to_thread(sheets.load_journal_rows)
                    if rows:
                        first_row = [str(cell).strip() for cell in rows[0]]
                        has_header = set(expected_columns).issubset(set(first_row))
                        body = rows[1:] if has_header else rows

                        if has_header:
                            header = [str(cell).strip() for cell in rows[0]]
                            normalized_rows = []
                            for item in body:
                                normalized_rows.append((item + [''] * len(header))[:len(header)])

                            frame = DataFrame(normalized_rows, columns=header)
                            frame = frame.reindex(columns=expected_columns, fill_value='')
                        else:
                            normalized_rows = []
                            for item in body:
                                normalized_rows.append((item + [''] * len(expected_columns))[:len(expected_columns)])

                            frame = DataFrame(normalized_rows, columns=expected_columns)
                        return frame
            except Exception:
                pass

        try:
            return await asyncio.to_thread(pd.read_csv, self.JOURNAL_PATH)
        except Exception:
            return pd.DataFrame(columns=['note', 'date', 'sum', 'account', 'counterparty', 'category'])

    def normalize_category(self, text: str):
        text = re.sub(r'^\d+(\.\d+)*\.\s*', '', text).strip()
        text = text.replace('ё', 'е').replace('Ё', 'Е')
        text = re.sub(r'\s+', ' ', text)
        return text.casefold()

    def format_money(self, value: float):
        abs_value = f"{abs(value):,.2f}".replace(',', ' ').replace('.', ',')
        return f"({abs_value})" if value < 0 else abs_value

    def parse_money(self, value: str):
        clean = value.strip()
        if not clean:
            return 0.0

        negative = clean.startswith('(') and clean.endswith(')')
        clean = clean.strip('()').replace(' ', '').replace(',', '.')

        try:
            amount = float(clean)
        except ValueError:
            return 0.0

        return -amount if negative else amount

    def build_grouped_amounts(self, df: pd.DataFrame):
        grouped: dict[str, float] = {}

        if df.empty:
            return grouped

        for _, row in df.iterrows():
            category = self.normalize_category(str(row.get('category', '')))
            try:
                amount = float(row.get('sum', 0) or 0)
            except (TypeError, ValueError):
                amount = 0.0

            grouped[category] = grouped.get(category, 0.0) + amount

        return grouped

    def get_category_amount(self, grouped: dict[str, float], category_name: str):
        aliases = self.CATEGORY_ALIASES.get(category_name, [category_name])
        total = 0.0
        for alias in aliases:
            total += grouped.get(self.normalize_category(alias), 0.0)
        return total

    def load_opening_balance(self):
        if not self.CFS_PATH.exists():
            return 0.0

        with self.CFS_PATH.open(newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get('Статья') == 'Остаток на начало периода':
                    return self.parse_money(row.get('Сумма', '0'))

        return 0.0

    async def build(self, prefer_local: bool = False, sync_google: bool = True):
        df = await self.load_journal(prefer_local=prefer_local)
        grouped = self.build_grouped_amounts(df)
        opening_balance = self.load_opening_balance()

        rows = [['Статья', 'Сумма'], ['Остаток на начало периода', self.format_money(opening_balance)], ['', '']]

        net_change = 0.0

        for section_name, items, total_label in self.REPORT_STRUCTURE:
            rows.append([section_name, ''])
            section_total = 0.0

            for display_name, category_name, sign in items:
                amount = self.get_category_amount(grouped, category_name) * sign
                section_total += amount
                rows.append([display_name, self.format_money(amount)])

            rows.append([total_label, self.format_money(section_total)])
            rows.append(['', ''])
            net_change += section_total

        closing_balance = opening_balance + net_change
        rows.append(['Изменение денежных средств за период', self.format_money(net_change)])
        rows.append(['Остаток на конец периода', self.format_money(closing_balance)])

        with self.CFS_PATH.open('w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

        # best-effort sync CFS report to Google Sheets
        if sync_google:
            try:
                sheets = GoogleSheetsStorage()
                if sheets.is_configured:
                    await asyncio.to_thread(sheets.replace_cfs_rows, rows)
            except Exception:
                pass

        return rows
