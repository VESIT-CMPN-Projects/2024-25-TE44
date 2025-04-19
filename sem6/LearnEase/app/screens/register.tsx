import axios from "axios";
import { useRouter } from "expo-router";
import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Image,
} from "react-native";
import DropDownPicker from "react-native-dropdown-picker";

export default function RegisterScreen() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [openClass, setOpenClass] = useState(false);
  const [selectedClass, setSelectedClass] = useState(null);
  const [classItems, setClassItems] = useState([
    { label: "Std 8", value: "8" },
    { label: "Std 9", value: "9" },
    { label: "Std 10", value: "10" },
  ]);
  const router=useRouter();
  const [openSubject, setOpenSubject] = useState(false);
  const [selectedSubjects, setSelectedSubjects] = useState([]);
  const [subjectItems, setSubjectItems] = useState([
    { label: "English", value: "English" },
    { label: "Science", value: "Science" },
    { label: "History", value: "History" },
  ]);
  const handleRegister=()=>{
    if(!username||!password||!confirmPassword||!selectedClass||selectedSubjects.length===0){
      alert("Please fill all the fields");
      return;
    }
    if(password!=confirmPassword){
      alert("Passwords do not match");
      return;
    }
    axios.post("http://192.168.174.44:5000/register",{
      username,
      password,
      selectedClass,
      selectedSubjects,
    })
    .then((response)=>{
      alert("Registered successfully");
      router.push("/screens/login");
    })
    .catch((error)=>{
      alert(error.response?.data?.message||"Registration failed");
    });
    };
  return (
    <View style={styles.container}>
      {/* Background Icons & Logo */}
      <Image
        source={require("../../assets/images/LE_Logo_light.png")}
        style={styles.backgroundImage}
      />

      {/* Title */}
      <Text style={styles.title}>Create Your Account</Text>

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
      <TextInput
        style={styles.input}
        placeholder="Re-enter Password"
        placeholderTextColor="#6B8E75"
        secureTextEntry
        value={confirmPassword}
        onChangeText={setConfirmPassword}
      />

      {/* Class Dropdown (Fixed Overlapping) */}
      <View style={[styles.dropdownWrapper, openClass && { zIndex: 10, elevation: 10 }]}>
        <DropDownPicker
          open={openClass}
          value={selectedClass}
          items={classItems}
          setOpen={setOpenClass}
          setValue={setSelectedClass}
          setItems={setClassItems}
          placeholder="Select Class"
          style={styles.dropdown}
          dropDownContainerStyle={styles.dropdownContainer}
        />
      </View>

      {/* Subject Dropdown (Fixed Overlapping) */}
      <View style={[styles.dropdownWrapper, openSubject && { zIndex: 9, elevation: 9 }]}>
        <DropDownPicker
          open={openSubject}
          value={selectedSubjects}
          items={subjectItems}
          setOpen={setOpenSubject}
          setValue={setSelectedSubjects}
          setItems={setSubjectItems}
          multiple={true}
          mode="BADGE"
          placeholder="Select Subject"
          style={styles.dropdown}
          dropDownContainerStyle={styles.dropdownContainer}
        />
      </View>

      {/* Sign Up Button */}
      <TouchableOpacity style={styles.button}>
        <Text style={styles.buttonText} onPress={handleRegister}>Sign Up</Text>
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
    height: 120,
    resizeMode: "contain",
  },
  title: {
    fontSize: 22,
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
  dropdownWrapper: {
    width: "100%",
    marginBottom: 15,
    zIndex:0
  },
  dropdown: {
    borderRadius: 25,
    backgroundColor: "#F0F8F2",
    borderColor: "#A2C1A0",
    zIndex:0
  },
  dropdownContainer: {
    backgroundColor: "#F0F8F2",
    borderColor: "#A2C1A0",
    zIndex:100
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
});
