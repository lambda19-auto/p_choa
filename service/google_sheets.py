from __future__ import annotations

from os import getenv
from pathlib import Path
import re
from typing import Any

from dotenv import find_dotenv, load_dotenv

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
except ImportError:  # pragma: no cover
    Credentials = None  # type: ignore[assignment]
    build = None  # type: ignore[assignment]

try:
    from .logging_setup import get_logger
except ImportError:
    from logging_setup import get_logger


logger = get_logger(__name__)


class GoogleSheetsStorage:
    JOURNAL_HEADER = ['note', 'date', 'sum', 'account', 'counterparty', 'category']

    def __init__(self):
        load_dotenv(find_dotenv())
        self.credentials_path = getenv('GOOGLE_CREDENTIALS_JSON', 'google_credentials.json')
        self.journal_url = getenv('GOOGLE_JOURNAL_SHEET_URL', '')
        self.cfs_url = getenv('GOOGLE_CFS_SHEET_URL', '')
        self._service = None

    @property
    def is_configured(self):
        return bool(self.journal_url and self.cfs_url and Path(self.credentials_path).exists())

    def _extract_sheet_id(self, url_or_id: str):
        if '/spreadsheets/d/' in url_or_id:
            match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url_or_id)
            if match:
                return match.group(1)
        return url_or_id

    def _extract_gid(self, url: str):
        match = re.search(r'[#&]gid=(\d+)', url)
        if not match:
            return None
        return int(match.group(1))

    def _sheet_name_by_gid(self, spreadsheet_id: str, gid: int):
        metadata = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        for sheet in metadata.get('sheets', []):
            props = sheet.get('properties', {})
            if props.get('sheetId') == gid:
                return props.get('title')
        return None

    @staticmethod
    def _normalize_sheet_title(title: str):
        return re.sub(r'\s+', '', title).lower()

    def _sheet_name_by_meaning(self, spreadsheet_id: str, purpose: str | None):
        metadata = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = metadata.get('sheets', [])
        if not sheets:
            return None

        titles = [sheet.get('properties', {}).get('title', '') for sheet in sheets]
        normalized_to_title = {self._normalize_sheet_title(title): title for title in titles if title}

        purpose_keywords = {
            'journal': ('журнал', 'journal', 'операц'),
            'cfs': ('оддс', 'cfs', 'cashflow', 'cash flow', 'движениеденежныхсредств'),
        }
        keywords = purpose_keywords.get((purpose or '').lower(), ())

        if keywords:
            for title in titles:
                normalized_title = self._normalize_sheet_title(title)
                if any(self._normalize_sheet_title(keyword) in normalized_title for keyword in keywords):
                    return title

        default_candidates_by_purpose = {
            'journal': ('journal', 'журнал', 'Лист1', 'Sheet1'),
            'cfs': ('cfs', 'оддс', 'Лист1', 'Sheet1'),
        }
        default_candidates = default_candidates_by_purpose.get(
            (purpose or '').lower(),
            ('Лист1', 'Sheet1'),
        )
        for candidate in default_candidates:
            found = normalized_to_title.get(self._normalize_sheet_title(candidate))
            if found:
                return found

        return titles[0] or None

    @staticmethod
    def _a1_range(sheet_name: str, cells: str):
        escaped_name = sheet_name.replace("'", "''")
        return f"'{escaped_name}'!{cells}"

    @property
    def service(self):
        if self._service is not None:
            return self._service
        if not self.is_configured:
            raise RuntimeError('Google Sheets is not configured')
        if Credentials is None or build is None:
            raise RuntimeError('google-api-python-client is not installed')

        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file(self.credentials_path, scopes=scopes)
        self._service = build('sheets', 'v4', credentials=creds)
        return self._service

    def _resolve_target(self, url_or_id: str, purpose: str | None = None):
        spreadsheet_id = self._extract_sheet_id(url_or_id)
        gid = self._extract_gid(url_or_id)
        if gid is None:
            sheet_name = self._sheet_name_by_meaning(spreadsheet_id, purpose)
            if not sheet_name:
                raise RuntimeError(f'Не найден ни один лист в таблице {spreadsheet_id}')
            return spreadsheet_id, sheet_name

        sheet_name = self._sheet_name_by_gid(spreadsheet_id, gid)
        if not sheet_name:
            raise RuntimeError(f'Не найден лист c gid={gid} в таблице {spreadsheet_id}')
        return spreadsheet_id, sheet_name

    def append_journal_row(self, row: list[Any]):
        spreadsheet_id, sheet_name = self._resolve_target(self.journal_url, purpose='journal')
        existing_rows = self.load_journal_rows()
        if not existing_rows:
            self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=self._a1_range(sheet_name, 'A:F'),
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body={'values': [self.JOURNAL_HEADER]},
            ).execute()

        body = {'values': [row]}
        self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=self._a1_range(sheet_name, 'A:F'),
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body,
        ).execute()

    def load_journal_rows(self):
        spreadsheet_id, sheet_name = self._resolve_target(self.journal_url, purpose='journal')
        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=self._a1_range(sheet_name, 'A:F'),
        ).execute()
        return result.get('values', [])

    def replace_cfs_rows(self, rows: list[list[Any]]):
        spreadsheet_id, sheet_name = self._resolve_target(self.cfs_url, purpose='cfs')
        self.service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=self._a1_range(sheet_name, 'A:Z'),
            body={},
        ).execute()

        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=self._a1_range(sheet_name, 'A1'),
            valueInputOption='USER_ENTERED',
            body={'values': rows},
        ).execute()
