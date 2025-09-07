# CKNbook - AI-Powered Nutrition Learning Platform

## 📋 Project Overview

CKNbook is a web-based AI application that provides interactive nutrition education based on the book "吃的營養科學觀" (The Science of Nutrition). The platform offers four main features: content fine-tuning, quiz generation, effective response generation, and encouragement feedback.

## 🎯 Features

### 1. **Page 1: Content Fine-tuning** (`/`)
- **Purpose**: Generate refined content based on user input and book knowledge
- **Functionality**: 
  - Analyzes user input against nutrition knowledge base
  - Provides enhanced, educational responses
  - Uses Google Gemini AI for content generation

### 2. **Page 2: Quiz Generation** (`/quiz`)
- **Purpose**: Create interactive quizzes for specific nutrition topics
- **Functionality**:
  - Select day/chapter (1-21) from nutrition book
  - Generates multiple-choice questions with 4 options
  - Includes correct answers and explanations
  - Uses chapter-specific content for question generation

### 3. **Page 3: Effective Response Generation** (`/effective-reply`)
- **Purpose**: Generate contextually appropriate responses with specific tones
- **Functionality**:
  - Tone selection: 溫暖 (Warm), 專業 (Professional), 活潑 (Lively)
  - Combines user input with relevant nutrition knowledge
  - Generates structured responses with feeling and knowledge components

### 4. **Page 4: Encouragement Feedback** (`/encouragement`)
- **Purpose**: Provide motivational feedback in Cantonese for user sharing
- **Functionality**:
  - Analyzes user input and categorizes into 5 encouragement types
  - Generates 3 different Cantonese encouragement options (30 words each)
  - Individual copy buttons for each option
  - Different styles: 溫馨鼓勵, 活潑讚美, 實用建議

## 🏗️ Technical Architecture

### Backend
- **Framework**: Flask 2.3.3
- **AI Integration**: Google Gemini API (google-generativeai 0.3.0)
- **Language**: Python 3.11+
- **Configuration**: Environment variables via python-dotenv
- **CORS**: flask-cors for cross-origin requests

### Frontend
- **Templates**: Jinja2 HTML templates
- **Styling**: Custom CSS with responsive design
- **JavaScript**: Vanilla JS for interactivity and copy functionality
- **Navigation**: Multi-page application with consistent navigation

### Deployment
- **Platform**: Google Cloud Run
- **Containerization**: Docker
- **Production File**: `main_production.py`
- **Requirements**: `requirements.txt`

## 📁 Project Structure

```
cknbook2/
├── main_production.py          # Production Flask application
├── main.py                     # Development Flask application
├── requirements.txt            # Python dependencies
├── requirements_production.txt # Production dependencies (includes flask-limiter)
├── Dockerfile                  # Container configuration
├── deploy-gcp.sh              # Cloud Run deployment script
├── gunicorn.conf.py           # WSGI server configuration
├── .env                       # Environment variables (API keys)
├── book_knowledge.txt         # Nutrition knowledge base
├── prompts/                   # AI prompt templates
│   ├── system_prompt.txt
│   ├── response_prompt.txt
│   └── quiz_prompt.txt
├── templates/                 # HTML templates
│   ├── index.html            # Page 1: Content fine-tuning
│   ├── quiz.html             # Page 2: Quiz generation
│   ├── effective_reply.html  # Page 3: Response generation
│   └── encouragement.html    # Page 4: Encouragement feedback
├── static/                   # Static assets
│   ├── style.css
│   └── script.js
└── knowledge/                # Chapter content (Day 1-21)
    ├── 第1天：營養學，一個令人著迷的話題.md
    ├── 第2天：怎樣吃早餐更管飽？多加點蛋白質吧！.md
    └── ... (Day 3-21)
```

## 🔧 API Endpoints

### Content Fine-tuning
- `GET /` - Render main page
- `POST /process` - Process user input and generate refined content

### Quiz Generation
- `GET /quiz` - Render quiz page
- `POST /generate-quiz` - Generate quiz for specific day

### Response Generation
- `GET /effective-reply` - Render response page
- `POST /generate-response` - Generate tone-specific response

