import sys
import os

# Add the current directory to sys.path to find the app module
sys.path.append(os.getcwd())

try:
    from app.schemas.auth import UserResponse
    print("Successfully imported UserResponse")
    
    # Mock user object with attributes
    class MockUser:
        def __init__(self):
            self.id = 1
            self.email = "test@example.com"
            self.full_name = "Test User"
            self.is_active = True
            self.created_at = None
            self.updated_at = None

    mock_user = MockUser()
    
    # This should work with Pydantic v2 and our refactored code
    response = UserResponse.model_validate(mock_user)
    print(f"Successfully validated model: {response}")
    print("Refactoring verified successfully!")

except Exception as e:
    print(f"Verification failed: {e}")
    import traceback
    traceback.print_exc()
