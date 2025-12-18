"""PDF export service using ReportLab."""

import io
from typing import Optional
from reportlab.lib.pagesizes import LETTER, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image as RLImage,
    PageBreak,
    Table,
    TableStyle,
)
from reportlab.lib import colors
from loguru import logger

from .base import BaseExporter, ExportResult


class PDFExporter(BaseExporter):
    """Export storybooks to PDF format."""

    def __init__(self, page_size=LETTER):
        """
        Initialize PDF exporter.

        Args:
            page_size: Page size (LETTER or A4)
        """
        self.page_size = page_size
        self.margin = 0.75 * inch

    async def export(self, story) -> ExportResult:
        """
        Export story to PDF.

        Args:
            story: Storybook document

        Returns:
            ExportResult with PDF data
        """
        logger.info(f"Exporting story '{story.title}' to PDF")

        # Create PDF buffer
        buffer = io.BytesIO()

        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            leftMargin=self.margin,
            rightMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin,
        )

        # Build content
        elements = await self._build_content(story)

        # Generate PDF
        doc.build(elements)

        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()

        filename = f"{self.sanitize_filename(story.title)}.pdf"

        logger.info(f"PDF export complete: {filename} ({len(pdf_data)} bytes)")

        return ExportResult(
            data=pdf_data,
            filename=filename,
            content_type="application/pdf",
            size=len(pdf_data),
        )

    async def _build_content(self, story) -> list:
        """
        Build PDF content elements.

        Args:
            story: Storybook document

        Returns:
            List of ReportLab elements
        """
        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=28,
            alignment=TA_CENTER,
            spaceAfter=30,
        )

        subtitle_style = ParagraphStyle(
            "CustomSubtitle",
            parent=styles["Normal"],
            fontSize=14,
            alignment=TA_CENTER,
            textColor=colors.gray,
            spaceAfter=50,
        )

        body_style = ParagraphStyle(
            "CustomBody",
            parent=styles["Normal"],
            fontSize=14,
            leading=20,
            alignment=TA_JUSTIFY,
            spaceAfter=15,
        )

        page_number_style = ParagraphStyle(
            "PageNumber",
            parent=styles["Normal"],
            fontSize=12,
            alignment=TA_CENTER,
            textColor=colors.gray,
        )

        # Cover page
        elements.append(Spacer(1, 0.5 * inch))

        # Cover image if available
        if story.cover_image_url:
            cover_data = await self.download_image(story.cover_image_url)
            if cover_data:
                cover_img = await self._create_image(cover_data, max_width=5*inch, max_height=5.5*inch)
                if cover_img:
                    elements.append(cover_img)
                    elements.append(Spacer(1, 0.3 * inch))

        elements.append(Paragraph(story.title, title_style))

        # Subtitle with format and age
        subtitle = f"A {story.generation_inputs.format.title()} for ages {story.generation_inputs.audience_age}"
        elements.append(Paragraph(subtitle, subtitle_style))

        elements.append(PageBreak())

        # Determine if comic format
        is_comic = story.generation_inputs.format == "comic"

        # Story pages
        for page in story.pages:
            if is_comic and page.panels:
                # Comic format: render panel grid
                panel_images = []
                for panel in page.panels:
                    if panel.illustration_url:
                        img_data = await self.download_image(panel.illustration_url)
                        if img_data:
                            panel_images.append(img_data)

                if panel_images:
                    # Create grid layout based on panel count
                    await self._add_comic_page(elements, panel_images, page.page_number)
            else:
                # Storybook format: single illustration + text
                if page.illustration_url:
                    img_data = await self.download_image(page.illustration_url)
                    if img_data:
                        img = await self._create_image(img_data, max_width=6*inch, max_height=5*inch)
                        if img:
                            elements.append(img)
                            elements.append(Spacer(1, 0.3 * inch))

                # Page text
                if page.text:
                    elements.append(Paragraph(page.text, body_style))

            # Page number
            elements.append(Spacer(1, 0.5 * inch))
            elements.append(Paragraph(f"- {page.page_number} -", page_number_style))

            elements.append(PageBreak())

        # End page
        elements.append(Spacer(1, 3 * inch))
        elements.append(Paragraph("The End", title_style))

        return elements

    async def _add_comic_page(
        self,
        elements: list,
        panel_images: list,
        page_number: int,
    ) -> None:
        """
        Add a comic page with panel grid layout.

        Args:
            elements: List of ReportLab elements to append to
            panel_images: List of panel image bytes
            page_number: Page number for alt text
        """
        panel_count = len(panel_images)

        # Calculate grid dimensions
        if panel_count == 1:
            cols, rows = 1, 1
        elif panel_count == 2:
            cols, rows = 2, 1
        elif panel_count <= 4:
            cols, rows = 2, 2
        elif panel_count <= 6:
            cols, rows = 3, 2
        else:
            cols, rows = 3, 3

        # Calculate cell size based on available space
        page_width = self.page_size[0] - 2 * self.margin
        page_height = self.page_size[1] - 2 * self.margin - 1.5 * inch  # Leave room for page number

        cell_width = (page_width - (cols - 1) * 0.1 * inch) / cols
        cell_height = (page_height - (rows - 1) * 0.1 * inch) / rows

        # Create table data with images
        table_data = []
        img_index = 0

        for row in range(rows):
            row_data = []
            for col in range(cols):
                if img_index < panel_count:
                    img = await self._create_image(
                        panel_images[img_index],
                        max_width=cell_width - 0.1 * inch,
                        max_height=cell_height - 0.1 * inch,
                    )
                    row_data.append(img if img else "")
                    img_index += 1
                else:
                    row_data.append("")
            table_data.append(row_data)

        # Create table
        table = Table(
            table_data,
            colWidths=[cell_width] * cols,
            rowHeights=[cell_height] * rows,
        )

        table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.gray),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))

        elements.append(table)

    async def _create_image(
        self,
        img_data: bytes,
        max_width: float = 6 * inch,
        max_height: float = 5 * inch,
    ) -> Optional[RLImage]:
        """
        Create ReportLab Image from bytes.

        Args:
            img_data: Image bytes
            max_width: Maximum image width
            max_height: Maximum image height

        Returns:
            ReportLab Image or None
        """
        try:
            from PIL import Image as PILImage

            # Get image dimensions
            img_buffer = io.BytesIO(img_data)
            pil_img = PILImage.open(img_buffer)
            orig_width, orig_height = pil_img.size

            # Calculate scaled dimensions
            width_ratio = max_width / orig_width
            height_ratio = max_height / orig_height
            scale = min(width_ratio, height_ratio, 1.0)

            width = orig_width * scale
            height = orig_height * scale

            # Create ReportLab image
            img_buffer.seek(0)
            rl_img = RLImage(img_buffer, width=width, height=height)
            rl_img.hAlign = "CENTER"

            return rl_img

        except Exception as e:
            logger.error(f"Failed to create image: {e}")
            return None
