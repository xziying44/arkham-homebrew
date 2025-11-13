# 🎴 Arkham Card Maker

---

<p align="center">
  <a href="https://github.com/xziying44/arkham-homebrew/releases">
    <img src="https://img.shields.io/github/v/release/xziying44/arkham-homebrew?include_prereleases&label=release" alt="release" />
  </a>
  <a href="https://github.com/xziying44/arkham-homebrew/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/xziying44/arkham-homebrew?label=license" alt="license: MIT" />
  </a>
  <img src="https://img.shields.io/badge/python-3.11%2B-blue?logo=python" alt="python 3.11+" />
  <img src="https://img.shields.io/badge/vue-3.x-42b883?logo=vue.js" alt="vue 3" />
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS-informational" alt="Platform: Windows | macOS" />
</p>

<p align="center">
  <a href="./README.md">简体中文</a> |
  <strong>English</strong>
</p>

**Custom Card Creation Tool for Arkham Horror LCG**

A visual card creation tool designed specifically for *Arkham Horror: The Card Game*. Easily create, edit, and export custom cards to craft your own terrifying adventure stories.

![Main Interface Preview](docs/screenshots/main-interface-preview.png)
*Main Interface Preview*

---

## ✨ Core Features

### 📝 Visual Card Editor
- **20+ Card Types Supported**: Investigator, Skill, Asset, Event, Weakness, Location, Agenda, Act, Enemy, and more
- **What-You-See-Is-What-You-Get**: Real-time preview of card effects with intuitive design adjustments
- **Smart Form System**: Automatically displays relevant fields based on card type, streamlining the editing workflow

### 🌐 Bilingual Support
- **Interface Languages**: Seamlessly switch between Chinese and English interfaces
- **Font System**: Automatically adapts Chinese and English fonts with mixed-script support
- **Rich Text Rendering**: Supports HTML-style tags (bold, italic, icons, line breaks, etc.)

### 🎨 Advanced Layout Controls
- **Illustration Transform Editor**: Precisely adjust image scale, crop, rotation, offset, and flip
- **Text Boundary Editor**: Customize text area position and size for complex layouts
- **Template System**: 305+ exquisite card templates covering all card types in the series

### 📦 Content Package Management
- **Project Organization**: Workspace-based file management supporting large-scale projects
- **Encounter Group System**: Easily manage card deck structures for scenarios and campaigns
- **Batch Operations**: Support for content package-level batch export and numbering

### 🎲 Multi-Format Export
- **Image Export**: PNG/JPG formats with customizable DPI and bleed settings
- **PDF Export**: Print-ready impositioned PDFs supporting A4, Letter, and other specifications
- **TTS Export**: One-click generation of Tabletop Simulator scripts and objects
- **ArkhamDB Export**: Export to ArkhamDB format for easy sharing

### 🚀 Professional Features
- **AI Bleed Processing**: Automatically generate bleed areas using LaMa or mirror algorithms
- **GitHub Image Hosting**: Integrated image hosting for quick card image sharing
- **Deck Builder**: Supports complex DeckOption systems for constructing optional decks
- **Upgrade Card System**: Investigator upgrade cards with Power Word script support

![Card Editor Interface](docs/screenshots/card-editor-interface.png)
*Card Editor Interface*

---

## 📥 Installation and Launch

### Windows

