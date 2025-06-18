from auth_service import get_user_credentials, revoke_user_credentials

def test_auth():
    user_email = input("Enter your Google account email: ")

    try:
        creds = get_user_credentials(user_email)
        print(f"Access Token: {creds.token}")
        print(f"Refresh Token: {creds.refresh_token}")
        print(f"Token Expiry: {creds.expiry}")
        print("✅ Authentication successful and token stored in MongoDB.")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")

def test_revoke():
    user_email = input("Enter the Google account email to revoke: ")

    try:
        revoke_user_credentials(user_email)
        print("✅ Token revoked successfully.")
    except Exception as e:
        print(f"❌ Error revoking token: {e}")

if __name__ == "__main__":
    print("1. Authenticate")
    print("2. Revoke")
    choice = input("Choose (1/2): ")

    if choice == "1":
        test_auth()
    elif choice == "2":
        test_revoke()
    else:
        print("Invalid choice.")
