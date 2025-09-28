import reflex as rx
import requests
import asyncio
import csv
import logging
from io import StringIO
from typing import TypedDict


class Rate(TypedDict):
    date: str
    rate: float


class CurrencyState(rx.State):
    currencies: list[str] = []
    from_currency: str = "USD"
    to_currency: str = "ZAR"
    dates_input: str = ""
    results: list[Rate] = []
    is_loading: bool = False
    error_message: str = ""

    @rx.event
    async def on_load(self):
        try:
            response = requests.get("https://api.frankfurter.app/currencies")
            response.raise_for_status()
            self.currencies = sorted(list(response.json().keys()))
        except requests.exceptions.RequestException as e:
            logging.exception(e)
            self.error_message = f"Failed to fetch currencies: {e}"

    @rx.event(background=True)
    async def get_fx_rates(self):
        async with self:
            if (
                not self.dates_input.strip()
                or not self.from_currency
                or (not self.to_currency)
            ):
                self.error_message = "Please provide dates and select both currencies."
                return
            self.is_loading = True
            self.results = []
            self.error_message = ""
        dates = [
            date.strip()
            for date in self.dates_input.split("""
""")
            if date.strip()
        ]
        temp_results = []
        for date in dates:
            try:
                api_url = f"https://api.frankfurter.app/{date}?from={self.from_currency}&to={self.to_currency}"
                response = await asyncio.to_thread(requests.get, api_url)
                response.raise_for_status()
                data = response.json()
                rate = data.get("rates", {}).get(self.to_currency)
                if rate is not None:
                    temp_results.append({"date": date, "rate": rate})
                else:
                    async with self:
                        self.error_message = f"No rate found for {date}"
            except requests.exceptions.RequestException as e:
                logging.exception(e)
                async with self:
                    self.error_message = f"Error fetching data for {date}: {e}"
                    self.is_loading = False
                return
            await asyncio.sleep(0.1)
        async with self:
            self.results = temp_results
            self.is_loading = False

    @rx.event
    def download_csv(self):
        if not self.results:
            return
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Date", "Exchange Rate"])
        for item in self.results:
            writer.writerow([item["date"], item["rate"]])
        csv_data = output.getvalue()
        return rx.download(data=csv_data, filename="exchange_rates.csv")