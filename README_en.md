[简体中文](./README.md) | **English**
# Arkham Homebrew Card Maker

A Flask-based tool for automatically generating custom cards for games like Arkham Horror. It leverages OpenAI to create card data from prompts and renders it into high-quality, beautifully designed card images.

## Features

- 🖼️ **Visual Card Design UI**: An intuitive web interface for designing and generating cards.
- 🤖 **AI-Powered Content**: Integrates with OpenAI to intelligently generate card names, text, and attributes.
- 🎨 **Highly Customizable**: Supports custom fonts, image assets, and style templates to match your vision.
- 📦 **Multiple Card Types**: Built-in support for various card templates, including:
    - Investigator Cards
    - Skill Cards
    - Asset Cards
    - Event Cards
    - Weakness Cards
    - Upgraded Cards
- 🌐 **Cross-Platform Desktop App**: Packaged as a simple web-based desktop application using Pywebview.

## Quick Start

### Standalone Executable (Windows)

The easiest way to get started without any installation.

1.  Go to the [Releases Page](https://github.com/xziying44/arkham-homebrew/releases).
2.  Download the latest version of `arkham-homebrew-windows-x64.zip`.
3.  Unzip the file to any directory.
4.  Double-click `Arkham Card Maker.exe` to run the application.

#### Directory Structure

After unzipping, your directory should look like this. Please ensure all required directories are present.

```
.
├── Arkham Card Maker.exe    # Main application
├── _internal/               # Runtime dependencies (Do not modify)
├── fonts/                   # Required font assets
├── images/                  # Required card templates and assets
├── prompt/                  # Required prompt templates for AI
└── config.json              # Configuration file (auto-generated on first run)
```

## Running from Source

If you prefer to run the application from the source code.

### Prerequisites

-   Python 3.9+
-   [Required font files](fonts/)
-   [Required image assets](images/)

### Installation

```bash
# Clone the repository
git clone https://github.com/xziying44/arkham-homebrew.git
cd arkham-homebrew

# Install the dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
python app.py
```

## Project Structure

```
.
├── app.py                 # Main application entry point
├── Card.py                # Core card rendering logic
├── create_card.py         # Card generation handler
├── requirements.txt       # Python dependencies
├── config.json            # Configuration file
├── fonts/                 # Font assets
├── images/                # Card templates and image assets
├── static/                # Static web assets (CSS, JS)
└── templates/             # HTML templates
```

## Development Guide

### Extending with New Card Types

1.  Add a new handler function for your card type in `create_card.py`.
2.  Extend the `Card` class in `Card.py` with a new rendering method for the new type.
3.  Add the corresponding image templates and assets to the `images/` directory.

## Contributing

Contributions are welcome via Issues and Pull Requests!

1.  Fork this repository.
2.  Create your feature branch (`git checkout -b feature/your-feature`).
3.  Commit your changes (`git commit -m 'Add some feature'`).
4.  Push to the branch (`git push origin feature/your-feature`).
5.  Open a Pull Request.

## License

This project is licensed under the MIT License.

MIT: [https://rem.mit-license.org](https://rem.mit-license.org/)