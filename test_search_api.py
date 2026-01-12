"""
Search API Integration Tests
Demonstrates all search endpoints with working examples
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/search"
HEADERS = {
    "Authorization": "Bearer YOUR_JWT_TOKEN",
    "Content-Type": "application/json"
}

class SearchAPITester:
    
    @staticmethod
    def test_full_text_search():
        """Test 1: Full-Text Keyword Search"""
        print("\n" + "="*60)
        print("TEST 1: Full-Text Keyword Search")
        print("="*60)
        
        url = f"{BASE_URL}/?q=service%20agreement&limit=10"
        response = requests.get(url, headers=HEADERS)
        
        print(f"Endpoint: GET {url}")
        print(f"Status: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
        assert response.status_code == 200
        assert "results" in response.json()
        assert response.json()["search_type"] == "full_text"
        assert response.json()["strategy"] == "PostgreSQL FTS + GIN Index"
        print("✓ PASSED")
    
    @staticmethod
    def test_semantic_search():
        """Test 2: Semantic Search with Embeddings"""
        print("\n" + "="*60)
        print("TEST 2: Semantic Search")
        print("="*60)
        
        url = f"{BASE_URL}/semantic/?q=payment%20terms&similarity_threshold=0.6&limit=10"
        response = requests.get(url, headers=HEADERS)
        
        print(f"Endpoint: GET {url}")
        print(f"Status: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
        assert response.status_code == 200
        assert response.json()["search_type"] == "semantic"
        assert response.json()["strategy"] == "pgvector + Embeddings"
        assert "threshold" in response.json()
        print("✓ PASSED")
    
    @staticmethod
    def test_hybrid_search():
        """Test 3: Hybrid Search (FTS + Semantic)"""
        print("\n" + "="*60)
        print("TEST 3: Hybrid Search")
        print("="*60)
        
        url = f"{BASE_URL}/hybrid/"
        payload = {
            "query": "renewal contract",
            "limit": 10,
            "weights": {
                "full_text": 0.6,
                "semantic": 0.4
            }
        }
        
        response = requests.post(url, json=payload, headers=HEADERS)
        
        print(f"Endpoint: POST {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print(f"Status: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
        assert response.status_code == 200
        assert response.json()["search_type"] == "hybrid"
        assert "full_text_score" in str(response.json()["results"])
        assert "semantic_score" in str(response.json()["results"])
        print("✓ PASSED")
    
    @staticmethod
    def test_advanced_search():
        """Test 4: Advanced Search with Filters"""
        print("\n" + "="*60)
        print("TEST 4: Advanced Search with Filters")
        print("="*60)
        
        url = f"{BASE_URL}/advanced/"
        payload = {
            "query": "contract",
            "filters": {
                "entity_type": "contract",
                "date_from": (datetime.now() - timedelta(days=365)).isoformat(),
                "date_to": datetime.now().isoformat(),
                "keywords": ["payment", "renewal"],
                "status": "active"
            },
            "limit": 20
        }
        
        response = requests.post(url, json=payload, headers=HEADERS)
        
        print(f"Endpoint: POST {url}")
        print(f"Payload: {json.dumps(payload, indent=2, default=str)}")
        print(f"Status: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
        assert response.status_code == 200
        assert response.json()["search_type"] == "advanced"
        assert "filters_applied" in response.json()
        assert response.json()["strategy"] == "SQL WHERE clauses + Full-Text Search"
        print("✓ PASSED")
    
    @staticmethod
    def test_facets():
        """Test 5: Get Available Facets"""
        print("\n" + "="*60)
        print("TEST 5: Get Available Facets for Navigation")
        print("="*60)
        
        url = f"{BASE_URL}/facets/"
        response = requests.get(url, headers=HEADERS)
        
        print(f"Endpoint: GET {url}")
        print(f"Status: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
        assert response.status_code == 200
        result = response.json()
        assert "facets" in result
        assert "entity_types" in result["facets"]
        assert "keywords" in result["facets"]
        assert "date_range" in result["facets"]
        assert "total_documents" in result["facets"]
        print("✓ PASSED")
    
    @staticmethod
    def test_faceted_search():
        """Test 6: Faceted Search with Applied Filters"""
        print("\n" + "="*60)
        print("TEST 6: Faceted Search")
        print("="*60)
        
        url = f"{BASE_URL}/faceted/"
        payload = {
            "query": "",
            "facet_filters": {
                "entity_types": ["contract", "template"],
                "keywords": ["payment", "service"]
            },
            "limit": 20
        }
        
        response = requests.post(url, json=payload, headers=HEADERS)
        
        print(f"Endpoint: POST {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print(f"Status: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
        assert response.status_code == 200
        assert response.json()["search_type"] == "faceted"
        assert "applied_facets" in response.json()
        assert "available_facets" in response.json()
        print("✓ PASSED")
    
    @staticmethod
    def test_suggestions():
        """Test 7: Search Suggestions (Autocomplete)"""
        print("\n" + "="*60)
        print("TEST 7: Search Suggestions")
        print("="*60)
        
        url = f"{BASE_URL}/suggestions/?q=ser&limit=5"
        response = requests.get(url, headers=HEADERS)
        
        print(f"Endpoint: GET {url}")
        print(f"Status: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
        assert response.status_code == 200
        assert "suggestions" in response.json()
        assert "count" in response.json()
        assert isinstance(response.json()["suggestions"], list)
        print("✓ PASSED")
    
    @staticmethod
    def test_index_management():
        """Test 8: Index Management"""
        print("\n" + "="*60)
        print("TEST 8: Create/Update Search Index")
        print("="*60)
        
        url = f"{BASE_URL}/index/"
        payload = {
            "entity_type": "contract",
            "entity_id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "New Service Agreement 2024",
            "content": "This is a comprehensive service agreement...",
            "keywords": ["service", "agreement", "2024", "payment"]
        }
        
        response = requests.post(url, json=payload, headers=HEADERS)
        
        print(f"Endpoint: POST {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print(f"Status: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
        assert response.status_code in [200, 201]
        assert response.json()["success"] == True
        assert "index_id" in response.json()
        print("✓ PASSED")
    
    @staticmethod
    def test_analytics():
        """Test 9: Search Analytics"""
        print("\n" + "="*60)
        print("TEST 9: Search Analytics")
        print("="*60)
        
        url = f"{BASE_URL}/analytics/"
        response = requests.get(url, headers=HEADERS)
        
        print(f"Endpoint: GET {url}")
        print(f"Status: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
        assert response.status_code == 200
        result = response.json()
        assert "total_searches" in result
        assert "by_type" in result
        assert "avg_response_time_ms" in result
        assert all(t in result["by_type"] for t in ["full_text", "semantic", "hybrid", "faceted"])
        print("✓ PASSED")
    
    @staticmethod
    def test_error_handling():
        """Test 10: Error Handling"""
        print("\n" + "="*60)
        print("TEST 10: Error Handling")
        print("="*60)
        
        # Test 1: Empty query
        print("\n1. Testing empty query parameter...")
        url = f"{BASE_URL}/?q="
        response = requests.get(url, headers=HEADERS)
        print(f"   Status: {response.status_code}")
        assert response.status_code == 400
        print("   ✓ Correctly returned 400")
        
        # Test 2: Query too short
        print("\n2. Testing query too short...")
        url = f"{BASE_URL}/?q=a"
        response = requests.get(url, headers=HEADERS)
        print(f"   Status: {response.status_code}")
        assert response.status_code == 400
        print("   ✓ Correctly returned 400")
        
        # Test 3: Missing required fields in index creation
        print("\n3. Testing missing required fields...")
        url = f"{BASE_URL}/index/"
        payload = {
            "entity_type": "contract"
            # Missing: entity_id, title, content
        }
        response = requests.post(url, json=payload, headers=HEADERS)
        print(f"   Status: {response.status_code}")
        assert response.status_code == 400
        print("   ✓ Correctly returned 400")
        
        print("\n✓ ALL ERROR HANDLING TESTS PASSED")
    
    @staticmethod
    def run_all_tests():
        """Run all tests"""
        print("\n" + "="*60)
        print("SEARCH API COMPREHENSIVE TEST SUITE")
        print("="*60)
        
        try:
            SearchAPITester.test_full_text_search()
            SearchAPITester.test_semantic_search()
            SearchAPITester.test_hybrid_search()
            SearchAPITester.test_advanced_search()
            SearchAPITester.test_facets()
            SearchAPITester.test_faceted_search()
            SearchAPITester.test_suggestions()
            SearchAPITester.test_index_management()
            SearchAPITester.test_analytics()
            SearchAPITester.test_error_handling()
            
            print("\n" + "="*60)
            print("✓ ALL TESTS PASSED (10/10)")
            print("="*60)
            
        except AssertionError as e:
            print(f"\n✗ TEST FAILED: {str(e)}")
        except Exception as e:
            print(f"\n✗ ERROR: {str(e)}")


if __name__ == "__main__":
    SearchAPITester.run_all_tests()
