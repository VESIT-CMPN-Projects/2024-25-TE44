import React from "react";
import { useRouter, useLocalSearchParams } from "expo-router";
import { View, Text, FlatList, TouchableOpacity, ScrollView, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { Svg, Circle } from "react-native-svg";
import { prepareQuizData } from "./work/prepareQuizData";

const ScoreCard = () => {
  const router = useRouter();
  const params = useLocalSearchParams();

  const score = parseInt(params.score as string || "0");
  const total = parseInt(params.total as string || "0");
  const questions = params.questions ? JSON.parse(params.questions as string) : [];
  const selectedOptions = params.selectedOptions ? JSON.parse(params.selectedOptions as string) : [];
  const correctOptions = params.correctOptions ? JSON.parse(params.correctOptions as string) : [];

  const { questions: formattedQuestions, answers: formattedAnswers } = prepareQuizData(
    questions,
    selectedOptions,
    correctOptions
  );

  const percentage = total > 0 ? Math.round((score / total) * 100) : 0;
  const isHighScore = percentage >= 80;
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  const handleNavigate = () => {
    router.push({
      pathname: isHighScore ? "/generate-schedule" : "/recommendation-schedule",
      params: {
        questions: JSON.stringify(formattedQuestions),
        answers: JSON.stringify(formattedAnswers),
        score: score.toString(),
        total: total.toString(),
        correctOptions: JSON.stringify(correctOptions),
        selectedOptions: JSON.stringify(selectedOptions)
      }
    });
  };

  return (
    <ScrollView contentContainerStyle={styles.scrollContainer}>
      <View style={styles.container}>
        <View style={styles.scoreVisualization}>
          <Svg width={200} height={200}>
            <Circle cx={100} cy={100} r={radius} stroke="#E0E0E0" strokeWidth={12} fill="none"/>
            <Circle cx={100} cy={100} r={radius} stroke={isHighScore ? "#4CAF50" : "#FF9800"} strokeWidth={12} fill="none" strokeDasharray={circumference} strokeDashoffset={strokeDashoffset} strokeLinecap="round" transform="rotate(-90, 100, 100)"/>
          </Svg>
          <View style={styles.scoreText}>
            <Text style={styles.scorePercentage}>{percentage}%</Text>
            <Text style={styles.scoreFraction}>{score}/{total}</Text>
            <Text style={styles.performanceTag}>{isHighScore ? "Excellent!" : "Keep Going!"}</Text>
          </View>
        </View>

        <View style={styles.messageContainer}>
          <Text style={styles.messageTitle}>{isHighScore ? "Mastery Achieved!" : "Room for Growth"}</Text>
          <Text style={styles.messageText}>
            {isHighScore ? "You've demonstrated strong understanding of these concepts" : "Let's focus on strengthening these areas"}
          </Text>
        </View>

        <View style={styles.breakdownContainer}>
          <Text style={styles.sectionTitle}>Detailed Analysis</Text>
          <FlatList
            data={formattedQuestions}
            scrollEnabled={false}
            keyExtractor={(_, index) => index.toString()}
            renderItem={({ item, index }) => {
              const answer = formattedAnswers[index];
              const isCorrect = answer.isCorrect;
              const correctAnswer = correctOptions[index];
              const selectedAnswer = selectedOptions[index];
              return (
                <View style={[styles.questionCard, isCorrect ? styles.correctCard : styles.incorrectCard]}>
                  <View style={styles.questionHeader}>
                    <Text style={styles.subjectPill}>{item.subject}</Text>
                    <Text style={styles.difficultyPill}>{item.difficulty.toUpperCase()}</Text>
                  </View>
                  <Text style={styles.questionText}>{item.text}</Text>
                  <View style={styles.topicRow}>
                    <Ionicons name={isCorrect ? "checkmark" : "close"} size={20} color={isCorrect ? "#4CAF50" : "#F44336"}/>
                    <Text style={styles.topicText}>{item.topic}{item.subtopic ? ` • ${item.subtopic}` : ''}</Text>
                  </View>
                  {!isCorrect && (
                    <View style={styles.answerSection}>
                      <Text style={styles.answerLabel}>Your answer:</Text>
                      <Text style={styles.incorrectAnswer}>{selectedAnswer}</Text>
                      <Text style={styles.answerLabel}>Correct answer:</Text>
                      <Text style={styles.correctAnswer}>{correctAnswer}</Text>
                    </View>
                  )}
                </View>
              );
            }}
          />
        </View>

        <View style={styles.actionButtons}>
          <TouchableOpacity style={[styles.button, styles.primaryButton]} onPress={handleNavigate}>
            <Text style={styles.buttonText}>{isHighScore ? "Continue to Plan" : "Get Recommendations"}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.button, styles.secondaryButton]} onPress={() => router.push("/")}>
            <Text style={[styles.buttonText, styles.secondaryButtonText]}>Back to Home</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  scrollContainer: { flexGrow: 1, backgroundColor: "#F5F5F5" },
  container: { flex: 1, padding: 24, paddingBottom: 40 },
  scoreVisualization: { alignItems: "center", justifyContent: "center", marginVertical: 24, position: "relative" },
  scoreText: { position: "absolute", alignItems: "center", justifyContent: "center" },
  scorePercentage: { fontSize: 36, fontWeight: "700", color: "#212121" },
  scoreFraction: { fontSize: 18, color: "#616161", marginTop: 4 },
  performanceTag: { fontSize: 16, fontWeight: "600", color: "#4CAF50", marginTop: 8, paddingHorizontal: 12, paddingVertical: 4, borderRadius: 12, backgroundColor: "#E8F5E9" },
  messageContainer: { marginBottom: 24, alignItems: "center" },
  messageTitle: { fontSize: 22, fontWeight: "700", color: "#212121", marginBottom: 8 },
  messageText: { fontSize: 16, color: "#616161", textAlign: "center", lineHeight: 24 },
  breakdownContainer: { marginBottom: 24 },
  sectionTitle: { fontSize: 18, fontWeight: "600", color: "#212121", marginBottom: 16, paddingLeft: 8 },
  questionCard: { backgroundColor: "#FFFFFF", borderRadius: 12, padding: 16, marginBottom: 12, shadowColor: "#000", shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 2 },
  correctCard: { borderLeftWidth: 4, borderLeftColor: "#4CAF50" },
  incorrectCard: { borderLeftWidth: 4, borderLeftColor: "#F44336" },
  questionHeader: { flexDirection: "row", marginBottom: 12, gap: 8 },
  subjectPill: { backgroundColor: "#E3F2FD", color: "#1976D2", paddingHorizontal: 12, paddingVertical: 4, borderRadius: 12, fontSize: 12, fontWeight: "600" },
  difficultyPill: { backgroundColor: "#F5F5F5", color: "#616161", paddingHorizontal: 12, paddingVertical: 4, borderRadius: 12, fontSize: 12, fontWeight: "600" },
  questionText: { fontSize: 15, color: "#212121", lineHeight: 22, marginBottom: 12 },
  topicRow: { flexDirection: "row", alignItems: "center", gap: 8 },
  topicText: { fontSize: 14, color: "#616161" },
  answerSection: { marginTop: 12, paddingTop: 12, borderTopWidth: 1, borderTopColor: "#EEEEEE" },
  answerLabel: { fontSize: 14, color: "#616161", marginBottom: 4 },
  correctAnswer: { fontSize: 15, color: "#4CAF50", fontWeight: "600", marginBottom: 8 },
  incorrectAnswer: { fontSize: 15, color: "#F44336", fontWeight: "600", marginBottom: 8, textDecorationLine: "line-through" },
  actionButtons: { gap: 12 },
  button: { borderRadius: 12, paddingVertical: 16, alignItems: "center", justifyContent: "center" },
  primaryButton: { backgroundColor: "#3B7253" },
  secondaryButton: { backgroundColor: "transparent", borderWidth: 1, borderColor: "#E0E0E0" },
  buttonText: { fontSize: 16, fontWeight: "600", color: "#FFFFFF" },
  secondaryButtonText: { color: "#3B7253" }
});

export default ScoreCard;