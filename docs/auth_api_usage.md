# Authentication API Usage Guide

This guide explains how to use the authentication endpoints for login and registration via OTP (email), Google, and Discord.

---

## 1. Registration and Email Verification (OTP)

### Step 1: Register

- **Endpoint:** `POST /api/auth/register/`
- **Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "newpassword"
  }
  ```
- **Response (Success):**
  ```json
  {
    "detail": "Registration successful. Please verify your email with the OTP sent."
  }
  ```
- **Notes:**
  - Registers a new user and sends an OTP to the provided email.
  - If the user already exists, you get:  
    `{ "detail": "User already registered." }`

---

### Step 2: Verify OTP

- **Endpoint:** `POST /api/auth/verify-otp/`
- **Body:**
  ```json
  {
    "email": "user@example.com",
    "code": "123456"
  }
  ```
- **Response (Success):**
  ```json
  {
    "refresh": "<refresh_token>",
    "access": "<access_token>"
  }
  ```
- **Notes:**
  - Verifies the OTP and activates the user account.
  - If the OTP is invalid or expired (valid for 15 minutes), you get:  
    `{ "detail": "Invalid or expired OTP." }`
  - If the user is not found, you get:  
    `{ "detail": "User not found." }`

---

### Step 3: Login with OTP (for verified users)

- **Endpoint:** `POST /api/auth/send-otp/`
- **Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "userpassword"
  }
  ```
- **Response:**
  ```json
  { "detail": "OTP sent." }
  ```
- **Notes:**
  - Only verified users can request an OTP for login.
  - If the user is not verified, you get:  
    `{ "detail": "User is not verified. Please verify your email first." }`

---

## 2. Google Social Login/Register

### Step 1: Obtain Google OAuth Token

- Use Google OAuth on the frontend to get an ID token.

### Step 2: Send Token to Backend

- **Endpoint:** `POST /api/auth/social/google/`
- **Body:**
  ```json
  {
    "token": "<google_id_token>"
  }
  ```
- **Response (Success):**
  ```json
  {
    "refresh": "<refresh_token>",
    "access": "<access_token>"
  }
  ```
- **Notes:**
  - If the email is new, a user is registered automatically.
  - If the email exists, the user is logged in.
  - If the token is invalid, you get:  
    `{ "detail": "Invalid Google token." }`

---

## 3. Discord Social Login/Register

### Step 1: Obtain Discord OAuth Token

- Use Discord OAuth on the frontend to get an access token.

### Step 2: Send Token to Backend

- **Endpoint:** `POST /api/auth/social/discord/`
- **Body:**
  ```json
  {
    "token": "<discord_access_token>"
  }
  ```
- **Response (Success):**
  ```json
  {
    "refresh": "<refresh_token>",
    "access": "<access_token>"
  }
  ```
- **Notes:**
  - If the email is new, a user is registered automatically.
  - If the email exists, the user is logged in.
  - If the token is invalid, you get:  
    `{ "detail": "Invalid Discord token." }`

---

**General Notes:**
- All successful authentication responses return JWT tokens (`refresh` and `access`).
- The frontend should store and use these tokens for authenticated requests.
- OTPs are valid for 15 minutes and can only be used once. 