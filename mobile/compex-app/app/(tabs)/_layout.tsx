import { Tabs } from 'expo-router';
import { View, StyleSheet, Platform } from 'react-native';
import { Text } from '@/components/ui/Text';
import { Colors, Spacing, Typography, Radius } from '@/constants/theme';

// SVG-free icon components using Unicode / text symbols
// Replace with a proper icon library (e.g. @expo/vector-icons) for production

function TabIcon({
  focused,
  icon,
  label,
}: {
  focused: boolean;
  icon: string;
  label: string;
}) {
  return (
    <View style={tabStyles.iconWrapper}>
      <Text
        style={[
          tabStyles.icon,
          { color: focused ? Colors.brand : Colors.mutedForeground },
        ]}
      >
        {icon}
      </Text>
      <Text
        style={[
          tabStyles.label,
          { color: focused ? Colors.brand : Colors.mutedForeground },
          focused && tabStyles.labelActive,
        ]}
      >
        {label}
      </Text>
      {focused && <View style={tabStyles.dot} />}
    </View>
  );
}

const tabStyles = StyleSheet.create({
  iconWrapper: {
    alignItems: 'center',
    paddingTop: Spacing[1],
    gap: 2,
    position: 'relative',
  },
  icon: {
    fontSize: 20,
    lineHeight: 22,
  },
  label: {
    fontSize: Typography.sizes.xs,
    fontFamily: Typography.fonts.sansMedium,
  },
  labelActive: {
    fontFamily: Typography.fonts.sansSemiBold,
  },
  dot: {
    position: 'absolute',
    top: -4,
    right: -4,
    width: 5,
    height: 5,
    borderRadius: 999,
    backgroundColor: Colors.brand,
  },
});

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: Colors.card,
          borderTopColor: Colors.border,
          borderTopWidth: 1,
          height: Platform.OS === 'ios' ? 82 : 64,
          paddingBottom: Platform.OS === 'ios' ? 24 : Spacing[2],
          paddingTop: Spacing[1],
          elevation: 0,
          shadowOpacity: 0,
        },
        tabBarShowLabel: false,
        tabBarActiveTintColor: Colors.brand,
        tabBarInactiveTintColor: Colors.mutedForeground,
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          tabBarIcon: ({ focused }) => (
            <TabIcon focused={focused} icon="⊞" label="Home" />
          ),
        }}
      />
      <Tabs.Screen
        name="problems"
        options={{
          title: 'Practice',
          tabBarIcon: ({ focused }) => (
            <TabIcon focused={focused} icon="✎" label="Practice" />
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: ({ focused }) => (
            <TabIcon focused={focused} icon="◎" label="Profile" />
          ),
        }}
      />
    </Tabs>
  );
}
