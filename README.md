# Cloud-Agnostic Agent with LangGraph

A sophisticated AI agent built with LangGraph and Google Gemini LLM that provides cloud-agnostic architecture recommendations for React frontend and Java microservices backend applications. The agent can work with both AWS and Azure, learn from user feedback, and generate production-ready code templates.

## 🌟 Features

### 🧠 Intelligent Architecture Recommendations
- **Cloud-Agnostic Solutions**: Provides recommendations that work on both AWS and Azure
- **AI-Powered Analysis**: Uses Google Gemini LLM for intelligent requirement analysis
- **Multi-Service Architecture**: Supports React frontends with Java microservices backends
- **Cost Optimization**: Includes cost estimates and optimization suggestions

### 🎯 Template Generation
- **React Frontend Templates**: Complete React applications with TypeScript, Material-UI, PWA support
- **Java Microservices Templates**: Spring Boot services with JPA, Security, Monitoring, and Docker
- **Cloud-Specific Configurations**: AWS and Azure deployment configurations
- **Best Practices**: Follows industry best practices for security, performance, and maintainability

### 🔄 Self-Learning Mechanism
- **Feedback Processing**: Learns from user ratings and feedback
- **Preference Adaptation**: Adapts recommendations based on user preferences
- **Pattern Recognition**: Identifies successful architecture patterns
- **Continuous Improvement**: Improves recommendations over time

### ☁️ Multi-Cloud Support
- **AWS Integration**: Complete AWS service recommendations and configurations
- **Azure Integration**: Full Azure service support with best practices
- **Cloud Service Mapping**: Maps equivalent services across cloud providers
- **Cost Comparison**: Compares costs between different cloud options

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Agent                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────── │
│  │ Requirements    │  │ Recommendations │  │ Implementation │
│  │ Analysis        │→ │ Generation      │→ │ Generation     │
│  └─────────────────┘  └─────────────────┘  └─────────────── │
│           ↓                     ↓                     ↓      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────── │
│  │ Template        │  │ Feedback        │  │ Learning       │
│  │ Generation      │  │ Processing      │  │ System         │
│  └─────────────────┘  └─────────────────┘  └─────────────── │
├─────────────────────────────────────────────────────────────┤
│                  Google Gemini LLM                         │
├─────────────────────────────────────────────────────────────┤
│     AWS Adapter     │     Azure Adapter     │   Templates  │
│  ┌─────────────────┐ │ ┌─────────────────┐   │ ┌───────────│
│  │ ECS/Fargate     │ │ │ Container Apps  │   │ │ React     │
│  │ RDS/Aurora      │ │ │ PostgreSQL      │   │ │ Templates │
│  │ S3/CloudFront   │ │ │ Storage/CDN     │   │ │           │
│  │ API Gateway     │ │ │ API Management  │   │ │ Java      │
│  │ CloudWatch      │ │ │ Monitor/Insights│   │ │ Templates │
│  └─────────────────┘ │ └─────────────────┘   │ └─────────── │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API Key
- AWS credentials (optional)
- Azure credentials (optional)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd AgenticAiLangGraph
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Get Google Gemini API Key:**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add it to your `.env` file:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

### Basic Usage

```python
from src.agent.agent import create_agent

# Initialize the agent
agent = create_agent("your_gemini_api_key")

# Process a query
query = """
I need a scalable e-commerce application with:
- React frontend
- Java microservices backend
- PostgreSQL database
- Deployable on AWS and Azure
"""

result = await agent.process_query(query)
print(f"Generated {len(result['recommendations'])} recommendations")
```

### Run Examples

1. **Basic Example:**
   ```bash
   python examples/basic_usage.py
   ```

2. **Advanced API Server:**
   ```bash
   python examples/advanced_api.py
   ```

3. **Access API Documentation:**
   - Open http://localhost:8000/docs for Swagger UI
   - Open http://localhost:8000/redoc for ReDoc

## 📋 Detailed Usage

### 1. Architecture Recommendations

The agent analyzes your requirements and provides detailed recommendations:

```python
import asyncio
from src.agent.agent import create_agent

async def get_recommendations():
    agent = create_agent("your_gemini_api_key")
    
    query = """
    Build a microservices application with:
    - React frontend with authentication
    - 3 Java microservices (user, product, order)
    - PostgreSQL for data persistence
    - Redis for caching
    - File storage for images
    - Monitoring and logging
    - Budget conscious but scalable
    """
    
    result = await agent.process_query(query)
    
    for rec in result["recommendations"]:
        print(f"Recommendation: {rec.title}")
        print(f"Confidence: {rec.confidence_score}")
        print(f"Resources: {len(rec.resources)}")
        print(f"Estimated Cost: ${rec.estimated_cost}/month")

asyncio.run(get_recommendations())
```

### 2. Template Generation

Generate production-ready code templates:

```python
from src.templates.react.template_generator import ReactTemplateGenerator, ReactTemplateConfig
from src.templates.java.template_generator import JavaTemplateGenerator, JavaTemplateConfig

# React template
react_config = ReactTemplateConfig(
    app_name="E-commerce Frontend",
    cloud_provider="aws",
    api_endpoint="https://api.example.com",
    authentication_enabled=True,
    pwa_enabled=True
)

react_generator = ReactTemplateGenerator()
react_files = react_generator.generate_template(react_config)

# Java template
java_config = JavaTemplateConfig(
    service_name="user-service",
    group_id="com.example",
    artifact_id="user-service",
    package_name="com.example.userservice",
    cloud_provider="aws"
)

java_generator = JavaTemplateGenerator()
java_files = java_generator.generate_template(java_config)
```

### 3. Feedback and Learning

Provide feedback to improve recommendations:

```python
# Provide feedback
feedback = {
    "session_id": "session_123",
    "recommendation_id": "rec_456",
    "rating": 4.5,
    "text": "Great cost optimization, but could use more monitoring",
    "preferences": {
        "cost_importance": "high",
        "monitoring_importance": "medium"
    }
}

result = await agent.provide_feedback("session_123", feedback)
print(f"Insights generated: {result['insights_generated']}")

# Get learning summary
summary = agent.feedback_processor.get_learning_summary()
print(f"Total feedback: {summary['total_feedback_entries']}")
print(f"Average rating: {summary['feedback_statistics']['average_rating']}")
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# AWS (Optional - uses default credential chain)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Azure (Optional - uses default credential chain)
AZURE_SUBSCRIPTION_ID=your_subscription_id
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
```

### Configuration File

The agent uses `config/config.yaml` for detailed configuration:

```yaml
gemini:
  model_name: "gemini-1.5-pro"
  temperature: 0.7
  max_tokens: 8192

agent:
  learning:
    enabled: true
    storage_path: "learning_data.json"
    confidence_threshold: 0.7

templates:
  react:
    default_ui_framework: "material-ui"
    typescript_enabled: true
    pwa_enabled: true
  
  java:
    default_java_version: "17"
    default_spring_boot_version: "3.2.0"
    security_enabled: true
```

## 📚 API Reference

### REST API Endpoints

When running the advanced API server:

#### Generate Recommendations
```http
POST /recommendations
Content-Type: application/json

{
  "query": "Your architecture requirements",
  "context": {},
  "preferred_cloud_providers": ["aws", "azure"],
  "budget_constraints": 1000.0
}
```

#### Submit Feedback
```http
POST /feedback
Content-Type: application/json

{
  "session_id": "session_123",
  "recommendation_id": "rec_456",
  "rating": 4.5,
  "feedback_text": "Great recommendation!",
  "preferences": {"cost_importance": "high"}
}
```

#### Get Learning Summary
```http
GET /learning
```

#### Health Check
```http
GET /health
```

### Python API

#### Core Classes

- **`CloudAgnosticAgent`**: Main agent class
- **`GeminiLLMIntegration`**: Google Gemini integration
- **`AWSAdapter`**: AWS service recommendations
- **`AzureAdapter`**: Azure service recommendations  
- **`FeedbackProcessor`**: Learning and feedback processing
- **`ReactTemplateGenerator`**: React template generation
- **`JavaTemplateGenerator`**: Java template generation

## 🎯 Use Cases

### 1. Startup Architecture Planning
```python
query = """
Early-stage startup needs:
- MVP React web app
- Simple Java API
- User authentication
- File uploads
- Minimal cost
- Easy to scale later
"""
```

### 2. Enterprise Migration
```python
query = """
Migrate legacy monolith to:
- Modern React frontend
- Java microservices
- Cloud-native architecture
- High availability
- Enterprise security
- Multi-region deployment
"""
```

