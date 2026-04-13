"""
Environment variable validation on startup
Ensures all required env vars are set before app starts
"""
from app.config import settings
import logging
import sys

logger = logging.getLogger(__name__)

REQUIRED_VARS = {
    'DATABASE_URL': 'Database connection string',
    'JWT_SECRET': 'JWT signing secret (min 32 chars)',
    'GROQ_API_KEY': 'Groq API key for LLM',
}

OPTIONAL_VARS = {
    'SMTP_SERVER': 'Email SMTP server (for email notifications)',
    'EMAIL_ADDRESS': 'Email address for notifications',
    'GOOGLE_CALENDAR_CREDENTIALS': 'Google Calendar API credentials',
}


def validate_environment():
    """Validate required environment variables"""
    errors = []
    warnings = []

    # Check required variables
    for var_name, description in REQUIRED_VARS.items():
        value = getattr(settings, var_name, None)
        if not value:
            errors.append(f"❌ {var_name}: {description} - NOT SET")
        elif var_name == 'JWT_SECRET' and len(value) < 32:
            errors.append(f"❌ {var_name}: Must be at least 32 characters (current: {len(value)})")
        elif var_name == 'DATABASE_URL':
            if 'postgresql' in value.lower():
                logger.info(f"✅ Using PostgreSQL database")
            elif 'sqlite' in value.lower():
                warnings.append(f"⚠️  Using SQLite database (not recommended for production)")

    # Check optional variables
    for var_name, description in OPTIONAL_VARS.items():
        value = getattr(settings, var_name, None)
        if not value:
            warnings.append(f"⚠️  {var_name}: {description} - NOT SET (optional)")

    # Log results
    if errors:
        logger.error("\n" + "="*60)
        logger.error("ENVIRONMENT VALIDATION FAILED")
        logger.error("="*60)
        for error in errors:
            logger.error(error)
        logger.error("="*60)
        sys.exit(1)

    if warnings:
        logger.warning("\n" + "-"*60)
        logger.warning("ENVIRONMENT WARNINGS")
        logger.warning("-"*60)
        for warning in warnings:
            logger.warning(warning)
        logger.warning("-"*60)

    logger.info("✅ Environment validation passed")
