import { useState, useEffect } from "react";
import { useLocalSearchParams } from "expo-router";
import { 
  View, 
  Text, 
  StyleSheet, 
  FlatList, 
  TouchableOpacity, 
  ActivityIndicator,
  Alert
} from "react-native";
import { generateStudyPlan } from "./work/connector";

export default function GenerateScheduleScreen() {
  const params = useLocalSearchParams();
  const topics = params.topics ? JSON.parse(params.topics as string) : {};
  const weakSubjects = params.weakSubjects ? JSON.parse(params.weakSubjects as string) : [];
  const hoursPerDay = params.hoursPerDay as string || "5";

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [scheduleData, setScheduleData] = useState<any>(null);
  const [completedTopics, setCompletedTopics] = useState<Record<string, boolean>>({});

  useEffect(() => {
    const fetchSchedule = async () => {
      setIsLoading(true);
      try {
        const response = await generateStudyPlan(hoursPerDay, weakSubjects, topics);
        
        if (response.error) {
          setError(response.error);
        } else {
          setScheduleData(response);
        }
      } catch (err) {
        setError("Failed to generate schedule. Please try again.");
        console.error("Schedule generation error:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSchedule();
  }, []);

  const toggleCompletion = (day: string, index: number) => {
    const topicKey = `${day}-${index}`;
    setCompletedTopics((prev) => ({
      ...prev,
      [topicKey]: !prev[topicKey],
    }));
  };

  if (isLoading) {
    return (
      <View style={styles.centeredContainer}>
        <ActivityIndicator size="large" color="#3C896D" />
        <Text style={styles.loadingText}>Generating your personalized schedule...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centeredContainer}>
        <Text style={styles.errorText}>Error: {error}</Text>
        <TouchableOpacity style={styles.retryButton}>
          <Text style={styles.buttonText}>Try Again</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (!scheduleData || !scheduleData.studyPlan || scheduleData.studyPlan.length === 0) {
    return (
      <View style={styles.centeredContainer}>
        <Text style={styles.errorText}>No schedule data available.</Text>
        <TouchableOpacity style={styles.retryButton}>
          <Text style={styles.buttonText}>Try Again</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Your Study Schedule</Text>
      <Text style={styles.subHeader}>
        {weakSubjects.length > 0 
          ? `Focus areas: ${weakSubjects.join(', ')}`
          : 'Balanced study plan'}
      </Text>

      <FlatList
        data={scheduleData.studyPlan}
        keyExtractor={(item) => item.day}
        renderItem={({ item }) => (
          <View style={styles.daySection}>
            <Text style={styles.dayHeader}>{item.day}</Text>
            {item.sessions.map((session: any, index: number) => {
              const topicKey = `${item.day}-${index}`;
              const isCompleted = completedTopics[topicKey] || false;

              return (
                <View key={`${item.day}-${index}`} style={styles.scheduleItem}>
                  <Text style={styles.timeText}>{session.time_allocated}</Text>
                  <View style={styles.row}>
                    <View style={styles.subjectContainer}>
                      <Text style={[styles.subjectText, isCompleted && styles.strikeThrough]}>
                        {session.subject}
                      </Text>
                      <Text style={[styles.topicText, isCompleted && styles.strikeThrough]}>
                        {session.topic}
                      </Text>
                    </View>
                    <TouchableOpacity
                      style={[styles.radioButton, isCompleted && styles.radioSelected]}
                      onPress={() => toggleCompletion(item.day, index)}
                    />
                  </View>
                  <Text style={styles.studyTip}>💡 {session.study_tips}</Text>
                </View>
              );
            })}
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    padding: 20, 
    backgroundColor: "#FFF" 
  },
  header: { 
    fontSize: 26, 
    fontWeight: "bold", 
    textAlign: "center", 
    color: "#265C3A", 
    marginBottom: 6 
  },
  subHeader: {
    fontSize: 16,
    textAlign: "center",
    color: "#4FB286",
    marginBottom: 15,
    fontStyle: "italic"
  },
  centeredContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 20
  },
  loadingText: {
    fontSize: 18,
    color: "#3C896D",
    marginTop: 15,
    textAlign: "center"
  },
  errorText: {
    fontSize: 18,
    color: "#FF6347",
    marginBottom: 20,
    textAlign: "center"
  },
  retryButton: {
    backgroundColor: "#3C896D",
    padding: 15,
    borderRadius: 8,
    alignItems: "center",
    width: "60%"
  },
  buttonText: {
    fontSize: 18,
    color: "#FFF",
    fontWeight: "bold"
  },
  /* Day Header */
  daySection: { marginBottom: 20 },
  dayHeader: { fontSize: 20, fontWeight: "bold", color: "#3C896D", marginBottom: 10 },

  /* Schedule Items */
  scheduleItem: { marginBottom: 15, backgroundColor: "#F5F5F5", borderRadius: 10, padding: 10 },
  timeText: { fontSize: 16, color: "#265C3A", marginBottom: 5, fontWeight: "bold" },
  row: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#4FB286",
    paddingVertical: 12,
    paddingHorizontal: 15,
    borderRadius: 10,
    justifyContent: "space-between",
  },
  subjectContainer: {
    flex: 1,
  },
  subjectText: { 
    color: "#FFF", 
    fontSize: 16, 
    fontWeight: "bold" 
  },
  topicText: {
    color: "#E0E0E0",
    fontSize: 14,
  },
  strikeThrough: { 
    textDecorationLine: "line-through", 
    color: "#D3D3D3" 
  },

  /* Radio Button */
  radioButton: {
    width: 18,
    height: 18,
    borderRadius: 9,
    borderWidth: 2,
    borderColor: "#FFF",
    backgroundColor: "transparent",
  },
  radioSelected: { backgroundColor: "#FFF" },

  /* Study Tip */
  studyTip: { marginTop: 8, fontSize: 14, color: "#3B7253", fontStyle: "italic", padding: 5 },
});