# StorAI-Booker Application Specification

## 1. Overview

StorAI-Booker is a web-based application that leverages Large Language Models (LLMs) to generate personalized, illustrated storybooks for children. The application provides an intuitive interface for creating custom stories, managing a library of generated books, and configuring generation parameters.

### 1.1 Purpose
Enable users to generate age-appropriate, illustrated storybooks and comic books tailored to specific audiences, topics, and creative preferences using AI-powered generation.

### 1.2 Key Capabilities
- Custom storybook and comic book generation based on user inputs
- Multi-page illustrated narratives with consistent characters and style
- Support for both traditional storybook and comic book formats
- Library management for generated storybooks
- Configurable LLM providers and generation settings
- Story coherence validation and error correction

## 2. Application Views

### 2.1 Generation View

The primary interface for creating new storybooks.

#### Input Fields
- **Audience Information**
  - Age (numeric or range)
  - Gender (optional, for personalization)

- **Story Parameters**
  - Topic (text input)
  - Setting (text input, e.g., "enchanted forest", "outer space")

- **Format & Style**
  - Story Format (dropdown: "Traditional Storybook" or "Comic Book")
  - Illustration Style (dropdown/text, e.g., "watercolor", "cartoon", "realistic", "manga", "superhero comic", "graphic novel")

- **Character Definitions**
  - User-described characters (multi-line text or structured form)
  - Support for multiple character entries

- **Book Configuration**
  - Number of Pages (numeric input)
  - Panels per Page (numeric input, 1-9, only visible for Comic Book format)

#### Actions
- **Generate Story** - Initiates the story generation flow
- **Save Draft** - Saves current inputs for later use
- **Load Template** - Pre-populate from library entry

### 2.2 Library View

Displays all previously generated storybooks.

#### Display Components
- Grid or list view of storybooks
- Each entry shows:
  - Story title
  - Cover illustration (first page or generated cover)
  - Format badge (Storybook or Comic Book)
  - Generation date
  - Audience age
  - Page count
  - Topic/setting summary

#### Actions per Storybook
- **View** - Opens the storybook in reader mode
- **Regenerate Similar** - Loads the generation view with the original inputs pre-populated
- **Delete** - Removes the storybook from library
- **Export** (optional) - Download as PDF or other format

#### Reader Mode
- Full-screen or modal view
- Page-by-page navigation
- **Traditional Storybook Display**:
  - Single illustration with accompanying text below/overlay
- **Comic Book Display**:
  - Panel-based layout (grid or custom arrangement)
  - Speech bubbles and dialogue integrated into panels
  - Sound effect text (POW!, BOOM!, etc.) for action scenes
- Reading controls (previous, next, jump to page)
- Format-adaptive layout (automatically adjusts based on story format)

### 2.3 Settings View

Configuration interface for application behavior and integrations.

#### Story Generation Settings
- **Age Range Restrictions**
  - Minimum age (default: 3)
  - Maximum age (default: 12)
  - Enforcement toggle

- **Content Filters**
  - NSFW toggle (default: off)
  - Violence level filter
  - Scary content filter

- **Generation Limits**
  - Retry limit for coherence corrections (default: 3)
  - Maximum concurrent page generations
  - Timeout settings

- **Quality Settings**
  - Coherence check strictness
  - Illustration prompt detail level

#### LLM Provider Settings
- **Provider Configuration**
  - Primary provider selection (OpenAI, Anthropic, local, etc.)
  - Fallback provider (optional)

- **API Credentials**
  - API keys per provider (secure input)
  - API endpoint URLs (for custom/local providers)

- **Model Selection**
  - Text generation model
  - Image generation model
  - Coordination/orchestration model

#### Application Settings
- Theme (light/dark mode)
- Default illustration style
- Default page count
- Auto-save preferences

## 3. Story Generation Flow

### 3.1 High-Level Process

```
User Input → Initial Generation → Concurrent Page Generation → Assembly & Validation → Output
```

