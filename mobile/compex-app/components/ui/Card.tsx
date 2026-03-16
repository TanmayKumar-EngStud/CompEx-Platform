import React from 'react';
import { View, StyleSheet, ViewProps } from 'react-native';
import { Colors, Radius, Spacing, Shadows } from '@/constants/theme';

interface CardProps extends ViewProps {
  children: React.ReactNode;
  shadow?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export function Card({
  children,
  shadow = false,
  padding = 'md',
  style,
  ...props
}: CardProps) {
  return (
    <View
      style={[
        styles.card,
        shadow && Shadows.md,
        padding === 'none' && styles.paddingNone,
        padding === 'sm' && styles.paddingSm,
        padding === 'md' && styles.paddingMd,
        padding === 'lg' && styles.paddingLg,
        style,
      ]}
      {...props}
    >
      {children}
    </View>
  );
}

// CardHeader sub-component
interface CardSectionProps {
  children: React.ReactNode;
  style?: ViewProps['style'];
}

export function CardHeader({ children, style }: CardSectionProps) {
  return <View style={[styles.cardHeader, style]}>{children}</View>;
}

export function CardContent({ children, style }: CardSectionProps) {
  return <View style={[styles.cardContent, style]}>{children}</View>;
}

export function CardFooter({ children, style }: CardSectionProps) {
  return <View style={[styles.cardFooter, style]}>{children}</View>;
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.card,
    borderRadius: Radius.lg,
    borderWidth: 1,
    borderColor: Colors.cardBorder,
    overflow: 'hidden',
  },
  paddingNone: {},
  paddingSm: { padding: Spacing[3] },
  paddingMd: { padding: Spacing[4] },
  paddingLg: { padding: Spacing[6] },
  cardHeader: {
    paddingHorizontal: Spacing[4],
    paddingTop: Spacing[4],
    paddingBottom: Spacing[2],
  },
  cardContent: {
    paddingHorizontal: Spacing[4],
    paddingVertical: Spacing[3],
  },
  cardFooter: {
    paddingHorizontal: Spacing[4],
    paddingBottom: Spacing[4],
    paddingTop: Spacing[2],
  },
});
