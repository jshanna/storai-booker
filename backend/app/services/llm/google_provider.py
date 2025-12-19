"""Google Gemini LLM provider implementation."""
import json
import re
import asyncio
from typing import Type, Optional, Any
from pydantic import BaseModel, ValidationError
from google import genai
from google.genai.types import GenerateContentConfig
from loguru import logger

from app.services.llm.base import BaseLLMProvider


def repair_truncated_json(json_text: str) -> str:
    """
    Attempt to repair truncated JSON by closing unclosed brackets and strings.

    Args:
        json_text: Potentially truncated JSON string

    Returns:
        Repaired JSON string (may still be invalid)
    """
    # Track open brackets/braces
    stack = []
    in_string = False
    escape_next = False
    last_comma_pos = -1

    for i, char in enumerate(json_text):
        if escape_next:
            escape_next = False
            continue

        if char == '\\':
            escape_next = True
            continue

        if char == '"' and not escape_next:
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == ',':
            last_comma_pos = i
        elif char in '{[':
            stack.append(char)
        elif char == '}':
            if stack and stack[-1] == '{':
                stack.pop()
        elif char == ']':
            if stack and stack[-1] == '[':
                stack.pop()

    # If we ended inside a string, close it
    if in_string:
        json_text += '"'

    # Remove trailing comma if present (often causes issues)
    if last_comma_pos > 0 and last_comma_pos == len(json_text.rstrip()) - 1:
        json_text = json_text[:last_comma_pos] + json_text[last_comma_pos + 1:]

    # Close any unclosed brackets
    while stack:
        bracket = stack.pop()
        if bracket == '{':
            json_text += '}'
        elif bracket == '[':
            json_text += ']'

    return json_text


class GoogleGeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider using native google-genai SDK."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-pro-latest",
        temperature: float = 0.7,
        max_retries: int = 3,
    ):
        """
        Initialize Google Gemini provider.

        Args:
            api_key: Google API key
            model: Gemini model ID (e.g., 'gemini-1.5-pro-latest', 'gemini-1.5-flash-latest')
            temperature: Sampling temperature (0.0-1.0)
            max_retries: Maximum number of retry attempts on failure
        """
        super().__init__(api_key, model, temperature)
        self.max_retries = max_retries

    def get_client(self) -> genai.Client:
        """
        Get or create the Gemini client.

        Returns:
            genai.Client instance
        """
        if not self._client:
            self._client = genai.Client(api_key=self.api_key)
            logger.info(f"Initialized Gemini provider with model: {self.model}")

        return self._client

    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text from a prompt using Gemini.

        Args:
            prompt: Text prompt
            max_tokens: Maximum tokens to generate (optional)
            **kwargs: Additional parameters (e.g., stop sequences)

        Returns:
            Generated text string

        Raises:
            Exception: If generation fails after retries
        """
        try:
            client = self.get_client()

            # Build generation config
            config = GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=max_tokens if max_tokens else 8192,
            )

            # Generate
            logger.debug(f"Generating text with Gemini ({self.model})")

            # Use asyncio.to_thread since the SDK is sync
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=self.model,
                contents=prompt,
                config=config,
            )

            # Extract text content
            if not response.candidates or len(response.candidates) == 0:
                raise ValueError("No candidates returned from Gemini API")

            candidate = response.candidates[0]
            if not candidate.content or not candidate.content.parts:
                raise ValueError("No content in response from Gemini API")

            text = candidate.content.parts[0].text

            logger.debug(f"Generated {len(text)} characters")
            return text

        except Exception as e:
            logger.error(f"Gemini text generation failed: {e}")
            raise

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[BaseModel],
        **kwargs
    ) -> BaseModel:
        """
        Generate structured output matching a Pydantic model.

        Uses a two-step approach:
        1. Ask Gemini to generate JSON matching the schema
        2. Parse and validate with Pydantic

        Includes retry logic for JSON parsing failures with truncation repair.

        Args:
            prompt: Text prompt
            response_model: Pydantic model for output structure
            **kwargs: Additional parameters

        Returns:
            Instance of response_model

        Raises:
            ValidationError: If output doesn't match schema
            Exception: If generation fails after all retries
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                client = self.get_client()

                # Get JSON schema from Pydantic model
                schema = response_model.model_json_schema()

                # Build enhanced prompt with schema instructions
                schema_str = json.dumps(schema, indent=2)
                enhanced_prompt = f"""{prompt}

Please generate a JSON response matching this exact schema:

{schema_str}

Important:
- Output only valid JSON, no additional text
- All required fields must be present
- Use appropriate data types as specified in the schema
- Be creative and detailed in your responses
- Do not wrap the JSON in markdown code blocks
- Keep text content concise to avoid truncation"""

                # Build generation config with increased token limit
                config = GenerateContentConfig(
                    temperature=self.temperature,
                    max_output_tokens=16384,  # Increased from 8192 to reduce truncation
                )

                # Generate
                logger.debug(
                    f"Generating structured output for {response_model.__name__} "
                    f"(attempt {attempt + 1}/{self.max_retries})"
                )

                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=self.model,
                    contents=enhanced_prompt,
                    config=config,
                )

                # Extract JSON
                if not response.candidates or len(response.candidates) == 0:
                    # Check if content was blocked by safety filters
                    if hasattr(response, 'prompt_feedback'):
                        feedback = response.prompt_feedback
                        logger.warning(f"Gemini blocked request. Prompt feedback: {feedback}")
                        raise ValueError(f"Content blocked by Gemini safety filters: {feedback}")
                    raise ValueError("No candidates returned from Gemini API")

                candidate = response.candidates[0]
                if not candidate.content or not candidate.content.parts:
                    raise ValueError("No content in response from Gemini API")

                json_text = candidate.content.parts[0].text.strip()

                # Remove markdown code blocks if present
                if json_text.startswith("```json"):
                    json_text = json_text[7:]  # Remove ```json
                if json_text.startswith("```"):
                    json_text = json_text[3:]  # Remove ```
                if json_text.endswith("```"):
                    json_text = json_text[:-3]  # Remove trailing ```

                json_text = json_text.strip()

                # Sanitize control characters in JSON strings
                def sanitize_json_string(match):
                    s = match.group(0)
                    # Replace literal newlines, tabs, and carriage returns with escaped versions
                    s = s.replace('\n', '\\n')
                    s = s.replace('\r', '\\r')
                    s = s.replace('\t', '\\t')
                    # Remove other control characters (0x00-0x1F except those we just escaped)
                    s = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', s)
                    return s

                # Apply sanitization to string values in JSON
                json_text = re.sub(r'"([^"\\]*(\\.[^"\\]*)*)"', sanitize_json_string, json_text)

                # Parse JSON with repair fallback
                data = None
                try:
                    data = json.loads(json_text)
                except json.JSONDecodeError as e:
                    logger.warning(f"Initial JSON parse failed: {e}")
                    logger.debug(f"Attempting to repair truncated JSON...")

                    # Try to repair truncated JSON
                    repaired_json = repair_truncated_json(json_text)
                    try:
                        data = json.loads(repaired_json)
                        logger.info("Successfully repaired truncated JSON")
                    except json.JSONDecodeError as repair_error:
                        logger.error(f"JSON repair failed: {repair_error}")
                        logger.error(f"Raw response (first 500 chars): {json_text[:500]}")
                        logger.error(f"Raw response (last 200 chars): {json_text[-200:]}")
                        raise ValueError(f"Invalid JSON from Gemini (repair failed): {e}")

                # Validate with Pydantic
                try:
                    result = response_model.model_validate(data)
                    logger.debug(f"Successfully parsed {response_model.__name__}")
                    return result

                except ValidationError as e:
                    logger.error(f"Pydantic validation failed: {e}")
                    logger.error(f"Data: {json.dumps(data, indent=2)[:500]}")
                    raise

            except ValueError as e:
                # JSON parsing or content blocking errors - retry
                last_error = e
                error_msg = str(e).lower()

                # Don't retry safety blocks
                if "blocked" in error_msg or "safety" in error_msg:
                    raise

                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"Structured generation failed (attempt {attempt + 1}), "
                        f"retrying in {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Structured generation failed after {self.max_retries} attempts")
                    raise

            except Exception as e:
                logger.error(f"Gemini structured generation failed: {e}")
                raise

        # Should not reach here, but just in case
        if last_error:
            raise last_error
        raise RuntimeError("Structured generation failed unexpectedly")

    async def generate_with_system_message(
        self,
        system_message: str,
        user_message: str,
        **kwargs
    ) -> str:
        """
        Generate text with separate system and user messages.

        Args:
            system_message: System instructions
            user_message: User prompt
            **kwargs: Additional parameters

        Returns:
            Generated text

        Note:
            Gemini converts system messages to human messages internally
        """
        try:
            # Combine system and user messages
            combined_prompt = f"""System Instructions: {system_message}

User Request: {user_message}"""

            return await self.generate_text(combined_prompt, **kwargs)

        except Exception as e:
            logger.error(f"Gemini generation with system message failed: {e}")
            raise

    async def generate_vision_structured(
        self,
        prompt: str,
        image_bytes: bytes,
        response_model: Type[BaseModel],
        **kwargs
    ) -> BaseModel:
        """
        Generate structured output from text + image input (multimodal).

        Uses Gemini's vision capabilities to analyze an image and return
        structured feedback matching the provided Pydantic model.

        Args:
            prompt: Text instructions for analysis
            image_bytes: Image data as bytes (PNG/JPEG)
            response_model: Pydantic model class for output structure
            **kwargs: Additional parameters

        Returns:
            Instance of response_model with analysis results

        Raises:
            ValidationError: If output doesn't match schema
            Exception: If generation fails
        """
        from io import BytesIO
        from PIL import Image as PILImage

        last_error = None

        for attempt in range(self.max_retries):
            try:
                client = self.get_client()

                # Convert image bytes to PIL Image
                pil_image = PILImage.open(BytesIO(image_bytes))

                # Get JSON schema from Pydantic model
                schema = response_model.model_json_schema()

                # Build enhanced prompt with schema instructions
                schema_str = json.dumps(schema, indent=2)
                enhanced_prompt = f"""{prompt}

Please analyze the image and generate a JSON response matching this exact schema:

{schema_str}

Important:
- Output only valid JSON, no additional text
- All required fields must be present
- Scores should be integers from 1-10
- Provide specific, actionable feedback
- Do not wrap the JSON in markdown code blocks"""

                # Build generation config
                config = GenerateContentConfig(
                    temperature=self.temperature,
                    max_output_tokens=8192,
                )

                # Generate with multimodal input [image, text]
                logger.debug(
                    f"Generating vision-structured output for {response_model.__name__} "
                    f"(attempt {attempt + 1}/{self.max_retries})"
                )

                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=self.model,
                    contents=[pil_image, enhanced_prompt],
                    config=config,
                )

                # Extract JSON
                if not response.candidates or len(response.candidates) == 0:
                    if hasattr(response, 'prompt_feedback'):
                        feedback = response.prompt_feedback
                        logger.warning(f"Gemini blocked vision request. Prompt feedback: {feedback}")
                        raise ValueError(f"Content blocked by Gemini safety filters: {feedback}")
                    raise ValueError("No candidates returned from Gemini API")

                candidate = response.candidates[0]
                if not candidate.content or not candidate.content.parts:
                    raise ValueError("No content in response from Gemini API")

                json_text = candidate.content.parts[0].text.strip()

                # Remove markdown code blocks if present
                if json_text.startswith("```json"):
                    json_text = json_text[7:]
                if json_text.startswith("```"):
                    json_text = json_text[3:]
                if json_text.endswith("```"):
                    json_text = json_text[:-3]

                json_text = json_text.strip()

                # Sanitize control characters in JSON strings
                def sanitize_json_string(match):
                    s = match.group(0)
                    s = s.replace('\n', '\\n')
                    s = s.replace('\r', '\\r')
                    s = s.replace('\t', '\\t')
                    s = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', s)
                    return s

                json_text = re.sub(r'"([^"\\]*(\\.[^"\\]*)*)"', sanitize_json_string, json_text)

                # Parse JSON with repair fallback
                data = None
                try:
                    data = json.loads(json_text)
                except json.JSONDecodeError as e:
                    logger.warning(f"Initial JSON parse failed: {e}")
                    repaired_json = repair_truncated_json(json_text)
                    try:
                        data = json.loads(repaired_json)
                        logger.info("Successfully repaired truncated JSON")
                    except json.JSONDecodeError as repair_error:
                        logger.error(f"JSON repair failed: {repair_error}")
                        logger.error(f"Raw response (first 500 chars): {json_text[:500]}")
                        raise ValueError(f"Invalid JSON from Gemini vision: {e}")

                # Validate with Pydantic
                try:
                    result = response_model.model_validate(data)
                    logger.debug(f"Successfully parsed vision output {response_model.__name__}")
                    return result

                except ValidationError as e:
                    logger.error(f"Pydantic validation failed: {e}")
                    logger.error(f"Data: {json.dumps(data, indent=2)[:500]}")
                    raise

            except ValueError as e:
                last_error = e
                error_msg = str(e).lower()

                # Don't retry safety blocks
                if "blocked" in error_msg or "safety" in error_msg:
                    raise

                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"Vision-structured generation failed (attempt {attempt + 1}), "
                        f"retrying in {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Vision-structured generation failed after {self.max_retries} attempts")
                    raise

            except Exception as e:
                logger.error(f"Gemini vision-structured generation failed: {e}")
                raise

        if last_error:
            raise last_error
        raise RuntimeError("Vision-structured generation failed unexpectedly")
