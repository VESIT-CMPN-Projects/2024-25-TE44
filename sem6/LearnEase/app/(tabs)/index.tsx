import React, { useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

const subjects = [
  { name: 'Social Science', type: 'all' },
  { name: 'English', type: 'strong' },
  { name: 'Chemistry', type: 'all' },
  { name: 'Biology', type: 'weak' },
];

const HomeScreen = () => {
  const [selectedTab, setSelectedTab] = useState('all');

  return (
    <View style={styles.container}>
      <ScrollView>
        {/* Greeting */}
        <Text style={styles.greeting}>Hi Kareena! 👋</Text>

        {/* Tabs */}
        <View style={styles.tabsContainer}>
          {['all', 'weak', 'strong'].map((tab) => (
            <TouchableOpacity
              key={tab}
              style={[styles.tab, selectedTab === tab && styles.activeTab]}
              onPress={() => setSelectedTab(tab)}
            >
              <Text style={[styles.tabText, selectedTab === tab && styles.activeTabText]}>
                {tab === 'all' ? 'All Subjects' : tab === 'weak' ? 'Weak Subjects' : 'Strong Subjects'}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Subjects Grid */}
        <View style={styles.subjectsContainer}>
          {subjects
            .filter((subject) => selectedTab === 'all' || subject.type === selectedTab)
            .map((subject, index) => (
              <LinearGradient
                key={index}
                colors={['#4EC490', '#428E6C']}
                style={styles.subjectCard}
              >
                <Text style={styles.subjectText}>{subject.name}</Text>
                <View style={styles.iconContainer}>
                  <Ionicons name="book-outline" size={28} color="#428E6C" />
                </View>
              </LinearGradient>
            ))}
        </View>

        {/* Productivity Section */}
        <View style={styles.productivityHeader}>
          <Text style={styles.sectionTitle}>Productivity</Text>
          <Text style={styles.moreText}>More {'>'}</Text>
        </View>

        {/* Productivity Items */}
        {[
          { title: 'Biodiversity', category: 'Biology' },
          { title: 'Periodic Table', category: 'Chemistry' }
        ].map((item, index) => (
          <View key={index} style={styles.taskCard}>
            <Ionicons name="book-outline" size={24} color="#387961" style={styles.taskIcon} />
            <View style={styles.taskTextContainer}>
              <Text style={styles.taskTitle}>{item.title}</Text>
              <Text style={styles.taskCategory}>{item.category}</Text>
            </View>
            <TouchableOpacity style={styles.startButton}>
              <Text style={styles.startText}>START</Text>
            </TouchableOpacity>
          </View>
        ))}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: 'white', padding: 20 },
  greeting: { fontSize: 26, fontWeight: 'bold', color: '#1c3b2e' },

  tabsContainer: {
    flexDirection: 'row',
    borderRadius: 25,
    backgroundColor: '#F1F8F4',
    padding: 6,
    marginVertical: 10,
  },
  tab: { flex: 1, paddingVertical: 10, borderRadius: 18, alignItems: 'center' },
  activeTab: { backgroundColor: '#A3D9C9' },
  tabText: { color: '#387961', fontWeight: '500' },
  activeTabText: { color: 'white', fontWeight: 'bold' },

  subjectsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginVertical: 15,
  },
  subjectCard: {
    width: '47%',
    height: 130, // Adjusted for correct proportions
    borderRadius: 12,
    justifyContent: 'space-between',
    padding: 12,
    marginVertical: 6,
    position: 'relative',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 5,
    elevation: 6,
  },
  subjectText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'left',
  },
  iconContainer: {
    alignSelf: 'flex-end',
    backgroundColor: 'white',
    padding: 10,
    borderRadius: 10,
  },

  productivityHeader: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 20 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: '#1c3b2e' },
  moreText: { color: '#387961', fontWeight: 'bold' },

  taskCard: {
    flexDirection: 'row',
    backgroundColor: '#EAF7F0',
    padding: 15,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 12,
  },
  taskIcon: { marginRight: 12 },
  taskTextContainer: { flex: 1 },
  taskTitle: { fontSize: 16, fontWeight: 'bold', color: '#1c3b2e' },
  taskCategory: { fontSize: 14, color: '#387961' },
  startButton: { backgroundColor: '#387961', paddingVertical: 6, paddingHorizontal: 18, borderRadius: 6 },
  startText: { color: 'white', fontWeight: 'bold' },
});

export default HomeScreen;
