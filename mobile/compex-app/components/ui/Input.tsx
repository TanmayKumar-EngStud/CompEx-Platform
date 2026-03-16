import React, { useState } from 'react';
import {
  TextInput,
  TextInputProps,
  View,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { Text } from './Text';
import { Colors, Radius, Spacing, Typography } from '@/constants/theme';

interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
  hint?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  onRightIconPress?: () => void;
}

export function Input({
  label,
  error,
  hint,
  leftIcon,
  rightIcon,
  onRightIconPress,
  style,
  ...props
}: InputProps) {
  const [focused, setFocused] = useState(false);

  return (
    <View style={styles.wrapper}>
      {label && (
        <Text style={styles.label} weight="medium">
          {label}
        </Text>
      )}
      <View
        style={[
          styles.container,
          focused && styles.containerFocused,
          !!error && styles.containerError,
        ]}
      >
        {leftIcon && <View style={styles.leftIcon}>{leftIcon}</View>}
        <TextInput
          style={[
            styles.input,
            leftIcon ? styles.inputWithLeft : null,
            rightIcon ? styles.inputWithRight : null,
            style,
          ]}
          placeholderTextColor={Colors.mutedForeground}
          selectionColor={Colors.brand}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          {...props}
        />
        {rightIcon && (
          <TouchableOpacity
            style={styles.rightIcon}
            onPress={onRightIconPress}
            hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
          >
            {rightIcon}
          </TouchableOpacity>
        )}
      </View>
      {error ? (
        <Text style={styles.error}>{error}</Text>
      ) : hint ? (
        <Text style={styles.hint}>{hint}</Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    width: '100%',
    gap: Spacing[1] + 2,
  },
  label: {
    fontSize: Typography.sizes.sm,
    color: Colors.foreground,
    marginBottom: 2,
  },
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.card,
    borderRadius: Radius.md,
    borderWidth: 1,
    borderColor: Colors.border,
    minHeight: 44,
  },
  containerFocused: {
    borderColor: Colors.ring,
  },
  containerError: {
    borderColor: Colors.destructive,
  },
  input: {
    flex: 1,
    paddingHorizontal: Spacing[3],
    paddingVertical: Spacing[2] + 2,
    fontFamily: Typography.fonts.sans,
    fontSize: Typography.sizes.base,
    color: Colors.foreground,
  },
  inputWithLeft: {
    paddingLeft: Spacing[2],
  },
  inputWithRight: {
    paddingRight: Spacing[2],
  },
  leftIcon: {
    paddingLeft: Spacing[3],
  },
  rightIcon: {
    paddingRight: Spacing[3],
  },
  error: {
    fontSize: Typography.sizes.xs,
    color: Colors.destructive,
  },
  hint: {
    fontSize: Typography.sizes.xs,
    color: Colors.mutedForeground,
  },
});
