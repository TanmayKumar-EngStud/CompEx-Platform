# User Management Feature

This feature handles user authentication, profiles, and preferences.

## Components

* **login-form.tsx**: Form for user login
* **signup-form.tsx**: Form for user registration
* **profile-editor.tsx**: Interface for editing user profile
* **preferences-panel.tsx**: Panel for setting user preferences
* **avatar-uploader.tsx**: Component for uploading profile pictures

## Services

* **auth-service.ts**: Functions for authentication
* **profile-service.ts**: Functions for managing user profiles
* **preferences-service.ts**: Functions for managing user preferences

## Hooks

* **use-auth.ts**: Manages authentication state
* **use-profile.ts**: Manages user profile data
* **use-preferences.ts**: Manages user preferences

## Stores

* **auth-store.ts**: Zustand store for authentication state
* **profile-store.ts**: Zustand store for profile state
* **preferences-store.ts**: Zustand store for preferences state

## Integration Flow

1. User logs in via `login-form.tsx`
2. `use-auth.ts` authenticates and stores user session
3. `profile-editor.tsx` allows user to update profile information
4. `preferences-panel.tsx` allows user to set study preferences
5. Preferences are used across the application to personalize experience

## API Interactions

- Authenticates via `/api/auth/login` and `/api/auth/signup`
- Fetches user profile from `/api/users/profile`
- Updates profile via `/api/users/profile/update`
- Manages preferences via `/api/users/preferences`

## Data Models

This feature interacts with the following database models:
- `User`: Core user information
- `UserProfile`: Extended user profile data
- `UserPreference`: User's application preferences
- `Session`: Authentication sessions

## State Management

The user state is managed through Zustand stores:

```typescript
// Example of auth-store.ts structure
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => Promise<void>;
  signup: (userData: UserData) => Promise<void>;
}
```

## Integration with Other Features

- **Exam Management**: Provides user context for exam preferences
- **Question Solving**: Associates question attempts with user
- **User Analytics**: Provides user context for analytics