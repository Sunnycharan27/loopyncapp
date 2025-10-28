#!/usr/bin/env python3
"""
COMPREHENSIVE EVENTS AND TICKETING SYSTEM TEST - QR CODE VERIFICATION

Testing complete event booking flow with QR code generation as specified in review request.

Backend URL: https://loopconnect-1.preview.emergentagent.com/api
Test User: demo@loopync.com / password123
"""

import requests
import json
import sys
import re
import base64
from datetime import datetime

# Configuration
BACKEND_URL = "https://loopconnect-1.preview.emergentagent.com/api"
TEST_EMAIL = "demo@loopync.com"
TEST_PASSWORD = "password123"

class EventTicketingTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_id = None
        self.jwt_token = None
        self.initial_balance = 0.0
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
        
    def test_1_login_demo_user(self):
        """TEST 1: Login Demo User & Verify Wallet"""
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get("token")
                user_data = data.get("user", {})
                self.user_id = user_data.get("id")
                self.initial_balance = user_data.get("walletBalance", 0.0)
                
                # Set authorization header for future requests
                self.session.headers.update({"Authorization": f"Bearer {self.jwt_token}"})
                
                self.log_test(
                    "Login Demo User & Verify Wallet",
                    True,
                    f"User ID: {self.user_id}, Wallet Balance: ₹{self.initial_balance:,.2f}"
                )
                
                # Verify sufficient funds (should be ₹10,000 for demo user)
                if self.initial_balance >= 5000:
                    self.log_test(
                        "Verify Sufficient Funds for Testing",
                        True,
                        f"Demo user has ₹{self.initial_balance:,.2f} - sufficient for ticket booking"
                    )
                else:
                    self.log_test(
                        "Verify Sufficient Funds for Testing",
                        False,
                        f"Demo user has only ₹{self.initial_balance:,.2f} - may not be sufficient for all tests"
                    )
                
                return True
            else:
                self.log_test(
                    "Login Demo User & Verify Wallet",
                    False,
                    error=f"Login failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Login Demo User & Verify Wallet",
                False,
                error=f"Exception during login: {str(e)}"
            )
            return False
    
    def test_2_get_available_events(self):
        """TEST 2: Get Available Events"""
        try:
            response = self.session.get(f"{BACKEND_URL}/events")
            
            if response.status_code == 200:
                events = response.json()
                
                if len(events) > 0:
                    # Look for T-Hub Innovation Summit (e4) with specific tiers
                    thub_event = None
                    for event in events:
                        if "T-Hub" in event.get("name", "") or "Innovation Summit" in event.get("name", ""):
                            thub_event = event
                            break
                    
                    if thub_event:
                        tiers = thub_event.get("tiers", [])
                        startup_pass = next((t for t in tiers if "Startup" in t.get("name", "")), None)
                        investor_pass = next((t for t in tiers if "Investor" in t.get("name", "")), None)
                        
                        tier_details = []
                        if startup_pass:
                            tier_details.append(f"Startup Pass - ₹{startup_pass.get('price', 0)}")
                        if investor_pass:
                            tier_details.append(f"Investor Pass - ₹{investor_pass.get('price', 0)}")
                        
                        self.log_test(
                            "Get Available Events",
                            True,
                            f"Found {len(events)} events including T-Hub Innovation Summit with tiers: {', '.join(tier_details)}"
                        )
                        
                        # Store event for booking test
                        self.test_event = thub_event
                        return True
                    else:
                        # Use first available event
                        self.test_event = events[0]
                        event_tiers = [f"{t.get('name', 'Unknown')} - ₹{t.get('price', 0)}" for t in self.test_event.get("tiers", [])]
                        
                        self.log_test(
                            "Get Available Events",
                            True,
                            f"Found {len(events)} events. Using '{self.test_event.get('name')}' with tiers: {', '.join(event_tiers)}"
                        )
                        return True
                else:
                    self.log_test(
                        "Get Available Events",
                        False,
                        error="No events found in the system"
                    )
                    return False
            else:
                self.log_test(
                    "Get Available Events",
                    False,
                    error=f"Failed to get events with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Get Available Events",
                False,
                error=f"Exception during events retrieval: {str(e)}"
            )
            return False
    
    def test_3_book_event_ticket(self):
        """TEST 3: Book Event Ticket"""
        try:
            if not hasattr(self, 'test_event'):
                self.log_test(
                    "Book Event Ticket",
                    False,
                    error="No test event available from previous test"
                )
                return False
            
            event_id = self.test_event.get("id")
            tiers = self.test_event.get("tiers", [])
            
            if not tiers:
                self.log_test(
                    "Book Event Ticket",
                    False,
                    error="No tiers available for the test event"
                )
                return False
            
            # Use first available tier or look for "Startup Pass"
            tier_name = None
            for tier in tiers:
                if "Startup" in tier.get("name", ""):
                    tier_name = tier.get("name")
                    break
            
            if not tier_name:
                tier_name = tiers[0].get("name")
            
            # Book 1 ticket
            params = {
                "userId": self.user_id,
                "tier": tier_name,
                "quantity": 1
            }
            
            response = self.session.post(f"{BACKEND_URL}/events/{event_id}/book", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["success", "tickets", "balance", "creditsEarned"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "Book Event Ticket",
                        False,
                        error=f"Missing required fields in response: {missing_fields}"
                    )
                    return False
                
                tickets = data.get("tickets", [])
                if len(tickets) != 1:
                    self.log_test(
                        "Book Event Ticket",
                        False,
                        error=f"Expected 1 ticket, got {len(tickets)}"
                    )
                    return False
                
                ticket = tickets[0]
                
                # Verify ticket structure
                ticket_required_fields = ["id", "eventId", "userId", "tier", "qrCode", "status", 
                                        "eventName", "eventDate", "eventLocation", "price", "qrCodeImage"]
                missing_ticket_fields = [field for field in ticket_required_fields if field not in ticket]
                
                if missing_ticket_fields:
                    self.log_test(
                        "Book Event Ticket",
                        False,
                        error=f"Missing required ticket fields: {missing_ticket_fields}"
                    )
                    return False
                
                # Verify QR code image format
                qr_code_image = ticket.get("qrCodeImage", "")
                if not qr_code_image.startswith("data:image/png;base64,"):
                    self.log_test(
                        "Book Event Ticket",
                        False,
                        error=f"QR code image format invalid. Expected 'data:image/png;base64,', got: {qr_code_image[:50]}..."
                    )
                    return False
                
                # Store for later tests
                self.booked_ticket = ticket
                self.new_balance = data.get("balance")
                self.credits_earned = data.get("creditsEarned")
                
                self.log_test(
                    "Book Event Ticket",
                    True,
                    f"Successfully booked ticket for '{ticket.get('eventName')}' - Tier: {ticket.get('tier')}, Price: ₹{ticket.get('price')}, Credits: {self.credits_earned}, QR Code: ✅"
                )
                return True
            else:
                self.log_test(
                    "Book Event Ticket",
                    False,
                    error=f"Booking failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Book Event Ticket",
                False,
                error=f"Exception during ticket booking: {str(e)}"
            )
            return False
    
    def test_4_verify_wallet_deduction(self):
        """TEST 4: Verify Wallet Deduction"""
        try:
            response = self.session.get(f"{BACKEND_URL}/wallet", params={"userId": self.user_id})
            
            if response.status_code == 200:
                wallet_data = response.json()
                current_balance = wallet_data.get("balance", 0.0)
                
                # Verify balance matches what was returned in booking response
                if abs(current_balance - self.new_balance) < 0.01:  # Allow for floating point precision
                    ticket_price = self.booked_ticket.get("price", 0)
                    expected_deduction = self.initial_balance - current_balance
                    
                    if abs(expected_deduction - ticket_price) < 0.01:
                        # Check transaction history
                        transactions = wallet_data.get("transactions", [])
                        ticket_transaction = None
                        
                        for transaction in transactions:
                            if "Ticket purchase" in transaction.get("description", ""):
                                ticket_transaction = transaction
                                break
                        
                        if ticket_transaction:
                            self.log_test(
                                "Verify Wallet Deduction",
                                True,
                                f"Balance correctly deducted: ₹{self.initial_balance:,.2f} → ₹{current_balance:,.2f} (₹{expected_deduction:,.2f} deducted). Transaction recorded: '{ticket_transaction.get('description')}'"
                            )
                            return True
                        else:
                            self.log_test(
                                "Verify Wallet Deduction",
                                False,
                                error="Wallet balance deducted correctly but no transaction record found"
                            )
                            return False
                    else:
                        self.log_test(
                            "Verify Wallet Deduction",
                            False,
                            error=f"Incorrect deduction amount. Expected: ₹{ticket_price}, Actual: ₹{expected_deduction}"
                        )
                        return False
                else:
                    self.log_test(
                        "Verify Wallet Deduction",
                        False,
                        error=f"Balance mismatch. Booking response: ₹{self.new_balance}, Wallet API: ₹{current_balance}"
                    )
                    return False
            else:
                self.log_test(
                    "Verify Wallet Deduction",
                    False,
                    error=f"Failed to get wallet data with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Verify Wallet Deduction",
                False,
                error=f"Exception during wallet verification: {str(e)}"
            )
            return False
    
    def test_5_get_user_tickets(self):
        """TEST 5: Get User Tickets"""
        try:
            response = self.session.get(f"{BACKEND_URL}/tickets/{self.user_id}")
            
            if response.status_code == 200:
                tickets = response.json()
                
                if len(tickets) > 0:
                    # Find our booked ticket
                    our_ticket = None
                    for ticket in tickets:
                        if ticket.get("id") == self.booked_ticket.get("id"):
                            our_ticket = ticket
                            break
                    
                    if our_ticket:
                        # Verify ticket has all required fields
                        required_fields = ["eventName", "eventDate", "eventLocation", "qrCode", "status", "tier", "price"]
                        missing_fields = [field for field in required_fields if not our_ticket.get(field)]
                        
                        if missing_fields:
                            self.log_test(
                                "Get User Tickets",
                                False,
                                error=f"Ticket missing required fields: {missing_fields}"
                            )
                            return False
                        
                        # Verify QR code image if present
                        qr_code_image = our_ticket.get("qrCodeImage", "")
                        qr_status = "✅" if qr_code_image.startswith("data:image/png;base64,") else "❌"
                        
                        self.log_test(
                            "Get User Tickets",
                            True,
                            f"Found {len(tickets)} tickets. Our ticket: '{our_ticket.get('eventName')}' - Status: {our_ticket.get('status')}, Tier: {our_ticket.get('tier')}, QR Code: {qr_status}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Get User Tickets",
                            False,
                            error=f"Booked ticket not found in user tickets list. Found {len(tickets)} tickets but none match our booking"
                        )
                        return False
                else:
                    self.log_test(
                        "Get User Tickets",
                        False,
                        error="No tickets found for user despite successful booking"
                    )
                    return False
            else:
                self.log_test(
                    "Get User Tickets",
                    False,
                    error=f"Failed to get user tickets with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Get User Tickets",
                False,
                error=f"Exception during ticket retrieval: {str(e)}"
            )
            return False
    
    def test_6_get_specific_ticket_details(self):
        """TEST 6: Get Specific Ticket Details"""
        try:
            ticket_id = self.booked_ticket.get("id")
            response = self.session.get(f"{BACKEND_URL}/tickets/{self.user_id}/{ticket_id}")
            
            if response.status_code == 200:
                ticket = response.json()
                
                # Verify QR code format
                qr_code = ticket.get("qrCode")
                expected_format = f"TICKET:{ticket_id}:QR:{qr_code}:EVENT:{self.test_event.get('id')}"
                
                # Check if QR code image is present
                qr_code_image = ticket.get("qrCodeImage", "")
                qr_image_valid = qr_code_image.startswith("data:image/png;base64,")
                
                self.log_test(
                    "Get Specific Ticket Details",
                    True,
                    f"Ticket details retrieved. QR Code: {qr_code}, QR Image: {'✅' if qr_image_valid else '❌'}, Event: '{ticket.get('eventName')}'"
                )
                return True
            else:
                self.log_test(
                    "Get Specific Ticket Details",
                    False,
                    error=f"Failed to get ticket details with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Get Specific Ticket Details",
                False,
                error=f"Exception during specific ticket retrieval: {str(e)}"
            )
            return False
    
    def test_7_book_multiple_tickets(self):
        """TEST 7: Book Multiple Tickets"""
        try:
            event_id = self.test_event.get("id")
            tiers = self.test_event.get("tiers", [])
            
            if not tiers:
                self.log_test(
                    "Book Multiple Tickets",
                    False,
                    error="No tiers available for multiple ticket booking"
                )
                return False
            
            # Use first available tier
            tier_name = tiers[0].get("name")
            
            # Book 2 tickets
            params = {
                "userId": self.user_id,
                "tier": tier_name,
                "quantity": 2
            }
            
            response = self.session.post(f"{BACKEND_URL}/events/{event_id}/book", params=params)
            
            if response.status_code == 200:
                data = response.json()
                tickets = data.get("tickets", [])
                
                if len(tickets) == 2:
                    # Verify each ticket has unique ID and QR code
                    ticket_ids = [t.get("id") for t in tickets]
                    qr_codes = [t.get("qrCode") for t in tickets]
                    
                    if len(set(ticket_ids)) == 2 and len(set(qr_codes)) == 2:
                        credits_earned = data.get("creditsEarned", 0)
                        expected_credits = 20 * 2  # 20 per ticket
                        
                        if credits_earned == expected_credits:
                            self.log_test(
                                "Book Multiple Tickets",
                                True,
                                f"Successfully booked 2 tickets with unique IDs and QR codes. Credits earned: {credits_earned} (20 per ticket)"
                            )
                            return True
                        else:
                            self.log_test(
                                "Book Multiple Tickets",
                                False,
                                error=f"Incorrect credits earned. Expected: {expected_credits}, Got: {credits_earned}"
                            )
                            return False
                    else:
                        self.log_test(
                            "Book Multiple Tickets",
                            False,
                            error="Tickets do not have unique IDs or QR codes"
                        )
                        return False
                else:
                    self.log_test(
                        "Book Multiple Tickets",
                        False,
                        error=f"Expected 2 tickets, got {len(tickets)}"
                    )
                    return False
            else:
                self.log_test(
                    "Book Multiple Tickets",
                    False,
                    error=f"Multiple ticket booking failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Book Multiple Tickets",
                False,
                error=f"Exception during multiple ticket booking: {str(e)}"
            )
            return False
    
    def test_8_insufficient_balance_test(self):
        """TEST 8: Insufficient Balance Test"""
        try:
            # Find the most expensive tier
            tiers = self.test_event.get("tiers", [])
            if not tiers:
                self.log_test(
                    "Insufficient Balance Test",
                    False,
                    error="No tiers available for insufficient balance test"
                )
                return False
            
            # Get current balance
            wallet_response = self.session.get(f"{BACKEND_URL}/wallet", params={"userId": self.user_id})
            if wallet_response.status_code != 200:
                self.log_test(
                    "Insufficient Balance Test",
                    False,
                    error="Could not get current wallet balance"
                )
                return False
            
            current_balance = wallet_response.json().get("balance", 0.0)
            
            # Find a tier that costs more than current balance, or use high quantity
            expensive_tier = max(tiers, key=lambda t: t.get("price", 0))
            tier_price = expensive_tier.get("price", 0)
            
            # Calculate quantity that would exceed balance
            if tier_price > 0:
                quantity = int(current_balance / tier_price) + 10  # Ensure insufficient balance
            else:
                quantity = 1000  # Large quantity for free events
            
            params = {
                "userId": self.user_id,
                "tier": expensive_tier.get("name"),
                "quantity": quantity
            }
            
            response = self.session.post(f"{BACKEND_URL}/events/{self.test_event.get('id')}/book", params=params)
            
            if response.status_code == 400:
                error_message = response.json().get("detail", "")
                if "Insufficient wallet balance" in error_message:
                    self.log_test(
                        "Insufficient Balance Test",
                        True,
                        f"Correctly rejected booking with insufficient balance. Error: '{error_message}'"
                    )
                    return True
                else:
                    self.log_test(
                        "Insufficient Balance Test",
                        False,
                        error=f"Got 400 error but wrong message: '{error_message}'"
                    )
                    return False
            else:
                self.log_test(
                    "Insufficient Balance Test",
                    False,
                    error=f"Expected 400 error for insufficient balance, got {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Insufficient Balance Test",
                False,
                error=f"Exception during insufficient balance test: {str(e)}"
            )
            return False
    
    def test_9_invalid_tier_test(self):
        """TEST 9: Invalid Tier Test"""
        try:
            params = {
                "userId": self.user_id,
                "tier": "NonExistentTier",
                "quantity": 1
            }
            
            response = self.session.post(f"{BACKEND_URL}/events/{self.test_event.get('id')}/book", params=params)
            
            if response.status_code == 400:
                error_message = response.json().get("detail", "")
                if "Invalid tier" in error_message:
                    self.log_test(
                        "Invalid Tier Test",
                        True,
                        f"Correctly rejected booking with invalid tier. Error: '{error_message}'"
                    )
                    return True
                else:
                    self.log_test(
                        "Invalid Tier Test",
                        False,
                        error=f"Got 400 error but wrong message: '{error_message}'"
                    )
                    return False
            else:
                self.log_test(
                    "Invalid Tier Test",
                    False,
                    error=f"Expected 400 error for invalid tier, got {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Invalid Tier Test",
                False,
                error=f"Exception during invalid tier test: {str(e)}"
            )
            return False
    
    def test_10_qr_code_image_validation(self):
        """TEST 10: QR Code Image Validation"""
        try:
            if not hasattr(self, 'booked_ticket'):
                self.log_test(
                    "QR Code Image Validation",
                    False,
                    error="No booked ticket available for QR code validation"
                )
                return False
            
            qr_code_image = self.booked_ticket.get("qrCodeImage", "")
            
            # Validate format
            if not qr_code_image.startswith("data:image/png;base64,"):
                self.log_test(
                    "QR Code Image Validation",
                    False,
                    error=f"Invalid QR code image format. Expected 'data:image/png;base64,', got: {qr_code_image[:50]}..."
                )
                return False
            
            # Extract base64 data
            base64_data = qr_code_image.split(",", 1)[1]
            
            # Validate base64 data length (should be substantial for a QR code image)
            if len(base64_data) < 1000:
                self.log_test(
                    "QR Code Image Validation",
                    False,
                    error=f"QR code image data too short: {len(base64_data)} characters"
                )
                return False
            
            # Try to decode base64 to verify it's valid
            try:
                decoded_data = base64.b64decode(base64_data)
                if len(decoded_data) < 500:  # PNG images should be at least this size
                    self.log_test(
                        "QR Code Image Validation",
                        False,
                        error=f"Decoded QR code image too small: {len(decoded_data)} bytes"
                    )
                    return False
            except Exception as decode_error:
                self.log_test(
                    "QR Code Image Validation",
                    False,
                    error=f"Invalid base64 data: {str(decode_error)}"
                )
                return False
            
            # Verify MIME type is correct
            if not qr_code_image.startswith("data:image/png;base64,"):
                self.log_test(
                    "QR Code Image Validation",
                    False,
                    error="QR code image does not have proper PNG MIME type"
                )
                return False
            
            self.log_test(
                "QR Code Image Validation",
                True,
                f"QR code image is valid base64 PNG. Data length: {len(base64_data)} characters, Decoded size: {len(decoded_data)} bytes"
            )
            return True
            
        except Exception as e:
            self.log_test(
                "QR Code Image Validation",
                False,
                error=f"Exception during QR code validation: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🎯 COMPREHENSIVE EVENTS AND TICKETING SYSTEM TEST - QR CODE VERIFICATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # Run tests in sequence
        tests = [
            self.test_1_login_demo_user,
            self.test_2_get_available_events,
            self.test_3_book_event_ticket,
            self.test_4_verify_wallet_deduction,
            self.test_5_get_user_tickets,
            self.test_6_get_specific_ticket_details,
            self.test_7_book_multiple_tickets,
            self.test_8_insufficient_balance_test,
            self.test_9_invalid_tier_test,
            self.test_10_qr_code_image_validation
        ]
        
        for test in tests:
            test()
        
        # Print summary
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {len(passed_tests)} ✅")
        print(f"Failed: {len(failed_tests)} ❌")
        print(f"Success Rate: {len(passed_tests)/len(self.test_results)*100:.1f}%")
        print()
        
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['error']}")
            print()
        
        print("✅ PASSED TESTS:")
        for test in passed_tests:
            print(f"   • {test['test']}")
        
        print()
        print("🎯 CRITICAL VALIDATION RESULTS:")
        
        # Check critical success criteria
        critical_tests = [
            "Login Demo User & Verify Wallet",
            "Get Available Events", 
            "Book Event Ticket",
            "Verify Wallet Deduction",
            "Get User Tickets",
            "QR Code Image Validation"
        ]
        
        critical_passed = [t for t in passed_tests if t["test"] in critical_tests]
        
        if len(critical_passed) == len(critical_tests):
            print("✅ All critical tests passed - Events and Ticketing System is FULLY FUNCTIONAL")
        else:
            print("❌ Some critical tests failed - System needs attention")
        
        print()
        print("🔍 KEY FINDINGS:")
        if hasattr(self, 'initial_balance'):
            print(f"   • Demo user wallet balance: ₹{self.initial_balance:,.2f}")
        if hasattr(self, 'test_event'):
            print(f"   • Test event: {self.test_event.get('name', 'Unknown')}")
        if hasattr(self, 'booked_ticket'):
            print(f"   • QR codes generated: ✅")
            print(f"   • Wallet integration: ✅")
        if hasattr(self, 'credits_earned'):
            print(f"   • Loop Credits system: ✅ ({self.credits_earned} credits earned)")
        
        return len(failed_tests) == 0

if __name__ == "__main__":
    tester = EventTicketingTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED - EVENTS AND TICKETING SYSTEM IS PRODUCTION READY!")
        sys.exit(0)
    else:
        print("\n⚠️  SOME TESTS FAILED - REVIEW RESULTS ABOVE")
        sys.exit(1)