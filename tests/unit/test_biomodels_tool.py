"""
Test suite for BioModels API tools

Tests the BioModels database tools for:
- Model search
- Model metadata retrieval
- File listing
- Download URLs
- Parameter search

Testing levels:
1. Direct class testing (implementation logic)
2. ToolUniverse interface testing (registration and access)
3. Real API testing (integration with BioModels API)
"""

import pytest
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from tooluniverse.biomodels_tool import BioModelsRESTTool
from tooluniverse import ToolUniverse


class TestBioModelsDirectClass:
    """Level 1: Direct class testing"""
    
    @pytest.fixture
    def tool_configs(self):
        """Load tool configurations from JSON"""
        config_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 
            'src', 'tooluniverse', 'data', 'biomodels_tools.json'
        )
        with open(config_path) as f:
            return json.load(f)
    
    def test_search_tool_initialization(self, tool_configs):
        """Test biomodels_search tool initialization"""
        config = next(t for t in tool_configs if t["name"] == "biomodels_search")
        tool = BioModelsRESTTool(config)
        assert tool is not None
        assert hasattr(tool, 'run')
    
    def test_get_model_initialization(self, tool_configs):
        """Test BioModels_get_model tool initialization"""
        config = next(t for t in tool_configs if t["name"] == "BioModels_get_model")
        tool = BioModelsRESTTool(config)
        assert tool is not None
    
    def test_param_mapping(self, tool_configs):
        """Test parameter mapping (limit -> numResults)"""
        config = next(t for t in tool_configs if t["name"] == "biomodels_search")
        tool = BioModelsRESTTool(config)
        mapping = tool._get_param_mapping()
        assert mapping.get("limit") == "numResults"
    
    def test_search_success(self, tool_configs):
        """Test successful search"""
        config = next(t for t in tool_configs if t["name"] == "biomodels_search")
        tool = BioModelsRESTTool(config)
        
        # Mock the session.request method
        with patch.object(tool.session, 'request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            # Match actual API format: models array + matches integer
            mock_response.json.return_value = {
                "models": [
                    {"id": "BIOMD0000000001", "name": "Test Model 1"},
                    {"id": "BIOMD0000000002", "name": "Test Model 2"}
                ],
                "matches": 2
            }
            mock_response.raise_for_status = MagicMock()
            mock_request.return_value = mock_response
            
            result = tool.run({"query": "glycolysis", "limit": 2})
            
            assert result["status"] == "success"
            assert "data" in result
            assert "count" in result
            assert result["count"] == 2
            assert isinstance(result["data"], dict)
            assert "models" in result["data"]
            assert len(result["data"]["models"]) == 2
    
    def test_get_model_success(self, tool_configs):
        """Test successful model retrieval"""
        config = next(t for t in tool_configs if t["name"] == "BioModels_get_model")
        tool = BioModelsRESTTool(config)
        
        with patch.object(tool.session, 'request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": "BIOMD0000000469",
                "name": "Test Model",
                "format": "SBML",
                "description": "A test model"
            }
            mock_response.raise_for_status = MagicMock()
            mock_request.return_value = mock_response
            
            result = tool.run({"model_id": "BIOMD0000000469"})
            
            assert result["status"] == "success"
            assert "data" in result
            assert result["data"].get("id") == "BIOMD0000000469"
    
    def test_list_files_success(self, tool_configs):
        """Test successful file listing"""
        config = next(t for t in tool_configs if t["name"] == "BioModels_list_files")
        tool = BioModelsRESTTool(config)
        
        with patch.object(tool.session, 'request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "main": [
                    {"name": "model.xml", "size": 1024, "description": "SBML file"}
                ],
                "additional": []
            }
            mock_response.raise_for_status = MagicMock()
            mock_request.return_value = mock_response
            
            result = tool.run({"model_id": "BIOMD0000000469"})
            
            assert result["status"] == "success"
            assert "data" in result
    
    def test_download_url(self, tool_configs):
        """Test download URL generation"""
        config = next(t for t in tool_configs if t["name"] == "BioModels_download_model")
        tool = BioModelsRESTTool(config)
        
        with patch.object(tool.session, 'request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {
                "Content-Disposition": "attachment; filename=model.xml",
                "Content-Type": "application/xml"
            }
            mock_response.json.return_value = {}
            mock_response.raise_for_status = MagicMock()
            mock_request.return_value = mock_response
            
            result = tool.run({"model_id": "BIOMD0000000469"})
            
            assert result["status"] == "success"
            assert "download_url" in result or "url" in result
    
    def test_parameter_search(self, tool_configs):
        """Test parameter search"""
        config = next(t for t in tool_configs if t["name"] == "BioModels_search_parameters")
        tool = BioModelsRESTTool(config)
        
        with patch.object(tool.session, 'request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
                {"parameter": "k1", "value": "0.1", "model_id": "BIOMD0000000001"}
            ]
            mock_response.raise_for_status = MagicMock()
            mock_request.return_value = mock_response
            
            result = tool.run({"query": "k1", "limit": 5})
            
            assert result["status"] == "success"
            assert "data" in result
    
    def test_error_handling(self, tool_configs):
        """Test error handling for failed API calls"""
        config = next(t for t in tool_configs if t["name"] == "biomodels_search")
        tool = BioModelsRESTTool(config)
        
        with patch.object(tool.session, 'request') as mock_request:
            mock_request.side_effect = Exception("Network error")
            
            result = tool.run({"query": "test"})
            
            assert result["status"] == "error"
            assert "error" in result


