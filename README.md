# Mini-C Compiler with AI Code Generation and Fix Assistant

A full-stack application featuring a Mini-C compiler with AI-powered code generation and error fixing capabilities.

## Features

- **Mini-C Compiler**: Compiles a subset of C language using PLY (Python Lex-Yacc)
- **AI Code Generation**: Generate Mini-C code from natural language descriptions
- **AI Fix Assistant**: Automatically fix compilation errors with AI assistance
- **Monaco Editor**: Professional code editor with syntax highlighting
- **Real-time Error Display**: Structured error messages with line numbers and helpful suggestions

## Supported Mini-C Language Features

### Supported:
- Integer declarations: `int x;` or `int x = 5;`
- Assignments: `x = 5;` or `x = x + 2;`
- Arithmetic operators: `+`, `-`, `*`, `/`
- Printf statements with format specifiers:
  - `printf("%d", x);` - print single integer
  - `printf("%d %d", x, y);` - print multiple integers
  - Supported format specifiers: `%d`, `%i`
- If statements: `if (x > 5) { printf("%d", x); }`
- Comparison operators: `<`, `>`, `<=`, `>=`, `==`, `!=`

### Not Supported:
- Functions (no main(), no function definitions)
- Loops (for, while, do-while)
- Arrays and pointers
- Strings (except in printf format)
- else/switch statements

## Tech Stack

### Frontend
- React 18 (Vite)
- Tailwind CSS
- Monaco Editor

### Backend
- Python 3.11+ (FastAPI)
- PLY (Python Lex-Yacc)
- OpenAI SDK (configured for Gemini)

## Project Structure

```
mini-c-compiler/
├── backend/
│   ├── main.py          # FastAPI endpoints
│   ├── lexer.py         # PLY lexer (tokenizer)
│   ├── parser.py        # PLY parser (YACC) with improved error messages
│   ├── semantic.py      # Semantic analyzer with printf validation
│   ├── ai_service.py    # Gemini AI integration via OpenAI SDK
│   ├── requirements.txt # Python dependencies
│   ├── .env.example     # Environment variable template
│   └── .env             # Your API key (create this)
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ChatPanel.jsx    # Left panel - AI chat interface
    │   │   ├── CodeEditor.jsx   # Center panel - Monaco editor
    │   │   └── OutputPanel.jsx  # Right panel - errors & Fix button
    │   ├── App.jsx              # Main app with 3-panel layout
    │   ├── main.jsx
    │   └── index.css            # Tailwind imports
    ├── package.json
    ├── vite.config.js
    └── tailwind.config.js
```

## Setup Instructions

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- Gemini API key (for AI features)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd mini-c-compiler/backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your Gemini API key:
   ```bash
   # Copy the example file
   copy .env.example .env   # Windows
   cp .env.example .env     # macOS/Linux
   
   # Edit .env and add your API key
   GEMINI_API_KEY=your_actual_api_key_here
   ```

5. Run the backend server:
   ```bash
   python main.py
   ```
   
   The server will start at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd mini-c-compiler/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```
   
   The app will be available at `http://localhost:5173`

## API Endpoints

### POST /compile
Compile Mini-C code and return errors or success.

**Request:**
```json
{
  "code": "int x = 5;\nprintf(\"%d\", x);"
}
```

**Response (Success):**
```json
{
  "success": true,
  "errors": []
}
```

**Response (Error):**
```json
{
  "success": false,
  "errors": [
    {
      "line": 2,
      "type": "Syntax",
      "message": "Missing semicolon ';' at end of statement"
    }
  ]
}
```

### POST /generate
Generate Mini-C code from a natural language prompt.

**Request:**
```json
{
  "prompt": "Create a program that adds two numbers and prints the sum"
}
```

**Response:**
```json
{
  "code": "int x = 10;\nint y = 20;\nint sum;\nsum = x + y;\nprintf(\"%d\", sum);"
}
```

### POST /fix
Fix code using AI based on compiler errors.

**Request:**
```json
{
  "code": "x = 5;",
  "errors": "Line 1: Semantic Error - Variable 'x' is not declared"
}
```

**Response:**
```json
{
  "fixed_code": "int x;\nx = 5;"
}
```

### GET /health
Check API health and configuration status.

**Response:**
```json
{
  "status": "ok",
  "compiler": "ready",
  "ai_service": "ready",
  "api_key_configured": true
}
```

## Usage

1. **Generate Code**: Use the left chat panel to describe what code you want. The AI will generate valid Mini-C code.

2. **Edit Code**: Modify the generated code in the center Monaco editor.

3. **Compile**: Click the "Compile" button to check for errors.

4. **Fix Errors**: If errors occur, click "Fix with AI" to automatically fix them.

## Improved Error Messages

The compiler provides helpful, context-aware error messages:

- **Missing semicolon**: `Missing semicolon ';' at end of declaration`
- **Undeclared variable**: `Variable 'x' is not declared. Add 'int x;' before using it`
- **Duplicate declaration**: `Variable 'x' already declared (first declared at line 2)`
- **Unsupported features**: `Loops ('for') are not supported in Mini-C`
- **Printf format errors**: `printf format expects 2 argument(s), but 1 provided`
- **Unsupported format specifiers**: `Unsupported format specifier '%s' in printf. Only %d and %i are supported`

## Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and add it to your `backend/.env` file

## Troubleshooting

### AI features return 500 error
- Make sure `GEMINI_API_KEY` is set in `backend/.env`
- Verify the API key is valid at Google AI Studio
- Check if you've exceeded your API quota

### Compiler errors not showing
- Check that the backend server is running on port 8000
- Verify CORS is properly configured (it's set to allow all origins by default)

### Frontend not connecting to backend
- Ensure the backend is running at `http://localhost:8000`
- Check browser console for network errors
