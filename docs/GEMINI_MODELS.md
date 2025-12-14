# Google Gemini LLM Support

StorAI-Booker now supports Google Gemini as an LLM provider for story generation.

## Available Gemini Models

### Text Generation Models

**Gemini 1.5 Pro** (Recommended)
- Model ID: `gemini-1.5-pro`
- Best for: Complex story generation with rich narratives
- Context window: Up to 1M tokens
- Features: Multimodal, long context, high reasoning capability

**Gemini 1.5 Flash**
- Model ID: `gemini-1.5-flash`
- Best for: Fast story generation, cost-effective
- Context window: Up to 1M tokens
- Features: Optimized for speed and efficiency

**Gemini Pro**
- Model ID: `gemini-pro`
- Best for: General-purpose story generation
- Context window: 32k tokens
- Features: Balanced performance and cost

### Image Generation

Google's Imagen is not yet integrated but planned for future support.

## Setup Instructions

### 1. Get Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 2. Configure Backend

Add your API key to `.env`:

```bash
GOOGLE_API_KEY=your-google-api-key-here
DEFAULT_LLM_PROVIDER=google
DEFAULT_TEXT_MODEL=gemini-1.5-pro
```

### 3. Model Recommendations

For StorAI-Booker use cases:

**Best Quality:**
```env
DEFAULT_LLM_PROVIDER=google
DEFAULT_TEXT_MODEL=gemini-1.5-pro
```

**Fastest Generation:**
```env
DEFAULT_LLM_PROVIDER=google
DEFAULT_TEXT_MODEL=gemini-1.5-flash
```

**Balanced:**
```env
DEFAULT_LLM_PROVIDER=google
DEFAULT_TEXT_MODEL=gemini-pro
```

## Features

### Supported Features
✅ Story outline generation
✅ Character description expansion
✅ Page text generation
✅ Dialogue writing (for comic books)
✅ Age-appropriate content filtering
✅ Multi-turn conversations

### Coming Soon
⏳ Imagen integration for illustrations
⏳ Gemini Vision for image understanding
⏳ Multimodal story generation

## Configuration in Settings

You can configure Gemini in the Settings view:

```json
{
  "primary_llm_provider": {
    "name": "google",
    "api_key": "your-api-key-here",
    "text_model": "gemini-1.5-pro",
    "image_model": "dall-e-3"
  }
}
```

Note: For image generation, you'll still need to use OpenAI's DALL-E or another provider until Imagen support is added.

## Pricing

Google Gemini pricing (as of December 2024):

**Gemini 1.5 Pro**
- Input: $0.00125 per 1K characters
- Output: $0.005 per 1K characters

**Gemini 1.5 Flash**
- Input: $0.00025 per 1K characters
- Output: $0.0005 per 1K characters

**Gemini Pro**
- Input: $0.00025 per 1K characters
- Output: $0.0005 per 1K characters

See [Google AI Pricing](https://ai.google.dev/pricing) for current rates.

## Example Usage

### Using Gemini 1.5 Pro

```python
# This is handled automatically by LangChain integration
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    google_api_key=settings.google_api_key,
    temperature=0.7,
)

response = llm.invoke("Generate a story about...")
```

### Fallback Configuration

You can set Gemini as primary with OpenAI as fallback:

```json
{
  "primary_llm_provider": {
    "name": "google",
    "api_key": "google-api-key",
    "text_model": "gemini-1.5-pro"
  },
  "fallback_llm_provider": {
    "name": "openai",
    "api_key": "openai-api-key",
    "text_model": "gpt-4-turbo-preview"
  }
}
```

## Troubleshooting

### Error: "Invalid API Key"
- Verify your API key is correct
- Check that API is enabled in Google Cloud Console

### Error: "Quota exceeded"
- Check your usage limits in Google AI Studio
- Consider using Gemini Flash for faster/cheaper generation

### Slow response times
- Try using `gemini-1.5-flash` instead of `gemini-1.5-pro`
- Reduce context window if possible

## Comparison with Other Providers

| Feature | Gemini 1.5 Pro | GPT-4 Turbo | Claude 3 Opus |
|---------|----------------|-------------|---------------|
| Context Window | 1M tokens | 128k tokens | 200k tokens |
| Speed | Medium | Medium | Fast |
| Cost (input) | $1.25/1M | $10/1M | $15/1M |
| Story Quality | Excellent | Excellent | Excellent |
| Multimodal | Yes | Yes | Yes |

## Best Practices

1. **Use Gemini 1.5 Flash for initial testing** - It's fast and cheap
2. **Use Gemini 1.5 Pro for production** - Better quality and reasoning
3. **Set appropriate temperature** - 0.7-0.9 for creative stories
4. **Enable safety settings** - Use Google's built-in safety filters
5. **Monitor costs** - Track API usage in Google AI Studio

## Links

- [Google AI Studio](https://makersuite.google.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [LangChain Google GenAI](https://python.langchain.com/docs/integrations/llms/google_ai)
- [Pricing](https://ai.google.dev/pricing)

---

**Last Updated**: 2025-12-14
**Supported Models**: gemini-1.5-pro, gemini-1.5-flash, gemini-pro
