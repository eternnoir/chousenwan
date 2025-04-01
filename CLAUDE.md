# CLAUDE.md - Development Guidelines

## Commands
- Start server: `uvicorn app.main:app --reload`
- Run tests: `bash test_agent.sh`
- Linting: Use `flake8` for Python linting
- Type checking: Use `mypy`

## Code Style
- **Imports**: Group standard lib, third-party, and local imports
- **Type Hints**: Always use type annotations (see `typing` imports)
- **Naming**: 
  - Use snake_case for functions/variables
  - Use PascalCase for classes
  - Use descriptive names in English
- **Documentation**: Use docstrings for functions/methods
- **Error Handling**: Use try/except with specific exceptions
- **API Schema**: Define with Pydantic models in schemas.py
- **Agent Config**: Define tools with function_tool decorator
- **Internationalization**: Comments in traditional Chinese allowed

## Project Structure
- `app/`: Main application code
- `app/main.py`: FastAPI endpoints
- `app/schemas.py`: Pydantic data models
- `app/agent_config.py`: Agent definitions and tools
- `app/session_manager.py`: Session state management

## Rules
- When you modify the code, you must also update the corresponding documentation accordingly. Like README.md or docs folder.
- You are a senior software engineer, and your code adheres to excellent software development principles such as Clean Code and SOLID.