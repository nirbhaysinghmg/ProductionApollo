# Apollo Tyres Conversational AI Chatbot

A sophisticated conversational AI chatbot built for Apollo Tyres that provides personalized tyre recommendations through natural dialogue. The chatbot uses advanced language models, vector databases, and analytics to deliver an engaging customer experience.

## 🏗️ Architecture Overview

### Core Components

```
apoloTyreSample/
├── app/                          # Main application directory
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Configuration management
│   ├── database.py              # Database utilities
│   ├── analytics.py             # Analytics and event tracking
│   ├── geocoding.py             # Location services
│   ├── llm_setup.py             # Language model configuration
│   ├── vector_store.py          # Vector database management
│   ├── schemas.py               # Pydantic data models
│   └── routers/                 # API route handlers
│       ├── __init__.py
│       └── chat.py              # Chat endpoints and WebSocket
├── data/                        # Data storage
│   └── apolloTyres_combined_cleaned.csv
├── chroma_db/                   # Vector database storage
├── frontend/                    # Web interface
├── ssl/                         # SSL certificates
└── requirements.txt             # Python dependencies
```

## 🚀 Key Features

### 1. **Conversational AI**
- **Natural Dialogue**: Engages users in natural conversation
- **Context Awareness**: Remembers conversation history within sessions
- **Personalized Responses**: Tailors recommendations based on user input
- **Follow-up Questions**: Asks relevant questions to understand user needs

### 2. **Intelligent Tyre Recommendations**
- **Vehicle-Specific**: Recognizes different vehicle types (cars, SUVs, bikes, trucks)
- **Usage-Based**: Considers driving patterns (city, highway, off-road)
- **Priority-Focused**: Adapts to user priorities (fuel efficiency, performance, comfort)
- **Location-Aware**: Provides location-specific recommendations

### 3. **Real-time Analytics**
- **User Tracking**: Monitors user sessions and interactions
- **Conversation Analytics**: Tracks message patterns and engagement
- **Performance Metrics**: Measures response times and success rates
- **Lead Generation**: Captures potential customer information

### 4. **Location Services**
- **Geocoding**: Converts coordinates to city names
- **Local Recommendations**: Suggests nearby dealers and services
- **Weather Considerations**: Factors in local weather conditions
- **Regional Preferences**: Adapts to regional driving patterns

## 🔧 Technical Stack

### Backend
- **FastAPI**: Modern, fast web framework for APIs
- **Python 3.10+**: Core programming language
- **MySQL**: Primary database for analytics and user data
- **ChromaDB**: Vector database for semantic search
- **Google Gemini AI**: Advanced language model for conversations

### Frontend
- **HTML/CSS/JavaScript**: Web interface
- **WebSocket**: Real-time communication
- **Responsive Design**: Mobile-friendly interface

### Infrastructure
- **SSL/HTTPS**: Secure communication
- **CORS**: Cross-origin resource sharing
- **Background Tasks**: Automated cleanup and maintenance

## 🗄️ Database Schema

### Core Tables

#### `users`
- User identification and tracking
- Session history and engagement metrics
- Activity timestamps and status

#### `sessions`
- WebSocket session management
- Page URL tracking and duration
- Message count and status

#### `conversations`
- Conversation grouping and management
- Start/end times and duration
- Status tracking (active/completed)

#### `messages`
- Individual message storage
- User/bot message classification
- Timestamp and content tracking

#### `analytics_events`
- Custom event tracking
- User behavior analysis
- Performance monitoring

## 🤖 AI/ML Components

### 1. **Language Model (Google Gemini)**
```python
# Configuration
LLM_MODEL = "gemini-2.0-flash"
EMBED_MODEL = "models/embedding-001"
```

### 2. **Vector Database (ChromaDB)**
- **Embeddings**: Google's embedding model
- **Chunk Size**: 1000 characters with 100 character overlap
- **Search**: Semantic similarity with k=5 results
- **Persistence**: Local storage in `chroma_db/`

### 3. **Conversational Chain**
```python
ConversationalRetrievalChain.from_llm(
    llm=llm_setup.get_llm(),
    retriever=vector_store.as_retriever(),
    combine_docs_chain_kwargs={"prompt": SYSTEM_PROMPT}
)
```

## 📡 API Endpoints

### Chat Endpoints
- `POST /chat/query`: Process user questions
- `POST /chat/generate-questions`: Generate suggested questions
- `WebSocket /chat/ws`: Real-time chat interface

### Analytics Endpoints
- `GET /analytics/`: Overall analytics dashboard
- `GET /analytics/sessions`: Session-specific analytics
- `GET /analytics/conversations`: Conversation analytics
- `GET /analytics/messages`: Message analytics
- `POST /analytics/leads`: Lead capture
- `POST /analytics/human_handover`: Human handover tracking

## 🔄 Conversation Flow

### 1. **Initial Interaction**
```
User: "I have a Honda City, suggest tyres"
Bot: "That's a great vehicle — many Honda City owners prefer Apollo's Alnac 4G or Amazer 4G Life for comfort and smooth rides. But before we lock it in, can I ask — do you mostly drive within the city, go on long drives, or do some off-roading too?"
```

### 2. **Information Gathering**
```
User: "Mostly city driving"
Bot: "Got it! For smooth city drives, comfort and fuel efficiency matter most. Would you say you're more focused on saving fuel, or do you enjoy performance and a quiet ride too?"
```

