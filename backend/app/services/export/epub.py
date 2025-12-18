"""EPUB export service using ebooklib."""

import io
import uuid
from ebooklib import epub
from loguru import logger

from .base import BaseExporter, ExportResult


class EPUBExporter(BaseExporter):
    """Export storybooks to EPUB format."""

    async def export(self, story) -> ExportResult:
        """
        Export story to EPUB.

        Args:
            story: Storybook document

        Returns:
            ExportResult with EPUB data
        """
        logger.info(f"Exporting story '{story.title}' to EPUB")

        # Create EPUB book
        book = epub.EpubBook()

        # Set metadata
        book.set_identifier(f"storai-{story.id}")
        book.set_title(story.title)
        book.set_language("en")
        book.add_author("StorAI Booker")

        # Add metadata
        book.add_metadata("DC", "description", story.generation_inputs.topic)
        book.add_metadata("DC", "subject", f"Children's {story.generation_inputs.format}")

        # Default CSS
        style = """
        body {
            font-family: Georgia, serif;
            line-height: 1.6;
            text-align: justify;
        }
        h1 {
            text-align: center;
            margin-bottom: 2em;
        }
        .cover {
            text-align: center;
            margin: 0;
            padding: 0;
        }
        .cover img {
            max-width: 100%;
            height: auto;
        }
        .page {
            page-break-before: always;
        }
        .page-image {
            text-align: center;
            margin: 1em 0;
        }
        .page-image img {
            max-width: 100%;
            height: auto;
        }
        .page-text {
            font-size: 1.2em;
            margin: 1em 2em;
        }
        .page-number {
            text-align: center;
            color: #888;
            margin-top: 2em;
        }
        .the-end {
            text-align: center;
            font-size: 2em;
            margin-top: 3em;
        }
        .comic-grid {
            display: grid;
            gap: 4px;
            margin: 0.5em;
        }
        .comic-grid-2x1 { grid-template-columns: 1fr 1fr; }
        .comic-grid-2x2 { grid-template-columns: 1fr 1fr; }
        .comic-grid-3x2 { grid-template-columns: 1fr 1fr 1fr; }
        .comic-grid-3x3 { grid-template-columns: 1fr 1fr 1fr; }
        .panel {
            border: 1px solid #333;
            overflow: hidden;
        }
        .panel img {
            width: 100%;
            height: auto;
            display: block;
        }
        """

        css = epub.EpubItem(
            uid="style",
            file_name="style/main.css",
            media_type="text/css",
            content=style,
        )
        book.add_item(css)

        chapters = []
        images = []

        # Cover image
        if story.cover_image_url:
            cover_data = await self.download_image(story.cover_image_url)
            if cover_data:
                book.set_cover("cover.png", cover_data)
                images.append(("cover.png", cover_data))

        # Title page
        title_chapter = epub.EpubHtml(
            title="Title",
            file_name="title.xhtml",
            lang="en",
        )
        title_content = f"""
        <html>
        <head><link rel="stylesheet" href="style/main.css"/></head>
        <body>
            <div class="cover">
                <h1>{self._escape_html(story.title)}</h1>
                <p>A {story.generation_inputs.format.title()} for ages {story.generation_inputs.audience_age}</p>
            </div>
        </body>
        </html>
        """
        title_chapter.content = title_content
        title_chapter.add_item(css)
        book.add_item(title_chapter)
        chapters.append(title_chapter)

        # Determine if comic format
        is_comic = story.generation_inputs.format == "comic"

        # Story pages
        for page in story.pages:
            page_chapter = epub.EpubHtml(
                title=f"Page {page.page_number}",
                file_name=f"page_{page.page_number:02d}.xhtml",
                lang="en",
            )

            # Build page content
            content_parts = ['<html><head><link rel="stylesheet" href="style/main.css"/></head><body><div class="page">']

            if is_comic and page.panels:
                # Comic format: render panel grid
                panel_count = len(page.panels)
                grid_class = self._get_grid_class(panel_count)

                content_parts.append(f'<div class="comic-grid {grid_class}">')

                for panel in page.panels:
                    if panel.illustration_url:
                        img_data = await self.download_image(panel.illustration_url)
                        if img_data:
                            img_filename = f"images/page_{page.page_number:02d}_panel_{panel.panel_number:02d}.png"
                            images.append((img_filename, img_data))
                            content_parts.append(f'<div class="panel"><img src="{img_filename}" alt="Page {page.page_number}, Panel {panel.panel_number}"/></div>')

                content_parts.append('</div>')
            else:
                # Storybook format: single image + text
                if page.illustration_url:
                    img_data = await self.download_image(page.illustration_url)
                    if img_data:
                        img_filename = f"images/page_{page.page_number:02d}.png"
                        images.append((img_filename, img_data))
                        content_parts.append(f'<div class="page-image"><img src="{img_filename}" alt="Page {page.page_number}"/></div>')

                # Add text
                if page.text:
                    content_parts.append(f'<div class="page-text">{self._escape_html(page.text)}</div>')

            # Page number
            content_parts.append(f'<div class="page-number">- {page.page_number} -</div>')

            content_parts.append("</div></body></html>")

            page_chapter.content = "".join(content_parts)
            page_chapter.add_item(css)
            book.add_item(page_chapter)
            chapters.append(page_chapter)

        # End page
        end_chapter = epub.EpubHtml(
            title="The End",
            file_name="end.xhtml",
            lang="en",
        )
        end_chapter.content = """
        <html>
        <head><link rel="stylesheet" href="style/main.css"/></head>
        <body>
            <div class="the-end">The End</div>
        </body>
        </html>
        """
        end_chapter.add_item(css)
        book.add_item(end_chapter)
        chapters.append(end_chapter)

        # Add images to book
        for img_filename, img_data in images:
            if img_filename != "cover.png":  # Cover is added separately
                img_item = epub.EpubItem(
                    uid=img_filename.replace("/", "_"),
                    file_name=img_filename,
                    media_type="image/png",
                    content=img_data,
                )
                book.add_item(img_item)

        # Define spine and TOC
        book.spine = ["nav"] + chapters
        book.toc = chapters

        # Add navigation files
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Write EPUB to buffer
        buffer = io.BytesIO()
        epub.write_epub(buffer, book, {})
        epub_data = buffer.getvalue()
        buffer.close()

        filename = f"{self.sanitize_filename(story.title)}.epub"

        logger.info(f"EPUB export complete: {filename} ({len(epub_data)} bytes)")

        return ExportResult(
            data=epub_data,
            filename=filename,
            content_type="application/epub+zip",
            size=len(epub_data),
        )

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        if not text:
            return ""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    def _get_grid_class(self, panel_count: int) -> str:
        """Get CSS grid class based on panel count."""
        if panel_count <= 2:
            return "comic-grid-2x1"
        elif panel_count <= 4:
            return "comic-grid-2x2"
        elif panel_count <= 6:
            return "comic-grid-3x2"
        else:
            return "comic-grid-3x3"
