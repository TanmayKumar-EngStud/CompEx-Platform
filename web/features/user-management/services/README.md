# User Management Services

This directory contains service functions that handle business logic for the user management feature.

## Available Services

* **auth-service.ts**: Functions for authentication
* **profile-service.ts**: Functions for managing user profiles
* **preferences-service.ts**: Functions for managing user preferences

## Service Details

### auth-service.ts

Functions for user authentication:

```typescript
// Login user
async function login(email: string, password: string) {
  // Authenticates user credentials
  // Returns user data and token
}

// Register new user
async function register(userData: UserRegistrationData) {
  // Validates registration data
  // Creates new user account
  // Returns user data and token
}

// Logout user
async function logout() {
  // Invalidates current session
  // Clears authentication state
}

// Reset password
async function resetPassword(email: string) {
  // Sends password reset email
  // Returns success status
}

// Verify email
async function verifyEmail(token: string) {
  // Verifies email verification token
  // Updates user verification status
}
```

### profile-service.ts

Functions for managing user profiles:

```typescript
// Get user profile
async function getUserProfile(userId: string) {
  // Fetches user profile data
  // Includes personal info and preferences
}

// Update user profile
async function updateUserProfile(userId: string, profileData: Partial<UserProfile>) {
  // Validates profile data
  // Updates user profile
  // Returns updated profile
}

// Upload profile picture
async function uploadProfilePicture(userId: string, file: File) {
  // Validates and processes image
  // Uploads to storage
  // Updates profile with image URL
}

// Delete user account
async function deleteUserAccount(userId: string) {
  // Confirms deletion
  // Removes user data
  // Handles cleanup of related data
}
```

### preferences-service.ts

Functions for managing user preferences:

```typescript
// Get user preferences
async function getUserPreferences(userId: string) {
  // Fetches user preferences
  // Includes exam, UI, and notification preferences
}

// Update user preferences
async function updateUserPreferences(userId: string, preferences: Partial<UserPreferences>) {
  // Updates specific preferences
  // Returns updated preferences
}

// Set default preferences
async function setDefaultPreferences(userId: string) {
  // Resets preferences to default values
  // Used for new users or preference reset
}

// Get preference options
async function getPreferenceOptions() {
  // Fetches available preference options
  // Used for preference selection UI
}
```

## Integration with API

These services interact with the following API endpoints:
- `/api/auth/login` - User login
- `/api/auth/register` - User registration
- `/api/auth/logout` - User logout
- `/api/users/profile` - Profile management
- `/api/users/preferences` - Preference management

## Integration with Components

These services are used by:
- Login and registration forms
- Profile editor components
- Preferences panel components
- Account management components

## Error Handling

All services include proper error handling:
- Authentication failures
- Validation errors
- Permission issues
- Network errors

## Security Considerations

These services implement security best practices:
- Password hashing
- Token validation
- Input sanitization
- Rate limiting