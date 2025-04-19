import { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  SafeAreaView,
} from "react-native";
import { useRouter } from "expo-router";
import { Picker } from "@react-native-picker/picker";

const subjectsData = {
  English: [
    "Grammar Basics",
    "Tenses",
    "Active & Passive Voice",
    "Speech",
    "Writing Skills",
    "Comprehension",
    "Essay Writing",
    "Letter Writing",
    "Punctuation",
    "Vocabulary Building",
  ],
  Maths: [
    "Algebra",
    "Trigonometry",
    "Geometry",
    "Probability",
    "Statistics",
    "Calculus",
    "Functions",
    "Matrices",
    "Polynomials",
    "Graphs",
  ],
  Science: [
    "Physics - Motion",
    "Physics - Light",
    "Chemistry - Atoms",
    "Chemistry - Bonding",
    "Biology - Cells",
    "Biology - Genetics",
    "Physics - Energy",
    "Chemistry - Reactions",
    "Biology - Ecosystems",
    "Science - Technology",
  ],
  "Social Science": [
    "History - Revolutions",
    "History - Empires",
    "Geography - Climate",
    "Geography - Maps",
    "Civics - Constitution",
    "Civics - Rights",
    "Economics - Trade",
    "Economics - Banking",
    "History - World Wars",
    "Social - Environment",
  ],
};

