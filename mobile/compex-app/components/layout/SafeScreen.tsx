import React from 'react';
import { View, ScrollView, StyleSheet, ViewStyle, RefreshControl } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Colors, Spacing } from '@/constants/theme';

interface SafeScreenProps {
  children: React.ReactNode;
  scrollable?: boolean;
  padded?: boolean;
  style?: ViewStyle;
  contentStyle?: ViewStyle;
  onRefresh?: () => void;
  refreshing?: boolean;
  edges?: ('top' | 'bottom' | 'left' | 'right')[];
}

export function SafeScreen({
  children,
  scrollable = false,
  padded = true,
  style,
  contentStyle,
  onRefresh,
  refreshing = false,
  edges = ['top', 'left', 'right'],
}: SafeScreenProps) {
  return (
    <SafeAreaView style={[styles.safe, style]} edges={edges}>
      {scrollable ? (
        <ScrollView
          style={styles.scroll}
          contentContainerStyle={[
            padded && styles.padded,
            contentStyle,
          ]}
          showsVerticalScrollIndicator={false}
          refreshControl={
            onRefresh ? (
              <RefreshControl
                refreshing={refreshing}
                onRefresh={onRefresh}
                tintColor={Colors.mutedForeground}
              />
            ) : undefined
          }
        >
          {children}
        </ScrollView>
      ) : (
        <View style={[styles.container, padded && styles.padded, contentStyle]}>
          {children}
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  scroll: {
    flex: 1,
  },
  container: {
    flex: 1,
  },
  padded: {
    paddingHorizontal: Spacing[4],
    paddingTop: Spacing[4],
  },
});
