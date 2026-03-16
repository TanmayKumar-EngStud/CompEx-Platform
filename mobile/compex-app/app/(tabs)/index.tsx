import React from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Text } from '@/components/ui/Text';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Colors, Spacing, Typography, Radius } from '@/constants/theme';

const { width } = Dimensions.get('window');

// ─── Mock data (replace with real API calls via React Query) ───────────────
const MOCK_USER = { name: 'Tanmay', streak: 12 };

const QUICK_STATS = [
  { label: 'Questions\nSolved', value: '248', color: Colors.brand },
  { label: 'Accuracy', value: '76%', color: Colors.success },
  { label: 'Day\nStreak', value: '12🔥', color: Colors.warning },
  { label: 'Rank', value: '#142', color: Colors.gre },
];

const RECENT_ACTIVITY = [
  {
    exam: 'GRE',
    section: 'Quants',
    topic: 'Number Properties',
    score: '8/10',
    time: '2h ago',
    variant: 'gre' as const,
  },
  {
    exam: 'GMAT',
    section: 'Verbal',
    topic: 'Critical Reasoning',
    score: '6/10',
    time: '1d ago',
    variant: 'gmat' as const,
  },
  {
    exam: 'GRE',
    section: 'Verbal',
    topic: 'Reading Comprehension',
    score: '9/10',
    time: '2d ago',
    variant: 'gre' as const,
  },
];

const PRACTICE_SHORTCUTS = [
  { label: 'GRE Quants', icon: '∑', color: Colors.gre, examType: 'GRE', section: 'Quants' },
  { label: 'GRE Verbal', icon: '✦', color: Colors.gre, examType: 'GRE', section: 'Verbal' },
  { label: 'GMAT Verbal', icon: '◈', color: Colors.gmat, examType: 'GMAT', section: 'Verbal' },
  { label: 'SAT Math', icon: '⟡', color: Colors.sat, examType: 'SAT', section: 'Math' },
];

// ─── Sub-components ────────────────────────────────────────────────────────
function StatCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <View style={[styles.statCard, { borderColor: color + '30' }]}>
      <Text style={[styles.statValue, { color }]} weight="bold">{value}</Text>
      <Text style={styles.statLabel} variant="muted">{label}</Text>
    </View>
  );
}

function ActivityRow({
  exam, section, topic, score, time, variant,
}: (typeof RECENT_ACTIVITY)[0]) {
  const correct = parseInt(score.split('/')[0]);
  const total = parseInt(score.split('/')[1]);
  const pct = (correct / total) * 100;

  return (
    <View style={styles.activityRow}>
      <View style={styles.activityLeft}>
        <View style={styles.activityMeta}>
          <Badge label={exam} variant={variant} />
          <Text variant="muted" size="xs">{section} · {time}</Text>
        </View>
        <Text style={styles.activityTopic} weight="medium">{topic}</Text>
        {/* Mini progress bar */}
        <View style={styles.miniBarBg}>
          <View
            style={[
              styles.miniBarFill,
              {
                width: `${pct}%` as any,
                backgroundColor: pct >= 80 ? Colors.success : pct >= 60 ? Colors.warning : Colors.error,
              },
            ]}
          />
        </View>
      </View>
      <Text
        style={[
          styles.activityScore,
          { color: pct >= 80 ? Colors.success : pct >= 60 ? Colors.warning : Colors.error },
        ]}
        weight="semibold"
      >
        {score}
      </Text>
    </View>
  );
}

