import pytest
import requests
import json
import os
from pathlib import Path


class TestCustosAPI:
    """Test suite for Custos API endpoints"""
    
    @classmethod
    def setup_class(cls):
        """Setup test configuration"""
        cls.base_url = os.environ.get('CUSTOS_URL', 'http://localhost:5555')
        cls.primary_token = os.environ.get('CUSTOS_PRIMARY_TOKEN')
        cls.emergency_token = os.environ.get('CUSTOS_EMERGENCY_TOKEN')
        
        if not cls.primary_token or not cls.emergency_token:
            pytest.skip("Tokens not provided. Set CUSTOS_PRIMARY_TOKEN and CUSTOS_EMERGENCY_TOKEN")
    
    def setup_method(self):
        """Ensure clean state before each test"""
        # Unlock server before each test to ensure consistent starting state
        headers = {
            'Authorization': f'Bearer {self.emergency_token}',
            'Content-Type': 'application/json'
        }
        requests.post(f"{self.base_url}/unlock", headers=headers)
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'locked' in data
        assert 'time' in data
        assert 'data_count' in data
    
    def test_store_data(self):
        """Test storing data"""
        headers = {
            'Authorization': f'Bearer {self.primary_token}',
            'Content-Type': 'application/json'
        }
        payload = {'data': 'test-secret-data-123'}
        
        response = requests.put(
            f"{self.base_url}/data/test-key",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data['status'] == 'stored'
    
    def test_retrieve_data(self):
        """Test retrieving stored data"""
        # First store data to retrieve
        headers = {
            'Authorization': f'Bearer {self.primary_token}',
            'Content-Type': 'application/json'
        }
        payload = {'data': 'test-secret-data-123'}
        
        store_response = requests.put(
            f"{self.base_url}/data/test-key",
            headers=headers,
            json=payload
        )
        assert store_response.status_code == 201
        
        # Now retrieve it
        headers = {'Authorization': f'Bearer {self.primary_token}'}
        
        response = requests.get(
            f"{self.base_url}/data/test-key",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['data'] == 'test-secret-data-123'
    
    def test_lock_server(self):
        """Test locking the server"""
        headers = {
            'Authorization': f'Bearer {self.emergency_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(f"{self.base_url}/lock", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'locked'
    
    def test_locked_retrieval_fails(self):
        """Test that data retrieval fails when locked"""
        # First store some data (server starts unlocked due to setup_method)
        headers = {
            'Authorization': f'Bearer {self.primary_token}',
            'Content-Type': 'application/json'
        }
        payload = {'data': 'test-data-for-lock-test'}
        
        store_response = requests.put(
            f"{self.base_url}/data/lock-test-key",
            headers=headers,
            json=payload
        )
        assert store_response.status_code == 201
        
        # Now lock the server
        headers = {
            'Authorization': f'Bearer {self.emergency_token}',
            'Content-Type': 'application/json'
        }
        lock_response = requests.post(f"{self.base_url}/lock", headers=headers)
        assert lock_response.status_code == 200
        
        # Now test that retrieval fails due to lock
        headers = {'Authorization': f'Bearer {self.primary_token}'}
        
        response = requests.get(
            f"{self.base_url}/data/lock-test-key",
            headers=headers
        )
        
        assert response.status_code == 423
        data = response.json()
        assert 'locked' in data['error'].lower()
    
    def test_unlock_server(self):
        """Test unlocking the server"""
        headers = {
            'Authorization': f'Bearer {self.emergency_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(f"{self.base_url}/unlock", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'unlocked'
    
    def test_unlocked_retrieval_works(self):
        """Test that data can be stored and retrieved when unlocked"""
        # Ensure server is unlocked first
        headers = {
            'Authorization': f'Bearer {self.emergency_token}',
            'Content-Type': 'application/json'
        }
        unlock_response = requests.post(f"{self.base_url}/unlock", headers=headers)
        assert unlock_response.status_code == 200
        
        # Verify server is unlocked by checking health
        health_response = requests.get(f"{self.base_url}/health")
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert health_data['locked'] == False
        
        # Store some new data to verify unlock works
        headers = {
            'Authorization': f'Bearer {self.primary_token}',
            'Content-Type': 'application/json'
        }
        payload = {'data': 'unlocked-test-data'}
        
        store_response = requests.put(
            f"{self.base_url}/data/unlock-test-key",
            headers=headers,
            json=payload
        )
        assert store_response.status_code == 201
        
        # Retrieve the data we just stored
        headers = {'Authorization': f'Bearer {self.primary_token}'}
        response = requests.get(
            f"{self.base_url}/data/unlock-test-key",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['data'] == 'unlocked-test-data'
    
    def test_unauthorized_access(self):
        """Test that unauthorized requests are rejected"""
        response = requests.get(f"{self.base_url}/data/test-key")
        assert response.status_code == 401
        
        headers = {'Authorization': 'Bearer invalid-token'}
        response = requests.get(f"{self.base_url}/data/test-key", headers=headers)
        assert response.status_code == 401
    
    def test_nonexistent_data(self):
        """Test retrieving non-existent data"""
        # Ensure server is unlocked for this test
        headers = {
            'Authorization': f'Bearer {self.emergency_token}',
            'Content-Type': 'application/json'
        }
        requests.post(f"{self.base_url}/unlock", headers=headers)
        
        # Now test retrieving non-existent data
        headers = {'Authorization': f'Bearer {self.primary_token}'}
        
        response = requests.get(
            f"{self.base_url}/data/nonexistent-key",
            headers=headers
        )
        
        assert response.status_code == 404
        data = response.json()
        assert 'not found' in data['error'].lower()