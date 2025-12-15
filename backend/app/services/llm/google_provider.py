"""Google Gemini LLM provider implementation."""
import json
from typing import Type, Optional, Any
from pydantic import BaseModel, ValidationError
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from loguru import logger

from app.services.llm.base import BaseLLMProvider


class GoogleGeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider using LangChain."""

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

    def get_client(self) -> ChatGoogleGenerativeAI:
        """
        Get or create the Gemini client.

        Returns:
            ChatGoogleGenerativeAI instance
        """
        if not self._client:
            self._client = ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=self.api_key,
                temperature=self.temperature,
                max_retries=self.max_retries,
                convert_system_message_to_human=True,  # Gemini compatibility
            )
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

            # Build message
            message = HumanMessage(content=prompt)

            # Add max_output_tokens if specified
            invoke_kwargs = {}
            if max_tokens:
                invoke_kwargs["max_output_tokens"] = max_tokens

            # Merge additional kwargs
            invoke_kwargs.update(kwargs)

            # Generate
            logger.debug(f"Generating text with Gemini ({self.model})")
            response = await client.ainvoke([message], **invoke_kwargs)

            # Extract text content
            text = response.content

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

        Args:
            prompt: Text prompt
            response_model: Pydantic model for output structure
            **kwargs: Additional parameters

        Returns:
            Instance of response_model

        Raises:
            ValidationError: If output doesn't match schema
            Exception: If generation fails
        """
        try:
            client = self.get_client()

            # Get JSON schema from Pydantic model
            schema = response_model.model_json_schema()

            # Build system message with schema instructions
            system_msg = (
                "You are a helpful assistant that generates valid JSON responses. "
                "Your output must be valid JSON that matches the provided schema exactly. "
                "Do not include any explanatory text, only output the JSON object."
            )

            # Build human message with prompt and schema
            schema_str = json.dumps(schema, indent=2)
            human_msg = f"""{prompt}

Please generate a JSON response matching this exact schema:

{schema_str}

Important:
- Output only valid JSON, no additional text
- All required fields must be present
- Use appropriate data types as specified in the schema
- Be creative and detailed in your responses"""

            # Generate
            logger.debug(f"Generating structured output for {response_model.__name__}")
            response = await client.ainvoke([
                SystemMessage(content=system_msg),
                HumanMessage(content=human_msg)
            ])

            # Extract and clean JSON
            json_text = response.content.strip()

            # Remove markdown code blocks if present
            if json_text.startswith("```json"):
                json_text = json_text[7:]  # Remove ```json
            if json_text.startswith("```"):
                json_text = json_text[3:]  # Remove ```
            if json_text.endswith("```"):
                json_text = json_text[:-3]  # Remove trailing ```

            json_text = json_text.strip()

            # Parse JSON
            try:
                data = json.loads(json_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}")
                logger.error(f"Raw response: {json_text[:500]}")
                raise ValueError(f"Invalid JSON from Gemini: {e}")

            # Validate with Pydantic
            try:
                result = response_model.model_validate(data)
                logger.debug(f"Successfully parsed {response_model.__name__}")
                return result

            except ValidationError as e:
                logger.error(f"Pydantic validation failed: {e}")
                logger.error(f"Data: {json.dumps(data, indent=2)[:500]}")
                raise

        except Exception as e:
            logger.error(f"Gemini structured generation failed: {e}")
            raise

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
            client = self.get_client()

            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=user_message)
            ]

            logger.debug(f"Generating with system message using {self.model}")
            response = await client.ainvoke(messages, **kwargs)

            return response.content

        except Exception as e:
            logger.error(f"Gemini generation with system message failed: {e}")
            raise
