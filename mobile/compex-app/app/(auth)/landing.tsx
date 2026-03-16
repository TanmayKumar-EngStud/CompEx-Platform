import React from 'react';
import {
  View,
  StyleSheet,
  Dimensions,
  Image,
  Platform,
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Text } from '@/components/ui/Text';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Colors, Spacing, Typography, Radius } from '@/constants/theme';

const { width, height } = Dimensions.get('window');

// Exam type pill data
const EXAM_PILLS = [
  { label: 'GRE', variant: 'gre' as const, top: '12%', left: '8%', rotate: '-8deg' },
  { label: 'GMAT', variant: 'gmat' as const, top: '20%', right: '10%', rotate: '6deg' },
  { label: 'SAT', variant: 'sat' as const, top: '30%', left: '18%', rotate: '4deg' },
  { label: 'Quants', variant: 'gre' as const, top: '35%', right: '6%', rotate: '-5deg' },
  { label: 'Verbal', variant: 'sat' as const, top: '42%', left: '4%', rotate: '7deg' },
  { label: 'RC', variant: 'gmat' as const, top: '48%', right: '20%', rotate: '-4deg' },
];

// Stat card data
const STATS = [
  { value: '50K+', label: 'Questions' },
  { value: '98%', label: 'Accuracy' },
  { value: '10K+', label: 'Students' },
];

export default function LandingScreen() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'left', 'right']}>
      <StatusBar style="light" />

      {/* Background gradient effect using layered views */}
      <View style={styles.gradientTop} />
      <View style={styles.gradientBottom} />

      {/* Floating decorative pills */}
      <View style={StyleSheet.absoluteFill} pointerEvents="none">
        {EXAM_PILLS.map((pill, i) => (
          <View
            key={i}
            style={[
              styles.floatingPill,
              {
                top: pill.top as any,
                left: pill.left as any,
                right: pill.right as any,
                transform: [{ rotate: pill.rotate }],
              },
            ]}
          >
            <Badge label={pill.label} variant={pill.variant} />
          </View>
        ))}
      </View>

      <View style={styles.container}>
        {/* Header / Logo */}
        <View style={styles.logoSection}>
          <View style={styles.logoMark}>
            <Text style={styles.logoLetter}>C</Text>
          </View>
          <Text style={styles.logoText} weight="bold">
            CompEx
          </Text>
        </View>

        {/* Hero text */}
        <View style={styles.heroSection}>
          <Text style={styles.headline} weight="bold">
            Ace Your{'\n'}
            <Text style={[styles.headline, styles.headlineAccent]}>GRE, GMAT</Text>
            {'\n'}& SAT
          </Text>
          <Text style={styles.subheadline} variant="muted">
            Adaptive practice questions, AI-powered explanations, and real-time
            performance analytics — built for serious test-takers.
          </Text>
        </View>

        {/* Stats row */}
        <View style={styles.statsRow}>
          {STATS.map((stat, i) => (
            <React.Fragment key={stat.label}>
              <View style={styles.statItem}>
                <Text style={styles.statValue} weight="bold">
                  {stat.value}
                </Text>
                <Text variant="muted" size="xs">
                  {stat.label}
                </Text>
              </View>
              {i < STATS.length - 1 && <View style={styles.statDivider} />}
            </React.Fragment>
          ))}
        </View>

        {/* CTA Buttons */}
        <View style={styles.ctaSection}>
          <Button
            variant="brand"
            size="lg"
            fullWidth
            onPress={() => router.push('/(auth)/signup')}
          >
            Get Started — It's Free
          </Button>

          <Button
            variant="outline"
            size="lg"
            fullWidth
            onPress={() => router.push('/(auth)/login')}
          >
            Sign In
          </Button>
        </View>

        {/* Footer */}
        <Text style={styles.footer} variant="muted">
          No credit card required · Cancel anytime
        </Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  gradientTop: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: height * 0.5,
    // Simulated radial glow using borderRadius
    borderBottomLeftRadius: width,
    borderBottomRightRadius: width,
    opacity: 0.06,
    backgroundColor: Colors.brand,
  },
  gradientBottom: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: 200,
    backgroundColor: Colors.background,
    opacity: 0.95,
  },

  container: {
    flex: 1,
    paddingHorizontal: Spacing[6],
    justifyContent: 'flex-end',
    paddingBottom: Spacing[8],
    gap: Spacing[6],
  },

  // Floating pills
  floatingPill: {
    position: 'absolute',
    opacity: 0.4,
  },

  // Logo
  logoSection: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing[2],
    position: 'absolute',
    top: Spacing[5],
    left: Spacing[6],
  },
  logoMark: {
    width: 32,
    height: 32,
    borderRadius: Radius.md,
    backgroundColor: Colors.brand,
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoLetter: {
    color: '#fff',
    fontSize: Typography.sizes.lg,
    fontFamily: Typography.fonts.sansBold,
  },
  logoText: {
    fontSize: Typography.sizes.lg,
    color: Colors.foreground,
  },

  // Hero
  heroSection: {
    gap: Spacing[3],
  },
  headline: {
    fontSize: Typography.sizes['4xl'],
    color: Colors.foreground,
    lineHeight: Typography.sizes['4xl'] * 1.1,
    letterSpacing: -1,
  },
  headlineAccent: {
    color: Colors.brand,
  },
  subheadline: {
    fontSize: Typography.sizes.base,
    lineHeight: Typography.sizes.base * 1.6,
    color: Colors.mutedForeground,
  },

  // Stats
  statsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.card,
    borderRadius: Radius.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    paddingVertical: Spacing[4],
    paddingHorizontal: Spacing[2],
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
    gap: 2,
  },
  statValue: {
    fontSize: Typography.sizes.xl,
    color: Colors.foreground,
  },
  statDivider: {
    width: 1,
    height: 32,
    backgroundColor: Colors.border,
  },

  // CTAs
  ctaSection: {
    gap: Spacing[3],
  },

  // Footer
  footer: {
    textAlign: 'center',
    fontSize: Typography.sizes.xs,
  },
});
