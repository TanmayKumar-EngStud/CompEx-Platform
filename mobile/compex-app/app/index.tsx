/**
 * Root index — checks auth state and routes accordingly.
 * Logged in  → (tabs)/index (Dashboard)
 * Logged out → (auth)/landing
 */
import { useEffect } from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { getToken } from '@/lib/auth';
import { Colors } from '@/constants/theme';

export default function RootIndex() {
  const router = useRouter();

  useEffect(() => {
    async function checkAuth() {
      const token = await getToken();
      if (token) {
        router.replace('/(tabs)');
      } else {
        router.replace('/(auth)/landing');
      }
    }
    checkAuth();
  }, []);

  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color={Colors.foreground} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: Colors.background,
  },
});
