import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Dimensions,
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Text } from '@/components/ui/Text';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Colors, Spacing, Typography, Radius } from '@/constants/theme';
import { clearAuth } from '@/lib/auth';

const { width } = Dimensions.get('window');

// ─── Mock data ─────────────────────────────────────────────────────────────
const MOCK_PROFILE = {
  name: 'Tanmay',
  email: 'tanmay44a@gmail.com',
  username: 'tanmay44a',
  joinDate: 'Jan 2026',
  avatar: 'T',
  plan: 'Pro',
  targetExam: 'GRE',
  targetScore: 330,
  examDate: 'May 2026',
};

const LIFETIME_STATS = [
  { label: 'Total\nSolved', value: '248', icon: '✎' },
  { label: 'Accuracy', value: '76%', icon: '◎' },
  { label: 'Best\nStreak', value: '21🔥', icon: '🏆' },
  { label: 'Avg\nTime', value: '2m 4s', icon: '⏱' },
];

const EXAM_PROGRESS = [
  { exam: 'GRE', variant: 'gre' as const, solved: 156, total: 500, accuracy: 78 },
  { exam: 'GMAT', variant: 'gmat' as const, solved: 72, total: 400, accuracy: 71 },
  { exam: 'SAT', variant: 'sat' as const, solved: 20, total: 300, accuracy: 85 },
];

const SETTINGS_ITEMS = [
  { icon: '⚙', label: 'Account Settings', action: 'settings' },
  { icon: '🔔', label: 'Notifications', action: 'notifications' },
  { icon: '📊', label: 'Performance Analytics', action: 'analytics' },
  { icon: '💳', label: 'Subscription & Billing', action: 'billing' },
  { icon: '❓', label: 'Help & Support', action: 'support' },
  { icon: '★', label: 'Rate the App', action: 'rate' },
];

// ─── Sub-components ────────────────────────────────────────────────────────
function ExamProgressRow({
  exam, variant, solved, total, accuracy,
}: (typeof EXAM_PROGRESS)[0]) {
  const pct = (solved / total) * 100;

  return (
    <View style={progStyles.row}>
      <View style={progStyles.left}>
        <Badge label={exam} variant={variant} />
        <Text variant="muted" size="xs" style={{ marginLeft: 'auto' }}>
          {solved}/{total}
        </Text>
      </View>
      <View style={progStyles.barBg}>
        <View
          style={[
            progStyles.barFill,
            {
              width: `${pct}%` as any,
              backgroundColor:
                exam === 'GRE' ? Colors.gre : exam === 'GMAT' ? Colors.gmat : Colors.sat,
            },
          ]}
        />
      </View>
      <Text variant="muted" size="xs">{accuracy}% accuracy</Text>
    </View>
  );
}

const progStyles = StyleSheet.create({
  row: { gap: Spacing[1] + 2 },
  left: { flexDirection: 'row', alignItems: 'center' },
  barBg: {
    height: 6,
    backgroundColor: Colors.border,
    borderRadius: Radius.full,
    overflow: 'hidden',
  },
  barFill: {
    height: '100%',
    borderRadius: Radius.full,
  },
});

