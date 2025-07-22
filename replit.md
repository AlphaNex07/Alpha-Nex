# Alpha Nex - Content Platform Replit Guide

## Overview

Alpha Nex is a comprehensive content management platform that combines user-generated content collection with AI-powered quality assurance and a gamified reward system. The platform allows users to upload various types of content (videos, audio, documents, code, images), review others' submissions, and earn XP points that can be converted to monetary rewards. The system includes sophisticated moderation, KYC verification, and administrative controls.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web application with SQLAlchemy ORM
- **Database**: SQLite by default (configurable via DATABASE_URL environment variable)
- **Authentication**: Flask-Login for session management with password hashing
- **File Handling**: Werkzeug secure file uploads with size/type validation
- **Background Tasks**: APScheduler for automated periodic tasks
- **AI Integration**: OpenAI GPT-4o for content quality analysis and duplicate detection

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 responsive design
- **Styling**: Custom CSS with monochrome theme inspired by professional platforms
- **JavaScript**: Vanilla JS for interactive features, form validation, and file upload handling
- **Icons**: Font Awesome for consistent iconography
- **Typography**: Inter font family for modern, clean appearance

### Security Model
- **Authentication**: Email/password with secure hashing using Werkzeug
- **File Validation**: Extension whitelist, file size limits, and secure filename handling
- **Rate Limiting**: Daily upload quotas per user (500MB default)
- **Content Moderation**: AI-powered duplicate/spam detection with human review workflow

## Key Components

### User Management System
- **User Model**: Comprehensive user profiles with XP tracking, strike system, and KYC verification
- **Role-Based Access**: Regular users, administrators, and banned user states
- **Strike System**: Separate tracking for uploader and reviewer violations (3-strike rule)
- **Daily Limits**: Upload bandwidth restrictions that reset daily

### Content Management
- **Upload System**: Multi-format file support (video, audio, documents, code, images)
- **Review Workflow**: Peer review system where users evaluate uploaded content quality
- **AI Quality Control**: Automated content analysis for duplicates and spam detection
- **File Organization**: Secure file storage with categorization and metadata tracking

### Gamification & Rewards
- **XP Point System**: Points earned for uploads, reviews, and quality bonuses
- **Withdrawal System**: Mechanism to convert XP points to monetary rewards
- **Achievement Tracking**: User progress monitoring and engagement metrics

### Administrative Tools
- **Admin Panel**: Comprehensive dashboard for managing users, content, and violations
- **KYC Management**: Identity verification workflow with document and selfie validation
- **Strike Management**: Tools for issuing warnings and managing user violations
- **Content Moderation**: Review queue for flagged or problematic content

## Data Flow

### Upload Process
1. User selects file and provides description/category
2. Frontend validates file type, size, and daily quota
3. AI service analyzes content description for quality/duplicates
4. File is securely stored with metadata in database
5. Upload is queued for peer review
6. User receives XP points for successful upload

### Review Process
1. Reviewers are presented with unreviewed content
2. Reviewers rate content as good/bad with detailed feedback
3. Multiple reviews are aggregated for quality scoring
4. Poor quality content may be flagged or removed
5. Reviewers earn XP points for participation
6. Strike system handles reviewer misconduct

### Admin Workflow
1. Administrators monitor pending KYC verifications
2. Review withdrawal requests and process payments
3. Handle user appeals and strike disputes
4. Oversee platform health metrics and user engagement

## External Dependencies

### Required Services
- **OpenAI API**: Content quality analysis and duplicate detection (GPT-4o model)
- **Database**: SQLite default, PostgreSQL recommended for production
- **File Storage**: Local filesystem (uploads/ directory)

### Optional Integrations
- **Email Service**: User verification and notifications (configuration ready)
- **Payment Gateway**: For XP point to currency conversion
- **Cloud Storage**: Alternative to local file storage for scalability

### Environment Variables
- `SESSION_SECRET`: Flask session encryption key
- `DATABASE_URL`: Database connection string
- `OPENAI_API_KEY`: OpenAI API authentication

## Deployment Strategy

### Development Setup
- Local SQLite database for rapid prototyping
- File uploads stored in local uploads/ directory
- Background scheduler for automated tasks
- Debug logging enabled for troubleshooting

### Production Considerations
- Database migration to PostgreSQL for scalability
- Cloud file storage (AWS S3, Google Cloud Storage)
- Load balancing for high traffic scenarios
- Automated backup systems for user data
- Enhanced security measures and rate limiting

### Scalability Features
- Database connection pooling configured
- Background task scheduling for resource-intensive operations
- Modular architecture allows for microservice migration
- API-ready structure for mobile app integration

The platform is designed to handle growth from small community to large-scale content platform while maintaining data integrity and user experience quality.

## Recent Updates

### January 2025
- Enhanced code documentation with function docstrings
- Improved logging configuration for better debugging
- Added visual improvements to templates with consistent iconography
- Updated CSS and JavaScript headers for better maintainability
- Fixed Flask-Login routing configuration
- Resolved JavaScript form validation issues

### July 2025
- Successfully migrated from Replit Agent to standard Replit environment
- Configured PostgreSQL database for production scalability  
- Set up OpenAI API integration with proper secret management
- Verified all core platform features working (uploads, reviews, XP system)
- Application running on port 5000 with gunicorn server
- Removed all KYC verification requirements from user workflow
- Converted review system to website feedback functionality
- Enhanced code documentation and formatting across all files
- Improved template comments and JavaScript performance optimization
- Added comprehensive docstrings to models, forms, and utility functions
- Enhanced CSS and HTML template comments for better maintainability
- Improved route documentation with detailed function descriptions
- Updated OpenAI service with enhanced parameter documentation
- Added helpful comments to base templates and configuration files
- Refined project description and metadata across configuration files