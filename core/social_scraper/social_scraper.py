import subprocess
from textual.app import App, ComposeResult
from textual.widgets import Footer, Label, ListItem, ListView


class NearApp(App):
    CSS = """
    Screen {
        align: center middle;
    }

    ListView > ListItem > Label {
        text-align: center;
        width: 99%;
    }

    ListView {
        width: 30;
        height: auto;
        margin: 2 2;
    }

    Label {
        padding: 1 2;
    }
    """

    def __init__(self):
        super().__init__()
        self.selected_action = None

    def compose(self) -> ComposeResult:
        self.theme = "dracula"
        menu_items = [
            "Instagram",
            "TikTok",
            "Youtube",
        ]
        list_view = ListView(*[ListItem(Label(item)) for item in menu_items])
        yield Label("   Select a social network")
        yield list_view

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        label = event.item.query_one(Label).renderable
        if label == "Instagram":
            self.selected_action = "instagram"
        if label == "TikTok":
            self.selected_action = "tiktok"
        if label == "Youtube":
            self.selected_action = "youtube"
        else:
            pass
        self.exit()


if __name__ == "__main__":
    app = NearApp()
    app.run()

    # Esegui azione dopo l'uscita dall'app
    if app.selected_action == "instagram":
        subprocess.run(["python3", "core/social_scraper/instagram.py"])
    elif app.selected_action == "tiktok":
        subprocess.run(["python3", "core/social_scraper/tiktok.py"])
    elif app.selected_action == "youtube":
        subprocess.run(["python3", "core/social_scraper/youtube.py"])

