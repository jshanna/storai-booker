# StorAI-Booker Features Guide

A comprehensive guide to all features in StorAI-Booker.

## Table of Contents

- [Getting Started](#getting-started)
- [Creating Stories](#creating-stories)
- [Your Library](#your-library)
- [Reading Stories](#reading-stories)
- [Sharing Stories](#sharing-stories)
- [Discovering Stories](#discovering-stories)
- [Exporting Stories](#exporting-stories)
- [Account Management](#account-management)
- [Settings](#settings)

## Getting Started

### Creating an Account

1. Click **Sign up** in the header
2. Choose your sign-up method:
   - **Email/Password**: Enter your details and create a password
   - **Google**: Sign in with your Google account
   - **GitHub**: Sign in with your GitHub account
3. You'll be automatically logged in after registration

### Navigating the App

The header provides quick access to all sections:

- **Home** - Landing page with app information
- **Browse** - Discover public stories from other users
- **Generate** - Create new stories
- **Library** - View your personal story collection
- **Saved** - View stories you've bookmarked
- **Settings** - Configure app settings and API keys

## Creating Stories

### Starting a New Story

1. Navigate to **Generate** from the header
2. Fill out the story creation form:

#### Basic Information
- **Title**: Give your story a name (or leave blank for AI-generated title)
- **Format**: Choose between:
  - **Storybook**: Traditional illustrated story with text and pictures
  - **Comic Book**: Panel-based format with dialogue and action

#### Audience
- **Target Age**: Select the age range (3-12 years)
- **Theme**: Optional theme like adventure, friendship, or fantasy

#### Characters
- **Main Character**: Describe your protagonist
- **Supporting Characters**: Add additional characters (optional)
- Click **Add Character** to include more characters

#### Story Details
- **Setting**: Where does the story take place?
- **Plot Points**: Key events you want in the story (optional)
- **Page Count**: Number of pages (5-20)
- **Illustration Style**: Choose from watercolor, digital art, cartoon, anime, etc.

### Using Templates

1. Click **Use Template** at the top of the form
2. Browse templates by category (Adventure, Fantasy, Educational, etc.)
3. Select a template to pre-fill the form
4. Customize any fields as desired

### Generation Progress

After clicking **Generate**:

1. A progress dialog shows the current status
2. Watch as pages are generated one by one
3. Generation typically takes 3-5 minutes for a 10-page story
4. You can close the dialog - generation continues in the background
5. Check progress anytime in your Library

## Your Library

### Viewing Your Stories

1. Navigate to **Library** from the header
2. Your stories appear in a grid layout
3. Each card shows:
   - Cover image (or placeholder)
   - Title
   - Format badge (Storybook/Comic)
   - Status (Generating, Complete, Error)
   - Creation date

### Filtering Stories

Use the filters at the top:

- **Search**: Find stories by title
- **Format**: Filter by Storybook or Comic
- **Status**: Filter by Generating, Complete, or Error
- **Sharing**: Filter by Shared, Not Shared, or All

### Managing Stories

Click the **...** menu on any story card for options:

- **Read Story**: Open the story reader
- **Export**: Download in various formats
- **Share**: Enable/disable public sharing
- **View Artifacts**: See character sheets and generation prompts
- **Delete**: Remove the story permanently

## Reading Stories

### Story Reader

Click **Read Story** on any completed story to open the reader:

- **Full-screen mode** for immersive reading
- **Page navigation** with arrows or swipe gestures
- **Page indicator** shows current position
- **Keyboard shortcuts**: Arrow keys for navigation

### Storybook Format

- Large illustration at the top
- Story text below the image
- Smooth page transitions

### Comic Book Format

- Full-page comic panels
- Integrated dialogue and speech bubbles
- Sound effects rendered on the page

### Reader Controls

- **Previous/Next** buttons to navigate
- **Page number** display
- **Exit** button to return to Library
- **Keyboard**: Left/Right arrows, Escape to exit

## Sharing Stories

### Enabling Sharing

1. Open your story's **...** menu
2. Click **Share**
3. Toggle **Public sharing** on
4. Copy the share link

### Share Link Features

When sharing is enabled:
- Anyone with the link can view the story
- No account required to view
- Viewers can leave comments
- You can disable sharing anytime

### Managing Comments

On shared stories, you can:
- View all comments in the story reader
- Delete inappropriate comments (story owner only)
- Comments show author name and timestamp

### Disabling Sharing

1. Open the Share dialog
2. Toggle **Public sharing** off
3. The share link will no longer work
4. Existing comments are preserved (reappear if re-shared)

## Discovering Stories

### Browse Page

Navigate to **Browse** to discover public stories:

1. See stories shared by all users
2. Filter by format (Storybook/Comic)
3. View story details: title, author, page count
4. Click any story to read it

### Saving Stories

To save a story for later:

1. Click the **bookmark** icon on any story card
2. The icon fills in to show it's saved
3. Access saved stories from **Saved** in the header

### Saved Stories Page

Navigate to **Saved** to see your bookmarked stories:

- All stories you've saved appear here
- Click the bookmark icon to remove from saved
- Click any story to read it

## Exporting Stories

### Available Formats

Click **Export** in the story menu to download:

| Format | Best For |
|--------|----------|
| **PDF** | Printing, reading on any device |
| **EPUB** | E-readers (Kindle, Kobo, Apple Books) |
| **CBZ** | Comic reader apps |
| **Images** | Individual page images (ZIP) |

### How to Export

1. Open the story's **...** menu
2. Click **Export**
3. Choose your preferred format
4. Download starts automatically

### Export Notes

- PDF includes all pages with proper formatting
- EPUB works with most e-reader software
- CBZ is the standard comic book archive format
- Images ZIP contains all illustrations at full resolution

## Account Management

### Profile Page

Access your profile from the user menu (top right):

- View and edit your display name
- Update your avatar
- See your email address
- Manage linked accounts (Google, GitHub)

### Changing Password

1. Go to **Profile**
2. Click **Change Password**
3. Enter your current password
4. Enter and confirm your new password
5. Click **Update Password**

### Linking OAuth Accounts

Connect additional login methods:

1. Go to **Profile**
2. Under **Linked Accounts**, click **Link** next to Google or GitHub
3. Complete the OAuth flow
4. You can now log in with that account

### Unlinking Accounts

1. Go to **Profile**
2. Click **Unlink** next to the account
3. Confirm the action

Note: You must keep at least one login method (password or OAuth).

## Settings

### Accessing Settings

Navigate to **Settings** from the header (requires login).

### LLM Provider Settings

Configure your AI provider:

- **Provider**: Select Google Gemini (default)
- **API Key**: Enter your Google API key
- **Text Model**: Model for story text generation
- **Image Model**: Model for illustration generation

### Generation Defaults

Set default values for new stories:

- **Default Format**: Storybook or Comic
- **Default Page Count**: 5-20 pages
- **Default Illustration Style**: Your preferred art style

### Content Filters

Configure content safety:

- **Age Range**: Minimum and maximum target age
- **NSFW Filter**: Keep enabled for child-safe content
- **Violence Filter**: Adjust sensitivity

### Testing Your Configuration

1. Enter your API key
2. Click **Test Connection**
3. A success message confirms the key works

## Tips and Best Practices

### Better Story Generation

- **Be specific** with character descriptions
- **Include personality traits** not just appearance
- **Set clear themes** for more focused stories
- **Use templates** as starting points
- **Shorter stories** (5-10 pages) generate faster

### Character Consistency

- The system generates character reference sheets
- View them in **View Artifacts**
- More detailed descriptions = better consistency

### Handling Errors

If generation fails:
- Check your API key in Settings
- Try a simpler story (fewer pages)
- Adjust content if safety filters triggered
- Check the error message for details

### Performance Tips

- Generation takes 3-5 minutes for 10 pages
- Keep the tab open or check Library for status
- Stories are saved automatically
- You can queue multiple generations

## Keyboard Shortcuts

### Story Reader
| Key | Action |
|-----|--------|
| `←` | Previous page |
| `→` | Next page |
| `Esc` | Exit reader |

### Navigation
| Key | Action |
|-----|--------|
| `/` | Focus search (Library) |

## FAQ

### How long does story generation take?

Typically 3-5 minutes for a 10-page story. Comic books may take slightly longer due to more complex image generation.

### Can I edit a generated story?

Currently, stories cannot be edited after generation. You can delete and regenerate with different parameters.

### Why did my story fail to generate?

Common reasons:
- Invalid or expired API key
- Content safety filters triggered
- Rate limits on your API account
- Network connectivity issues

### Are my stories private?

Yes, by default all stories are private. Only you can see them. You must explicitly enable sharing to make a story public.

### How do I get a Google API key?

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy it to your Settings page

### What's the cost of generating stories?

Using Google Gemini, approximately $0.65-0.95 per 10-page story. Costs vary based on page count and complexity.

---

For technical issues, see the [Troubleshooting Guide](TROUBLESHOOTING.md).
