import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { Text } from './Text';
import { Colors, Radius, Spacing, Typography } from '@/constants/theme';

type BadgeVariant =
  | 'default'
  | 'secondary'
  | 'outline'
  | 'success'
  | 'warning'
  | 'error'
  | 'info'
  | 'gre'
  | 'gmat'
  | 'sat'
  | 'easy'
  | 'medium'
  | 'hard';

interface BadgeProps {
  label: string;
  variant?: BadgeVariant;
  style?: ViewStyle;
}

export function Badge({ label, variant = 'default', style }: BadgeProps) {
  return (
    <View style={[styles.base, badgeStyles[variant], style]}>
      <Text style={[styles.text, textStyles[variant]]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  base: {
    alignSelf: 'flex-start',
    paddingHorizontal: Spacing[2] + 2,
    paddingVertical: 2,
    borderRadius: Radius.full,
    borderWidth: 1,
  },
  text: {
    fontSize: Typography.sizes.xs,
    fontFamily: Typography.fonts.sansMedium,
    lineHeight: 16,
  },
});

const badgeStyles: Record<BadgeVariant, ViewStyle> = {
  default: { backgroundColor: Colors.secondary, borderColor: Colors.border },
  secondary: { backgroundColor: Colors.muted, borderColor: Colors.border },
  outline: { backgroundColor: 'transparent', borderColor: Colors.border },
  success: { backgroundColor: 'rgba(34,197,94,0.15)', borderColor: 'rgba(34,197,94,0.4)' },
  warning: { backgroundColor: 'rgba(245,158,11,0.15)', borderColor: 'rgba(245,158,11,0.4)' },
  error: { backgroundColor: 'rgba(239,68,68,0.15)', borderColor: 'rgba(239,68,68,0.4)' },
  info: { backgroundColor: 'rgba(6,182,212,0.15)', borderColor: 'rgba(6,182,212,0.4)' },
  gre: { backgroundColor: 'rgba(139,92,246,0.15)', borderColor: 'rgba(139,92,246,0.4)' },
  gmat: { backgroundColor: 'rgba(245,158,11,0.15)', borderColor: 'rgba(245,158,11,0.4)' },
  sat: { backgroundColor: 'rgba(6,182,212,0.15)', borderColor: 'rgba(6,182,212,0.4)' },
  easy: { backgroundColor: 'rgba(34,197,94,0.15)', borderColor: 'rgba(34,197,94,0.4)' },
  medium: { backgroundColor: 'rgba(245,158,11,0.15)', borderColor: 'rgba(245,158,11,0.4)' },
  hard: { backgroundColor: 'rgba(239,68,68,0.15)', borderColor: 'rgba(239,68,68,0.4)' },
};

const textStyles: Record<BadgeVariant, object> = {
  default: { color: Colors.foreground },
  secondary: { color: Colors.mutedForeground },
  outline: { color: Colors.mutedForeground },
  success: { color: Colors.success },
  warning: { color: Colors.warning },
  error: { color: Colors.error },
  info: { color: Colors.info },
  gre: { color: Colors.gre },
  gmat: { color: Colors.gmat },
  sat: { color: Colors.sat },
  easy: { color: Colors.easy },
  medium: { color: Colors.warning },
  hard: { color: Colors.hard },
};
