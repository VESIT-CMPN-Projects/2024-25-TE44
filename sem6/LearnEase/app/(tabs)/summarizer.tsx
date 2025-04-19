import React, { useState } from "react";
import {
  Text,
  View,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  Alert,
  Image,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import * as DocumentPicker from "expo-document-picker";
import axios from "axios"; 
import { router } from "expo-router";

interface Document {
  uri: string;
  name: string;
  size: number;
  mimeType: string;
}

export default function SummarizerScreen() {
  const [selectedPdf, setSelectedPdf] = useState<Document | null>(null);
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");

  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: "application/pdf",
        copyToCacheDirectory: true,
      });

      if (!result.canceled) {
        const { uri, name, size } = result.assets[0];
        setSelectedPdf({ uri, name, size, mimeType: "application/pdf" });
      } else {
        Alert.alert("Selection Canceled", "Please select a PDF document.");
      }
    } catch (error) {
      console.error("Error while picking document:", error);
      Alert.alert("Error", "Failed to pick the document.");
    }
  };

  const sendPdfForSummary = async () => {
    if (!selectedPdf) {
      Alert.alert("No PDF selected", "Please select a PDF before sending.");
      return;
    }
  
    setLoading(true);
    const formData = new FormData();
    formData.append("file", {
      uri: selectedPdf.uri,
      name: selectedPdf.name,
      type: "application/pdf",
    });
  
    try {
      // 1️⃣ Upload PDF to Express (local storage + MongoDB)
      const uploadResponse = await axios.post(
        "http://192.168.174.44:5000/api/upload",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
  
      console.log("Upload Success:", uploadResponse.data);
  
      
      if (uploadResponse.data.pdf && uploadResponse.data.pdf.summary) {
        setSummary(uploadResponse.data.pdf.summary);
      } else {
        
        const summaryResponse = await axios.post(
          "http://192.168.174.44:8000/upload_pdf/",
          formData,
          { headers: { "Content-Type": "multipart/form-data" } }
        );
  
        console.log("Summary Response:", summaryResponse.data);
        setSummary(summaryResponse.data.summary);
      }
    } catch (error) {
      console.error("Error Response:", error.response?.data || error.message);
      Alert.alert("Error", "Failed to generate summary");
    }
  
    setLoading(false);
  };

  return (
    <KeyboardAvoidingView
      style={{ flex: 1 }}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
      keyboardVerticalOffset={80}
    >
      <View style={styles.container}>
        {/* Show Logo if No PDF Selected */}
        {!selectedPdf && !loading && (
          <View style={styles.centeredLogoContainer}>
            <Image
              source={require("../../assets/images/LE_Logo_light.png")}
              style={styles.logo}
            />
          </View>
        )}

        {/* Show Summary or Loading Indicator */}
        <ScrollView style={styles.summaryContainer}>
          {loading ? (
            <Text style={styles.loadingText}>Loading summary...</Text>
          ) : selectedPdf && summary ? (
            <>
              {/* PDF File Info */}
              <View style={styles.pdfInfo}>
                <Ionicons name="document-outline" size={24} color="green" />
                <Text style={styles.pdfName}>{selectedPdf.name}</Text>
              </View>

              {/* Summary Display */}
              <Text style={styles.summary}>{summary}</Text>
            </>
          ) : null}
        </ScrollView>

        {/* Input Area */}
        <View style={styles.inputArea}>
          <TextInput
            style={styles.textInput}
            placeholder="Ask your queries..."
            value={query}
            onChangeText={setQuery}
          />
          <View style={styles.rightIcons}>
            {/* PDF Picker Button */}
            <TouchableOpacity onPress={pickDocument} style={styles.iconContainer}>
              <Ionicons name="document-outline" size={24} color="green" />
            </TouchableOpacity>

            <View style={styles.divider} />

            {/* Quiz Button */}
            <TouchableOpacity style={styles.quizButton} onPress={() => router.push({pathname: "/quiz", params: {summary} })}>
              <Text style={styles.quizText}>Quiz</Text>
            </TouchableOpacity>

            <View style={styles.divider} />

            {/* Send Button */}
            <TouchableOpacity onPress={sendPdfForSummary} style={styles.sendButton}>
              <Ionicons name="send" size={24} color="green" />
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#ffffff",
  },
  centeredLogoContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  logo: {
    alignSelf: "center",
  },
  summaryContainer: {
    flex: 1,
    width: "100%",
    padding: 20,
  },
  loadingText: {
    textAlign: "center",
    fontSize: 16,
    color: "#333",
  },
  pdfInfo: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 10,
  },
  pdfName: {
    marginLeft: 10,
    fontSize: 16,
    color: "#333",
  },
  summary: {
    fontSize: 13,
    color: "#555",
  },
  inputArea: {
    flexDirection: "row",
    alignItems: "center",
    padding: 10,
    borderTopWidth: 1,
    borderTopColor: "#ccc",
    backgroundColor: "#fff",
  },
  textInput: {
    flex: 1,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#ccc",
    paddingHorizontal: 10,
    height: 40,
    marginRight: 10,
    backgroundColor: "#f9f9f9",
    color: "#333",
  },
  rightIcons: {
    flexDirection: "row",
    alignItems: "center",
  },
  iconContainer: {
    padding: 5,
  },
  divider: {
    width: 1,
    height: 20,
    backgroundColor: "#ccc",
    marginHorizontal: 10,
  },
  quizButton: {
    padding: 5,
    backgroundColor: "#e0f7fa",
    borderRadius: 5,
  },
  quizText: {
    color: "green",
    fontSize: 16,
  },
  sendButton: {
    padding: 5,
  },
});