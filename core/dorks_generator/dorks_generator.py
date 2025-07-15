from textual.app import App, ComposeResult
from textual.widgets import Input, Static, Button, Select
from textual.containers import Vertical
from rich.text import Text

class DorkGeneratorApp(App):
    CSS = """
Screen {
    align: center middle;
}

Vertical {
    width: 60%;
    min-width: 60;
    height: auto;
}

Input, Select, Button {
    margin-top: 1;
    width: 100%;
}

Static#output_box {
    border: round white;
    padding: 1 2;
    max-height: 20;
    overflow-y: auto;
    width: 100%;
    margin-top: 1;
}

Static#status_msg {
    margin-top: 1;
    color: green;
}
"""

    input_value: str = ""
    input_type: str = "username"

    def compose(self) -> ComposeResult:
        self.theme = "dracula"
        yield Vertical(
            Input(placeholder="Enter username, email or phone", id="input_field"),
            Select(options=[
                ("Username", "username"),
                ("Email", "email"),
                ("Phone Number", "phone"),
            ], prompt="Select input type", id="input_type"),
            Button("Generate Dorks", id="generate_btn"),
            Static("", id="output_box"),
            Static("", id="status_msg")
        )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.input_value = event.value.strip()

    def on_select_changed(self, event: Select.Changed) -> None:
        self.input_type = event.value

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "generate_btn":
            self.input_value = self.query_one("#input_field", Input).value.strip()
            self.input_type = self.query_one("#input_type", Select).value
            output_box = self.query_one("#output_box", Static)
            status_msg = self.query_one("#status_msg", Static)

            if not self.input_value:
                output_box.update("[red]Error: Empty input[/red]")
                status_msg.update("")
                return

            dorks = self.generate_dorks(self.input_value, self.input_type)
            output_text = Text()

            filename = f"{self.input_value.lower()}.txt"

            with open(filename, "w", encoding="utf-8") as f:
                for dork in dorks:
                    output_text.append(f"{dork}\n", style="green")
                    f.write(dork + "\n")

            output_box.update(output_text)
            status_msg.update(f"[bold green]Dorks saved in {filename}[/bold green]")

    def generate_dorks(self, value: str, input_type: str) -> list[str]:
        filetypes = ["txt", "pdf", "csv", "doc", "docx", "log", "json", "xml", "xls", "xlsx", "odt"]
        dorks = []

        if input_type == "username":
            base = f'"{value}"%2B(!Password|!password|!PASSWORD|passwd|login)'
        elif input_type == "email":
            base = f'"{value}"%2B!e-mail'
        elif input_type == "phone":
            base = f'"{value}"%2B(contact|tel|telefono|number|cell|phone)'
        else:
            base = f'"{value}"'

        for ext in filetypes:
            query = f'https://yandex.com/search/?text={base}+mime:{ext}'
            dorks.append(query)

        return dorks

if __name__ == "__main__":
    DorkGeneratorApp().run()