// ─── Main screen ───────────────────────────────────────────────────────────
export default function ProfileScreen() {
  const router = useRouter();

  async function handleLogout() {
    Alert.alert('Sign Out', 'Are you sure you want to sign out?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Sign Out',
        style: 'destructive',
        onPress: async () => {
          await clearAuth();
          router.replace('/(auth)/landing');
        },
      },
    ]);
  }

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'left', 'right']}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.headerRow}>
          <Text style={styles.title} weight="bold">Profile</Text>
          <Button variant="ghost" size="sm" onPress={handleLogout}>
            <Text style={{ color: Colors.destructive, fontSize: Typography.sizes.sm }}>
              Sign Out
            </Text>
          </Button>
        </View>

        {/* Avatar + basic info */}
        <Card style={styles.profileCard}>
          <View style={styles.avatarRow}>
            {/* Avatar circle */}
            <View style={styles.avatar}>
              <Text style={styles.avatarLetter}>{MOCK_PROFILE.avatar}</Text>
            </View>

            <View style={styles.profileInfo}>
              <View style={styles.nameRow}>
                <Text weight="bold" size="lg">{MOCK_PROFILE.name}</Text>
                <Badge
                  label={MOCK_PROFILE.plan}
                  variant="info"
                  style={{ marginLeft: Spacing[2] }}
                />
              </View>
              <Text variant="muted" size="sm">@{MOCK_PROFILE.username}</Text>
              <Text variant="muted" size="xs" style={{ marginTop: 2 }}>
                Member since {MOCK_PROFILE.joinDate}
              </Text>
            </View>
          </View>

          {/* Target exam banner */}
          <View style={styles.targetBanner}>
            <View style={styles.targetItem}>
              <Text variant="muted" size="xs">Target Exam</Text>
              <Badge label={MOCK_PROFILE.targetExam} variant="gre" />
            </View>
            <View style={styles.targetDivider} />
            <View style={styles.targetItem}>
              <Text variant="muted" size="xs">Target Score</Text>
              <Text weight="semibold">{MOCK_PROFILE.targetScore}</Text>
            </View>
            <View style={styles.targetDivider} />
            <View style={styles.targetItem}>
              <Text variant="muted" size="xs">Exam Date</Text>
              <Text weight="semibold" size="sm">{MOCK_PROFILE.examDate}</Text>
            </View>
          </View>
        </Card>

        {/* Lifetime stats */}
        <Text style={styles.sectionTitle} weight="semibold">Lifetime Stats</Text>
        <View style={styles.statsGrid}>
          {LIFETIME_STATS.map(stat => (
            <View key={stat.label} style={styles.statCard}>
              <Text style={styles.statIcon}>{stat.icon}</Text>
              <Text weight="bold" size="xl" style={{ marginTop: Spacing[1] }}>
                {stat.value}
              </Text>
              <Text variant="muted" size="xs" style={{ textAlign: 'center', lineHeight: 15 }}>
                {stat.label}
              </Text>
            </View>
          ))}
        </View>

        {/* Exam progress */}
        <Text style={styles.sectionTitle} weight="semibold">Exam Progress</Text>
        <Card>
          <View style={styles.examProgressList}>
            {EXAM_PROGRESS.map((ep, i) => (
              <View key={ep.exam}>
                <ExamProgressRow {...ep} />
                {i < EXAM_PROGRESS.length - 1 && <View style={styles.divider} />}
              </View>
            ))}
          </View>
        </Card>

        {/* Settings list */}
        <Text style={styles.sectionTitle} weight="semibold">Settings</Text>
        <Card padding="none">
          {SETTINGS_ITEMS.map((item, i) => (
            <View key={item.action}>
              <TouchableOpacity
                style={styles.settingsRow}
                onPress={() => Alert.alert('Coming soon', `${item.label} will be available soon`)}
                activeOpacity={0.7}
              >
                <Text style={styles.settingsIcon}>{item.icon}</Text>
                <Text style={styles.settingsLabel} weight="medium">
                  {item.label}
                </Text>
                <Text style={styles.settingsChevron} variant="muted">›</Text>
              </TouchableOpacity>
              {i < SETTINGS_ITEMS.length - 1 && <View style={styles.settingsDivider} />}
            </View>
          ))}
        </Card>

        {/* Version */}
        <Text style={styles.version} variant="muted">
          CompEx v1.0.0 · Made with ❤️ for serious test-takers
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.background },
  scroll: { flex: 1 },
  content: {
    paddingHorizontal: Spacing[4],
    paddingTop: Spacing[4],
    paddingBottom: Spacing[10],
    gap: Spacing[2],
  },

  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing[4],
  },
  title: {
    fontSize: Typography.sizes['2xl'],
    letterSpacing: -0.3,
  },

  // Profile card
  profileCard: {
    gap: 0,
    overflow: 'hidden',
  },
  avatarRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing[4],
    padding: Spacing[4],
  },
  avatar: {
    width: 64,
    height: 64,
    borderRadius: Radius.full,
    backgroundColor: Colors.brand,
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  },
  avatarLetter: {
    fontSize: Typography.sizes['2xl'],
    color: '#fff',
    fontFamily: Typography.fonts.sansBold,
  },
  profileInfo: {
    flex: 1,
    gap: 2,
  },
  nameRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },

  // Target banner
  targetBanner: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: Colors.border,
    paddingVertical: Spacing[3],
    paddingHorizontal: Spacing[4],
  },
  targetItem: {
    flex: 1,
    alignItems: 'center',
    gap: 4,
  },
  targetDivider: {
    width: 1,
    backgroundColor: Colors.border,
    marginVertical: 4,
  },

  // Stats
  sectionTitle: {
    fontSize: Typography.sizes.base,
    marginTop: Spacing[4],
    marginBottom: Spacing[2],
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing[3],
  },
  statCard: {
    width: (width - Spacing[4] * 2 - Spacing[3]) / 2 - 1,
    backgroundColor: Colors.card,
    borderRadius: Radius.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    padding: Spacing[4],
    alignItems: 'center',
    gap: 2,
  },
  statIcon: {
    fontSize: 22,
  },

  // Exam progress
  examProgressList: {
    gap: Spacing[3],
  },
  divider: {
    height: 1,
    backgroundColor: Colors.border,
    marginVertical: Spacing[1],
  },

  // Settings
  settingsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: Spacing[4],
    paddingVertical: Spacing[3] + 2,
    gap: Spacing[3],
  },
  settingsIcon: {
    fontSize: 18,
    width: 24,
    textAlign: 'center',
  },
  settingsLabel: {
    flex: 1,
    fontSize: Typography.sizes.sm,
  },
  settingsChevron: {
    fontSize: Typography.sizes.lg,
    lineHeight: Typography.sizes.lg * 1.4,
  },
  settingsDivider: {
    height: 1,
    backgroundColor: Colors.border,
    marginLeft: Spacing[4] + 24 + Spacing[3],
  },

  version: {
    textAlign: 'center',
    fontSize: Typography.sizes.xs,
    marginTop: Spacing[6],
  },
});
