import React from "react";
import { Text, View, StyleSheet, Image } from "react-native";

export default function NotificationScreen() {
  return (
    <View style={styles.container}>
      {/* Notification Cards */}
      <View style={styles.notificationCard}>
        <Text style={styles.notificationTitle}>
          You’re 80% Done with Biodiversity!
        </Text>
        <Text style={styles.notificationMessage}>
          Keep up the great work! Just a few more lessons to go before you complete this module.
        </Text>
      </View>

      <View style={styles.notificationCard}>
        <Text style={styles.notificationTitle}>Your Daily Goal is Ready!</Text>
        <Text style={styles.notificationMessage}>
          Today’s target: Complete 2 lessons in History and 1 quiz. Let’s achieve it together!
        </Text>
      </View>

      {/* Centered Logo */}
      <View style={styles.centeredLogoContainer}>
        <Image
          source={require("../../assets/images/LE_Logo_light.png")}
          style={styles.logo}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#FFFFFF",
    paddingTop: 40,
    alignItems: "center",
  },
  notificationCard: {
    backgroundColor: "#D3F5DA",
    padding: 15,
    marginBottom: 10,
    borderRadius: 10,
    width: "90%",
    elevation: 3, // For subtle shadow on Android
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 3,
  },
  notificationTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#265C3F",
  },
  notificationMessage: {
    fontSize: 14,
    color: "#4A705D",
    marginTop: 5,
  },
  centeredLogoContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  logo: {
    alignSelf: "center",
    width: 150,
    height: 150,
    resizeMode: "contain",
  },
});
