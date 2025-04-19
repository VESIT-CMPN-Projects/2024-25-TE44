import React, { useState, useEffect } from "react";
import { useLocalSearchParams, useRouter } from "expo-router";

// REACT NATIVE //
import {
  View,
  Text,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  Alert,
} from "react-native";
import axios from "axios";

type QuizQuestion = {
  question: string;
  options: string[];
  correct_answer: string;
};

const QuizScreen = () => {
  const { summary } = useLocalSearchParams();
  const [quizData, setQuizData] = useState<QuizQuestion[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  const [score, setScore] = useState(0);
  const [timer, setTimer] = useState(30);
  const [loading, setLoading] = useState(true);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleOptionSelect = (option: string) => {
    const newSelections = [...selectedOptions];
    newSelections[currentQuestionIndex] = option;
    setSelectedOptions(newSelections);
  };

  useEffect(() => {
    if (!summary) return;
    const fetchMCQs = async () => {
      try {
        const res = await axios.post("http://192.168.174.44:8000/generate_mcqs/", {
          paragraph: summary,
          num_questions: 5, 
        });
        
        // Make sure we have valid questions data
        if (res.data && res.data.mcqs && Array.isArray(res.data.mcqs)) {
          setQuizData(res.data.mcqs);
          console.log(res.data.mcqs);
        } else {
          console.error("Invalid questions data format:", res.data);
          // Set empty array to prevent undefined errors
          setQuizData([]);
        }
        setLoading(false);
      } catch (error) {
        console.error("API failed: ", error);
        setLoading(false);
        // Set empty array to prevent undefined errors
        setQuizData([]);
      }
    };
    fetchMCQs();
  }, [summary]);

  // Timer Effect
  useEffect(() => {
    // Only run timer if we have quiz data and haven't reached the end
    if (timer > 0 && quizData.length > 0 && currentQuestionIndex < quizData.length&&!isSubmitted) {
      const interval = setInterval(() => {
        setTimer((prev) => prev - 1);
      }, 1000);
      return () => clearInterval(interval);
    } else if (quizData.length > 0 && currentQuestionIndex < quizData.length) {
      // Only auto-progress if we have quiz data and haven't reached the end
      handleNext();
    }
  }, [timer, quizData, currentQuestionIndex]);

  const router = useRouter();

  const handleNext = () => {
    if (currentQuestionIndex < quizData.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setTimer(30);
    } else {
      // Calculate correct score
      const score = selectedOptions.filter(
        (option, index) => option === quizData[index].correct_answer
      ).length;

      // Pass selected answers AND correct answers properly
      router.push({
        pathname: "/score-card",
        params: {
          score: score.toString(),
          total: quizData.length.toString(),
          questions: JSON.stringify(quizData.map((q) => q.question)), // Send only questions
          selectedOptions: JSON.stringify(selectedOptions), // Send user selected options
          correctOptions: JSON.stringify(quizData.map((q) => q.correct_answer)), // Send correct answers
        },
      });
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
      setTimer(30);
    }
  };

  // Show loading state if data isn't ready
  if (loading) {
    return (
      <View style={styles.container}>
        <Text style={{ textAlign: "center", fontSize: 18, marginTop: 50 }}>
          Loading quiz...
        </Text>
      </View>
    );
  }

  // Show a message if we have no quiz questions
  if (!quizData || quizData.length === 0) {
    return (
      <View style={styles.container}>
        <Text style={{ textAlign: "center", fontSize: 18, marginTop: 50 }}>
          No quiz questions available. Please try again.
        </Text>
      </View>
    );
  }

  // Make sure we have a valid current question
  const currentQuestion = quizData[currentQuestionIndex];
  if (!currentQuestion) {
    return (
      <View style={styles.container}>
        <Text style={{ textAlign: "center", fontSize: 18, marginTop: 50 }}>
          Error loading question. Please try again.
        </Text>
      </View>
    );
  }

  // Now we can safely render the quiz UI
  return (
    <View style={styles.container}>
      {/* Top Section */}
      <View style={styles.topSection}>
        <TouchableOpacity
          onPress={handlePrevious}
          disabled={currentQuestionIndex === 0}
        >
          <Text
            style={[
              styles.previousText,
              currentQuestionIndex === 0 && styles.disabledText,
            ]}
          >
            {"< Previous"}
          </Text>
        </TouchableOpacity>
        <Text style={styles.progressText}>
          {currentQuestionIndex + 1}/{quizData.length}
        </Text>
      </View>

      {/* Timer */}
      <View style={styles.timerContainer}>
        <Text style={styles.timerText}>{timer}</Text>
      </View>

      {/* Question */}
      <View style={styles.questionBox}>
        <Text style={styles.questionText}>
          {currentQuestion.question}
        </Text>
      </View>

      {/* Options */}
      <FlatList
        data={currentQuestion.options || []}
        keyExtractor={(item, index) => index.toString()}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={[
              styles.optionButton,
              selectedOptions[currentQuestionIndex] === item && styles.selectedOption,
            ]}
            onPress={() => handleOptionSelect(item)}
          >
            <Text style={styles.optionText}>{item}</Text>
          </TouchableOpacity>
        )}
      />

<TouchableOpacity
        style={[styles.nextButton, !selectedOptions[currentQuestionIndex] && styles.disabledButton]}
        onPress={handleNext}
        disabled={!selectedOptions[currentQuestionIndex]}
      >
        <Text style={styles.nextButtonText}>
          {currentQuestionIndex === quizData.length - 1 ? "Submit" : "Next"}
        </Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: "#FAFAFA" },

  topSection: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 10,
  },
  previousText: { color: "#2E7D32", fontSize: 16, fontWeight: "bold" },
  disabledText: { color: "gray" }, // Style when disabled
  progressText: { fontSize: 18, fontWeight: "bold" },

  timerContainer: {
    alignSelf: "center",
    backgroundColor: "#DFF0D8",
    padding: 15,
    borderRadius: 50,
    marginBottom: 15,
  },
  timerText: { fontSize: 24, fontWeight: "bold", color: "#388E3C" },

  questionBox: {
    backgroundColor: "#DFF0D8",
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
  },
  questionText: { fontSize: 16, textAlign: "center", fontWeight: "600" },

  optionButton: {
    padding: 15,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#4CAF50",
    marginVertical: 5,
    backgroundColor: "#F0FFF4",
  },
  selectedOption: { backgroundColor: "#A5D6A7" },
  optionText: { fontSize: 16 },

  nextButton: {
    marginTop: 20,
    backgroundColor: "#2E7D32",
    padding: 15,
    borderRadius: 10,
    alignItems: "center",
  },
  disabledButton: { backgroundColor: "#B0BEC5" },
  nextButtonText: { color: "white", fontSize: 18, fontWeight: "bold" },
});

export default QuizScreen;