// ─── Main screen ───────────────────────────────────────────────────────────
export default function DashboardScreen() {
  const router = useRouter();
  const hour = new Date().getHours();
  const greeting =
    hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'left', 'right']}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text variant="muted" size="sm">{greeting},</Text>
            <Text style={styles.userName} weight="bold">{MOCK_USER.name} 👋</Text>
          </View>
          <TouchableOpacity style={styles.notifButton}>
            <Text style={styles.notifIcon}>🔔</Text>
          </TouchableOpacity>
        </View>

        {/* Streak banner */}
        <View style={styles.streakBanner}>
          <Text style={styles.streakFire}>🔥</Text>
          <View style={styles.streakText}>
            <Text size="sm" weight="semibold">
              {MOCK_USER.streak}-day streak!
            </Text>
            <Text variant="muted" size="xs">
              Keep it up — solve at least 1 problem today
            </Text>
          </View>
          <Button variant="brand" size="sm" onPress={() => router.push('/(tabs)/problems')}>
            Practice
          </Button>
        </View>

        {/* Quick stats */}
        <View style={styles.sectionHeader}>
          <Text weight="semibold">Your Progress</Text>
        </View>
        <View style={styles.statsGrid}>
          {QUICK_STATS.map(stat => (
            <StatCard key={stat.label} {...stat} />
          ))}
        </View>

        {/* Practice shortcuts */}
        <View style={styles.sectionHeader}>
          <Text weight="semibold">Quick Practice</Text>
          <TouchableOpacity onPress={() => router.push('/(tabs)/problems')}>
            <Text style={styles.seeAll}>See all →</Text>
          </TouchableOpacity>
        </View>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.shortcutsRow}
        >
          {PRACTICE_SHORTCUTS.map(shortcut => (
            <TouchableOpacity
              key={shortcut.label}
              style={[styles.shortcutCard, { borderColor: shortcut.color + '40' }]}
              onPress={() => router.push('/(tabs)/problems')}
            >
              <Text style={[styles.shortcutIcon, { color: shortcut.color }]}>
                {shortcut.icon}
              </Text>
              <Text size="xs" weight="medium" style={{ textAlign: 'center' }}>
                {shortcut.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Recent activity */}
        <View style={styles.sectionHeader}>
          <Text weight="semibold">Recent Activity</Text>
        </View>
        <Card padding="none">
          {RECENT_ACTIVITY.map((activity, i) => (
            <View key={i}>
              <View style={styles.activityPad}>
                <ActivityRow {...activity} />
              </View>
              {i < RECENT_ACTIVITY.length - 1 && <View style={styles.divider} />}
            </View>
          ))}
        </Card>

        {/* Start mock test CTA */}
        <Card style={styles.mockCta}>
          <View style={styles.mockCtaContent}>
            <View style={styles.mockCtaText}>
              <Text weight="bold" size="lg">Ready for a mock test?</Text>
              <Text variant="muted" size="sm" style={{ marginTop: 4 }}>
                Simulate real exam conditions and track your score
              </Text>
            </View>
            <Button
              variant="brand"
              size="md"
              onPress={() => {}}
            >
              Start Mock
            </Button>
          </View>
        </Card>
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

  // Header
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: Spacing[4],
  },
  userName: {
    fontSize: Typography.sizes['2xl'],
    letterSpacing: -0.3,
  },
  notifButton: {
    width: 40,
    height: 40,
    borderRadius: Radius.md,
    backgroundColor: Colors.card,
    borderWidth: 1,
    borderColor: Colors.border,
    alignItems: 'center',
    justifyContent: 'center',
  },
  notifIcon: { fontSize: 18 },

  // Streak banner
  streakBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.card,
    borderRadius: Radius.lg,
    borderWidth: 1,
    borderColor: Colors.warning + '40',
    padding: Spacing[3],
    gap: Spacing[3],
    marginBottom: Spacing[2],
  },
  streakFire: { fontSize: 24 },
  streakText: { flex: 1, gap: 2 },

  // Sections
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: Spacing[4],
    marginBottom: Spacing[2],
  },
  seeAll: { color: Colors.brand, fontSize: Typography.sizes.sm },

  // Stats grid
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
    padding: Spacing[4],
    gap: Spacing[1],
  },
  statValue: {
    fontSize: Typography.sizes['2xl'],
    lineHeight: Typography.sizes['2xl'] * 1.1,
  },
  statLabel: {
    fontSize: Typography.sizes.xs,
    lineHeight: 16,
  },

  // Shortcuts
  shortcutsRow: {
    gap: Spacing[3],
    paddingRight: Spacing[4],
  },
  shortcutCard: {
    width: 88,
    height: 88,
    backgroundColor: Colors.card,
    borderRadius: Radius.lg,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: Spacing[1] + 2,
    padding: Spacing[2],
  },
  shortcutIcon: {
    fontSize: 28,
    lineHeight: 32,
  },

  // Activity
  activityPad: {
    padding: Spacing[4],
  },
  activityRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: Spacing[3],
  },
  activityLeft: {
    flex: 1,
    gap: Spacing[1] + 2,
  },
  activityMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing[2],
  },
  activityTopic: {
    fontSize: Typography.sizes.sm,
    color: Colors.foreground,
  },
  miniBarBg: {
    height: 3,
    backgroundColor: Colors.border,
    borderRadius: 99,
    overflow: 'hidden',
    width: '100%',
  },
  miniBarFill: {
    height: '100%',
    borderRadius: 99,
  },
  activityScore: {
    fontSize: Typography.sizes.sm,
    flexShrink: 0,
  },
  divider: {
    height: 1,
    backgroundColor: Colors.border,
    marginHorizontal: Spacing[4],
  },

  // Mock CTA
  mockCta: {
    marginTop: Spacing[4],
    borderColor: Colors.brand + '40',
  },
  mockCtaContent: {
    padding: Spacing[4],
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: Spacing[4],
  },
  mockCtaText: { flex: 1 },
});
