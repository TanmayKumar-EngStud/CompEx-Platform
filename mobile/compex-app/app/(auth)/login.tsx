import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  TouchableOpacity,
  ScrollView,
  Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Text } from '@/components/ui/Text';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Colors, Spacing, Typography, Radius } from '@/constants/theme';
import { authApi } from '@/lib/api';
import { setToken, setUser } from '@/lib/auth';

export default function LoginScreen() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});

  function validate(): boolean {
    const newErrors: typeof errors = {};
    if (!email.trim()) newErrors.email = 'Email is required';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) newErrors.email = 'Enter a valid email';
    if (!password) newErrors.password = 'Password is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  async function handleLogin() {
    if (!validate()) return;
    setLoading(true);
    try {
      const { token, user } = await authApi.login(email.trim().toLowerCase(), password);
      await setToken(token);
      await setUser(user);
      router.replace('/(tabs)');
    } catch (err: any) {
      Alert.alert('Login Failed', err.message ?? 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  }

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'left', 'right']}>
      <KeyboardAvoidingView
        style={styles.kav}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView
          contentContainerStyle={styles.scroll}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* Back */}
          <TouchableOpacity
            onPress={() => router.back()}
            style={styles.backButton}
            hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
          >
            <Text style={styles.backIcon}>←</Text>
          </TouchableOpacity>

          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.title} weight="bold">Welcome back</Text>
            <Text variant="muted" size="base">
              Sign in to continue your prep journey
            </Text>
          </View>

          {/* Form */}
          <View style={styles.form}>
            <Input
              label="Email"
              placeholder="you@example.com"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
              error={errors.email}
            />

            <Input
              label="Password"
              placeholder="••••••••"
              value={password}
              onChangeText={setPassword}
              secureTextEntry={!showPassword}
              autoCapitalize="none"
              error={errors.password}
              rightIcon={
                <Text style={styles.toggleText}>
                  {showPassword ? 'Hide' : 'Show'}
                </Text>
              }
              onRightIconPress={() => setShowPassword(v => !v)}
            />

            {/* Forgot password */}
            <TouchableOpacity style={styles.forgotRow}>
              <Text style={styles.forgotText}>Forgot password?</Text>
            </TouchableOpacity>

            <Button
              variant="brand"
              size="lg"
              fullWidth
              loading={loading}
              onPress={handleLogin}
            >
              Sign In
            </Button>
          </View>

          {/* Divider */}
          <View style={styles.divider}>
            <View style={styles.dividerLine} />
            <Text variant="muted" size="xs" style={styles.dividerText}>or continue with</Text>
            <View style={styles.dividerLine} />
          </View>

          {/* Google Sign In placeholder */}
          <Button
            variant="outline"
            size="lg"
            fullWidth
            onPress={() => Alert.alert('Coming soon', 'Google sign-in will be available soon')}
          >
            Continue with Google
          </Button>

          {/* Footer */}
          <View style={styles.footer}>
            <Text variant="muted" size="sm">Don't have an account? </Text>
            <TouchableOpacity onPress={() => router.replace('/(auth)/signup')}>
              <Text style={styles.signupLink} size="sm" weight="semibold">Sign up</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  kav: { flex: 1 },
  scroll: {
    flexGrow: 1,
    paddingHorizontal: Spacing[6],
    paddingBottom: Spacing[10],
  },

  backButton: {
    marginTop: Spacing[4],
    marginBottom: Spacing[4],
    width: 36,
    height: 36,
    borderRadius: Radius.md,
    backgroundColor: Colors.card,
    borderWidth: 1,
    borderColor: Colors.border,
    alignItems: 'center',
    justifyContent: 'center',
  },
  backIcon: {
    color: Colors.foreground,
    fontSize: Typography.sizes.lg,
    lineHeight: Typography.sizes.lg * 1.4,
  },

  header: {
    marginBottom: Spacing[8],
    gap: Spacing[1] + 2,
  },
  title: {
    fontSize: Typography.sizes['3xl'],
    color: Colors.foreground,
    letterSpacing: -0.5,
  },

  form: {
    gap: Spacing[4],
    marginBottom: Spacing[6],
  },
  toggleText: {
    color: Colors.mutedForeground,
    fontSize: Typography.sizes.xs,
    fontFamily: Typography.fonts.sansMedium,
  },
  forgotRow: {
    alignSelf: 'flex-end',
    marginTop: -Spacing[2],
  },
  forgotText: {
    color: Colors.brand,
    fontSize: Typography.sizes.sm,
    fontFamily: Typography.fonts.sansMedium,
  },

  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing[3],
    marginVertical: Spacing[5],
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: Colors.border,
  },
  dividerText: {
    flexShrink: 0,
  },

  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: Spacing[6],
  },
  signupLink: {
    color: Colors.brand,
  },
});
