# 🔍 SEARCH SYSTEM QUICK START GUIDE

## Overview
The search system is fully operational with 9 API endpoints for different search strategies. All endpoints require JWT authentication.

---

## 📚 API Endpoints

### 1. Full-Text Search (Keyword Search)
**Endpoint:** `GET /api/search/?q=query`

Returns documents matching keywords using PostgreSQL Full-Text Search (FTS) with GIN indexes.

**Request:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/search/?q=service&limit=20"
```

**Response:**
```json
{
  "query": "service",
  "results": [
    {
      "id": "uuid",
      "title": "Service Agreement",
      "content": "...",
      "keywords": ["service", "agreement"],
      "relevance_score": 0.95,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "count": 1,
  "response_time_ms": 344
}
```

**Parameters:**
- `q` (required): Search query
- `limit` (optional): Max results (default: 20)

**Best For:** Legal terms, exact keywords, fast searches

---

### 2. Semantic Search (AI-Powered)
**Endpoint:** `GET /api/search/semantic/?q=query`

Returns semantically similar documents using Gemini API embeddings.

**Request:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/search/semantic/?q=agreement&limit=10"
```

**Response:**
```json
{
  "query": "agreement",
  "search_type": "semantic",
  "results": [
    {
      "id": "uuid",
      "title": "License Agreement",
      "similarity_score": 0.87,
      "embedding_model": "gemini"
    }
  ],
  "count": 1
}
```

**Best For:** Concept matching, semantic similarity, intelligent search

---

### 3. Hybrid Search (Best Results)
**Endpoint:** `POST /api/search/hybrid/`

Combines Full-Text Search (60%) + Semantic Search (40%) for best relevance.

**Request:**
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "contract"}' \
  "http://localhost:8000/api/search/hybrid/"
```

**Response:**
```json
{
  "query": "contract",
  "search_type": "hybrid",
  "results": [...],
  "count": 1,
  "ranking_formula": "(fts_score × 0.6) + (semantic_score × 0.4)"
}
```

**Best For:** Highest relevance results, balanced approach

---

### 4. Advanced Search (Filtered)
**Endpoint:** `POST /api/search/advanced/`

Full-text search with SQL filters for complex queries.

**Request:**
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "payment",
    "filters": {
      "entity_type": "contract",
      "keywords": ["payment", "terms"],
      "date_from": "2023-01-01",
      "date_to": "2024-12-31"
    },
    "limit": 20
  }' \
  "http://localhost:8000/api/search/advanced/"
```

**Supported Filters:**
- `entity_type`: Filter by document type (contract, etc.)
- `keywords`: Match specific keywords (array)
- `date_from`: Start date (ISO8601)
- `date_to`: End date (ISO8601)
- `status`: Document status from metadata

**Best For:** Complex queries with multiple criteria

---

### 5. Faceted Search (Navigation)
**Endpoint:** `POST /api/search/faceted/`

Search with facet-based navigation for exploration.

**Request:**
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "agreement",
    "facets": {
      "entity_types": ["contract"],
      "keywords": ["legal"]
    }
  }' \
  "http://localhost:8000/api/search/faceted/"
```

**Best For:** Guided search, facet exploration

---

### 6. Facets Navigation
**Endpoint:** `GET /api/search/facets/`

Get available facets for navigation without search.

**Request:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/search/facets/"
```

**Response:**
```json
{
  "facets": {
    "entity_types": [
      {"name": "contract", "count": 5},
      {"name": "agreement", "count": 3}
    ],
    "keywords": [
      {"name": "service", "count": 4},
      {"name": "payment", "count": 3}
    ],
    "total_documents": 8,
    "date_range": {
      "earliest": "2023-01-01T00:00:00Z",
      "latest": "2024-12-31T23:59:59Z"
    }
  }
}
```

**Best For:** Exploring available data

---

### 7. Autocomplete Suggestions
**Endpoint:** `GET /api/search/suggestions/?q=query`

Get autocomplete suggestions based on indexed content.

**Request:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/search/suggestions/?q=ser"
```

**Response:**
```json
{
  "query": "ser",
  "suggestions": [
    {"text": "service agreement", "frequency": 5},
    {"text": "service", "frequency": 3}
  ],
  "count": 2
}
```

**Best For:** Autocomplete in search UI

---

### 8. Search Index Management
**Endpoint:** `POST /api/search/index/` (Create)

Create or update a search index for a document.

**Request:**
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "contract",
    "entity_id": "00000000-0000-0000-0000-000000000001",
    "title": "Service Agreement",
    "content": "Full contract text...",
    "keywords": ["service", "agreement", "legal"]
  }' \
  "http://localhost:8000/api/search/index/"
```