1. **Download the Application**
   Visit the [GitHub Releases](https://github.com/xziying44/arkham-homebrew/releases) page and download the latest version of `arkham-homebrew-windows-x64.zip`

2. **Extract the Files**
   Extract the ZIP file to any directory (recommended to avoid paths with non-ASCII characters)

3. **Run the Program**
   Double-click `Arkham Card Maker.exe` to launch the application

**Example directory layout (Windows release)**:

```text
Arkham Card Maker/
├── Arkham Card Maker.exe   # Main executable (double-click to run)
├── _internal/              # Runtime dependencies and resources
│   ├── fonts/              # Font resources
│   ├── images/             # Templates and artwork
│   ├── templates/          # TTS scripts and other templates
│   └── ...                 # Other internal dependencies
├── global_config.json      # Global configuration
├── recent_directories.json # Recent workspace history
└── logs/                   # Runtime logs
```

![Installation Directory Structure](docs/screenshots/installation-directory.png)
*Installation Directory Structure Example*

### macOS

1. **Download the Application**
   Visit the [GitHub Releases](https://github.com/xziying44/arkham-homebrew/releases) page and download based on your Mac chip type:
   - **Apple Silicon (M1/M2/M3)**: Download `Arkham-Card-Maker-macOS-arm64.dmg`
   - **Intel Chip**: Download `Arkham-Card-Maker-macOS-x86_64.dmg`

2. **Install the Application**
   - Double-click the `.dmg` file to open the installer
   - Drag "Arkham Card Maker" into the "Applications" folder

3. **First Launch**
   - Open the "Applications" folder and find "Arkham Card Maker"
   - Right-click and select "Open" (first launch requires authorization to run unsigned application)
   - Click "Open" in the security prompt that appears

![First Launch Screen](docs/screenshots/first-launch-screen.png)
*First Launch Screen*

---

## 🚀 Quick Start

### Step 1: Select Workspace

After the first launch, you need to select or create a workspace directory to store card files:

1. Click the **"Select Workspace Directory"** button
2. Choose an empty directory or create a new folder (recommended to create separate directories for each project)
3. The application will automatically load the workspace file tree

![Select Workspace](docs/screenshots/select-workspace.png)
*Select Workspace Directory*

### Step 2: Create Your First Card

1. **Create a Card File**
   Right-click a directory in the left file tree, select **"New File"**, and enter a filename (e.g., `my-card.card`)

2. **Choose Card Type**
   In the editing panel, select a type from the **"Card Type"** dropdown menu (e.g., "Skill", "Asset", etc.)

3. **Fill in Card Information**
   Complete the card fields according to the form prompts:
   - **Basic Information**: Card name, subtitle, traits, etc.
   - **Numerical Attributes**: Cost, skill icons, health/sanity, etc.
   - **Text Content**: Card description, rules text, flavor text, etc.
   - **Illustration Settings**: Upload or select illustration images

4. **Real-time Preview**
   The right preview panel displays card effects in real-time. Click **"Save"** when satisfied with your adjustments

![Quick Card Creation Flow](docs/screenshots/quick-card-creation-flow.png)
*Quick Card Creation Flow*

### Step 3: Advanced Editing (Optional)

For more precise layout control:

- **Illustration Layout Editor**: Click the **"Illustration Layout"** tab to adjust image scale, crop, rotation, and other parameters
- **Text Boundary Editor**: Click the **"Text Boundaries"** tab to customize text area position and size

### Step 4: Export Cards

After completing editing, you can export to multiple formats:

1. **Single Card Export**
   - Click the **"Export"** button in the top right corner of the card editor
   - Select format (PNG/JPG), size (Standard/Poker/Tarot, etc.), and bleed options
   - Click confirm, and the image will be saved to the corresponding directory in the workspace

2. **Batch Export**
   - Switch to the **"TTS Export"** page
   - Select content package or encounter group
   - Click **"Export TTS"** or **"Export PNP PDF"** to batch generate all cards

![Export Options Panel](docs/screenshots/export-options-panel.png)
*Export Options Panel*

---

## 📖 More Resources

- **User Guide**: [Complete User Manual](docs/user-guide-en.md) (detailed feature descriptions and advanced usage)
- **GitHub Repository**: [https://github.com/xziying44/arkham-homebrew](https://github.com/xziying44/arkham-homebrew)
- **Issue Tracker**: [Submit an Issue](https://github.com/xziying44/arkham-homebrew/issues)
- **Changelog**: [View Releases](https://github.com/xziying44/arkham-homebrew/releases)

---

## 🤝 Contributing and Feedback

If you encounter issues or have suggestions for improvements, please participate through:

- Submit an [Issue](https://github.com/xziying44/arkham-homebrew/issues) on GitHub
- Email the project maintainers
- Join discussions and feature suggestions

---

## 📄 License

This project is open source under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Thank you for using Arkham Card Maker! Enjoy your creative journey!** 🎉
