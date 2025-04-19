// app/tabs/_layout.tsx

import { Tabs } from "expo-router";
import Ionicons from '@expo/vector-icons/Ionicons';


export default function TabLayout() {
  return (
    <Tabs
    screenOptions={{
      tabBarActiveTintColor: '#0D6948',
      headerShown: false,
    }}
    >
      <Tabs.Screen 
        name="index"
        options={{
          tabBarLabel: "Home",
          tabBarIcon: ({ color, focused }) => (
            <Ionicons name={focused ? 'home-sharp' : 'home-outline'} color={color} size={24} />
          ),
        }}
      />
      <Tabs.Screen 
        name="summarizer" 
        options={{
          tabBarLabel: "Summarizer",
          tabBarIcon: ({ color, focused }) => (
            <Ionicons name={focused ? 'document-text' : 'document-text-outline'} color={color} size={24} />
          ),
        }}
      />
      <Tabs.Screen 
        name="schedule" 
        options={{
          tabBarLabel: "Schedule",
          tabBarIcon: ({ color, focused }) => (
            <Ionicons name={focused ? 'calendar' : 'calendar-outline'} color={color} size={24} />
          ),
        }}
      />
      <Tabs.Screen 
        name="notifications" 
        options={{
          tabBarLabel: "Notifications",
          tabBarIcon: ({ color, focused }) => (
            <Ionicons name={focused ? 'notifications' : 'notifications-outline'} color={color} size={24} />
          ),
        }}
      />
      <Tabs.Screen 
        name="profile" 
        options={{
          tabBarLabel: "Profile",
          tabBarIcon: ({ color, focused }) => (
            <Ionicons name={focused ? 'person' : 'person-outline'} color={color} size={24} />
          ),
        }}
      />
    </Tabs>
  );
}
