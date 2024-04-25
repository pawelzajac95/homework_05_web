import aiohttp
import asyncio
from datetime import datetime, timedelta


class NbpApiClient:
    API_URL = 'http://api.nbp.pl/api/exchangerates/rates/a/{currency_code}/{start_date}/{end_date}/'

    async def fetch_exchange_rates(self, currency_code, start_date, end_date):
        url = self.API_URL.format(
            currency_code=currency_code, start_date=start_date, end_date=end_date)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    raise ValueError(f"Failed to fetch data: {
                                     response.status} - {response.reason}")


class ExchangeRateAnalyzer:
    def __init__(self, api_client):
        self.api_client = api_client

    async def get_exchange_rates(self, currency_code, days):
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)
                      ).strftime('%Y-%m-%d')
        try:
            data = await self.api_client.fetch_exchange_rates(currency_code, start_date, end_date)
            return data
        except ValueError as e:
            print(f"Error: {e}")
            return []


async def main():
    api_client = NbpApiClient()
    analyzer = ExchangeRateAnalyzer(api_client)

    try:
        eur_data = await analyzer.get_exchange_rates('EUR', 10)
        usd_data = await analyzer.get_exchange_rates('USD', 10)

        formatted_results = []
        for rate_data in eur_data['rates']:
            rate_date = rate_data['effectiveDate']
            eur_rate = rate_data['mid']
            for usd_rate_data in usd_data['rates']:
                if usd_rate_data['effectiveDate'] == rate_date:
                    usd_rate = usd_rate_data['mid']
                    break
            formatted_results.append({
                rate_date: {
                    'EUR': {'sale': eur_rate, 'purchase': eur_rate},
                    'USD': {'sale': usd_rate, 'purchase': usd_rate}
                }
            })

        print(formatted_results)

    except aiohttp.ClientError as e:
        print(f"Network error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
