import React from 'react';
import { Text as RNText, TextProps, StyleSheet } from 'react-native';
import { Colors, Typography } from '@/constants/theme';

type TextVariant = 'default' | 'muted' | 'heading' | 'subheading' | 'label' | 'caption';
type TextSize = 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl';
type TextWeight = 'normal' | 'medium' | 'semibold' | 'bold';

interface AppTextProps extends TextProps {
  variant?: TextVariant;
  size?: TextSize;
  weight?: TextWeight;
  children: React.ReactNode;
}

export function Text({
  variant = 'default',
  size,
  weight,
  style,
  children,
  ...props
}: AppTextProps) {
  return (
    <RNText
      style={[
        styles.base,
        variant === 'muted' && styles.muted,
        variant === 'heading' && styles.heading,
        variant === 'subheading' && styles.subheading,
        variant === 'label' && styles.label,
        variant === 'caption' && styles.caption,
        size && { fontSize: Typography.sizes[size] },
        weight === 'medium' && { fontFamily: Typography.fonts.sansMedium },
        weight === 'semibold' && { fontFamily: Typography.fonts.sansSemiBold },
        weight === 'bold' && { fontFamily: Typography.fonts.sansBold },
        style,
      ]}
      {...props}
    >
      {children}
    </RNText>
  );
}

const styles = StyleSheet.create({
  base: {
    fontFamily: Typography.fonts.sans,
    fontSize: Typography.sizes.base,
    color: Colors.foreground,
    lineHeight: Typography.sizes.base * Typography.lineHeights.normal,
  },
  muted: {
    color: Colors.mutedForeground,
  },
  heading: {
    fontFamily: Typography.fonts.sansBold,
    fontSize: Typography.sizes['3xl'],
    color: Colors.foreground,
    lineHeight: Typography.sizes['3xl'] * Typography.lineHeights.tight,
    letterSpacing: Typography.letterSpacing.tight,
  },
  subheading: {
    fontFamily: Typography.fonts.sansSemiBold,
    fontSize: Typography.sizes.xl,
    color: Colors.foreground,
    lineHeight: Typography.sizes.xl * Typography.lineHeights.tight,
  },
  label: {
    fontFamily: Typography.fonts.sansMedium,
    fontSize: Typography.sizes.sm,
    color: Colors.foreground,
    letterSpacing: Typography.letterSpacing.wide,
  },
  caption: {
    fontFamily: Typography.fonts.sans,
    fontSize: Typography.sizes.xs,
    color: Colors.mutedForeground,
  },
});