### 3. **Personalized Recommendation**
```
User: "Fuel efficiency is important"
Bot: "Perfect. Based on that, Apollo's Amazer 4G Life is an excellent choice — it's built for great mileage and long tread life in urban conditions..."
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10+
- MySQL 8.0+
- Google Gemini API key

### 1. **Clone Repository**
```bash
git clone <repository-url>
cd apoloTyreSample
```

### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Environment Configuration**
```bash
# Create .env file
cp .env.example .env

# Configure environment variables
GEMINI_API_KEY=your_gemini_api_key
DB_HOST=localhost
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=chatbot_analytics
```

### 4. **Database Setup**
```sql
-- Run the SQL queries from sqlqueries.sql
mysql -u your_user -p your_database < sqlqueries.sql
```

### 5. **Data Preparation**
```bash
# Place your CSV data in data/apolloTyres_combined_cleaned.csv
# Or use the web scraping functionality
```

### 6. **SSL Certificate Setup**
```bash
# Generate SSL certificates
./generate-ssl.sh
```

### 7. **Start Application**
```bash
# Start backend
python -m app.main

# Start frontend (in separate terminal)
./start-frontend.sh
```

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
GEMINI_API_KEY=your_gemini_api_key
LLM_MODEL=gemini-2.0-flash
EMBED_MODEL=models/embedding-001

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=chatbot_analytics

# Data Configuration
CSV_PATH=data/apolloTyres_combined_cleaned.csv
PERSIST_DIRECTORY=chroma_db
```

### System Prompt Customization
The chatbot's personality and behavior can be customized in `app/llm_setup.py`:

```python
SYSTEM_PROMPT = PromptTemplate(
    input_variables=["context", "question", "chat_history", "user_location"],
    template="""Your custom prompt here..."""
)
```

## 📊 Analytics & Monitoring

### Real-time Metrics
- **Active Sessions**: Number of concurrent users
- **Message Volume**: Messages per hour/day
- **Response Times**: Average response latency
- **User Engagement**: Session duration and interaction patterns

### Business Intelligence
- **Lead Generation**: Captured customer information
- **Product Interest**: Most discussed tyre models
- **Geographic Distribution**: User locations and preferences
- **Conversation Quality**: Success rates and user satisfaction

## 🔒 Security Features

### Data Protection
- **SSL/HTTPS**: Encrypted communication
- **CORS**: Controlled cross-origin access
- **Input Validation**: Sanitized user inputs
- **Session Management**: Secure session handling

### Privacy Compliance
- **GDPR Ready**: Configurable data retention
- **No Personal Data**: Minimal personal information storage
- **User Consent**: Transparent data usage
- **Data Anonymization**: Anonymous analytics tracking

## 🚀 Deployment

### Production Setup
```bash
# Using systemd service
sudo cp apollo-chatbot.service /etc/systemd/system/
sudo systemctl enable apollo-chatbot
sudo systemctl start apollo-chatbot
```

### Docker Deployment
```dockerfile
# Dockerfile example
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 9006
CMD ["python", "-m", "app.main"]
```

### Load Balancing
- **Nginx**: Reverse proxy configuration
- **Multiple Instances**: Horizontal scaling
- **Health Checks**: Automated monitoring
- **SSL Termination**: Centralized SSL management

## 🧪 Testing

### Automated Tests
```bash
# Run comprehensive tests
python test_scenarios.py

# Test conversational flow
python test_conversational.py

# Test API endpoints
python test_api_direct.py
```

### Manual Testing
Use the questions from `MANUAL_TEST_QUESTIONS.md` to verify:
- Conversational flow
- Response quality
- Context awareness
- Personalization accuracy

## 🔄 Maintenance

### Regular Tasks
- **Database Cleanup**: Remove old sessions and messages
- **Vector Store Updates**: Refresh with new product data
- **Analytics Reports**: Generate weekly/monthly reports
- **Performance Monitoring**: Track response times and errors

### Backup Strategy
- **Database Backups**: Daily automated backups
- **Configuration Backups**: Version-controlled configs
- **Log Management**: Rotated log files
- **Disaster Recovery**: Multi-region deployment options

## 📈 Performance Optimization

### Caching Strategy
- **Redis**: Session and conversation caching
- **CDN**: Static asset delivery
- **Database Indexing**: Optimized query performance
- **Connection Pooling**: Efficient database connections

### Scalability
- **Horizontal Scaling**: Multiple application instances
- **Database Sharding**: Distributed data storage
- **Load Balancing**: Traffic distribution
- **Auto-scaling**: Dynamic resource allocation

## 🤝 Contributing

### Development Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

### Code Standards
- **PEP 8**: Python code style
- **Type Hints**: Function and variable typing
- **Documentation**: Comprehensive docstrings
- **Testing**: Unit and integration tests

## 📞 Support

### Documentation
- **API Documentation**: Available at `/docs` when running
- **Code Comments**: Inline documentation
- **Configuration Guide**: Environment setup
- **Troubleshooting**: Common issues and solutions

### Contact
- **Technical Issues**: GitHub issues
- **Feature Requests**: Pull requests
- **Business Inquiries**: Contact Apollo Tyres

## 📄 License

This project is proprietary software developed for Apollo Tyres. All rights reserved.

---

**Version**: 1.0.0  
**Last Updated**: July 2024  
**Maintainer**: Apollo Tyres Development Team 