The generation flow adapts based on the selected format (Traditional Storybook or Comic Book), with comic books requiring additional panel layout planning and dialogue formatting.

### 3.2 Detailed Flow

#### Phase 1: Initial Generation (Coordinating Agent)
The coordinating agent processes form inputs to create:

1. **Character Descriptions**
   - Expands user-provided character details
   - Ensures consistency in character attributes
   - Generates physical descriptions, personality traits

2. **Character Relation Map** (if multiple characters)
   - Defines relationships between characters
   - Establishes interaction patterns

3. **Story Outline**
   - Overall narrative arc
   - Beginning, middle, end structure
   - Key plot points
   - Moral or lesson (age-appropriate)

4. **Page Outlines**
   - Breakdown of story into N pages (per user input)
   - Scene description for each page
   - Key actions/events per page
   - Character appearances per page
   - **Comic Book Format Only**:
     - Panel layout per page (e.g., "2x2 grid", "horizontal strip", "splash page")
     - Panel-by-panel action breakdown
     - Dialogue and speech bubble placement
     - Sound effects placement

5. **Illustration Style Guide**
   - Detailed style parameters based on user selection
   - Consistency guidelines for visual elements
   - Color palette suggestions
   - **Comic Book Format Only**:
     - Panel border style (clean, rough, borderless)
     - Speech bubble style
     - Font recommendations for dialogue and sound effects

#### Phase 2: Concurrent Page Generation (Page Agents)
Multiple agents work in parallel to generate each page:

**For Traditional Storybook Pages:**
- **Input**: Page outline, character descriptions, illustration style guide, story context
- **Output**:
  - Page text (narrative for that page)
  - Illustration prompt (detailed prompt for image generation)

**For Comic Book Pages:**
- **Input**: Page outline, panel layout, character descriptions, illustration style guide, story context
- **Output (per panel)**:
  - Dialogue text with speaker attribution
  - Action description for the panel
  - Illustration prompt for the panel image
  - Speech bubble positions and types (round, jagged, thought, narration box)
  - Sound effects (if applicable)
- **Output (page level)**:
  - Panel arrangement instructions
  - Transition flow between panels

**Agent Responsibilities:**
- Maintain narrative consistency with story outline
- Use age-appropriate vocabulary and sentence structure
- Ensure character consistency
- Match tone and style across pages
- **Traditional Storybook**: Generate detailed illustration prompts that:
  - Specify characters in scene
  - Describe setting and mood
  - Include style directives
  - Maintain visual consistency
- **Comic Book**: Generate panel-specific content that:
  - Creates dynamic, visually interesting compositions per panel
  - Balances dialogue and action
  - Uses "show don't tell" principles
  - Maintains reading flow (left-to-right, top-to-bottom)
  - Incorporates dramatic angles and perspectives
  - Includes expressive character poses and facial expressions

#### Phase 3: Assembly and Validation (Coordinating Agent)
Once all page agents complete:

1. **Assembly**
   - Collect all page texts and illustration prompts
   - Order sequentially
   - Generate title (if not provided)

2. **Coherence Check**
   - Verify narrative flow
   - Check character consistency
   - Validate age-appropriateness
   - Ensure illustration prompt consistency

3. **Error Correction**
   - Identify inconsistent pages
   - Regenerate problematic pages (up to retry limit)
   - Re-validate after regeneration

4. **Finalization**
   - Mark generation as complete
   - Store in database
   - Generate thumbnail/cover
   - Add to library

#### Phase 4: Illustration Generation

**Traditional Storybook:**
- Process illustration prompts through image generation model
- Apply illustrations to corresponding pages
- Store final illustrated storybook

**Comic Book:**
- Process panel illustration prompts through image generation model (multiple per page)
- Composite panels into page layouts with borders and gutters
- Overlay speech bubbles and text using SVG or image manipulation
- Position sound effects text
- Apply any special effects (motion lines, impact stars, etc.)
- Store final illustrated comic book

### 3.3 Agent Architecture

