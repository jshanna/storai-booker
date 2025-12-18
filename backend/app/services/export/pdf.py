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
                # Comic format: render panel grid with page number included
                panel_images = []
                for panel in page.panels:
                    if panel.illustration_url:
                        img_data = await self.download_image(panel.illustration_url)
                        if img_data:
                            panel_images.append(img_data)

                if panel_images:
                    # Create grid layout with page number embedded
                    await self._add_comic_page(elements, panel_images, page.page_number, page_number_style)
                elements.append(PageBreak())
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

                # Page number (only for storybook format)
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
        page_number_style,
    ) -> None:
        """
        Add a comic page with panel grid layout that fills the page.

        Args:
            elements: List of ReportLab elements to append to
            panel_images: List of panel image bytes
            page_number: Page number
            page_number_style: Style for page number text
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

        # Calculate available space - leave room for page number
        page_width = self.page_size[0] - 2 * self.margin
        page_height = self.page_size[1] - 2 * self.margin - 0.4 * inch  # Space for page number

        # Gap between panels
        gap = 0.06 * inch

        # Calculate cell dimensions to fill the space
        total_gap_width = (cols - 1) * gap
        total_gap_height = (rows - 1) * gap
        cell_width = (page_width - total_gap_width) / cols
        cell_height = (page_height - total_gap_height) / rows

        # Padding inside each cell
        cell_padding = 3

        # Create table data with images - scale to fit (no cropping)
        table_data = []
        img_index = 0

        for row in range(rows):
            row_data = []
            for col in range(cols):
                if img_index < panel_count:
                    img = await self._create_panel_image(
                        panel_images[img_index],
                        target_width=cell_width - 2 * cell_padding,
                        target_height=cell_height - 2 * cell_padding,
                        crop=False,  # Scale to fit, don't crop
                    )
                    row_data.append(img if img else "")
                    img_index += 1
                else:
                    row_data.append("")
            table_data.append(row_data)

        # Create table with exact dimensions
        table = Table(
            table_data,
            colWidths=[cell_width] * cols,
            rowHeights=[cell_height] * rows,
        )

        table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOX", (0, 0), (-1, -1), 2, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 1.5, colors.black),
            ("LEFTPADDING", (0, 0), (-1, -1), cell_padding),
            ("RIGHTPADDING", (0, 0), (-1, -1), cell_padding),
            ("TOPPADDING", (0, 0), (-1, -1), cell_padding),
            ("BOTTOMPADDING", (0, 0), (-1, -1), cell_padding),
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ]))

        elements.append(table)
        # Add page number directly after table (no spacer to avoid overflow)
        elements.append(Paragraph(f"- {page_number} -", page_number_style))

    async def _create_panel_image(
        self,
        img_data: bytes,
        target_width: float,
        target_height: float,
        crop: bool = False,
    ) -> Optional[RLImage]:
        """
        Create a panel image scaled to fit within target dimensions.

        Args:
            img_data: Image bytes
            target_width: Maximum width
            target_height: Maximum height
            crop: If True, crop to fill exact dimensions. If False, scale to fit.

        Returns:
            ReportLab Image or None
        """
        try:
            from PIL import Image as PILImage

            # Open image
            img_buffer = io.BytesIO(img_data)
            pil_img = PILImage.open(img_buffer)
            orig_width, orig_height = pil_img.size

            # Calculate target pixel dimensions (150 DPI)
            target_width_px = int(target_width / inch * 150)
            target_height_px = int(target_height / inch * 150)

            if crop:
                # Crop to fill (cover) the target area
                orig_ratio = orig_width / orig_height
                target_ratio = target_width_px / target_height_px

                if orig_ratio > target_ratio:
                    # Image is wider - crop sides
                    new_width = int(orig_height * target_ratio)
                    left = (orig_width - new_width) // 2
                    pil_img = pil_img.crop((left, 0, left + new_width, orig_height))
                else:
                    # Image is taller - crop top/bottom
                    new_height = int(orig_width / target_ratio)
                    top = (orig_height - new_height) // 2
                    pil_img = pil_img.crop((0, top, orig_width, top + new_height))

                # Resize to exact target dimensions
                pil_img = pil_img.resize((target_width_px, target_height_px), PILImage.Resampling.LANCZOS)
                final_width = target_width
                final_height = target_height
            else:
                # Scale to fit (contain) - preserve aspect ratio
                width_ratio = target_width_px / orig_width
                height_ratio = target_height_px / orig_height
                scale = min(width_ratio, height_ratio)

                new_width_px = int(orig_width * scale)
                new_height_px = int(orig_height * scale)

                if scale < 1.0:
                    pil_img = pil_img.resize((new_width_px, new_height_px), PILImage.Resampling.LANCZOS)

                # Calculate display dimensions
                final_width = new_width_px / 150 * inch
                final_height = new_height_px / 150 * inch

            # Convert to RGB if necessary
            if pil_img.mode in ('RGBA', 'LA', 'P'):
                background = PILImage.new('RGB', pil_img.size, (255, 255, 255))
                if pil_img.mode == 'P':
                    pil_img = pil_img.convert('RGBA')
                if pil_img.mode == 'RGBA':
                    background.paste(pil_img, mask=pil_img.split()[-1])
                else:
                    background.paste(pil_img)
                pil_img = background

            # Save as compressed JPEG
            compressed_buffer = io.BytesIO()
            pil_img.save(compressed_buffer, format='JPEG', quality=80, optimize=True)
            compressed_buffer.seek(0)

            # Create ReportLab image
            rl_img = RLImage(compressed_buffer, width=final_width, height=final_height)
            rl_img.hAlign = "CENTER"

            return rl_img

        except Exception as e:
            logger.error(f"Failed to create panel image: {e}")
            return None

    async def _create_image(
        self,
        img_data: bytes,
        max_width: float = 6 * inch,
        max_height: float = 5 * inch,
    ) -> Optional[RLImage]:
        """
        Create ReportLab Image from bytes with compression.

        Args:
            img_data: Image bytes
            max_width: Maximum image width
            max_height: Maximum image height

        Returns:
            ReportLab Image or None
        """
        try:
            from PIL import Image as PILImage

            # Open and process image
            img_buffer = io.BytesIO(img_data)
            pil_img = PILImage.open(img_buffer)
            orig_width, orig_height = pil_img.size

            # Calculate target dimensions for PDF (72 DPI is standard for PDF)
            # Limit to reasonable pixel dimensions for the target size
            target_width_px = int(max_width / inch * 150)  # 150 DPI
            target_height_px = int(max_height / inch * 150)

            # Scale down if image is larger than target
            width_ratio = target_width_px / orig_width
            height_ratio = target_height_px / orig_height
            scale = min(width_ratio, height_ratio, 1.0)

            if scale < 1.0:
                new_width = int(orig_width * scale)
                new_height = int(orig_height * scale)
                pil_img = pil_img.resize((new_width, new_height), PILImage.Resampling.LANCZOS)

            # Convert to RGB if necessary (remove alpha channel)
            if pil_img.mode in ('RGBA', 'LA', 'P'):
                background = PILImage.new('RGB', pil_img.size, (255, 255, 255))
                if pil_img.mode == 'P':
                    pil_img = pil_img.convert('RGBA')
                background.paste(pil_img, mask=pil_img.split()[-1] if pil_img.mode == 'RGBA' else None)
                pil_img = background

            # Save as compressed JPEG
            compressed_buffer = io.BytesIO()
            pil_img.save(compressed_buffer, format='JPEG', quality=75, optimize=True)
            compressed_buffer.seek(0)

            # Calculate display dimensions
            display_width_ratio = max_width / pil_img.width
            display_height_ratio = max_height / pil_img.height
            display_scale = min(display_width_ratio, display_height_ratio, 1.0)

            width = pil_img.width * display_scale
            height = pil_img.height * display_scale

            # Create ReportLab image
            rl_img = RLImage(compressed_buffer, width=width, height=height)
            rl_img.hAlign = "CENTER"

            return rl_img

        except Exception as e:
            logger.error(f"Failed to create image: {e}")
            return None