### Encouragement Feedback
- `GET /encouragement` - Render encouragement page
- `POST /generate-encouragement` - Generate 3 Cantonese encouragement options

## 🤖 AI Integration

### Google Gemini API
- **Model**: gemini-pro
- **Usage**: Content generation, analysis, and response formatting
- **Rate Limiting**: Optional flask-limiter (disabled in production)
- **Error Handling**: Comprehensive error handling with fallbacks

### Prompt Engineering
- **System Prompts**: Role-based AI instructions
- **Response Formatting**: JSON-structured outputs
- **Language Requirements**: Cantonese for encouragement, Chinese for other features
- **Content Constraints**: Word limits and style specifications

## 🚀 Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY="your_api_key"

# Run development server
python main_production.py
```

### Cloud Run Deployment
```bash
# Deploy to Google Cloud Run
./deploy-gcp.sh
```

### Environment Variables
- `GOOGLE_API_KEY`: Google Gemini API key
- `PORT`: Server port (default: 8080 for Cloud Run)
- `FLASK_ENV`: Environment (production/development)

## 📊 Features in Detail

### Encouragement Types
1. **🎯【學習楷模】** - Learning Role Model
2. **🌟【深度學習】** - Deep Learning
3. **👍【精華筆記】** - Key Notes
4. **📚【優質分享】** - Quality Sharing
5. **💡【智慧啟發】** - Wisdom Inspiration

### Quiz Features
- **Chapter Selection**: Days 1-21 from nutrition book
- **Question Types**: Multiple choice with 4 options
- **Content Integration**: Uses specific chapter content
- **Answer Validation**: Includes correct answers and explanations

### Response Tones
- **溫暖 (Warm)**: Friendly and supportive
- **專業 (Professional)**: Authoritative and informative
- **活潑 (Lively)**: Energetic and engaging

## 🔒 Security & Performance

### Security
- **CORS**: Configured for cross-origin requests
- **Input Validation**: Server-side validation for all inputs
- **Error Handling**: Graceful error handling without exposing internals
- **Environment Variables**: Secure API key management

### Performance
- **Caching**: Template caching for improved performance
- **Rate Limiting**: Optional rate limiting (disabled in current deployment)
- **Error Recovery**: Fallback mechanisms for API failures
- **Logging**: Comprehensive logging for monitoring

## 📝 Development Notes

### Recent Updates
- **Page 4 Implementation**: Added 3-option Cantonese encouragement feature
- **Quiz Route Fix**: Resolved 404 errors for quiz generation
- **Dockerfile Update**: Changed to use main_production.py
- **Flask Limiter**: Made optional to prevent deployment issues

### Code Quality
- **Error Handling**: Try-catch blocks for all API calls
- **Logging**: Structured logging for debugging
- **Modularity**: Separate functions for different features
- **Documentation**: Inline comments and docstrings

## 🎨 User Interface

### Design Principles
- **Responsive**: Works on desktop and mobile devices
- **Intuitive**: Clear navigation between pages
- **Accessible**: Easy-to-use copy buttons and clear feedback
- **Consistent**: Uniform styling across all pages

### Navigation
- **Page Numbers**: Simple 1-2-3-4 navigation
- **Active States**: Visual indication of current page
- **Copy Functionality**: One-click copying for generated content

## 📈 Future Enhancements

### Potential Improvements
- **User Authentication**: User accounts and progress tracking
- **Content Management**: Admin interface for knowledge base updates
- **Analytics**: Usage tracking and performance metrics
- **Mobile App**: Native mobile application
- **Multi-language**: Support for additional languages

### Technical Debt
- **Rate Limiting**: Re-enable flask-limiter with proper Redis setup
- **Testing**: Add unit and integration tests
- **Monitoring**: Implement application monitoring
- **Caching**: Add Redis caching for improved performance

## 📞 Support & Maintenance

### Monitoring
- **Logs**: Application logs for error tracking
- **Health Checks**: Built-in health check endpoint
- **Performance**: Response time monitoring

### Maintenance
- **Dependencies**: Regular updates of Python packages
- **API Keys**: Secure management of Google API keys
- **Content**: Regular updates of nutrition knowledge base

---

**Version**: 1.0.0  
**Last Updated**: September 2025  
**Maintainer**: Development Team
