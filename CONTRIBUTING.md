# Contributing to DJ Mixing Platform

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/Xander-Vanlaer/dj-mixing/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Docker version, etc.)
   - Screenshots or logs if applicable

### Suggesting Features

1. Check [Issues](https://github.com/Xander-Vanlaer/dj-mixing/issues) for similar suggestions
2. Create a new issue with:
   - Feature description and use case
   - Why it would be useful
   - Possible implementation approach
   - Examples from other DJ software (optional)

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the coding standards (see below)
   - Write tests for new functionality
   - Update documentation as needed

4. **Test your changes**
   ```bash
   # Backend
   cd backend && pytest
   
   # Frontend
   cd frontend && npm test
   
   # Integration
   docker-compose up -d
   # Manual testing
   docker-compose down
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```
   
   Use conventional commits:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code style changes (formatting)
   - `refactor:` Code refactoring
   - `test:` Adding or updating tests
   - `chore:` Maintenance tasks

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Describe what your PR does
   - Link related issues
   - Include screenshots for UI changes
   - Request review from maintainers

## Development Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local backend development)
- Node.js 18+ (for local frontend development)

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

#### Database
```bash
docker-compose up db redis -d
cd backend
alembic upgrade head
```

## Coding Standards

### Python (Backend)

- Follow [PEP 8](https://pep8.org/)
- Use type hints where applicable
- Maximum line length: 100 characters
- Use meaningful variable names
- Write docstrings for functions and classes

Example:
```python
from typing import List, Optional

def analyze_track(file_path: str, options: Optional[dict] = None) -> dict:
    """
    Analyze an audio track for BPM, key, and other features.
    
    Args:
        file_path: Path to the audio file
        options: Optional analysis parameters
        
    Returns:
        Dictionary containing analysis results
        
    Raises:
        FileNotFoundError: If audio file doesn't exist
        AnalysisError: If analysis fails
    """
    # Implementation
    pass
```

### JavaScript/React (Frontend)

- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use functional components and hooks
- Use meaningful component and variable names
- Write JSDoc comments for complex functions

Example:
```javascript
/**
 * Deck component for playing and controlling audio tracks
 * @param {string} deckId - Unique identifier for the deck (deckA or deckB)
 * @param {string} label - Display label for the deck
 */
const Deck = ({ deckId, label }) => {
  // Implementation
};
```

### Formatting

We use automated formatters:

**Backend (Python):**
```bash
pip install black isort
black backend/app
isort backend/app
```

**Frontend (JavaScript):**
```bash
npm install --save-dev prettier
npm run format
```

## Project Structure

```
dj-mixing/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── main.py         # Application entry point
│   ├── alembic/            # Database migrations
│   └── tests/              # Backend tests
├── frontend/               # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── contexts/       # State management
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
│   └── tests/              # Frontend tests
└── docs/                   # Additional documentation
```

## Testing Requirements

All contributions should include appropriate tests:

### Backend Tests
- Unit tests for services and utilities
- Integration tests for API endpoints
- Test coverage >80%

### Frontend Tests
- Component tests using React Testing Library
- Integration tests for user flows
- Snapshot tests for UI components

Run tests before submitting PR:
```bash
# Backend
cd backend && pytest --cov=app

# Frontend
cd frontend && npm test -- --coverage
```

## Documentation

Update documentation for:
- New features → README.md, API.md
- API changes → API.md
- Configuration changes → DEPLOYMENT.md
- Code changes → Inline comments and docstrings

## Performance Considerations

When contributing, keep in mind:

### Backend
- Audio analysis should complete in <30 seconds
- API endpoints should respond in <100ms (excluding analysis)
- Use caching for expensive operations
- Optimize database queries

### Frontend
- Components should render in <100ms
- Waveform visualization should run at 60 FPS
- Minimize bundle size
- Use lazy loading for heavy components

## Security

- Never commit secrets or API keys
- Validate all user inputs
- Sanitize file uploads
- Use parameterized queries (SQLAlchemy ORM)
- Follow OWASP security guidelines

## Architecture Decisions

When making significant changes:

1. Discuss in an issue first
2. Consider backward compatibility
3. Update architecture diagrams if needed
4. Document rationale in code comments

## Areas Needing Contribution

We especially welcome contributions in:

- [ ] **Audio Analysis**: Improve BPM/key detection accuracy
- [ ] **Effects**: Add new audio effects (reverb, delay, filters)
- [ ] **Auto-Mix**: Machine learning for track selection
- [ ] **UI/UX**: Improve interface usability
- [ ] **Testing**: Increase test coverage
- [ ] **Documentation**: More examples and tutorials
- [ ] **Performance**: Optimize audio processing
- [ ] **Mobile**: Improve mobile/tablet support
- [ ] **Accessibility**: ARIA labels, keyboard navigation
- [ ] **Export**: Implement mix recording/export

## Review Process

1. Maintainers will review your PR within 7 days
2. Address feedback and requested changes
3. Once approved, maintainers will merge
4. Your contribution will be credited in release notes

## Questions?

- Open a [Discussion](https://github.com/Xander-Vanlaer/dj-mixing/discussions)
- Tag maintainers in issues
- Check existing documentation

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Recognition

Contributors will be acknowledged in:
- README.md Contributors section
- Release notes
- Project website (future)

Thank you for making the DJ Mixing Platform better! 🎵🎧
