from textual.app import App, ComposeResult
from textual.widgets import Input, Static, Footer
from textual.containers import Vertical
from textual.reactive import reactive
from rich.text import Text
import requests
from bs4 import BeautifulSoup
import os


class TikTokOSINTApp(App):
    CSS = """
Screen {
    align: center middle;
}

Vertical {
    height: 100%;
    width: 50%;
    min-width: 40;
}

Input {
    margin-top: 1;
    height: 3;
    margin-bottom: 1;
    width: 100%;
    max-width: 50;
}

Static#info_box, Static#message_box {
    width: 100%;
    max-width: 70;
    padding: 1 2;
}

Footer {
    dock: bottom;
}
    """

    BINDINGS = [("q", "quit", "Quit")]

    username = reactive("")
    info_box: Static
    message_box: Static

    def compose(self) -> ComposeResult:
        self.theme = "dracula"
        yield Vertical(
            Input(placeholder="Enter TikTok username and press Enter", id="username_input"),
            Static("", id="info_box"),
            Static("", id="message_box"),
        )

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        self.username = event.value.strip()
        self.info_box = self.query_one("#info_box", Static)
        self.message_box = self.query_one("#message_box", Static)

        if not self.username:
            self.info_box.update("[red]Please enter a username[/red]")
            return

        self.info_box.update("[yellow]Fetching data, please wait...[/yellow]")
        await self.run_scraper(self.username)

    async def run_scraper(self, username: str):
        url = f"https://socialblade.com/tiktok/user/{username}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                          " Chrome/114.0.0.0 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                self.info_box.update(f"[red]Error: Page not reachable (status code {response.status_code})[/red]")
                return

            soup = BeautifulSoup(response.text, "html.parser")

            container = soup.find("div", class_="hidden lg:block flex-1 outline-none pb-1")
            if not container:
                self.info_box.update("[red]Error: Could not find data container on the page[/red]")
                return

            stats = {}
            for stat_div in container.find_all("div", class_="py-1"):
                key_tag = stat_div.find("p", class_="m-0 text-[0.75em] font-medium capitalize pr-[50px]")
                val_tag = stat_div.find("p", class_="text-[1.25em] font-extralight pr-[50px]")

                if key_tag and val_tag:
                    key = key_tag.text.strip()
                    val = val_tag.text.strip()
                    stats[key] = val

            created_div = container.find("div", class_="py-1 block md:hidden lg:block")
            if created_div:
                key_created = created_div.find("p", class_="m-0 text-[0.75em] font-semibold capitalize")
                val_created = created_div.find("p", class_="text-[1.25em] font-extralight")
                if key_created and val_created:
                    stats[key_created.text.strip()] = val_created.text.strip()

            profile_img = soup.find("img", alt=lambda x: x and "profile picture" in x.lower())
            if profile_img:
                img_url = profile_img.get("src")
                if img_url:
                    stats["Profile Image URL"] = img_url
                else:
                    stats["Profile Image URL"] = "Not found"
            else:
                stats["Profile Image URL"] = "Not found"

            os.makedirs(username, exist_ok=True)

            with open(f"{username}/profile_info.txt", "w", encoding="utf-8") as f:
                for key, value in stats.items():
                    f.write(f"{key}: {value}\n")

            output = Text()
            for key, value in stats.items():
                output.append(f"{key}: ", style="bold cyan")
                output.append(f"{value}\n")

            self.info_box.update(output)
            self.message_box.update(f"[green]All data saved in folder './{username}'[/green]")

        except Exception as e:
            self.info_box.update(f"[red]Unexpected error: {e}[/red]")


if __name__ == "__main__":
    TikTokOSINTApp().run()


