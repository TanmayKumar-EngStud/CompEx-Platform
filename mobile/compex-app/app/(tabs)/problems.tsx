import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Dimensions,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Text } from '@/components/ui/Text';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Colors, Spacing, Typography, Radius } from '@/constants/theme';

const { width } = Dimensions.get('window');

// ─── Filters ───────────────────────────────────────────────────────────────
const EXAM_TYPES = ['All', 'GRE', 'GMAT', 'SAT'];
const SECTIONS: Record<string, string[]> = {
  All: ['All Sections'],
  GRE: ['All Sections', 'Quants', 'Verbal', 'AWA'],
  GMAT: ['All Sections', 'Quants', 'Verbal', 'IR', 'DI'],
  SAT: ['All Sections', 'Math', 'Reading', 'Writing'],
};
const DIFFICULTIES = [
  { label: 'All', variant: 'secondary' as const },
  { label: 'Easy', variant: 'easy' as const },
  { label: 'Medium', variant: 'medium' as const },
  { label: 'Hard', variant: 'hard' as const },
];

// ─── Mock problems ─────────────────────────────────────────────────────────
const MOCK_PROBLEMS = [
  {
    id: 1,
    examType: 'GRE',
    section: 'Quants',
    type: 'Quantitative Comparison',
    difficulty: 'Medium',
    topic: 'Number Properties',
    solved: true,
    correct: true,
    attempts: 1,
  },
  {
    id: 2,
    examType: 'GRE',
    section: 'Verbal',
    type: 'Text Completion',
    difficulty: 'Hard',
    topic: 'Vocabulary in Context',
    solved: false,
    correct: false,
    attempts: 0,
  },
  {
    id: 3,
    examType: 'GMAT',
    section: 'Verbal',
    type: 'Critical Reasoning',
    difficulty: 'Medium',
    topic: 'Assumption Questions',
    solved: true,
    correct: false,
    attempts: 2,
  },
  {
    id: 4,
    examType: 'GRE',
    section: 'Quants',
    type: 'Problem Solving',
    difficulty: 'Easy',
    topic: 'Algebra',
    solved: false,
    correct: false,
    attempts: 0,
  },
  {
    id: 5,
    examType: 'GMAT',
    section: 'Quants',
    type: 'Data Sufficiency',
    difficulty: 'Hard',
    topic: 'Geometry',
    solved: true,
    correct: true,
    attempts: 1,
  },
  {
    id: 6,
    examType: 'SAT',
    section: 'Math',
    type: 'Grid-In',
    difficulty: 'Medium',
    topic: 'Linear Equations',
    solved: false,
    correct: false,
    attempts: 0,
  },
];

type Problem = (typeof MOCK_PROBLEMS)[0];
type DifficultyVariant = 'easy' | 'medium' | 'hard';
type ExamVariant = 'gre' | 'gmat' | 'sat';

function difficultyVariant(d: string): DifficultyVariant {
  return d.toLowerCase() as DifficultyVariant;
}
function examVariant(e: string): ExamVariant {
  return e.toLowerCase() as ExamVariant;
}

