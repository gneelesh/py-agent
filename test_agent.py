"""
Unit tests for the Flight Search AI Agent
"""

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_memory_manager():
    """Test MemoryManager functionality."""
    print("Testing MemoryManager...")
    
    from memory_manager import MemoryManager
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        mm = MemoryManager(tmpdir)
        
        # Test saving flight data
        test_flights = [
            {
                'source': 'test',
                'price': 500,
                'departure_date': '2026-06-15',
                'return_date': '2026-07-01'
            }
        ]
        
        timestamp = datetime.now().isoformat()
        mm.save_flight_data(timestamp, test_flights)
        
        # Verify file was created
        assert (Path(tmpdir) / "flights_history.json").exists(), "flights_history.json not created"
        
        # Test retrieving data
        latest = mm.get_latest_flights()
        assert latest is not None, "Failed to retrieve latest flights"
        assert len(latest) == 1, f"Expected 1 flight, got {len(latest)}"
        assert latest[0]['price'] == 500, "Price mismatch"
        
        # Test saving analysis
        test_analysis = {
            'recommendation': 'Book now',
            'reasoning': 'Good price'
        }
        mm.save_analysis(timestamp, test_analysis)
        
        # Verify analysis file was created
        assert (Path(tmpdir) / "analysis_history.json").exists(), "analysis_history.json not created"
        
        # Test retrieving analysis
        latest_analysis = mm.get_latest_analysis()
        assert latest_analysis is not None, "Failed to retrieve latest analysis"
        assert latest_analysis['recommendation'] == 'Book now', "Analysis mismatch"
        
        # Test price tracking
        price_data = mm.get_historical_prices()
        assert price_data is not None, "Failed to retrieve price history"
        
    print("✓ MemoryManager tests passed")


def test_configuration_structure():
    """Test that configuration files are properly structured."""
    print("Testing configuration files...")
    
    # Test .env.example
    env_example_path = Path(__file__).parent / ".env.example"
    assert env_example_path.exists(), ".env.example not found"
    
    # Read and verify key variables are present
    with open(env_example_path) as f:
        content = f.read()
        required_vars = [
            'GROK_API_KEY',
            'DEPARTURE_AIRPORT',
            'DESTINATION_AIRPORT',
            'DEPARTURE_DATE_START',
            'RETURN_DATE_START'
        ]
        for var in required_vars:
            assert var in content, f"Required variable {var} not found in .env.example"
    
    print("✓ Configuration tests passed")


def test_dockerfile_structure():
    """Test that Dockerfile is properly structured."""
    print("Testing Dockerfile...")
    
    dockerfile_path = Path(__file__).parent / "Dockerfile"
    assert dockerfile_path.exists(), "Dockerfile not found"
    
    with open(dockerfile_path) as f:
        content = f.read()
        required_elements = [
            'FROM python',
            'WORKDIR /app',
            'COPY requirements.txt',
            'RUN pip install',
            'CMD ["python", "agent.py"]'
        ]
        for element in required_elements:
            assert element in content, f"Required element '{element}' not found in Dockerfile"
    
    print("✓ Dockerfile tests passed")


def test_requirements_file():
    """Test that requirements.txt contains necessary packages."""
    print("Testing requirements.txt...")
    
    req_path = Path(__file__).parent / "requirements.txt"
    assert req_path.exists(), "requirements.txt not found"
    
    with open(req_path) as f:
        content = f.read()
        required_packages = [
            'requests',
            'selenium',
            'schedule',
            'openai',
            'python-dotenv'
        ]
        for package in required_packages:
            assert package in content, f"Required package '{package}' not found in requirements.txt"
    
    print("✓ Requirements tests passed")


def test_agent_structure():
    """Test that agent.py has proper structure."""
    print("Testing agent.py structure...")
    
    agent_path = Path(__file__).parent / "agent.py"
    assert agent_path.exists(), "agent.py not found"
    
    with open(agent_path) as f:
        content = f.read()
        required_elements = [
            'class FlightAgent',
            'def search_flights',
            'def analyze_flights',
            'def run_daily_search',
            'def start',
            'if __name__ == "__main__"'
        ]
        for element in required_elements:
            assert element in content, f"Required element '{element}' not found in agent.py"
    
    print("✓ Agent structure tests passed")


def run_all_tests():
    """Run all tests."""
    print("=" * 50)
    print("Running Flight Search Agent Tests")
    print("=" * 50)
    print()
    
    tests = [
        test_configuration_structure,
        test_dockerfile_structure,
        test_requirements_file,
        test_agent_structure,
        test_memory_manager,
    ]
    
    failed = []
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed.append(test.__name__)
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed.append(test.__name__)
    
    print()
    print("=" * 50)
    if not failed:
        print("✓ All tests passed!")
        return 0
    else:
        print(f"✗ {len(failed)} test(s) failed:")
        for name in failed:
            print(f"  - {name}")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