```
Coordinating Agent
    ├─ Initial Story Planning
    ├─ Spawn Page Generation Agents (parallel)
    │   ├─ Page Agent 1
    │   ├─ Page Agent 2
    │   └─ Page Agent N
    ├─ Assembly & Validation
    └─ Error Correction & Retry Logic
```

### 3.4 Error Handling

- **Retry Mechanism**: Configurable retry limit (default: 3 attempts)
- **Failure Modes**:
  - Individual page generation failure → retry that page
  - Coherence validation failure → regenerate flagged pages
  - API timeout → retry with exponential backoff
  - Quota exceeded → notify user, save partial progress
- **Runaway Prevention**: Hard limit on total LLM calls per generation

## 4. Data Models

### 4.1 Storybook
```typescript
interface Storybook {
  id: string;
  title: string;
  createdAt: timestamp;
  generationInputs: GenerationInputs;
  metadata: StoryMetadata;
  pages: Page[];
  status: 'generating' | 'complete' | 'error';
  errorMessage?: string;
}
```

### 4.2 Generation Inputs
```typescript
interface GenerationInputs {
  audience: {
    age: number;
    gender?: string;
  };
  topic: string;
  setting: string;
  format: 'storybook' | 'comic';  // Story format
  illustrationStyle: string;
  characters: string[];  // User-described characters
  pageCount: number;
  panelsPerPage?: number;  // Only for comic format (1-9)
}
```

### 4.3 Story Metadata
```typescript
interface StoryMetadata {
  characterDescriptions: CharacterDescription[];
  characterRelations?: string;  // Relationship map
  storyOutline: string;
  pageOutlines: string[];
  illustrationStyleGuide: string;
}
```

### 4.4 Character Description
```typescript
interface CharacterDescription {
  name: string;
  physicalDescription: string;
  personality: string;
  role: string;  // protagonist, sidekick, etc.
}
```

### 4.5 Page
```typescript
interface Page {
  pageNumber: number;
  text: string;  // For storybook format
  illustrationPrompt: string;  // For storybook format
  illustrationUrl?: string;  // For storybook format
  panels?: ComicPanel[];  // For comic format
  layout?: string;  // Panel layout description for comic format
  generationAttempts: number;
  validated: boolean;
}

interface ComicPanel {
  panelNumber: number;
  dialogue: DialogueElement[];
  action: string;  // Description of what's happening in the panel
  illustrationPrompt: string;
  illustrationUrl?: string;
  soundEffects?: SoundEffect[];
}

interface DialogueElement {
  speaker: string;  // Character name or "narrator"
  text: string;
  bubbleType: 'speech' | 'thought' | 'narration' | 'shout' | 'whisper';
  position?: { x: number; y: number };  // Relative position in panel
}

interface SoundEffect {
  text: string;  // e.g., "POW!", "CRASH!", "WHOOSH!"
  position?: { x: number; y: number };
  style?: string;  // Font style or effect type
}
```

### 4.6 Settings
```typescript
interface AppSettings {
  storyGeneration: {
    ageRange: { min: number; max: number; enforce: boolean };
    nsfwFilter: boolean;
    retryLimit: number;
    maxConcurrentPages: number;
  };
  llmProviders: {
    primary: ProviderConfig;
    fallback?: ProviderConfig;
  };
  defaults: {
    format: 'storybook' | 'comic';
    illustrationStyle: string;
    pageCount: number;
    panelsPerPage: number;  // Default for comic format
  };
}

interface ProviderConfig {
  name: string;
  apiKey: string;
  endpoint?: string;
  models: {
    text: string;
    image: string;
    coordinator: string;
  };
}
```

## 5. Technical Requirements

### 5.1 Frontend
- **Framework**: Modern web framework (React, Vue, or Svelte)
- **State Management**: For generation progress tracking
- **Responsive Design**: Desktop and tablet support
- **Real-time Updates**: WebSocket or polling for generation progress
- **Comic Book Rendering**:
  - SVG or Canvas-based panel composition
  - Speech bubble rendering library or custom component
  - Text overlay capabilities for dialogue and sound effects
  - Dynamic panel layout engine

