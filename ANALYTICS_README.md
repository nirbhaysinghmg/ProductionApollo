# Apollo Tyres Chatbot Analytics System

## 📊 Overview

The Apollo Tyres chatbot analytics system provides comprehensive tracking and insights into user interactions, chat quality, and business metrics. It operates on a **dual-channel architecture** that captures events from both frontend widget interactions and backend chat processing.

## 🏗️ Architecture Overview

### Dual-Channel Analytics Capture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │    Analytics    │
│   Widget        │    │   Chat System   │    │    Database     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  User Events    │    │  Chat Events    │    │   Real-time     │
│  (Page views,   │    │  (Messages,     │    │   Dashboard     │
│   Widget usage) │    │   Sessions)     │    │   & Reports     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📱 Frontend Analytics Capture

### Event Types Captured

#### **User Interaction Events**
- **Page Visibility**: When users enter/leave the page
- **Widget Interactions**: Chat widget open/close events
- **Form Submissions**: Lead capture and contact forms
- **Navigation Events**: Page changes and user movement

#### **Chat Widget Events**
- **Widget Open**: When chat interface is activated
- **Widget Close**: When chat is closed by user
- **Session Duration**: Time spent in chat
- **User Engagement**: Interaction patterns and behavior

#### **Business Events**
- **Lead Generation**: Contact form submissions
- **Human Handover**: Requests for human support
- **Product Interest**: Specific product inquiries
- **Conversion Tracking**: User journey completion

### Data Collection Strategy

- **Real-time Capture**: Events captured immediately when they occur
- **Context Preservation**: Page URL, user location, session state
- **Asynchronous Processing**: Non-blocking event transmission
- **Retry Logic**: Failed requests are retried for reliability

## 🖥️ Backend Analytics Capture

### Automated Event Tracking

#### **Session Management Events**
- **Session Start**: WebSocket connection establishment
- **Session End**: Connection termination and cleanup
- **Session Duration**: Total time spent in session
- **Connection Quality**: WebSocket health and performance

#### **Chat Processing Events**
- **User Messages**: Every question and input from users
- **Bot Responses**: AI-generated responses and timing
- **Conversation Flow**: Message sequencing and context
- **Error Handling**: System failures and user experience issues

#### **System Performance Events**
- **Response Times**: Chat processing latency
- **Resource Usage**: System performance metrics
- **Error Rates**: Failure frequency and types
- **Scalability Metrics**: System capacity and load

### Event Processing Pipeline

1. **Event Interception**: Captured at various system touchpoints
2. **Classification**: Categorized into predefined event types
3. **Enrichment**: Additional context and metadata added
4. **Storage**: Persisted in normalized database structure
5. **Aggregation**: Real-time metrics and calculations
6. **Retrieval**: Available through analytics API endpoints

## 🗄️ Database Schema

### Core Analytics Tables

#### **Users Table**
```sql
users (
    user_id VARCHAR(255) PRIMARY KEY,
    first_seen_at DATETIME,
    last_active_at DATETIME,
    total_sessions INT,
    total_messages INT,
    total_duration INT,
    total_conversations INT,
    is_active BOOLEAN,
    user_type VARCHAR(50),
    last_page_url TEXT
)
```

#### **Sessions Table**
```sql
sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    start_time DATETIME,
    end_time DATETIME,
    duration INT,
    page_url TEXT,
    message_count INT,
    status ENUM('active', 'completed', 'error'),
    location_data JSON,
    last_message_time DATETIME
)
```

#### **Conversations Table**
```sql
conversations (
    conversation_id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255),
    user_id VARCHAR(255),
    start_time DATETIME,
    end_time DATETIME,
    duration INT,
    status ENUM('active', 'completed', 'handover')
)
```

#### **Messages Table**
```sql
messages (
    message_id VARCHAR(255) PRIMARY KEY,
    conversation_id VARCHAR(255),
    user_id VARCHAR(255),
    message_type ENUM('user', 'bot', 'system'),
    content TEXT,
    timestamp DATETIME
)
```

### Analytics Tables

#### **Lead Analytics**
```sql
lead_analytics (
    lead_id VARCHAR(255) PRIMARY KEY,
    lead_type VARCHAR(100),
    name VARCHAR(255),
    created_at DATETIME,
    updated_at DATETIME
)
```

#### **Human Handover**
```sql
human_handover (
    handover_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    requested_at DATETIME,
    issues JSON,
    support_option VARCHAR(100),
    last_message TEXT,
    status VARCHAR(50)
)
```

#### **Chatbot Close Events**
```sql
chatbot_close_events (
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    closed_at DATETIME,
    time_spent_seconds INT,
    last_user_message TEXT,
    last_bot_message TEXT
)
```

## 🔄 Data Flow Integration

### Event Synchronization

- **Shared Identifiers**: User and session IDs link events across channels
- **State Consistency**: Both channels maintain consistent user state
- **Temporal Alignment**: Events are timestamped and ordered chronologically
- **Conflict Resolution**: Backend events take precedence for critical data

### Data Aggregation

- **Multi-source Integration**: Combines frontend and backend data
- **Real-time Processing**: Analytics updated immediately as events occur
- **Completeness Assurance**: Multiple capture points ensure comprehensive coverage
- **Relationship Mapping**: Events linked through database relationships

