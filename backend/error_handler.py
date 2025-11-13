"""
Enhanced error handling and recovery system for LLM streaming
Implements exponential backoff, timeout handling, and error classification
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, Awaitable
from enum import Enum

from models import StreamEvent, ErrorData, StatusData


class ErrorType(Enum):
    """Classification of error types for appropriate handling"""
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    AUTH_ERROR = "auth_error"
    SERVICE_ERROR = "service_error"
    NETWORK_ERROR = "network_error"
    VALIDATION_ERROR = "validation_error"
    UNKNOWN_ERROR = "unknown_error"


class RetryStrategy:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt with exponential backoff"""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add jitter to prevent thundering herd
            delay *= (0.5 + random.random() * 0.5)
        
        return delay


class CircuitBreaker:
    """Circuit breaker pattern for provider failure handling"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half-open
    
    def can_execute(self) -> bool:
        """Check if execution is allowed based on circuit state"""
        if self.state == "closed":
            return True
        
        if self.state == "open":
            if (datetime.now() - self.last_failure_time).total_seconds() > self.recovery_timeout:
                self.state = "half-open"
                return True
            return False
        
        # half-open state
        return True
    
    def record_success(self):
        """Record successful execution"""
        self.failure_count = 0
        self.state = "closed"
    
    def record_failure(self):
        """Record failed execution"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"