**Response:**
```json
{
  "success": true,
  "message": "Index created",
  "index_id": "uuid"
}
```

**Delete Index:**
```bash
curl -X DELETE -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/search/index/00000000-0000-0000-0000-000000000001/"
```

**Best For:** Managing document indexes

---

### 9. Search Analytics
**Endpoint:** `GET /api/search/analytics/`

Get search analytics and performance metrics.

**Request:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/search/analytics/"
```

**Response:**
```json
{
  "total_searches": 12,
  "by_type": {
    "full_text": {
      "count": 3,
      "avg_response_time_ms": 450
    },
    "semantic": {
      "count": 2,
      "avg_response_time_ms": 550
    },
    "hybrid": {
      "count": 4,
      "avg_response_time_ms": 600
    }
  },
  "popular_queries": [
    "service",
    "agreement"
  ]
}
```

**Best For:** Monitoring and optimization

---

## 🔐 Authentication

All endpoints require JWT Bearer token authentication.

### Get Token
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }' \
  "http://localhost:8000/api/auth/login/"
```

### Use Token
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "http://localhost:8000/api/search/?q=test"
```

---

## ⚡ Performance Tips

### 1. Choose the Right Search Strategy
- **Keywords only** → Full-Text Search (fastest)
- **Concept matching** → Semantic Search (slower, more flexible)
- **Best results** → Hybrid Search (balanced)

### 2. Use Limits
- Always specify `limit` to avoid large result sets
- Default: 20, Maximum recommended: 100

### 3. Use Facets for Filtering
- Use facets instead of complex filters when possible
- Faceted search is highly optimized

### 4. Batch Operations
- For indexing multiple documents, use batch endpoints if available
- Reduces API overhead

---

## 🐛 Troubleshooting

### 401 Unauthorized
- Issue: Invalid or missing JWT token
- Solution: Get a fresh token via `/api/auth/login/`

### 404 Not Found
- Issue: Endpoint doesn't exist
- Solution: Verify the endpoint URL and method (GET/POST)

### 500 Internal Server Error
- Issue: Server error
- Solution: Check `/api/health/` and server logs

### No Results
- Issue: Search returns empty results
- Solution: Check that documents are indexed with correct keywords

### Slow Response Time
- Issue: Search taking > 1 second
- Solution: Use Full-Text Search instead of Semantic for large datasets

---

## 📊 Database Schema

### search_indices Table
Stores searchable documents with indexes.

```sql
CREATE TABLE search_indices (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  entity_type VARCHAR(50),
  entity_id UUID,
  title VARCHAR(255),
  content TEXT,
  keywords JSONB,
  metadata JSONB,
  search_vector TSVECTOR,  -- Full-text search index
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  indexed_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_search_vector ON search_indices USING GIN (search_vector);
CREATE INDEX idx_tenant_entity ON search_indices (tenant_id, entity_type);
```

### search_analytics Table
Tracks search performance and usage.

```sql
CREATE TABLE search_analytics (
  id UUID PRIMARY KEY,
  tenant_id UUID,
  user_id UUID,
  query VARCHAR(500),
  query_type VARCHAR(20),
  results_count INT,
  response_time_ms INT,
  clicked_result_id UUID,
  created_at TIMESTAMP
);
```

---

## 🚀 Deployment Checklist

Before deploying to production:

- [ ] Verify Gemini API key is set
- [ ] Configure PostgreSQL with GIN indexes
- [ ] Set up JWT secret key
- [ ] Configure CORS for frontend domain
- [ ] Set up logging and monitoring
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Test all 9 endpoints
- [ ] Verify authentication works
- [ ] Check response times
- [ ] Set up backups
- [ ] Configure rate limiting

---

## 📞 Support

For issues or questions:
1. Check the FINAL_TESTING_REPORT.md for detailed information
2. Review the API response error messages
3. Check Django server logs
4. Verify database connectivity

---

**System Status:** ✅ **FULLY OPERATIONAL**  
**Last Updated:** Today  
**All Endpoints:** 9/9 Working
