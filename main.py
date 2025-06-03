import asyncio
import time
from dataclasses import dataclass
from datetime import datetime

from selenium.common import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from telegram_bot import start_bot, send_to_all_clients


@dataclass(frozen=True)
class ApartmentCard:
    index: int
    about: str
    link: str


class SagaWebParser(Chrome):
    def __init__(self):
        options = Options()
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-blink-features=BlockCredentialedSubresources')
        options.add_argument('--disable-media')
        options.add_argument("--disable-gpu")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-infobars')
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument('--no-sandbox')
        options.add_argument('--mute-audio')
        options.add_argument('--lang=en')
        options.add_argument("--headless")
        super().__init__(options=options)

    def get_apartment_category(self):
        self.get("https://www.saga.hamburg/immobiliensuche?Kategorie=APARTMENT")

        try:
            WebDriverWait(self, 1).until(
                EC.element_to_be_clickable((By.XPATH, "//*[text()[contains(.,'Alles akzeptieren')]]"))
            ).click()
        except TimeoutException as ex:
            pass

    def parse_apartment_cards(self) -> list[ApartmentCard]:
        aparts = []

        self.get_apartment_category()

        try:
            try:
                apart_cards = WebDriverWait(self, 1).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//*[starts-with(@id, 'APARTMENT-card-')]"))
                )

                for apart_card in apart_cards:
                    index = apart_card.get_attribute("id").replace("APARTMENT-card-", "")
                    text = apart_card.text.replace("ANZEIGEN", "")
                    text = "\n".join(text.split("\n")[:-1])
                    link = apart_card.find_element(By.TAG_NAME, "a").get_attribute("href")
                    aparts.append(ApartmentCard(int(index), text, link))

            except TimeoutException as ex:
                print(ex)

        except TimeoutException as ex:
            print(ex)

        return aparts

async def new_cards_handler(cards: list[ApartmentCard]):
    for card in cards:
        print("NEW CARD FOUND!")
        print(card)
        print("_______________")

        message = (
            f"🏠 <b>Квартира №{card.index}</b>\n\n"
            f"📝 <b>Загальні дані:</b>\n"
            f"<i>{card.about}</i>\n\n"
            f"🔗 <a href=\"{card.link}\">Перейти до обʼєкта</a>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        )

        await send_to_all_clients(message)

async def saga_monitoring():
    parser = SagaWebParser()
    parsed_cards = set([])
    while True:
        try:
            cards = set(parser.parse_apartment_cards())
            new_cards = cards.difference(parsed_cards)
            if len(new_cards) > 0:
                parsed_cards.update(new_cards)
                await new_cards_handler(list(new_cards))
        except Exception as ex:
            print(f"error on parsing: {ex}")
            try:
                parser.close()
                parser.quit()
            except:
                pass
            parser = SagaWebParser()
            
        await asyncio.sleep(.001)

async def main():
    asyncio.create_task(saga_monitoring())
    await start_bot()



if __name__=="__main__":
    asyncio.run(main())