class ErrorHandler:
    """
    Enhanced error handling system with retry logic, circuit breakers,
    and structured logging for LLM streaming operations.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_strategies: Dict[ErrorType, RetryStrategy] = {
            ErrorType.RATE_LIMIT: RetryStrategy(max_retries=5, base_delay=2.0, max_delay=120.0),
            ErrorType.TIMEOUT: RetryStrategy(max_retries=3, base_delay=1.0, max_delay=30.0),
            ErrorType.SERVICE_ERROR: RetryStrategy(max_retries=3, base_delay=5.0, max_delay=60.0),
            ErrorType.NETWORK_ERROR: RetryStrategy(max_retries=4, base_delay=1.0, max_delay=30.0),
            ErrorType.AUTH_ERROR: RetryStrategy(max_retries=0),  # Don't retry auth errors
            ErrorType.VALIDATION_ERROR: RetryStrategy(max_retries=0),  # Don't retry validation errors
            ErrorType.UNKNOWN_ERROR: RetryStrategy(max_retries=2, base_delay=2.0, max_delay=30.0)
        }
    
    def classify_error(self, error: Exception, status_code: Optional[int] = None) -> ErrorType:
        """
        Classify error type for appropriate handling strategy.
        
        Args:
            error: The exception that occurred
            status_code: HTTP status code if applicable
            
        Returns:
            ErrorType: Classified error type
        """
        if status_code:
            if status_code == 429:
                return ErrorType.RATE_LIMIT
            elif status_code in [401, 403]:
                return ErrorType.AUTH_ERROR
            elif status_code >= 500:
                return ErrorType.SERVICE_ERROR
            elif status_code >= 400:
                return ErrorType.VALIDATION_ERROR
        
        error_str = str(error).lower()
        
        if "timeout" in error_str or "timed out" in error_str:
            return ErrorType.TIMEOUT
        elif "rate limit" in error_str or "too many requests" in error_str:
            return ErrorType.RATE_LIMIT
        elif "auth" in error_str or "unauthorized" in error_str:
            return ErrorType.AUTH_ERROR
        elif "network" in error_str or "connection" in error_str:
            return ErrorType.NETWORK_ERROR
        
        return ErrorType.UNKNOWN_ERROR
    
    def get_circuit_breaker(self, provider: str) -> CircuitBreaker:
        """Get or create circuit breaker for provider"""
        if provider not in self.circuit_breakers:
            self.circuit_breakers[provider] = CircuitBreaker()
        return self.circuit_breakers[provider]
    
    async def execute_with_retry(
        self,
        operation: Callable[[], Awaitable[Any]],
        provider: str,
        pane_id: str,
        session_id: str,
        context: Dict[str, Any] = None
    ) -> Any:
        """
        Execute operation with retry logic and circuit breaker protection.
        
        Args:
            operation: Async operation to execute
            provider: Provider name for circuit breaker
            pane_id: Pane identifier for logging
            session_id: Session identifier for logging
            context: Additional context for logging
            
        Returns:
            Operation result or raises final exception
        """
        circuit_breaker = self.get_circuit_breaker(provider)
        context = context or {}
        
        if not circuit_breaker.can_execute():
            self._log_structured(
                "error",
                "Circuit breaker open, operation blocked",
                session_id=session_id,
                pane_id=pane_id,
                provider=provider,
                **context
            )
            raise Exception(f"Circuit breaker open for provider {provider}")
        
        last_error = None
        
        for attempt in range(self.retry_strategies[ErrorType.UNKNOWN_ERROR].max_retries + 1):
            try:
                result = await operation()
                circuit_breaker.record_success()
                
                if attempt > 0:
                    self._log_structured(
                        "info",
                        f"Operation succeeded after {attempt} retries",
                        session_id=session_id,
                        pane_id=pane_id,
                        provider=provider,
                        attempt=attempt,
                        **context
                    )
                
                return result
                
            except Exception as error:
                last_error = error
                error_type = self.classify_error(error)
                retry_strategy = self.retry_strategies[error_type]
                
                self._log_structured(
                    "warning",
                    f"Operation failed: {str(error)}",
                    session_id=session_id,
                    pane_id=pane_id,
                    provider=provider,
                    attempt=attempt,
                    error_type=error_type.value,
                    **context
                )
                
                # Check if we should retry
                if attempt >= retry_strategy.max_retries:
                    circuit_breaker.record_failure()
                    break
                
                # Calculate delay and wait
                delay = retry_strategy.get_delay(attempt)
                
                self._log_structured(
                    "info",
                    f"Retrying in {delay:.2f} seconds",
                    session_id=session_id,
                    pane_id=pane_id,
                    provider=provider,
                    attempt=attempt,
                    delay=delay,
                    **context
                )
                
                await asyncio.sleep(delay)
        
        # All retries exhausted
        circuit_breaker.record_failure()
        self._log_structured(
            "error",
            f"Operation failed after all retries: {str(last_error)}",
            session_id=session_id,
            pane_id=pane_id,
            provider=provider,
            **context
        )
        
        raise last_error
    
    def create_error_event(
        self,
        error: Exception,
        pane_id: str,
        status_code: Optional[int] = None,
        context: Dict[str, Any] = None
    ) -> StreamEvent:
        """
        Create standardized error event from exception.
        
        Args:
            error: The exception that occurred
            pane_id: Pane identifier
            status_code: HTTP status code if applicable
            context: Additional context
            
        Returns:
            StreamEvent: Standardized error event
        """
        error_type = self.classify_error(error, status_code)
        retry_strategy = self.retry_strategies[error_type]
        
        return StreamEvent(
            type="error",
            pane_id=pane_id,
            data=ErrorData(
                message=str(error),
                code=error_type.value,
                retryable=retry_strategy.max_retries > 0
            )
        )
    
    def create_status_event(
        self,
        pane_id: str,
        status: str,
        message: Optional[str] = None
    ) -> StreamEvent:
        """Create standardized status event"""
        return StreamEvent(
            type="status",
            pane_id=pane_id,
            data=StatusData(status=status, message=message)
        )
    
    def _log_structured(
        self,
        level: str,
        message: str,
        session_id: str = None,
        pane_id: str = None,
        provider: str = None,
        **kwargs
    ):
        """
        Log with structured metadata for debugging and monitoring.
        
        Args:
            level: Log level (info, warning, error)
            message: Log message
            session_id: Session identifier
            pane_id: Pane identifier
            provider: Provider name
            **kwargs: Additional structured data
        """
        extra_data = {
            "session_id": session_id,
            "pane_id": pane_id,
            "provider": provider,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        
        # Filter out None values
        extra_data = {k: v for k, v in extra_data.items() if v is not None}
        
        log_message = f"{message} | {extra_data}"
        
        if level == "info":
            self.logger.info(log_message)
        elif level == "warning":
            self.logger.warning(log_message)
        elif level == "error":
            self.logger.error(log_message)
        else:
            self.logger.debug(log_message)
    
    def get_provider_health(self) -> Dict[str, Dict[str, Any]]:
        """
        Get health status of all providers based on circuit breaker states.
        
        Returns:
            Dict mapping provider names to health information
        """
        health_info = {}
        
        for provider, circuit_breaker in self.circuit_breakers.items():
            health_info[provider] = {
                "state": circuit_breaker.state,
                "failure_count": circuit_breaker.failure_count,
                "last_failure": circuit_breaker.last_failure_time.isoformat() if circuit_breaker.last_failure_time else None,
                "healthy": circuit_breaker.state == "closed"
            }
        
        return health_info


# Global error handler instance
error_handler = ErrorHandler()