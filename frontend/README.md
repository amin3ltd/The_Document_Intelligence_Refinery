# Document Intelligence Refinery - Dashboard

A modern, interactive dashboard for the Document Intelligence Refinery application. Built with React, Material-UI, and Wails for desktop deployment.

## Features

- **Smart Document Upload**: Drag & drop PDF files with automatic format detection
- **Multi-Strategy Extraction**: Tiered extraction using pdfplumber, Docling, MinerU, and VLMs
- **AI-Powered Query**: Ask questions in natural language with source citations
- **Audit & Verification**: Claim verification with confidence scores
- **Settings Management**: Configure VLM providers, extraction strategies, and storage

## Tech Stack

- **Frontend**: React 18 + TypeScript
- **UI Framework**: Material-UI (MUI) v5
- **State Management**: React Query + Zustand
- **Animations**: Framer Motion
- **Desktop**: Wails v2 (Go + WebView2)

## Getting Started

### Prerequisites

- Node.js 18+
- Go 1.21+ (for Wails)
- Wails CLI (`go install github.com/wailsapp/wails/v2/cmd/wails@latest`)

### Installation

```bash
# Install dependencies
npm install

# Run in development mode
npm run dev

# Build for production
npm run build

# Build desktop app with Wails
wails build
```

### Environment Variables

Create a `.env` file in the frontend directory:

```
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/         # Page components
│   ├── services/      # API services
│   ├── App.tsx        # Main application
│   └── index.tsx      # Entry point
├── public/            # Static assets
├── package.json       # Dependencies
├── vite.config.ts     # Vite configuration
└── wails.json        # Wails configuration
```

## Desktop Build

To build the desktop application:

```bash
# Install Wails
go install github.com/wailsapp/wails/v2/cmd/wails@latest

# Build
wails build
```

The executable will be in the `build/bin` directory.

## License

MIT
