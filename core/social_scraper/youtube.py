from textual.app import App, ComposeResult
from textual.widgets import Input, Static, Footer
from textual.containers import Vertical
from textual.reactive import reactive
from rich.text import Text
import requests
import re
import os


class YouTubeOSINTApp(App):
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

    channel_id = reactive("")
    info_box: Static
    message_box: Static

    def compose(self) -> ComposeResult:
        self.theme = "dracula"
        yield Vertical(
            Input(placeholder="Enter YouTube Channel ID or name and press Enter", id="channel_input"),
            Static("", id="info_box"),
            Static("", id="message_box"),
        )

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        self.channel_id = event.value.strip()
        self.info_box = self.query_one("#info_box", Static)
        self.message_box = self.query_one("#message_box", Static)

        if not self.channel_id:
            self.info_box.update("[red]Please enter a Channel ID or name[/red]")
            return

        self.info_box.update("[yellow]Fetching data, please wait...[/yellow]")
        await self.run_scraper(self.channel_id)

    async def run_scraper(self, channel_id: str):
        url = f'https://vidiq.com/youtube-stats/channel/{channel_id}/'

        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                self.info_box.update(f"[red]Error: Page not reachable (status code {response.status_code})[/red]")
                return

            html = response.text

            def extract(pattern, text=html, group=1):
                match = re.search(pattern, text, re.DOTALL)
                return match.group(group).strip() if match else "N/A"

            data = {}
            data['Username'] = extract(r'<title>(.*?)\'s YouTube Stats and Insights')
            data['Subscribers'] = extract(r'Subscribers</p></div><p class="mb-0 text-right text-white">([^<]+)</p>')
            data['Total Views'] = extract(r'The total video views count and its change in the last 30 days.*?<p[^>]*>([^<]+)</p>')
            data['Average Video Duration'] = extract(r'The average duration of the last 15 videos.*?<p[^>]*>([^<]+)</p>')
            data['Estimated Earnings'] = extract(r'An estimated value based on a default category.*?<p[^>]*>\$?([^<]+)</p>')
            data['Location'] = extract(r'Location</p></div><p class="mb-0 text-right text-white">([^<]+)</p>')
            data['Join Date'] = extract(r'Joined</p></div><p class="mb-0 text-right text-white">([^<]+)</p>')
            data['Category'] = extract(r'Category</p></div><p class="mb-0 text-right text-white">([^<]+)</p>')
            data['Video Count'] = extract(r'Videos</p></div><p class="mb-0 text-right text-white">([^<]+)</p>')
            data['Channel Description'] = extract(r'text-ellipsis text-sm font-medium text-white.*?>(.*?)</p></div>', group=1)
            desc = data.get("Channel Description", "")
            if len(desc) > 100:
                data["Channel Description"] = desc[:100].rstrip() + "..."

            os.makedirs(channel_id, exist_ok=True)

            with open(f"{channel_id}/profile_info.txt", "w", encoding="utf-8") as f:
                for key, value in data.items():
                    f.write(f"{key}: {value}\n")

            output = Text()
            for key, value in data.items():
                output.append(f"{key}: ", style="bold cyan")
                output.append(f"{value}\n")

            self.info_box.update(output)
            self.message_box.update(f"[green]All data saved in folder './{channel_id}'[/green]")

        except Exception as e:
            self.info_box.update(f"[red]Unexpected error: {e}[/red]")


if __name__ == "__main__":
    YouTubeOSINTApp().run()


