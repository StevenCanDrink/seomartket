from weasyprint import HTML, CSS
from weasyprint_assets.html_custom import html_string
from weasyprint.text.fonts import FontConfiguration
import os


class WeasyprintCustom:
    def __init__(self):
        pass

    async def create_pdf(self, html, name):
        font_config = FontConfiguration()
        css = CSS(
            filename="./public/output.css",
            font_config=font_config,
        )
        # Convert from URL
        # html = HTML("https://bio.tuyendung8k.com/create-cv")
        # html.write_pdf("output.pdf", stylesheets=[css], font_config=font_config)

        # Convert from HTML string

        os.makedirs("tmp", exist_ok=True)

        html = HTML(string=html)
        html.write_pdf(f"tmp/{name}.pdf", stylesheets=[css], font_config=font_config)
