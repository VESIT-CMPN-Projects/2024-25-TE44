import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Image,
} from "react-native";
import { useRouter } from "expo-router";
import axios from "axios";

export default function LoginScreen() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();

  const handleSubmit = () => {
    axios
      .post("http://192.168.174.44:5000/login", { username, password })
      .then((result) => {
        console.log("Response:", result.data); 
  
        if (result.data.message === "Success") {
          router.push("/(tabs)"); 
        } else {
          alert("Invalid credentials! Try again.");
        }
      })
      .catch((error) => {
        console.error("Login error:", error);
        alert("Something went wrong. Please try again.");
      });
  };
  
  return (
    <View style={styles.container}>
      {/* Background Icons & Logo */}
      <Image
        source={require("../../assets/images/LE_Logo_light.png")} // Replace with your background image
        style={styles.backgroundImage}
      />

      {/* Login Heading */}
      <Text style={styles.title}>Log In</Text>

      {/* Input Fields */}
      <TextInput
        style={styles.input}
        placeholder="Username"
        placeholderTextColor="#6B8E75"
        value={username}
        onChangeText={setUsername}
      />
      <TextInput
        style={styles.input}
        placeholder="Password"
        placeholderTextColor="#6B8E75"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
      />

      {/* Login Button */}
      <TouchableOpacity style={styles.button}>
        <Text style={styles.buttonText} onPress={handleSubmit}>Login</Text>
      </TouchableOpacity>

      {/* Forgot Password Link */}
      <TouchableOpacity>
        <Text style={styles.register}
        onPress={() => router.push("/screens/register")}
        >Don't have an account? Register now</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#FFFFFF",
    paddingHorizontal: 20,
  },
  backgroundImage: {
    position: "absolute",
    top: 40,
    width: "100%",
    height: 150,
    resizeMode: "contain",
  },
  logo: {
    width: 120,
    height: 120,
    marginBottom: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#2C5E4E",
    marginBottom: 15,
  },
  input: {
    width: "100%",
    height: 50,
    borderWidth: 1,
    borderColor: "#A2C1A0",
    borderRadius: 25,
    paddingHorizontal: 15,
    backgroundColor: "#F0F8F2",
    fontSize: 16,
    color: "#2C5E4E",
    marginBottom: 15,
  },
  button: {
    width: "50%",
    height: 50,
    backgroundColor: "#497A68",
    justifyContent: "center",
    alignItems: "center",
    borderRadius: 20,
    marginBottom: 10,
  },
  buttonText: {
    color: "#FFF",
    fontSize: 18,
    fontWeight: "bold",
  },
  register: {
    color: "#497A68",
    fontSize: 14,
    marginTop: 10,
  },
});
