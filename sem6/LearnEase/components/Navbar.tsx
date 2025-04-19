import React, { useState } from 'react';
import { View, Text, Image, StyleSheet, TouchableOpacity, Modal } from 'react-native';
import Ionicons from '@expo/vector-icons/Ionicons';
import { router } from "expo-router";

export default function Navbar() {
  const [modalVisible, setModalVisible] = useState(false);
  return (
    <View style={styles.navbar}>
      <View style={styles.logoContainer}>
        <Image
          source={require('../assets/images/LE_Logo.png')} 
          style={styles.logo}
          resizeMode="contain"
        />
      </View>
      <TouchableOpacity
        style={styles.menuIcon}
        onPress={() => setModalVisible(true)}
      >
        <Ionicons name="menu" size={30} color="rgba(13, 105, 72, 1)" />
      </TouchableOpacity>

      {/* Modal for Login/Logout */}
      <Modal
        transparent={true}
        animationType="fade"
        visible={modalVisible}
        onRequestClose={() => setModalVisible(false)}
      >
        <TouchableOpacity
          style={styles.modalOverlay}
          activeOpacity={1}
          onPress={() => setModalVisible(false)}
        >
          <View style={styles.modalContent}>
            {/* Login Button - Navigates to Login Page */}
            <TouchableOpacity
              style={styles.menuItem}
              onPress={() => {
                setModalVisible(false);
                router.push("/screens/login"); 
              }}
            >
              <Text style={styles.menuText}>Login</Text>
            </TouchableOpacity>

            {/* Logout Button - Add Logic for Logout */}
            <TouchableOpacity
              style={styles.menuItem}
              onPress={() => {
                setModalVisible(false);
                alert("Logout Clicked"); 
              }}
            >
              <Text style={styles.menuText}>Logout</Text>
            </TouchableOpacity>
          </View>
        </TouchableOpacity>
        </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  navbar: {
    marginTop:40,
    height: 60,
    backgroundColor: '#fff',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  logoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  logo: {
    width: 70,
    height: 50,
  },
  logoText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#416a57',
    marginLeft: 10,
  },
  menuIcon: {
    padding: 5,
  },
  modalOverlay: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(0,0,0,0.3)", 
  },
  modalContent: {
    backgroundColor: "white",
    padding: 20,
    borderRadius: 10,
    width: 150,
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 5,
  },
  menuItem: {
    paddingVertical: 10,
    width: "100%",
    alignItems: "center",
  },
  menuText: {
    fontSize: 16,
    color: "rgba(13, 105, 72, 1)",
    fontWeight: "bold",
  },
});
