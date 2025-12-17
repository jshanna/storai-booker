"""Input sanitization service to prevent XSS and injection attacks."""
import re
from typing import Optional
from loguru import logger


class InputSanitizer:
    """Service for sanitizing user inputs to prevent security vulnerabilities."""

    # Patterns for detecting potentially malicious content
    SCRIPT_PATTERN = re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL)
    HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
    SQL_INJECTION_PATTERN = re.compile(
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b\s+(FROM|INTO|TABLE|WHERE|VALUES))|"
        r"(--\s)|"
        r"(;\s*(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER))",
        re.IGNORECASE
    )
    NOSQL_INJECTION_PATTERN = re.compile(
        r'(\$where|\$ne|\$gt|\$lt|\$gte|\$lte|\$in|\$nin|\$regex|\$exists)',
        re.IGNORECASE
    )

    # Maximum lengths for different input types
    MAX_TITLE_LENGTH = 200
    MAX_TOPIC_LENGTH = 500
    MAX_SETTING_LENGTH = 500
    MAX_CHARACTER_LENGTH = 200

    @staticmethod
    def sanitize_text(text: str, remove_html: bool = True) -> str:
        """
        Sanitize text input by removing potentially dangerous content.

        Args:
            text: The text to sanitize
            remove_html: Whether to remove HTML tags

        Returns:
            Sanitized text
        """
        if not text:
            return ""

        # Remove script tags
        text = InputSanitizer.SCRIPT_PATTERN.sub('', text)

        # Remove HTML tags if requested
        if remove_html:
            text = InputSanitizer.HTML_TAG_PATTERN.sub('', text)

        # Remove null bytes
        text = text.replace('\x00', '')

        # Trim whitespace
        text = text.strip()

        return text

    @staticmethod
    def sanitize_title(title: str) -> str:
        """
        Sanitize story title.

        Args:
            title: The title to sanitize

        Returns:
            Sanitized title
        """
        sanitized = InputSanitizer.sanitize_text(title)

        # Truncate to maximum length
        if len(sanitized) > InputSanitizer.MAX_TITLE_LENGTH:
            logger.warning(f"Title truncated from {len(sanitized)} to {InputSanitizer.MAX_TITLE_LENGTH} characters")
            sanitized = sanitized[:InputSanitizer.MAX_TITLE_LENGTH]

        return sanitized

    @staticmethod
    def sanitize_topic(topic: str) -> str:
        """
        Sanitize story topic.

        Args:
            topic: The topic to sanitize

        Returns:
            Sanitized topic
        """
        sanitized = InputSanitizer.sanitize_text(topic)

        # Truncate to maximum length
        if len(sanitized) > InputSanitizer.MAX_TOPIC_LENGTH:
            logger.warning(f"Topic truncated from {len(sanitized)} to {InputSanitizer.MAX_TOPIC_LENGTH} characters")
            sanitized = sanitized[:InputSanitizer.MAX_TOPIC_LENGTH]

        return sanitized

    @staticmethod
    def sanitize_setting(setting: str) -> str:
        """
        Sanitize story setting.

        Args:
            setting: The setting to sanitize

        Returns:
            Sanitized setting
        """
        sanitized = InputSanitizer.sanitize_text(setting)

        # Truncate to maximum length
        if len(sanitized) > InputSanitizer.MAX_SETTING_LENGTH:
            logger.warning(f"Setting truncated from {len(sanitized)} to {InputSanitizer.MAX_SETTING_LENGTH} characters")
            sanitized = sanitized[:InputSanitizer.MAX_SETTING_LENGTH]

        return sanitized

    @staticmethod
    def sanitize_character(character: str) -> str:
        """
        Sanitize character description.

        Args:
            character: The character description to sanitize

        Returns:
            Sanitized character description
        """
        sanitized = InputSanitizer.sanitize_text(character)

        # Truncate to maximum length
        if len(sanitized) > InputSanitizer.MAX_CHARACTER_LENGTH:
            logger.warning(f"Character truncated from {len(sanitized)} to {InputSanitizer.MAX_CHARACTER_LENGTH} characters")
            sanitized = sanitized[:InputSanitizer.MAX_CHARACTER_LENGTH]

        return sanitized

    @staticmethod
    def check_injection_attempt(text: str) -> Optional[str]:
        """
        Check if text contains injection attack patterns.

        Args:
            text: The text to check

        Returns:
            Warning message if injection detected, None otherwise
        """
        # Check for SQL injection patterns
        if InputSanitizer.SQL_INJECTION_PATTERN.search(text):
            logger.warning(f"Potential SQL injection attempt detected: {text[:50]}...")
            return "Input contains potentially malicious SQL patterns"

        # Check for NoSQL injection patterns
        if InputSanitizer.NOSQL_INJECTION_PATTERN.search(text):
            logger.warning(f"Potential NoSQL injection attempt detected: {text[:50]}...")
            return "Input contains potentially malicious NoSQL patterns"

        return None

    @staticmethod
    def sanitize_all_inputs(
        title: Optional[str] = None,
        topic: Optional[str] = None,
        setting: Optional[str] = None,
        characters: Optional[list[str]] = None,
    ) -> dict:
        """
        Sanitize all story generation inputs at once.

        Args:
            title: Story title
            topic: Story topic
            setting: Story setting
            characters: List of character descriptions

        Returns:
            Dictionary with sanitized inputs

        Raises:
            ValueError: If injection attempt is detected
        """
        result = {}

        if title is not None:
            # Check for injection attempts
            injection_warning = InputSanitizer.check_injection_attempt(title)
            if injection_warning:
                raise ValueError(f"Title validation failed: {injection_warning}")
            result['title'] = InputSanitizer.sanitize_title(title)

        if topic is not None:
            injection_warning = InputSanitizer.check_injection_attempt(topic)
            if injection_warning:
                raise ValueError(f"Topic validation failed: {injection_warning}")
            result['topic'] = InputSanitizer.sanitize_topic(topic)

        if setting is not None:
            injection_warning = InputSanitizer.check_injection_attempt(setting)
            if injection_warning:
                raise ValueError(f"Setting validation failed: {injection_warning}")
            result['setting'] = InputSanitizer.sanitize_setting(setting)

        if characters is not None:
            sanitized_characters = []
            for char in characters:
                injection_warning = InputSanitizer.check_injection_attempt(char)
                if injection_warning:
                    raise ValueError(f"Character validation failed: {injection_warning}")
                sanitized_characters.append(InputSanitizer.sanitize_character(char))
            result['characters'] = sanitized_characters

        return result


# Singleton instance
sanitizer = InputSanitizer()
