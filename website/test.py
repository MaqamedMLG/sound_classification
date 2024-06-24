import requests
import time

def test_login():
    print("Testing Login...")
    url = "http://127.0.0.1:5000/login"
    login_data = {
        "email": "testuser@example.com",
        "password": "password123456789"
    }

    start_time = time.time()  # Start timing before request
    response = requests.post(url, data=login_data)
    elapsed_time = time.time() - start_time  # Calculate elapsed time

    print(f"Login request completed in {elapsed_time:.2f} seconds.")
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, "Failed to log in, status code was not 200."
    assert "Error" not in response.text, "Login failed due to an error."

def test_signup():
    print("Testing Signup...")
    url = "http://127.0.0.1:5000/sign-up"
    signup_data = {
        "email": "newuser@example.com",
        "firstName": "Test",
        "password1": "password123456789",
        "password2": "password123456789"
    }

    start_time = time.time()  # Start timing before request
    response = requests.post(url, data=signup_data)
    elapsed_time = time.time() - start_time  # Calculate elapsed time

    print(f"Signup request completed in {elapsed_time:.2f} seconds.")
    print(f"Status Code: {response.status_code}")

    assert response.status_code == 200, "Failed to sign up, status code was not 200."
    assert "Error" not in response.text, "Signup failed due to an error: " + response.text

def test_admin_login():
    print("Testing Admin Login...")
    url = "http://127.0.0.1:5000/login"
    admin_data = {
        "email": "admin@gmail.com",
        "password": "Kaunas2024LT"
    }

    start_time = time.time()  # Start timing before the request
    response = requests.post(url, data=admin_data)
    elapsed_time = time.time() - start_time  # Calculate elapsed time

    print(f"Admin login request completed in {elapsed_time:.2f} seconds.")
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, "Failed to log in as admin, status code was not 200."
    assert "Admin" in response.text, "Login failed or incorrect landing page for admin."


def test_logout():
    print("Testing Logout...")
    # First, perform a login to obtain any session cookies or tokens if needed
    login_url = "http://127.0.0.1:5000/login"
    login_data = {
        "email": "testuser@example.com",
        "password": "password123456789"
    }

    # Start timing before request
    start_time = time.time()
    session = requests.Session()  # Use a session object to maintain cookies between requests
    login_response = session.post(login_url, data=login_data)
    assert login_response.status_code == 200, "Login failed, cannot test logout."

    # Now, attempt to logout
    logout_url = "http://127.0.0.1:5000/logout"
    response = session.get(logout_url)  # Assuming logout is a GET request; adjust if it's a POST
    elapsed_time = time.time() - start_time

    print(f"Logout request completed in {elapsed_time:.2f} seconds.")
    print(f"Status Code: {response.status_code}")
    assert response.status_code in [200, 302], "Failed to log out, status code was not 200 or 302."
    assert "/login" in response.url or "Login" in response.text, "Logout did not redirect to the login page."


def test_change_profile():
    print("Testing Profile Update...")
    login_url = "http://127.0.0.1:5000/login"
    profile_url = "http://127.0.0.1:5000/profile"
    login_data = {
        "email": "newuserupdate123@example.com",
        "password": "Ordubad2"
    }

    # Start a session to persist login state
    session = requests.Session()
    response = session.post(login_url, data=login_data)
    assert response.status_code == 200, "Login failed, cannot test profile update."

    # Test changing the profile
    profile_data = {
        "firstName": "Update name",
        "email": "newuserupdate1@example.com",
        "password": "password123456789"  # Assume password change is optional
    }
    start_time = time.time()
    response = session.post(profile_url, data=profile_data)
    elapsed_time = time.time() - start_time

    print(f"Profile update request completed in {elapsed_time:.2f} seconds.")
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, "Failed to update profile, status code was not 200."
    assert "Profile updated" in response.text, "Profile update did not complete successfully."

if __name__ == "__main__":
    test_login()
    test_signup()
    test_admin_login()
    test_logout()
