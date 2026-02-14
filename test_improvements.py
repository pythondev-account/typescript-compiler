#!/usr/bin/env python3
"""
Test script to validate the improvements made to the routing and error handling functionality.
"""

import sys
import subprocess
from helper import (
    execute_command, 
    validate_ipv4_address, 
    validate_ipv4_network, 
    validate_route,
    get_routes
)

def test_validation_functions():
    """Test IP validation functions"""
    print("Testing validation functions...")
    
    # Test validate_ipv4_address
    assert validate_ipv4_address("192.168.1.1") == True, "Valid IP should pass"
    assert validate_ipv4_address("256.1.1.1") == False, "Invalid IP should fail"
    assert validate_ipv4_address("not_an_ip") == False, "Non-IP string should fail"
    
    # Test validate_ipv4_network
    assert validate_ipv4_network("192.168.1.0/24") == True, "Valid network should pass"
    assert validate_ipv4_network("192.168.1.1/32") == False, "/32 should fail (single host)"
    assert validate_ipv4_network("invalid/24") == False, "Invalid network should fail"
    
    # Test validate_route
    assert validate_route("192.168.1.0/24", "192.168.1.1") == True, "Valid route should pass"
    assert validate_route("invalid/24", "192.168.1.1") == False, "Invalid destination should fail"
    assert validate_route("192.168.1.0/24", "invalid") == False, "Invalid gateway should fail"
    
    print("✓ All validation tests passed!")
    return True

def test_execute_command_basic():
    """Test basic execute_command functionality"""
    print("\nTesting execute_command basic functionality...")
    
    # Test successful command
    result = execute_command("echo 'test'")
    assert result == "test", f"Expected 'test', got '{result}'"
    
    # Test command with timeout
    result = execute_command("echo 'timeout test'", timeout=5)
    assert result == "timeout test", "Timeout parameter should work"
    
    print("✓ Basic execute_command tests passed!")
    return True

def test_execute_command_errors():
    """Test execute_command error handling"""
    print("\nTesting execute_command error handling...")
    
    # Test command that fails with suppress_errors=True
    result = execute_command("exit 1", suppress_errors=True)
    assert result == "", "Suppressed error should return empty string"
    
    # Test command that fails with check=False
    result = execute_command("false", check=False)
    assert isinstance(result, str), "Should return string even on failure"
    
    # Test empty command validation
    try:
        execute_command("")
        assert False, "Empty command should raise ValueError"
    except ValueError:
        pass  # Expected
    
    print("✓ Error handling tests passed!")
    return True

def test_get_routes():
    """Test get_routes function"""
    print("\nTesting get_routes function...")
    
    # This should work on any Linux system
    routes = get_routes()
    assert isinstance(routes, str), "get_routes should return a string"
    
    print(f"✓ get_routes test passed! (Found {len(routes.splitlines())} routes)")
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("Running tests for routing and error handling improvements")
    print("=" * 60)
    
    tests = [
        test_validation_functions,
        test_execute_command_basic,
        test_execute_command_errors,
        test_get_routes,
    ]
    
    failed = []
    for test in tests:
        try:
            if not test():
                failed.append(test.__name__)
        except Exception as e:
            print(f"✗ {test.__name__} failed with exception: {e}")
            failed.append(test.__name__)
    
    print("\n" + "=" * 60)
    if not failed:
        print("✓ All tests passed successfully!")
        print("=" * 60)
        return 0
    else:
        print(f"✗ {len(failed)} test(s) failed:")
        for name in failed:
            print(f"  - {name}")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