### 3. E-commerce Platform
```python
query = """
E-commerce platform with:
- React storefront
- Java order/inventory services
- Payment processing
- Product catalog
- User management
- Analytics and reporting
"""
```

## 🛠️ Development

### Project Structure

```
AgenticAiLangGraph/
├── src/
│   ├── agent/                 # Core agent implementation
│   │   ├── agent.py          # Main LangGraph agent
│   │   ├── state.py          # Agent state management
│   │   └── gemini_integration.py
│   ├── cloud_adapters/       # Cloud service adapters
│   │   ├── aws_adapter.py    # AWS service recommendations
│   │   └── azure_adapter.py  # Azure service recommendations
│   ├── templates/            # Code template generators
│   │   ├── react/           # React templates
│   │   └── java/            # Java templates
│   └── learning/            # Learning and feedback
│       └── feedback_processor.py
├── config/                  # Configuration files
├── examples/               # Usage examples
├── requirements.txt       # Python dependencies
└── README.md
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📊 Supported Services

### AWS Services
- **Compute**: ECS Fargate, Lambda, EC2
- **Database**: RDS (PostgreSQL, MySQL), DynamoDB
- **Storage**: S3, EFS
- **Networking**: VPC, ALB, API Gateway
- **Caching**: ElastiCache Redis
- **Monitoring**: CloudWatch, X-Ray
- **Security**: IAM, Cognito, Secrets Manager

### Azure Services
- **Compute**: Container Apps, Functions, Virtual Machines
- **Database**: PostgreSQL Flexible Server, Cosmos DB
- **Storage**: Blob Storage, File Storage
- **Networking**: Virtual Network, Application Gateway, API Management
- **Caching**: Cache for Redis
- **Monitoring**: Application Insights, Log Analytics
- **Security**: Entra ID, Key Vault

## 🔒 Security Best Practices

The agent implements several security best practices:

1. **Credential Management**: Uses cloud credential chains (no hardcoded keys)
2. **Least Privilege**: Recommends minimal required permissions
3. **Encryption**: Enables encryption in transit and at rest
4. **Network Security**: Implements proper VPC and network segmentation
5. **Authentication**: Integrates with cloud identity providers
6. **Monitoring**: Includes security monitoring and logging

## 💰 Cost Optimization

The agent provides cost optimization through:

1. **Service Selection**: Chooses cost-effective services for requirements
2. **Right-sizing**: Recommends appropriate instance sizes
3. **Auto-scaling**: Implements scaling policies to optimize costs
4. **Storage Tiers**: Uses appropriate storage classes
5. **Reserved Instances**: Suggests reservation strategies
6. **Monitoring**: Includes cost monitoring and alerts

## 📈 Performance Features

- **Async Processing**: Non-blocking architecture recommendation generation
- **Caching**: Caches common recommendations and templates
- **Parallel Processing**: Processes multiple cloud providers simultaneously
- **Streaming**: Supports streaming responses for large templates
- **Rate Limiting**: Implements proper rate limiting for API calls

## 🐛 Troubleshooting

### Common Issues

1. **Missing API Key**
   ```
   Error: GEMINI_API_KEY environment variable is required
   ```
   Solution: Set your Gemini API key in the environment or `.env` file

2. **Cloud Credentials**
   ```
   Warning: AWS credentials not available
   ```
   Solution: Configure AWS CLI or set environment variables

3. **Import Errors**
   ```
   ImportError: No module named 'langgraph'
   ```
   Solution: Install dependencies with `pip install -r requirements.txt`

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or set environment variable:
```bash
export LOG_LEVEL=DEBUG
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Documentation**: Check this README and code comments
- **Issues**: Report bugs and request features via GitHub Issues
- **Examples**: See the `examples/` directory for usage examples
- **API Docs**: Access interactive docs at `/docs` when running the API server

## 🚀 Roadmap

- [ ] Support for additional cloud providers (GCP, Digital Ocean)
- [ ] More application frameworks (Python FastAPI, Node.js Express)
- [ ] Advanced cost optimization algorithms
- [ ] Integration with CI/CD pipelines
- [ ] Visual architecture diagrams
- [ ] Performance benchmarking tools
- [ ] Multi-language template support

---

**Built with ❤️ using LangGraph, Google Gemini, and modern cloud technologies**