### 5.2 Backend
- **API Server**: RESTful or GraphQL API
- **Agent Orchestration**: Multi-agent coordination system
- **Queue System**: For managing concurrent page and panel generations
- **Database**: Persistent storage for storybooks and settings
- **Image Processing**: For comic book panel composition and text overlay
  - Image manipulation library (Sharp, Pillow, ImageMagick)
  - Text rendering with custom fonts
  - Panel border and gutter generation

### 5.3 LLM Integration
- **Text Generation**: OpenAI GPT-4, Claude, or compatible
- **Image Generation**: DALL-E, Stable Diffusion, or Midjourney API
- **Agent Framework**: LangChain, AutoGen, or custom implementation

### 5.4 Storage
- **Database**: PostgreSQL, MongoDB, or similar
- **File Storage**: S3-compatible storage for illustrations
- **Caching**: Redis for API responses and generation state

## 6. API Endpoints

### 6.1 Story Generation
- `POST /api/stories/generate` - Initiate story generation
- `GET /api/stories/:id/status` - Check generation progress
- `GET /api/stories/:id` - Retrieve complete storybook
- `DELETE /api/stories/:id` - Delete storybook

### 6.2 Library
- `GET /api/stories` - List all storybooks
- `GET /api/stories/:id/pages/:pageNumber` - Get specific page

### 6.3 Settings
- `GET /api/settings` - Retrieve current settings
- `PUT /api/settings` - Update settings
- `POST /api/settings/validate-api-key` - Test LLM provider connection

## 7. User Experience Flow

### 7.1 Story Creation Journey
1. User navigates to Generation View
2. Fills out form with story parameters
3. Clicks "Generate Story"
4. Progress indicator shows:
   - Initial planning (10%)
   - Page generation (10-80%, incremental per page)
   - Validation and assembly (80-90%)
   - Illustration generation (90-100%)
5. On completion, redirect to Reader Mode or Library
6. User can view, save, or regenerate

### 7.2 Library Browsing
1. User navigates to Library View
2. Browses generated storybooks
3. Clicks "View" to read
4. In Reader Mode:
   - Swipe or click through pages
   - View illustrations and text
   - Exit back to Library
5. Clicks "Regenerate Similar" to create variations

## 8. Security & Privacy

### 8.1 API Key Management
- API keys encrypted at rest
- Never exposed in client-side code
- Secure transmission (HTTPS only)

### 8.2 Content Safety
- NSFW filter enabled by default
- Age-appropriate content validation
- User content moderation for character descriptions

### 8.3 Data Privacy
- User-generated content stored securely
- Optional export and deletion
- No sharing without explicit consent

## 9. Future Enhancements (Optional)

- Multi-language support
- Text-to-speech for reading aloud (with voice acting for comic book dialogue)
- Collaborative story creation
- Story templates and themes
- Print-on-demand integration
- User accounts and cloud sync
- Sharing and social features
- Custom illustration model fine-tuning
- Voice input for character descriptions
- Accessibility features (screen reader support, high contrast)
- **Comic Book Specific**:
  - Advanced panel layouts (splash pages, inset panels, irregular shapes)
  - Animated panel transitions for digital reading
  - Custom speech bubble styles and tails
  - Lettering font customization
  - Sound effect library and auto-placement
  - Page-to-page continuity checker for visual consistency
  - Motion blur and speed lines for action scenes
  - Manga/right-to-left reading mode support

## 10. Success Metrics

- Story generation success rate (target: >95%)
- Average generation time (target: <5 minutes)
- User satisfaction with story quality
- Coherence validation pass rate
- API cost per story
- User retention and library growth

---

**Document Version**: 1.1
**Last Updated**: 2025-12-14
**Status**: Updated Specification

## Revision History
- **v1.1** (2025-12-14): Added comic book format support with panel-based generation, dialogue systems, and enhanced data models
- **v1.0** (2025-12-14): Initial specification for traditional storybook generation
