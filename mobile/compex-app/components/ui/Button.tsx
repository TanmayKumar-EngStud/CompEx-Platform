import React from 'react';
import {
  TouchableOpacity,
  ActivityIndicator,
  StyleSheet,
  ViewStyle,
  TextStyle,
  TouchableOpacityProps,
  View,
} from 'react-native';
import { Text } from './Text';
import { Colors, Radius, Spacing, Typography } from '@/constants/theme';

type ButtonVariant = 'default' | 'secondary' | 'outline' | 'ghost' | 'destructive' | 'brand';
type ButtonSize = 'sm' | 'md' | 'lg' | 'icon';

interface ButtonProps extends TouchableOpacityProps {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  children?: React.ReactNode;
  fullWidth?: boolean;
}

export function Button({
  variant = 'default',
  size = 'md',
  loading = false,
  icon,
  iconPosition = 'left',
  children,
  fullWidth = false,
  style,
  disabled,
  ...props
}: ButtonProps) {
  const isDisabled = disabled || loading;

  return (
    <TouchableOpacity
      activeOpacity={0.75}
      disabled={isDisabled}
      style={[
        styles.base,
        styles[variant],
        styles[`size_${size}`],
        fullWidth && styles.fullWidth,
        isDisabled && styles.disabled,
        style,
      ]}
      {...props}
    >
      {loading ? (
        <ActivityIndicator
          size="small"
          color={variant === 'outline' || variant === 'ghost' || variant === 'secondary'
            ? Colors.foreground
            : Colors.primaryForeground}
        />
      ) : (
        <View style={styles.inner}>
          {icon && iconPosition === 'left' && (
            <View style={styles.iconLeft}>{icon}</View>
          )}
          {children && (
            <Text
              style={[
                styles.text,
                textVariantStyles[variant],
                size === 'sm' && styles.textSm,
                size === 'lg' && styles.textLg,
              ]}
              weight="medium"
            >
              {children}
            </Text>
          )}
          {icon && iconPosition === 'right' && (
            <View style={styles.iconRight}>{icon}</View>
          )}
        </View>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  base: {
    borderRadius: Radius.md,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
  },
  inner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconLeft: { marginRight: Spacing[2] },
  iconRight: { marginLeft: Spacing[2] },

  // Variants
  default: {
    backgroundColor: Colors.primary,
  },
  secondary: {
    backgroundColor: Colors.secondary,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  outline: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: Colors.border,
  },
  ghost: {
    backgroundColor: 'transparent',
  },
  destructive: {
    backgroundColor: Colors.destructive,
  },
  brand: {
    backgroundColor: Colors.brand,
  },

  // Sizes
  size_sm: { paddingHorizontal: Spacing[3], paddingVertical: Spacing[1] + 2, minHeight: 32 },
  size_md: { paddingHorizontal: Spacing[4], paddingVertical: Spacing[2] + 2, minHeight: 40 },
  size_lg: { paddingHorizontal: Spacing[6], paddingVertical: Spacing[3], minHeight: 48 },
  size_icon: { width: 40, height: 40, padding: 0, borderRadius: Radius.md },

  fullWidth: { width: '100%' },
  disabled: { opacity: 0.5 },

  // Text
  text: {
    fontFamily: Typography.fonts.sansMedium,
    fontSize: Typography.sizes.sm,
    color: Colors.primaryForeground,
  },
  textSm: { fontSize: Typography.sizes.xs },
  textLg: { fontSize: Typography.sizes.base },
});

const textVariantStyles: Record<ButtonVariant, TextStyle> = {
  default: { color: Colors.primaryForeground },
  secondary: { color: Colors.foreground },
  outline: { color: Colors.foreground },
  ghost: { color: Colors.foreground },
  destructive: { color: '#fff' },
  brand: { color: '#fff' },
};