// ─── Problem card ──────────────────────────────────────────────────────────
function ProblemCard({ problem }: { problem: Problem }) {
  const statusColor = problem.solved
    ? problem.correct
      ? Colors.success
      : Colors.error
    : Colors.mutedForeground;

  const statusIcon = problem.solved ? (problem.correct ? '✓' : '✗') : '○';
  const statusLabel = problem.solved
    ? problem.correct
      ? 'Correct'
      : 'Incorrect'
    : 'Unsolved';

  return (
    <TouchableOpacity activeOpacity={0.8}>
      <Card style={styles.problemCard} padding="none">
        <View style={styles.problemInner}>
          {/* Left status indicator */}
          <View style={[styles.statusBar, { backgroundColor: statusColor + '30', borderColor: statusColor + '60' }]}>
            <Text style={[styles.statusIcon, { color: statusColor }]}>{statusIcon}</Text>
          </View>

          {/* Content */}
          <View style={styles.problemContent}>
            <View style={styles.problemMeta}>
              <Badge label={problem.examType} variant={examVariant(problem.examType)} />
              <Badge label={problem.difficulty} variant={difficultyVariant(problem.difficulty)} />
              <Text variant="muted" size="xs" style={{ marginLeft: 'auto' }}>
                {problem.attempts > 0 ? `${problem.attempts} attempt${problem.attempts > 1 ? 's' : ''}` : 'New'}
              </Text>
            </View>

            <Text weight="medium" size="sm" style={{ marginTop: Spacing[1] + 2 }}>
              {problem.type}
            </Text>
            <Text variant="muted" size="xs" style={{ marginTop: 2 }}>
              {problem.section} · {problem.topic}
            </Text>

            <View style={styles.problemFooter}>
              <Text style={[styles.statusLabel, { color: statusColor }]} size="xs" weight="medium">
                {statusLabel}
              </Text>
              <Button variant="ghost" size="sm" style={{ paddingHorizontal: 0 }}>
                <Text style={{ color: Colors.brand, fontSize: Typography.sizes.xs }}>
                  Solve →
                </Text>
              </Button>
            </View>
          </View>
        </View>
      </Card>
    </TouchableOpacity>
  );
}

