#!/usr/bin/env python3
"""
GhostLink Backend API Test Suite
Tests all backend endpoints for the GhostLink smart link service.
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
import sys

# Backend URL from frontend environment
BACKEND_URL = "https://vanishurl.preview.emergentagent.com/api"

class GhostLinkTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.created_links = []  # Track created links for cleanup
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    async def test_root_endpoint(self):
        """Test GET /api/ - Should return GhostLink message"""
        try:
            async with self.session.get(f"{BACKEND_URL}/") as response:
                if response.status == 200:
                    data = await response.json()
                    expected_message = "GhostLink API - Self-Destructing Smart Links"
                    if data.get("message") == expected_message:
                        self.log_test("Root endpoint", True, f"Returned correct message: {data['message']}")
                        return True
                    else:
                        self.log_test("Root endpoint", False, f"Unexpected message: {data}")
                        return False
                else:
                    self.log_test("Root endpoint", False, f"HTTP {response.status}: {await response.text()}")
                    return False
        except Exception as e:
            self.log_test("Root endpoint", False, f"Exception: {str(e)}")
            return False
    
    async def test_create_link_click_based(self):
        """Test POST /api/links/create with click-based expiry"""
        test_data = {
            "originalUrl": "https://example.com/test-page",
            "expiryText": "expire after 3 clicks"
        }
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/links/create",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    if not data.get("success"):
                        self.log_test("Create link (click-based)", False, "Response success=False")
                        return False
                    
                    link_data = data.get("data", {})
                    
                    # Track created link
                    if "shortCode" in link_data:
                        self.created_links.append(link_data["shortCode"])
                    
                    # Verify required fields
                    required_fields = ["shortLink", "shortCode", "originalUrl", "expiryInfo", "status"]
                    missing_fields = [field for field in required_fields if field not in link_data]
                    
                    if missing_fields:
                        self.log_test("Create link (click-based)", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    # Verify expiry info
                    expiry_info = link_data.get("expiryInfo", {})
                    if expiry_info.get("type") != "clicks":
                        self.log_test("Create link (click-based)", False, f"Expected type 'clicks', got '{expiry_info.get('type')}'")
                        return False
                    
                    if expiry_info.get("clickLimit") != 3:
                        self.log_test("Create link (click-based)", False, f"Expected clickLimit 3, got {expiry_info.get('clickLimit')}")
                        return False
                    
                    if link_data.get("status") != "active":
                        self.log_test("Create link (click-based)", False, f"Expected status 'active', got '{link_data.get('status')}'")
                        return False
                    
                    if expiry_info.get("currentClicks") != 0:
                        self.log_test("Create link (click-based)", False, f"Expected currentClicks 0, got {expiry_info.get('currentClicks')}")
                        return False
                    
                    self.log_test("Create link (click-based)", True, f"Created link with shortCode: {link_data['shortCode']}, clickLimit: {expiry_info['clickLimit']}")
                    return True
                    
                else:
                    error_text = await response.text()
                    self.log_test("Create link (click-based)", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Create link (click-based)", False, f"Exception: {str(e)}")
            return False
    
    async def test_create_link_time_based(self):
        """Test POST /api/links/create with time-based expiry"""
        test_data = {
            "originalUrl": "https://google.com",
            "expiryText": "expire in 24 hours"
        }
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/links/create",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    if not data.get("success"):
                        self.log_test("Create link (time-based)", False, "Response success=False")
                        return False
                    
                    link_data = data.get("data", {})
                    
                    # Track created link
                    if "shortCode" in link_data:
                        self.created_links.append(link_data["shortCode"])
                    
                    # Verify expiry info
                    expiry_info = link_data.get("expiryInfo", {})
                    if expiry_info.get("type") != "time":
                        self.log_test("Create link (time-based)", False, f"Expected type 'time', got '{expiry_info.get('type')}'")
                        return False
                    
                    if expiry_info.get("timeLimit") is None:
                        self.log_test("Create link (time-based)", False, "Expected timeLimit to be set, got None")
                        return False
                    
                    if expiry_info.get("clickLimit") is not None:
                        self.log_test("Create link (time-based)", False, f"Expected clickLimit None, got {expiry_info.get('clickLimit')}")
                        return False
                    
                    self.log_test("Create link (time-based)", True, f"Created time-based link with timeLimit: {expiry_info['timeLimit']}")
                    return True
                    
                else:
                    error_text = await response.text()
                    self.log_test("Create link (time-based)", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Create link (time-based)", False, f"Exception: {str(e)}")
            return False
    
    async def test_create_link_hybrid(self):
        """Test POST /api/links/create with hybrid expiry"""
        test_data = {
            "originalUrl": "https://github.com",
            "expiryText": "expire after 5 clicks or tomorrow"
        }
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/links/create",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    if not data.get("success"):
                        self.log_test("Create link (hybrid)", False, "Response success=False")
                        return False
                    
                    link_data = data.get("data", {})
                    
                    # Track created link
                    if "shortCode" in link_data:
                        self.created_links.append(link_data["shortCode"])
                    
                    # Verify expiry info
                    expiry_info = link_data.get("expiryInfo", {})
                    if expiry_info.get("type") != "hybrid":
                        self.log_test("Create link (hybrid)", False, f"Expected type 'hybrid', got '{expiry_info.get('type')}'")
                        return False
                    
                    if expiry_info.get("clickLimit") != 5:
                        self.log_test("Create link (hybrid)", False, f"Expected clickLimit 5, got {expiry_info.get('clickLimit')}")
                        return False
                    
                    if expiry_info.get("timeLimit") is None:
                        self.log_test("Create link (hybrid)", False, "Expected timeLimit to be set, got None")
                        return False
                    
                    self.log_test("Create link (hybrid)", True, f"Created hybrid link with clickLimit: {expiry_info['clickLimit']}, timeLimit: {expiry_info['timeLimit']}")
                    return True
                    
                else:
                    error_text = await response.text()
                    self.log_test("Create link (hybrid)", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Create link (hybrid)", False, f"Exception: {str(e)}")
            return False
    
    async def test_get_link_details(self):
        """Test GET /api/links/{short_code} - Get link details"""
        if not self.created_links:
            self.log_test("Get link details", False, "No links created to test with")
            return False
        
        short_code = self.created_links[0]  # Use first created link
        
        try:
            async with self.session.get(f"{BACKEND_URL}/links/{short_code}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not data.get("success"):
                        self.log_test("Get link details", False, "Response success=False")
                        return False
                    
                    link_data = data.get("data", {})
                    required_fields = ["originalUrl", "status", "expiryInfo"]
                    missing_fields = [field for field in required_fields if field not in link_data]
                    
                    if missing_fields:
                        self.log_test("Get link details", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    self.log_test("Get link details", True, f"Retrieved link details for {short_code}")
                    return True
                    
                elif response.status == 404:
                    self.log_test("Get link details", False, f"Link {short_code} not found")
                    return False
                else:
                    error_text = await response.text()
                    self.log_test("Get link details", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Get link details", False, f"Exception: {str(e)}")
            return False
    
    async def test_click_tracking(self):
        """Test POST /api/links/{short_code}/click - Track clicks"""
        if not self.created_links:
            self.log_test("Click tracking", False, "No links created to test with")
            return False
        
        short_code = self.created_links[0]  # Use first created link
        
        try:
            async with self.session.post(f"{BACKEND_URL}/links/{short_code}/click") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not data.get("success"):
                        self.log_test("Click tracking", False, "Response success=False")
                        return False
                    
                    required_fields = ["shouldRedirect", "currentClicks", "status"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test("Click tracking", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    if data.get("currentClicks") < 1:
                        self.log_test("Click tracking", False, f"Expected currentClicks >= 1, got {data.get('currentClicks')}")
                        return False
                    
                    self.log_test("Click tracking", True, f"Tracked click, currentClicks: {data['currentClicks']}")
                    return True
                    
                else:
                    error_text = await response.text()
                    self.log_test("Click tracking", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Click tracking", False, f"Exception: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting GhostLink Backend API Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Test sequence
        tests = [
            self.test_root_endpoint,
            self.test_create_link_click_based,
            self.test_create_link_time_based,
            self.test_create_link_hybrid,
            self.test_get_link_details,
            self.test_click_tracking,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            result = await test()
            if result:
                passed += 1
            print()  # Add spacing between tests
        
        print("=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed. Check details above.")
            return False


async def main():
    """Main test runner"""
    async with GhostLinkTester() as tester:
        success = await tester.run_all_tests()
        return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)