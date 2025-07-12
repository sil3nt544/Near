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
            "          ,--.'| \n"
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
            ListItem(Label("Scrape Socials")),
            ListItem(Label("Subdomain Finder")),
        )
        yield self.menu

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        global next_action
        label = str(event.item.query_one(Label).renderable)
        if label == "Scan Username":
            next_action = "scan_username"
            self.exit()



if __name__ == "__main__":
    app = NearApp()
    app.run()

    # Dopo l'uscita da Textual
    if next_action == "scan_username":
            subprocess.run(["python3", "core/username_scan/username_scan.py"])