// ─── Main screen ───────────────────────────────────────────────────────────
export default function ProblemsScreen() {
  const [selectedExam, setSelectedExam] = useState('All');
  const [selectedSection, setSelectedSection] = useState('All Sections');
  const [selectedDifficulty, setSelectedDifficulty] = useState('All');
  const [search, setSearch] = useState('');

  const filtered = MOCK_PROBLEMS.filter(p => {
    if (selectedExam !== 'All' && p.examType !== selectedExam) return false;
    if (selectedSection !== 'All Sections' && p.section !== selectedSection) return false;
    if (selectedDifficulty !== 'All' && p.difficulty !== selectedDifficulty) return false;
    if (search && !p.topic.toLowerCase().includes(search.toLowerCase()) &&
        !p.type.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const sections = SECTIONS[selectedExam] ?? SECTIONS.All;

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'left', 'right']}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title} weight="bold">Practice</Text>
        <Text variant="muted" size="sm">{filtered.length} problems</Text>
      </View>

      {/* Search */}
      <View style={styles.searchBar}>
        <Input
          placeholder="Search problems, topics..."
          value={search}
          onChangeText={setSearch}
          leftIcon={<Text style={styles.searchIcon}>🔍</Text>}
        />
      </View>

      {/* Exam type filter */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.filterRow}
        style={styles.filterScroll}
      >
        {EXAM_TYPES.map(exam => (
          <TouchableOpacity
            key={exam}
            onPress={() => {
              setSelectedExam(exam);
              setSelectedSection('All Sections');
            }}
            style={[
              styles.examFilter,
              selectedExam === exam && styles.examFilterActive,
              exam !== 'All' && selectedExam === exam && {
                borderColor: Colors[exam.toLowerCase() as 'gre' | 'gmat' | 'sat'] + '80',
                backgroundColor: Colors[exam.toLowerCase() as 'gre' | 'gmat' | 'sat'] + '18',
              },
            ]}
          >
            <Text
              size="sm"
              weight={selectedExam === exam ? 'semibold' : 'normal'}
              style={{
                color: selectedExam === exam
                  ? exam === 'All'
                    ? Colors.foreground
                    : Colors[exam.toLowerCase() as 'gre' | 'gmat' | 'sat']
                  : Colors.mutedForeground,
              }}
            >
              {exam}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Section filter */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.sectionFilterRow}
        style={styles.filterScroll}
      >
        {sections.map(section => (
          <TouchableOpacity
            key={section}
            onPress={() => setSelectedSection(section)}
            style={[
              styles.sectionChip,
              selectedSection === section && styles.sectionChipActive,
            ]}
          >
            <Text
              size="xs"
              weight={selectedSection === section ? 'medium' : 'normal'}
              style={{ color: selectedSection === section ? Colors.foreground : Colors.mutedForeground }}
            >
              {section}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Difficulty filter */}
      <View style={styles.difficultyRow}>
        {DIFFICULTIES.map(diff => (
          <TouchableOpacity
            key={diff.label}
            onPress={() => setSelectedDifficulty(diff.label)}
            style={[
              styles.diffChip,
              selectedDifficulty === diff.label && styles.diffChipActive,
            ]}
          >
            <Text
              size="xs"
              weight={selectedDifficulty === diff.label ? 'semibold' : 'normal'}
              style={{
                color: selectedDifficulty === diff.label
                  ? diff.label === 'All' ? Colors.foreground
                    : diff.label === 'Easy' ? Colors.easy
                    : diff.label === 'Medium' ? Colors.warning
                    : Colors.hard
                  : Colors.mutedForeground,
              }}
            >
              {diff.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Problem list */}
      <FlatList
        data={filtered}
        keyExtractor={item => item.id.toString()}
        renderItem={({ item }) => <ProblemCard problem={item} />}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Text style={{ fontSize: 40 }}>🔍</Text>
            <Text variant="muted" style={{ textAlign: 'center', marginTop: Spacing[2] }}>
              No problems match your filters
            </Text>
            <Button
              variant="outline"
              size="sm"
              onPress={() => {
                setSelectedExam('All');
                setSelectedSection('All Sections');
                setSelectedDifficulty('All');
                setSearch('');
              }}
              style={{ marginTop: Spacing[4] }}
            >
              Clear Filters
            </Button>
          </View>
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.background },

  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'baseline',
    paddingHorizontal: Spacing[4],
    paddingTop: Spacing[4],
    paddingBottom: Spacing[2],
  },
  title: {
    fontSize: Typography.sizes['2xl'],
    letterSpacing: -0.3,
  },

  searchBar: {
    paddingHorizontal: Spacing[4],
    marginBottom: Spacing[1],
  },
  searchIcon: {
    fontSize: 14,
  },

  filterScroll: {
    flexGrow: 0,
  },
  filterRow: {
    paddingHorizontal: Spacing[4],
    paddingVertical: Spacing[2],
    gap: Spacing[2],
  },
  examFilter: {
    paddingHorizontal: Spacing[4],
    paddingVertical: Spacing[1] + 2,
    borderRadius: Radius.full,
    borderWidth: 1,
    borderColor: Colors.border,
    backgroundColor: Colors.card,
  },
  examFilterActive: {
    borderColor: Colors.foreground,
  },

  sectionFilterRow: {
    paddingHorizontal: Spacing[4],
    paddingVertical: Spacing[1],
    gap: Spacing[2],
  },
  sectionChip: {
    paddingHorizontal: Spacing[3],
    paddingVertical: Spacing[1],
    borderRadius: Radius.sm,
    backgroundColor: 'transparent',
  },
  sectionChipActive: {
    backgroundColor: Colors.secondary,
  },

  difficultyRow: {
    flexDirection: 'row',
    paddingHorizontal: Spacing[4],
    paddingVertical: Spacing[2],
    gap: Spacing[2],
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
    marginBottom: Spacing[2],
  },
  diffChip: {
    paddingHorizontal: Spacing[3],
    paddingVertical: Spacing[1],
    borderRadius: Radius.full,
    borderWidth: 1,
    borderColor: 'transparent',
  },
  diffChipActive: {
    backgroundColor: Colors.card,
    borderColor: Colors.border,
  },

  list: {
    paddingHorizontal: Spacing[4],
    gap: Spacing[3],
    paddingBottom: Spacing[10],
  },

  problemCard: {},
  problemInner: {
    flexDirection: 'row',
  },
  statusBar: {
    width: 44,
    alignItems: 'center',
    justifyContent: 'center',
    borderRightWidth: 1,
    padding: Spacing[3],
  },
  statusIcon: {
    fontSize: 18,
    fontFamily: Typography.fonts.sansBold,
  },
  problemContent: {
    flex: 1,
    padding: Spacing[3],
  },
  problemMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing[2],
    flexWrap: 'wrap',
  },
  problemFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: Spacing[2],
  },
  statusLabel: {},

  emptyState: {
    alignItems: 'center',
    paddingVertical: Spacing[10],
  },
});
