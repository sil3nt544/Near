from textual.app import App, ComposeResult
from textual.widgets import Footer, Label, ListItem, ListView

class NearApp(App):
    BINDINGS = []  # Disattiva tutte le shortcut, inclusa Ctrl+P (Command Palette)

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
        yield ListView(
            ListItem(Label("Scan Username")),
            ListItem(Label("Check Socials")),
            ListItem(Label("Subdomain Finder")),
        )

if __name__ == "__main__":
    NearApp().run()

