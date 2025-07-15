import subprocess
import sys

from textual.app import App, ComposeResult
from textual.widgets import Footer, Label, ListItem, ListView

# Flag globale per decidere cosa fare all'uscita
next_action = None


class NearApp(App):
    BINDINGS = []

    CSS = """
Screen {
    align: center middle;
}

ListView > ListItem > Label {
    text-align: center;
    width: 100%;
}

ListView {
    width: 30;
    height: auto;
    margin: 1 2;
}

Label {
    padding: 1 2;
}
    """

    def compose(self) -> ComposeResult:
        self.theme = "dracula"
        ascii_art = (
            "                  \n"
            "             ,--. \n"
            "           ,--. | \n"
            "       ,--,:  : | \n"
            "    ,`--.'`|  ' : \n"
            "    |   :  :  | | \n"
            "    :   |   \\ | : \n"
            "    |   : '  '; | \n"
            "    '   ' ;.    ; \n"
            "    |   | | \\   | e a r\n"
            "    '   : |  ; .' \n"
            "    |   | '`--'   \n"
            "    '   : |       \n"
            "    ;   |.'       \n"
            "    '---'         \n"
        )
        yield Label(ascii_art, id="title")
        self.menu = ListView(
            ListItem(Label("Scan Username")),
            ListItem(Label("Social Scraper")),
            ListItem(Label("Phone Lookup")),
            ListItem(Label("Dorks Generator")),
        )
        yield self.menu

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        global next_action
        label = str(event.item.query_one(Label).renderable)
        if label == "Scan Username":
            next_action = "scan_username"
        elif label == "Social Scraper":
            next_action = "social_scraper"
        elif label == "Phone Lookup":
            next_action = "phone_lookup"
        self.exit()



if __name__ == "__main__":
    app = NearApp()
    app.run()

    # Dopo l'uscita da Textual
    if next_action == "scan_username":
            subprocess.run(["python3", "core/username_scan/username_scan.py"])
    elif next_action == "social_scraper":
            subprocess.run(["python3", "core/social_scraper/social_scraper.py"])
    elif next_action == "phone_lookup":
            subprocess.run(["python3", "core/phone_lookup/phone_lookup.py"])