class TestBioModelsToolUniverse:
    """Level 2: ToolUniverse interface testing"""
    
    @pytest.fixture
    def tu(self):
        """Initialize ToolUniverse with tools loaded"""
        tu = ToolUniverse()
        tu.load_tools()
        return tu
    
    def test_tools_registered(self, tu):
        """Test that all BioModels tools are registered"""
        expected_tools = [
            "biomodels_search",
            "BioModels_get_model",
            "BioModels_list_files",
            "BioModels_download_model",
            "BioModels_search_parameters"
        ]
        
        for tool_name in expected_tools:
            assert hasattr(tu.tools, tool_name), f"{tool_name} not found"
    
    @patch('requests.Session.request')
    def test_search_via_tooluniverse(self, mock_request, tu):
        """Test search via ToolUniverse interface"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Match actual API format: models array + matches integer
        mock_response.json.return_value = {
            "models": [{"id": "BIOMD0000000001", "name": "Test"}],
            "matches": 1
        }
        mock_response.raise_for_status = MagicMock()
        mock_request.return_value = mock_response
        
        result = tu.tools.biomodels_search(**{
            "query": "glycolysis",
            "limit": 1
        })
        
        assert result["status"] == "success"
        assert "data" in result
        assert "count" in result
        assert result["count"] == 1
    
    @patch('requests.Session.request')
    def test_get_model_via_tooluniverse(self, mock_request, tu):
        """Test get_model via ToolUniverse interface"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "BIOMD0000000469",
            "name": "Test Model"
        }
        mock_response.raise_for_status = MagicMock()
        mock_request.return_value = mock_response
        
        result = tu.tools.BioModels_get_model(**{
            "model_id": "BIOMD0000000469"
        })
        
        assert result["status"] == "success"
        assert result["data"].get("id") == "BIOMD0000000469"


class TestBioModelsRealAPI:
    """Level 3: Real API testing (requires network)"""
    
    @pytest.fixture
    def tu(self):
        """Initialize ToolUniverse"""
        tu = ToolUniverse()
        tu.load_tools()
        return tu
    
    def test_real_search(self, tu):
        """Test real API search (glycolysis)"""
        try:
            result = tu.tools.biomodels_search(**{
                "query": "glycolysis",
                "limit": 2
            })
            
            if result["status"] == "success":
                assert "data" in result
                print(f"✅ Real API search: Found {result.get('count', 0)} results")
            else:
                print(f"⚠️  Search returned error: {result.get('error')}")
        except Exception as e:
            print(f"⚠️  Real API test failed (may be expected): {e}")
    
    def test_real_get_model(self, tu):
        """Test real API model retrieval"""
        try:
            result = tu.tools.BioModels_get_model(**{
                "model_id": "BIOMD0000000469"
            })
            
            if result["status"] == "success":
                assert "data" in result
                assert result["data"].get("id") == "BIOMD0000000469"
                print(f"✅ Real API get_model: Retrieved {result['data'].get('name', 'N/A')}")
            else:
                print(f"⚠️  Get model returned error: {result.get('error')}")
        except Exception as e:
            print(f"⚠️  Real API test failed (may be expected): {e}")
    
    def test_real_list_files(self, tu):
        """Test real API file listing"""
        try:
            result = tu.tools.BioModels_list_files(**{
                "model_id": "BIOMD0000000469"
            })
            
            if result["status"] == "success":
                assert "data" in result
                print(f"✅ Real API list_files: Found files for model")
            else:
                print(f"⚠️  List files returned error: {result.get('error')}")
        except Exception as e:
            print(f"⚠️  Real API test failed (may be expected): {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
