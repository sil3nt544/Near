from textual.app import App, ComposeResult
from textual.widgets import Input, Static, Footer
from textual.containers import Vertical
from textual.reactive import reactive
from rich.text import Text

import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import os

class PhoneLookupApp(App):
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

    phone_number = reactive("")
    info_box: Static
    message_box: Static

    def compose(self) -> ComposeResult:
        self.theme = "dracula"
        yield Vertical(
            Input(placeholder="Enter phone number with country code (+123...) and press Enter", id="phone_input"),
            Static("", id="info_box"),
            Static("", id="message_box"),
        )

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        self.phone_number = event.value.strip()
        self.info_box = self.query_one("#info_box", Static)
        self.message_box = self.query_one("#message_box", Static)

        self.info_box.update("[yellow]Looking up phone number, please wait...[/yellow]")
        await self.run_lookup(self.phone_number)

    async def run_lookup(self, phone: str):
        try:
            # Parsing the phone number
            parsed = phonenumbers.parse(phone, None)
            
            if not phonenumbers.is_valid_number(parsed):
                self.info_box.update(f"[red]Invalid phone number: {phone}[/red]")
                return
            
            number_type = phonenumbers.number_type(parsed)
            type_str = {
                0: "Unknown",
                1: "Fixed line",
                2: "Mobile",
                3: "Fixed line or Mobile",
                4: "Toll Free",
                5: "Premium Rate",
                6: "Shared Cost",
                7: "VoIP",
                8: "Personal Number",
                9: "Pager",
                10: "UAN",
                11: "Voicemail",
                12: "Unknown"
            }.get(number_type, "Unknown")

            region = geocoder.description_for_number(parsed, "en") or "Unknown"
            carrier_name = carrier.name_for_number(parsed, "en") or "Unknown"
            timezones = timezone.time_zones_for_number(parsed)
            country_code = parsed.country_code
            national_number = parsed.national_number
            
            data = {
                "Input Number": phone,
                "E164 Format": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
                "International Format": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                "National Format": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
                "Country Code": country_code,
                "National Number": national_number,
                "Number Type": type_str,
                "Carrier": carrier_name,
                "Region/City": region,
                "Timezones": ", ".join(timezones) if timezones else "Unknown",
            }

            # Save results
            folder_name = str(national_number)
            os.makedirs(folder_name, exist_ok=True)
            with open(f"{folder_name}/phone_info.txt", "w", encoding="utf-8") as f:
                for k, v in data.items():
                    f.write(f"{k}: {v}\n")

            # Prepare output text
            output = Text()
            for k, v in data.items():
                output.append(f"{k}: ", style="bold cyan")
                output.append(f"{v}\n")

            self.info_box.update(output)
            self.message_box.update(f"[green]All data saved in folder './{folder_name}'[/green]")

        except phonenumbers.NumberParseException as e:
            self.info_box.update(f"[red]Error parsing number: {e}[/red]")
        except Exception as e:
            self.info_box.update(f"[red]Unexpected error: {e}[/red]")

if __name__ == "__main__":
    PhoneLookupApp().run()


