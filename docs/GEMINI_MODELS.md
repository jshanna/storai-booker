# Google Gemini LLM Support

StorAI-Booker now supports Google Gemini as an LLM provider for story generation.

## Available Gemini Models

### Text Generation Models

**Gemini 2.0 Flash** (Newest - Experimental)
- Model ID: `gemini-2.0-flash-exp`
- Best for: Latest features, multimodal understanding
- Context window: Up to 1M tokens
- Features: Cutting-edge performance, fastest Gemini model yet
- Status: Experimental (December 2024)

**Gemini 1.5 Pro** (Recommended for Production)
- Model ID: `gemini-1.5-pro-latest` or `gemini-1.5-pro`
- Best for: Complex story generation with rich narratives
- Context window: Up to 2M tokens
- Features: Multimodal, long context, highest quality outputs
- Status: Stable, production-ready

**Gemini 1.5 Flash** (Recommended for Speed)
- Model ID: `gemini-1.5-flash-latest` or `gemini-1.5-flash`
- Best for: Fast story generation, cost-effective
- Context window: Up to 1M tokens
- Features: Optimized for speed and efficiency, 8x faster than 1.5 Pro
- Status: Stable, production-ready

**Gemini Experimental 1206**
- Model ID: `gemini-exp-1206`
- Best for: Testing experimental features
- Context window: Up to 2M tokens
- Features: Latest experimental capabilities
- Status: Experimental (December 2024)

**Note**: `gemini-pro` (legacy) is deprecated. Use `gemini-1.5-pro` or newer instead.

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
DEFAULT_TEXT_MODEL=gemini-1.5-pro-latest
```

### 3. Model Recommendations

For StorAI-Booker use cases:

**Best Quality (Production):**
```env
DEFAULT_LLM_PROVIDER=google
DEFAULT_TEXT_MODEL=gemini-1.5-pro-latest
```

**Fastest & Most Cost-Effective:**
```env
DEFAULT_LLM_PROVIDER=google
DEFAULT_TEXT_MODEL=gemini-1.5-flash-latest
```

**Cutting Edge (Experimental):**
```env
DEFAULT_LLM_PROVIDER=google
DEFAULT_TEXT_MODEL=gemini-2.0-flash-exp
```

**For Testing New Features:**
```env
DEFAULT_LLM_PROVIDER=google
DEFAULT_TEXT_MODEL=gemini-exp-1206
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

**Gemini 2.0 Flash** (Experimental - Free during preview)
- Input: Free while in preview
- Output: Free while in preview
- Free tier: 1,500 requests per day

**Gemini 1.5 Pro**
- Input: $1.25 per 1M tokens (≤128K), $2.50 per 1M tokens (>128K)
- Output: $5.00 per 1M tokens (≤128K), $10.00 per 1M tokens (>128K)
- Free tier: 2 requests per minute, 1,500 requests per day

**Gemini 1.5 Flash**
- Input: $0.075 per 1M tokens (≤128K), $0.15 per 1M tokens (>128K)
- Output: $0.30 per 1M tokens (≤128K), $0.60 per 1M tokens (>128K)
- Free tier: 15 requests per minute, 1,500 requests per day

**Gemini Experimental Models** (Free during preview)
- Free while in experimental phase
- Rate limits apply

See [Google AI Pricing](https://ai.google.dev/pricing) for current rates and free tier details.

## Example Usage

### Using Gemini 1.5 Pro (Latest)

```python
# This is handled automatically by LangChain integration
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-latest",
    google_api_key=settings.google_api_key,
    temperature=0.7,
)

response = llm.invoke("Generate a story about...")
```

### Using Gemini 2.0 Flash (Experimental)

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    google_api_key=settings.google_api_key,
    temperature=0.9,  # Higher temperature for creative story generation
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
    "text_model": "gemini-1.5-pro-latest"
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
- Try using `gemini-1.5-flash-latest` or `gemini-2.0-flash-exp` instead of `gemini-1.5-pro`
- Reduce context window if possible
- Use versioned model IDs (with `-latest`) for best performance

## Comparison with Other Providers

| Feature | Gemini 2.0 Flash | Gemini 1.5 Pro | GPT-4 Turbo | Claude 3.5 Sonnet |
|---------|------------------|----------------|-------------|-------------------|
| Context Window | 1M tokens | 2M tokens | 128k tokens | 200k tokens |
| Speed | Fastest | Medium | Medium | Fast |
| Cost (input ≤128K) | Free (preview) | $1.25/1M | $10/1M | $3/1M |
| Story Quality | Excellent | Excellent | Excellent | Excellent |
| Multimodal | Yes | Yes | Yes | Yes |
| Status | Experimental | Stable | Stable | Stable |

## Best Practices

1. **Start with Gemini 2.0 Flash for testing** - It's free during preview and very fast
2. **Use Gemini 1.5 Flash for cost-effective production** - Best price/performance
3. **Use Gemini 1.5 Pro for highest quality** - Best reasoning and long context
4. **Use `-latest` suffix for stable models** - Always get the newest stable version
5. **Set appropriate temperature** - 0.7-0.9 for creative stories
6. **Enable safety settings** - Use Google's built-in safety filters
7. **Monitor rate limits** - Free tier has generous limits (1,500 requests/day)
8. **Test experimental models** - Try `gemini-exp-1206` for cutting-edge features

## Links

- [Google AI Studio](https://makersuite.google.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [LangChain Google GenAI](https://python.langchain.com/docs/integrations/llms/google_ai)
- [Pricing](https://ai.google.dev/pricing)

---

**Last Updated**: 2025-12-14
**Supported Models**:
- Production: `gemini-1.5-pro-latest`, `gemini-1.5-flash-latest`
- Experimental: `gemini-2.0-flash-exp`, `gemini-exp-1206`
- Legacy: `gemini-1.5-pro`, `gemini-1.5-flash` (use `-latest` versions instead)