## 📊 Analytics Dashboard

### Real-time Metrics

#### **User Engagement**
- Active sessions count
- Total users and sessions
- Average session duration
- User retention rates

#### **Chat Performance**
- Message volume and frequency
- Response times and quality
- Conversation completion rates
- Error rates and types

#### **Business Metrics**
- Lead generation count
- Human handover requests
- Product interest patterns
- Conversion funnel analysis

### Analytics Endpoints

- `GET /analytics/` - Overall dashboard
- `GET /analytics/sessions` - Session analytics
- `GET /analytics/conversations` - Conversation analytics
- `GET /analytics/messages` - Message analytics
- `GET /analytics/user/{user_id}` - Individual user analytics
- `GET /analytics/leads` - Lead generation analytics
- `GET /analytics/human_handover` - Handover analytics

## 🎯 Business Intelligence

### Lead Generation Tracking

- **Conversion Funnels**: User journey from initial contact to lead submission
- **Engagement Scoring**: Users scored based on interaction quality
- **Opportunity Identification**: High-engagement users flagged for follow-up
- **ROI Measurement**: Chat investment vs. lead generation value

### Performance Optimization

- **Response Time Analysis**: System performance bottlenecks identified
- **User Satisfaction Metrics**: Chat quality and user experience measured
- **Resource Utilization**: System efficiency and scalability monitored
- **Capacity Planning**: Infrastructure requirements based on usage patterns

### User Experience Insights

- **Interaction Patterns**: How users navigate and engage with the chat
- **Pain Points**: Common issues and user frustrations
- **Success Metrics**: What leads to successful outcomes
- **Improvement Areas**: Opportunities for system enhancement

## 🛡️ Data Integrity & Security

### Reliability Mechanisms

- **Transaction Safety**: Database transactions ensure data consistency
- **Error Handling**: Failed analytics don't break core functionality
- **Data Validation**: Input data verified before storage
- **Backup Strategies**: Regular data backups and recovery procedures

### Privacy & Compliance

- **Minimal Data Collection**: Only necessary information captured
- **User Consent**: Analytics respect user privacy preferences
- **Data Retention**: Configurable retention policies
- **GDPR Compliance**: European privacy regulation adherence
- **Data Anonymization**: Personal information protection

## 🚀 Performance & Scalability

### Optimization Strategies

- **Asynchronous Processing**: Analytics don't block user interactions
- **Database Indexing**: Optimized queries for fast retrieval
- **Caching Strategies**: Frequently accessed metrics cached
- **Load Distribution**: Analytics processing distributed across workers

### Volume Handling

- **Event Batching**: High-volume events batched for efficiency
- **Database Partitioning**: Large datasets partitioned for performance
- **Horizontal Scaling**: Multiple analytics instances for high load
- **Resource Monitoring**: System performance continuously tracked

## 🔧 Configuration & Customization

### Environment Variables

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=chatbot_analytics

# Analytics Configuration
ANALYTICS_ENABLED=true
EVENT_RETENTION_DAYS=90
BATCH_PROCESSING_SIZE=1000
```

### Custom Event Types

- **Business-specific Events**: Custom tracking for specific use cases
- **Event Filtering**: Configurable event capture rules
- **Data Enrichment**: Custom metadata and context addition
- **Integration Hooks**: Third-party analytics platform integration

## 📈 Monitoring & Maintenance

### System Health Monitoring

- **Database Performance**: Query execution times and resource usage
- **API Response Times**: Analytics endpoint performance
- **Error Rates**: System failure monitoring and alerting
- **Resource Utilization**: CPU, memory, and storage monitoring

### Regular Maintenance Tasks

- **Data Cleanup**: Remove old analytics data based on retention policies
- **Performance Optimization**: Database query optimization and indexing
- **Backup Management**: Regular data backups and recovery testing
- **System Updates**: Analytics system updates and improvements

## 🧪 Testing & Quality Assurance

### Analytics Testing

- **Event Capture Testing**: Verify all events are properly captured
- **Data Integrity Testing**: Ensure data accuracy and consistency
- **Performance Testing**: Load testing for high-volume scenarios
- **Integration Testing**: End-to-end analytics flow validation

### Quality Metrics

- **Data Completeness**: Percentage of expected events captured
- **Data Accuracy**: Validation of captured data against source
- **System Reliability**: Uptime and error rate monitoring
- **Performance Benchmarks**: Response time and throughput targets

## 🔮 Future Enhancements

### Planned Features

- **Advanced Analytics**: Machine learning-powered insights
- **Predictive Analytics**: User behavior prediction and recommendations
- **Real-time Alerts**: Automated notifications for critical metrics
- **Custom Dashboards**: User-configurable analytics views
- **API Integrations**: Third-party business intelligence tools

### Scalability Improvements

- **Microservices Architecture**: Distributed analytics processing
- **Real-time Streaming**: Event stream processing for instant insights
- **Data Lake Integration**: Big data analytics and storage
- **Cloud Deployment**: Multi-region analytics infrastructure

---

**Version**: 1.0.0  
**Last Updated**: July 2024  
**Maintainer**: Apollo Tyres Development Team  
**Documentation**: Comprehensive analytics system guide for developers and stakeholders