export default function ScheduleScreen() {
  const [weakSubjects, setWeakSubjects] = useState<string[]>([]);
  const [selectedSubjects, setSelectedSubjects] = useState<string[]>([]);
  const [selectedTopics, setSelectedTopics] = useState<Record<string, string[]>>({});
  const [hoursPerDay, setHoursPerDay] = useState("5"); // Default: 5 hours per day
  const router = useRouter();

  const toggleSubjectSelection = (subject: string) => {
    setSelectedSubjects((prev) =>
      prev.includes(subject)
        ? prev.filter((s) => s !== subject)
        : [...prev, subject]
    );
  };

  const toggleWeakSubject = (subject: string) => {
    setWeakSubjects((prev) =>
      prev.includes(subject)
        ? prev.filter((s) => s !== subject)
        : [...prev, subject]
    );
  };

  const toggleTopicSelection = (subject: string, topic: string) => {
    setSelectedTopics((prev) => ({
      ...prev,
      [subject]: prev[subject]?.includes(topic)
        ? prev[subject].filter((t) => t !== topic)
        : [...(prev[subject] || []), topic],
    }));
  };

  const handleGenerateSchedule = () => {
    if (selectedSubjects.length === 0) return;
    router.push({
      pathname: "/generate-schedule",
      params: {
        topics: JSON.stringify(selectedTopics),
        weakSubjects: JSON.stringify(weakSubjects),
        hoursPerDay,
      },
    });
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Fixed Header Section */}
      <View style={styles.fixedHeader}>
        <Text style={styles.header}>Schedule Setup</Text>

        {/* Number of Hours Dropdown */}
        <Text style={styles.label}>Number of Hours per Day</Text>
        <View style={styles.dropdown}>
          <Picker
            selectedValue={hoursPerDay}
            onValueChange={(value) => setHoursPerDay(value)}
            style={{ color: "#3C896D" }}
          >
            {Array.from({ length: 8 }, (_, i) => (i + 1).toString()).map((hour) => (
              <Picker.Item key={hour} label={hour} value={hour} />
            ))}
          </Picker>
        </View>
      </View>

      {/* Scrollable Content */}
      <ScrollView style={styles.scrollContainer} contentContainerStyle={styles.scrollContent}>
        {/* Subjects Selection */}
        <Text style={styles.subHeader}>Select Subjects</Text>
        <View style={styles.subjectContainer}>
          {Object.keys(subjectsData).map((subject) => (
            <TouchableOpacity
              key={subject}
              style={[
                styles.subjectCard,
                selectedSubjects.includes(subject) && styles.selectedSubject,
              ]}
              onPress={() => toggleSubjectSelection(subject)}
            >
              <Text style={styles.subjectText}>{subject}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Weak Subjects Selection */}
        {selectedSubjects.length > 0 && (
          <View style={styles.weakSubjectsContainer}>
            <Text style={styles.subHeader}>Select Weak Subjects</Text>
            <View style={styles.subjectContainer}>
              {selectedSubjects.map((subject) => (
                <TouchableOpacity
                  key={`weak-${subject}`}
                  style={[
                    styles.weakSubjectCard,
                    weakSubjects.includes(subject) && styles.selectedWeakSubject,
                  ]}
                  onPress={() => toggleWeakSubject(subject)}
                >
                  <Text style={styles.subjectText}>{subject}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}

        {/* Topics Selection */}
        {selectedSubjects.length > 0 && (
          <View style={styles.topicContainer}>
            <Text style={styles.subHeader}>Select Topics</Text>
            {selectedSubjects.map((subject) => (
              <View key={subject} style={styles.subjectSection}>
                <Text style={styles.subjectTitle}>{subject}</Text>
                <View style={styles.topicList}>
                  {subjectsData[subject].map((topic) => (
                    <TouchableOpacity
                      key={topic}
                      style={[
                        styles.topicCard,
                        selectedTopics[subject]?.includes(topic) && styles.selectedTopic,
                      ]}
                      onPress={() => toggleTopicSelection(subject, topic)}
                    >
                      <Text style={styles.topicText}>{topic}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
            ))}
          </View>
        )}

        {/* Generate Button */}
        {selectedSubjects.length > 0 && Object.keys(selectedTopics).length > 0 && (
          <TouchableOpacity
            style={styles.generateButton}
            onPress={handleGenerateSchedule}
          >
            <Text style={styles.buttonText}>Generate Schedule</Text>
          </TouchableOpacity>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    backgroundColor: "#FFFFFF", 
  },
  fixedHeader: {
    backgroundColor: "#FFFFFF",
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: "#E0E0E0",
  },
  scrollContainer: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
    paddingTop: 10,
  },
  header: { 
    fontSize: 24, 
    fontWeight: "bold", 
    textAlign: "center", 
    marginBottom: 10, 
    color: "#3C896D" 
  },
  label: { 
    fontSize: 18, 
    fontWeight: "bold", 
    color: "#4FB286", 
    marginBottom: 5 
  },
  dropdown: { 
    borderWidth: 1, 
    borderColor: "#4FB286", 
    borderRadius: 5, 
    marginBottom: 5 
  },
  subHeader: { 
    fontSize: 20, 
    fontWeight: "bold", 
    marginVertical: 10, 
    color: "#4FB286" 
  },
  subjectContainer: { 
    flexDirection: "row", 
    flexWrap: "wrap", 
    justifyContent: "space-around" 
  },
  weakSubjectsContainer: {
    marginTop: 10,
  },
  subjectCard: { 
    backgroundColor: "#4FB286", 
    padding: 15, 
    margin: 5, 
    borderRadius: 10, 
    width: "45%", 
    alignItems: "center" 
  },
  weakSubjectCard: {
    backgroundColor: "#FFA07A", // Light salmon color for weak subjects
    padding: 15, 
    margin: 5, 
    borderRadius: 10, 
    width: "45%", 
    alignItems: "center"
  },
  selectedSubject: { 
    backgroundColor: "#3C896D" 
  },
  selectedWeakSubject: {
    backgroundColor: "#FF6347" // Tomato color for selected weak subjects
  },
  subjectText: { 
    fontSize: 16, 
    color: "#FFFFFF", 
    fontWeight: "bold" 
  },
  topicContainer: { 
    marginTop: 10 
  },
  subjectSection: { 
    marginBottom: 15 
  },
  subjectTitle: { 
    fontSize: 18, 
    fontWeight: "bold", 
    marginBottom: 5, 
    color: "#3C896D" 
  },
  topicList: { 
    flexDirection: "row", 
    flexWrap: "wrap", 
    justifyContent: "space-around" 
  },
  topicCard: { 
    backgroundColor: "#4FB286", 
    padding: 10, 
    margin: 5, 
    borderRadius: 5, 
    width: "45%", 
    alignItems: "center" 
  },
  selectedTopic: { 
    backgroundColor: "#3C896D" 
  },
  topicText: { 
    fontSize: 16, 
    color: "#FFFFFF" 
  },
  generateButton: { 
    backgroundColor: "#3C896D", 
    padding: 15, 
    borderRadius: 8, 
    alignItems: "center", 
    marginTop: 20,
    marginBottom: 10 
  },
  buttonText: { 
    fontSize: 18, 
    color: "#FFF", 
    fontWeight: "bold" 
  },
});