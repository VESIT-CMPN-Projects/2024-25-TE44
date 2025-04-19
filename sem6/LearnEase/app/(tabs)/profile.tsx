import React, { useState } from "react";
import { View, Text, Image, TouchableOpacity, StyleSheet } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";

const router = useRouter();

const ProfileScreen = () => {
  const [selectedSubject, setSelectedSubject] = useState(null);

  return (
    <View style={styles.container}>
      {/* Profile Section */}
      <View style={styles.profileContainer}>
        <Image
          source={require("../../assets/images/profile.png")}
          style={styles.profileImage}
        />
        <View>
          <Text style={styles.name}>Kareena Lachhani</Text>
          <Text style={styles.subtitle}>A Keen Learner</Text>
        </View>
      </View>

      {/* Stats Section */}
      <View style={styles.statsContainer}>
        <LinearGradient colors={["#4EC490", "#428E6C"]} style={styles.statCard}>
          <Text style={styles.statValue}>13 hrs</Text>
          <Text style={styles.statLabel}>No of hours per week</Text>
        </LinearGradient>

        <LinearGradient colors={["#4EC490", "#428E6C"]} style={styles.statCard}>
          <Image
            source={require("../../assets/images/badge.png")}
            style={styles.badgeIcon}
          />
          <Text style={styles.statValue}>6 Badges</Text>
          <Text style={styles.statLabel}>Work hard and get a badge</Text>
        </LinearGradient>
      </View>

      {/* Subjects Section */}
      <Text style={styles.sectionTitle}>SUBJECTS</Text>
      <View style={styles.subjectsContainer}>
        <TouchableOpacity
          style={styles.subjectCard}
          onPress={() => setSelectedSubject("Add")}
        >
          <Ionicons name="add-circle-outline" size={40} color="#2F5233" />
        </TouchableOpacity>

        <TouchableOpacity
          style={[
            styles.subjectCard,
            selectedSubject === "English" && styles.selectedSubject,
          ]}
          onPress={() => setSelectedSubject("English")}
        >
          <Ionicons name="book-outline" size={35} color="#2F5233" />
          <Text style={styles.subjectText}>English</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[
            styles.subjectCard,
            selectedSubject === "Chemistry" && styles.selectedSubject,
          ]}
          onPress={() => setSelectedSubject("Chemistry")}
        >
          <Ionicons name="book-outline" size={35} color="#2F5233" />
          <Text style={styles.subjectText}>Chemistry</Text>
        </TouchableOpacity>
      </View>

      {/* Services Section */}
      <View style={styles.servicesHeader}>
        <Text style={styles.sectionTitle}>SERVICES</Text>
        <Text style={styles.moreText}>More &gt;</Text>
      </View>

      <View style={styles.servicesContainer}>
        <TouchableOpacity style={styles.serviceCard}>
          <Image
            source={require("../../assets/images/summarizer.png")}
            style={styles.serviceIcon}
          />
          <Text style={styles.serviceText}>Summarizer</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.serviceCard}
          onPress={() => router.push("/generate-schedule")}
        >
          <Image
            source={require("../../assets/images/schedule.png")}
            style={styles.serviceIcon}
          />
          <Text style={styles.serviceText}>Schedule Recommendation</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#FFFFFF",
    padding: 20,
  },
  profileContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 20,
  },
  profileImage: {
    width: 70,
    height: 70,
    borderRadius: 35,
    marginRight: 15,
  },
  name: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#2F5233",
  },
  subtitle: {
    fontSize: 14,
    color: "#4A7C59",
  },
  statsContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 20,
  },
  statCard: {
    width: "48%",
    padding: 20,
    borderRadius: 15,
    alignItems: "center",
  },
  statValue: {
    fontSize: 22,
    fontWeight: "bold",
    color: "#FFFFFF",
  },
  statLabel: {
    fontSize: 14,
    color: "#FFFFFF",
    textAlign: "center",
    marginTop: 5,
  },
  badgeIcon: {
    width: 50,
    height: 50,
    marginBottom: 5,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#2F5233",
    marginBottom: 10,
  },
  subjectsContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 20,
  },
  subjectCard: {
    width: 100,
    height: 100,
    backgroundColor: "#E8F5E9",
    borderRadius: 15,
    justifyContent: "center",
    alignItems: "center",
    elevation: 2,
  },
  subjectText: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#2F5233",
    marginTop: 5,
  },
  selectedSubject: {
    borderWidth: 2,
    borderColor: "#4A90E2",
    backgroundColor: "#FFFFFF",
  },
  servicesHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  moreText: {
    fontSize: 14,
    color: "#4A7C59",
  },
  servicesContainer: {
    flexDirection: "column", // Changed to column to stack services vertically
    gap: 15, // Added spacing between services
  },
  serviceCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#F1F8F5",
    padding: 15,
    borderRadius: 10,
    marginBottom: 10, // Added margin for separation
  },
  serviceIcon: {
    width: 30,
    height: 30,
    marginRight: 10,
  },
  serviceText: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#2F5233",
  },
});

export default ProfileScreen;
