"""Phase 1 Features: Environment Variables, Collections, and Assertions."""

import re
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime


class VariableSubstitution:
    """Handle {{VARIABLE}} substitution in requests."""
    
    VARIABLE_PATTERN = r'\{\{(\w+)\}\}'
    
    @staticmethod
    def substitute(text: Optional[str], variables: Dict[str, str]) -> Optional[str]:
        """Replace {{VAR}} with values from environment."""
        if not text:
            return text
        
        def replace_var(match):
            var_name = match.group(1)
            return variables.get(var_name, f"{{{{UNDEFINED:{var_name}}}}}")
        
        return re.sub(VariableSubstitution.VARIABLE_PATTERN, replace_var, text)
    
    @staticmethod
    def substitute_dict(data: Dict[str, Any], variables: Dict[str, str]) -> Dict[str, Any]:
        """Recursively substitute variables in a dictionary."""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = VariableSubstitution.substitute(value, variables)
            elif isinstance(value, dict):
                result[key] = VariableSubstitution.substitute_dict(value, variables)
            elif isinstance(value, list):
                result[key] = [
                    VariableSubstitution.substitute(item, variables) if isinstance(item, str)
                    else VariableSubstitution.substitute_dict(item, variables) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                result[key] = value
        return result
    
    @staticmethod
    def extract_variables(text: Optional[str]) -> List[str]:
        """Extract all {{VARIABLE}} names from text."""
        if not text:
            return []
        return re.findall(VariableSubstitution.VARIABLE_PATTERN, text)


class AssertionValidator:
    """Validate response against assertions."""
    
    @staticmethod
    def get_nested_value(obj: Any, path: str) -> Optional[Any]:
        """Get value from nested object using dot notation."""
        if path == "status":
            return obj  # Special case for status code
        
        keys = path.split(".")
        current = obj
        
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return None
        
        return current
    
    @staticmethod
    def validate(response: Dict[str, Any], assertions: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Validate response against assertions.
        Returns (success: bool, messages: List[str])
        """
        errors = []
        
        for assertion in assertions:
            field = assertion.get("field", "")
            operator = assertion.get("operator", "")
            expected = assertion.get("expected")
            
            # Get actual value
            if field == "status":
                actual = response.get("status_code")
            elif field == "response_time":
                actual = response.get("response_time")
            else:
                body = response.get("body", {})
                actual = AssertionValidator.get_nested_value(body, field)
            
            # Validate
            is_valid = AssertionValidator._validate_assertion(actual, operator, expected)
            
            if not is_valid:
                errors.append(
                    f"Assertion failed: {field} {operator} {expected} "
                    f"(actual: {actual})"
                )
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _validate_assertion(actual: Any, operator: str, expected: Any) -> bool:
        """Validate a single assertion."""
        if operator == "equals":
            return actual == expected
        elif operator == "not_equals":
            return actual != expected
        elif operator == "contains":
            if isinstance(actual, str):
                return expected in actual
            elif isinstance(actual, list):
                return expected in actual
            return False
        elif operator == "not_contains":
            if isinstance(actual, str):
                return expected not in actual
            elif isinstance(actual, list):
                return expected not in actual
            return True
        elif operator == "greater_than":
            try:
                return float(actual) > float(expected)
            except (TypeError, ValueError):
                return False
        elif operator == "less_than":
            try:
                return float(actual) < float(expected)
            except (TypeError, ValueError):
                return False
        elif operator == "greater_than_or_equal":
            try:
                return float(actual) >= float(expected)
            except (TypeError, ValueError):
                return False
        elif operator == "less_than_or_equal":
            try:
                return float(actual) <= float(expected)
            except (TypeError, ValueError):
                return False
        elif operator == "exists":
            return actual is not None
        elif operator == "not_exists":
            return actual is None
        elif operator == "is_type":
            type_map = {
                "string": str,
                "number": (int, float),
                "boolean": bool,
                "array": list,
                "object": dict,
                "null": type(None),
            }
            return isinstance(actual, type_map.get(expected, type(None)))
        
        return False


class PerformanceTracker:
    """Track request performance metrics."""
    
    def __init__(self):
        self.metrics = []
    
    def record(self, name: str, method: str, url: str, status: int, 
               response_time: float, timestamp: Optional[datetime] = None):
        """Record a request's performance."""
        self.metrics.append({
            "name": name,
            "method": method,
            "url": url,
            "status": status,
            "response_time": response_time,
            "timestamp": timestamp or datetime.now().isoformat(),
        })
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self.metrics:
            return {}
        
        times = [m["response_time"] for m in self.metrics]
        
        return {
            "total_requests": len(self.metrics),
            "avg_response_time": sum(times) / len(times),
            "min_response_time": min(times),
            "max_response_time": max(times),
            "success_rate": sum(1 for m in self.metrics if 200 <= m["status"] < 300) / len(self.metrics) * 100,
        }
    
    def get_by_url(self, url: str) -> List[Dict[str, Any]]:
        """Get all metrics for a specific URL."""
        return [m for m in self.metrics if m["url"] == url]
