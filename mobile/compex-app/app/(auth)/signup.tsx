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

export default function SignupScreen() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ name?: string; email?: string; password?: string }>({});

  function validate(): boolean {
    const e: typeof errors = {};
    if (!name.trim()) e.name = 'Name is required';
    if (!email.trim()) e.email = 'Email is required';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) e.email = 'Enter a valid email';
    if (!password) e.password = 'Password is required';
    else if (password.length < 8) e.password = 'Must be at least 8 characters';
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSignup() {
    if (!validate()) return;
    setLoading(true);
    try {
      const { token, user } = await authApi.signup(
        email.trim().toLowerCase(),
        password,
        name.trim()
      );
      await setToken(token);
      await setUser(user);
      router.replace('/(tabs)');
    } catch (err: any) {
      Alert.alert('Signup Failed', err.message ?? 'Could not create account');
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
            <Text style={styles.title} weight="bold">Create account</Text>
            <Text variant="muted" size="base">
              Start your competitive exam prep today
            </Text>
          </View>

          {/* Exam type selector */}
          <View style={styles.examRow}>
            {[
              { label: 'GRE', color: Colors.gre },
              { label: 'GMAT', color: Colors.gmat },
              { label: 'SAT', color: Colors.sat },
            ].map(exam => (
              <View
                key={exam.label}
                style={[styles.examChip, { borderColor: exam.color + '50', backgroundColor: exam.color + '18' }]}
              >
                <Text style={{ color: exam.color, fontSize: Typography.sizes.xs, fontFamily: Typography.fonts.sansMedium }}>
                  {exam.label}
                </Text>
              </View>
            ))}
            <Text variant="muted" size="xs" style={{ marginLeft: Spacing[1] }}>
              All included
            </Text>
          </View>

          {/* Form */}
          <View style={styles.form}>
            <Input
              label="Full Name"
              placeholder="Your name"
              value={name}
              onChangeText={setName}
              autoCapitalize="words"
              autoCorrect={false}
              error={errors.name}
            />

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
              placeholder="Min. 8 characters"
              value={password}
              onChangeText={setPassword}
              secureTextEntry={!showPassword}
              autoCapitalize="none"
              error={errors.password}
              hint={!errors.password ? 'Use a mix of letters and numbers' : undefined}
              rightIcon={
                <Text style={styles.toggleText}>
                  {showPassword ? 'Hide' : 'Show'}
                </Text>
              }
              onRightIconPress={() => setShowPassword(v => !v)}
            />

            <Button
              variant="brand"
              size="lg"
              fullWidth
              loading={loading}
              onPress={handleSignup}
            >
              Create Account
            </Button>
          </View>

          {/* Terms */}
          <Text style={styles.terms} variant="muted">
            By creating an account, you agree to our{' '}
            <Text style={styles.termsLink}>Terms of Service</Text>
            {' '}and{' '}
            <Text style={styles.termsLink}>Privacy Policy</Text>.
          </Text>

          {/* Footer */}
          <View style={styles.footer}>
            <Text variant="muted" size="sm">Already have an account? </Text>
            <TouchableOpacity onPress={() => router.replace('/(auth)/login')}>
              <Text style={styles.loginLink} size="sm" weight="semibold">Sign in</Text>
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
    marginBottom: Spacing[5],
    gap: Spacing[1] + 2,
  },
  title: {
    fontSize: Typography.sizes['3xl'],
    color: Colors.foreground,
    letterSpacing: -0.5,
  },
  examRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing[2],
    marginBottom: Spacing[6],
  },
  examChip: {
    paddingHorizontal: Spacing[3],
    paddingVertical: Spacing[1],
    borderRadius: Radius.full,
    borderWidth: 1,
  },
  form: {
    gap: Spacing[4],
    marginBottom: Spacing[5],
  },
  toggleText: {
    color: Colors.mutedForeground,
    fontSize: Typography.sizes.xs,
    fontFamily: Typography.fonts.sansMedium,
  },
  terms: {
    fontSize: Typography.sizes.xs,
    lineHeight: Typography.sizes.xs * 1.7,
    textAlign: 'center',
    marginBottom: Spacing[5],
  },
  termsLink: {
    color: Colors.brand,
    fontSize: Typography.sizes.xs,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loginLink: {
    color: Colors.brand,
  },
});
