import asyncio
import time
from dataclasses import dataclass
from datetime import datetime

from selenium.common import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.ie.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from telegram_bot import start_bot, send_to_all_clients


@dataclass(frozen=True)
class ApartmentCard:
    index: int
    about: str
    link: str

@dataclass(frozen=True)
class ImmomioCredentials:
    email: str
    password: str

class SagaWebParser(Chrome):
    def __init__(self, immomio_credentials: ImmomioCredentials):
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
        # options.add_argument("--headless")
        super().__init__(options=options)
        try:
            if not self.login_to_immomio(immomio_credentials):
                raise RuntimeError("login_to_immomio returned False")
            else:
                print("Successfully logged in to immomio")
        except Exception as ex:
            raise RuntimeError(f"Failed to login lmmomio cause of: {ex}")

    def login_to_immomio(self, creds: ImmomioCredentials):
        self.get("https://tenant.immomio.com/de/auth/login")

        # enter email
        WebDriverWait(self, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))
        ).send_keys(creds.email)

        # click submit
        WebDriverWait(self, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[type=submit]"))
        ).click()

        # enter password
        WebDriverWait(self, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=password]"))
        ).send_keys(creds.password)

        # click submit
        WebDriverWait(self, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=submit]"))
        ).click()

        try:
            feedback_text = WebDriverWait(self, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".alert .kc-feedback-text"))
            ).text
            raise RuntimeError(feedback_text)
        except TimeoutException:
            pass

        if not self.is_immomio_profile_page():
            raise RuntimeError("#accountDropdown hasn`t been found.")

        return True

    def is_immomio_profile_page(self) -> bool:
        try:
            WebDriverWait(self, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#accountDropdown"))
            )
            return True
        except TimeoutException:
            return False

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

    def handle_apartment_card(self, card: ApartmentCard) -> bool:
        self.get(card.link)

        try:
            lnk = WebDriverWait(self, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.btn-icon"))
            ).get_attribute("href")
            self.get(lnk)
        except Exception as ex:
            return False

        try:
            WebDriverWait(self, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "app-application-actions button[type=button]"))
            ).click()
        except Exception as ex:
            return False

        if not self.is_immomio_profile_page():
            return False

        return True

async def new_cards_handler(cards: list[ApartmentCard], handled: dict[str, bool]):
    for card in cards:
        print("NEW CARD FOUND!")
        print(card)
        print("_______________")

        message = (
            f"🏠 <b>Квартира №{card.index}</b>\n\n"
            f"📝 <b>Загальні дані:</b>\n"
            f"<i>{card.about}</i>\n\n"
            f"🔗 <a href=\"{card.link}\">Перейти до обʼєкта</a>\n"
            f"━━━━━━━"
            f"🚀 <b>Заявку надіслано!</b>" if handled.get(card.link, False) else ""
        )

        await send_to_all_clients(message)

async def saga_monitoring(immomio_creds: ImmomioCredentials):
    parser = SagaWebParser(immomio_creds)
    parsed_cards = set([])
    while True:
        try:
            cards = set(parser.parse_apartment_cards())
            new_cards = cards.difference(parsed_cards)
            if len(new_cards) > 0:
                parsed_cards.update(new_cards)
                handled_cards = {}
                for new_card in new_cards:
                    handled_cards[new_card.link] = parser.handle_apartment_card(new_card)
                await new_cards_handler(list(new_cards), handled_cards)
        except Exception as ex:
            print(f"error on parsing: {ex}")
            try:
                parser.close()
                parser.quit()
            except:
                pass
            parser = SagaWebParser(immomio_creds)
            
        await asyncio.sleep(.001)

async def main():
    asyncio.create_task(saga_monitoring(immomio_creds=ImmomioCredentials(
        email="koval321@gmail.com",
        password="#Ab111111"
    )))
    await start_bot()



if __name__=="__main__":
    asyncio.run(main())
