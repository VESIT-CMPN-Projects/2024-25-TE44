import { useState, useEffect } from "react";
import { useLocalSearchParams, useRouter } from "expo-router";
import { 
  View, 
  Text, 
  StyleSheet, 
  FlatList, 
  TouchableOpacity, 
  ActivityIndicator,
  ScrollView,
  TextInput
} from "react-native";
import { analyzeMaharashtraQuiz, generateStudyPlan } from "./work/recommendation-engine";
import { prepareQuizData } from "./work/prepareQuizData";

export default function RecommendationSchedule() {
  const router = useRouter();
  const params = useLocalSearchParams();
  
  // Parse incoming data
  const questions = params.questions ? JSON.parse(params.questions as string) : [];
  const answers = params.answers ? JSON.parse(params.answers as string) : [];
  const score = params.score ? parseInt(params.score as string) : 0;
  const total = params.total ? parseInt(params.total as string) : 0;

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [scheduleData, setScheduleData] = useState<any>(null);
  const [completedTopics, setCompletedTopics] = useState<Record<string, boolean>>({});
  const [availableHours, setAvailableHours] = useState<number>(2); // Default 2 hours

  useEffect(() => {
    const generateRecommendedSchedule = async () => {
      setIsLoading(true);
      try {
        const { questions: formattedQuestions, answers: formattedAnswers } = prepareQuizData(
          questions,
          [],
          []
        );

        const analyses = analyzeMaharashtraQuiz(formattedQuestions, formattedAnswers);
        const studyPlan = generateStudyPlan(analyses, availableHours, 7); // Use user's selected hours
        
        setScheduleData({
          studyPlan: studyPlan.map((dayPlan, index) => ({
            day: `Day ${index + 1}`,
            totalHours: (dayPlan.sessions.reduce((sum, session) => sum + session.duration, 0) / 60).toFixed(1),
            sessions: dayPlan.sessions.map(session => ({
              subject: session.subject,
              topic: session.topic,
              subtopic: session.subtopic,
              time_allocated: `${Math.round(session.duration / 60 * 10) / 10}h`,
              study_tips: session.tasks,
              resources: session.resources.slice(0, 2)
            }))
          })),
          weakAreas: analyses.flatMap(analysis => 
            analysis.weakTopics.map(topic => ({
              name: `${topic.topic} (${analysis.subject})`,
              hours: topic.normalizedScore < 0.3 ? 3 : 
                    topic.normalizedScore < 0.6 ? 2 : 1
            }))
          )
        });

      } catch (err) {
        setError("Failed to generate recommendations. Please try again.");
        console.error("Recommendation error:", err);
      } finally {
        setIsLoading(false);
      }
    };

    generateRecommendedSchedule();
  }, [availableHours]); // Re-run when hours change

  const toggleCompletion = (day: string, index: number) => {
    const topicKey = `${day}-${index}`;
    setCompletedTopics(prev => ({
      ...prev,
      [topicKey]: !prev[topicKey],
    }));
  };

  const handleContinue = () => {
    router.push({
      pathname: "/",
      params: { message: "Recommendation completed!" }
    });
  };

  if (isLoading) {
    return (
      <View style={styles.centeredContainer}>
        <ActivityIndicator size="large" color="#3C896D" />
        <Text style={styles.loadingText}>Creating your personalized study plan...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centeredContainer}>
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity 
          style={styles.retryButton}
          onPress={() => router.back()}
        >
          <Text style={styles.buttonText}>Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.header}>Your Study Plan</Text>
      <Text style={styles.subHeader}>
        Score: {score}/{total} ({Math.round((score/total)*100)}%)
      </Text>

      {/* Hours Selection */}
      <View style={styles.hoursSelectionContainer}>
        <Text style={styles.hoursLabel}>Select Daily Study Hours:</Text>
        <View style={styles.hoursButtonsContainer}>
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((hours) => (
            <TouchableOpacity
              key={hours}
              style={[
                styles.hourButton,
                availableHours === hours && styles.hourButtonSelected
              ]}
              onPress={() => setAvailableHours(hours)}
            >
              <Text style={[
                styles.hourButtonText,
                availableHours === hours && styles.hourButtonTextSelected
              ]}>
                {hours}h
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Focus Areas Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Focus Areas</Text>
        <View style={styles.focusAreasContainer}>
          {scheduleData?.weakAreas.map((area: any, index: number) => (
            <View key={index} style={styles.focusAreaItem}>
              <Text style={styles.focusAreaText}>• {area.name}</Text>
              <Text style={styles.focusAreaHours}>{area.hours}h</Text>
            </View>
          ))}
        </View>
      </View>

      {/* Daily Schedule Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Daily Schedule</Text>
        {scheduleData?.studyPlan.map((day: any) => (
          <View key={day.day} style={styles.dayCard}>
            <View style={styles.dayHeader}>
              <Text style={styles.dayTitle}>{day.day}</Text>
              <Text style={styles.dayTotal}>{day.totalHours}h total</Text>
            </View>
            
            {day.sessions.map((session: any, index: number) => {
              const topicKey = `${day.day}-${index}`;
              const isCompleted = completedTopics[topicKey];

              return (
                <View key={topicKey} style={[
                  styles.sessionCard,
                  isCompleted && styles.completedSession
                ]}>
                  <View style={styles.sessionHeader}>
                    <Text style={styles.sessionSubject}>{session.subject}</Text>
                    <Text style={styles.sessionTime}>{session.time_allocated}</Text>
                  </View>
                  
                  <Text style={styles.sessionTopic}>
                    {session.topic}{session.subtopic && ` (${session.subtopic})`}
                  </Text>
                  
                  <View style={styles.tipsContainer}>
                    {session.study_tips.map((tip: string, i: number) => (
                      <Text key={i} style={styles.tipText}>• {tip}</Text>
                    ))}
                  </View>
                  
                  {session.resources.length > 0 && (
                    <Text style={styles.resourcesText}>
                      📚 {session.resources.join(', ')}
                    </Text>
                  )}

                  <TouchableOpacity
                    style={[styles.completionButton, isCompleted && styles.completedButton]}
                    onPress={() => toggleCompletion(day.day, index)}
                  >
                    <Text style={styles.completionButtonText}>
                      {isCompleted ? 'Completed' : 'Mark Complete'}
                    </Text>
                  </TouchableOpacity>
                </View>
              );
            })}
          </View>
        ))}
      </View>

      <TouchableOpacity 
        style={styles.continueButton}
        onPress={handleContinue}
      >
        <Text style={styles.buttonText}>Finish</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f8f9fa'
  },
  centeredContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20
  },
  loadingText: {
    fontSize: 16,
    color: '#3C896D',
    marginTop: 16,
    textAlign: 'center'
  },
  errorText: {
    fontSize: 16,
    color: '#FF6347',
    marginBottom: 16,
    textAlign: 'center'
  },
  header: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#265C3A',
    textAlign: 'center',
    marginBottom: 4
  },
  subHeader: {
    fontSize: 16,
    color: '#4FB286',
    textAlign: 'center',
    marginBottom: 24
  },
  hoursSelectionContainer: {
    marginBottom: 20,
    backgroundColor: '#FFF',
    borderRadius: 10,
    padding: 16
  },
  hoursLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#265C3A',
    marginBottom: 12
  },
  hoursButtonsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    gap: 8
  },
  hourButton: {
    backgroundColor: '#E8F5E9',
    borderRadius: 8,
    padding: 10,
    minWidth: 50,
    alignItems: 'center'
  },
  hourButtonSelected: {
    backgroundColor: '#3C896D'
  },
  hourButtonText: {
    color: '#3C896D',
    fontWeight: '600'
  },
  hourButtonTextSelected: {
    color: '#FFF'
  },
  section: {
    marginBottom: 24
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#265C3A',
    marginBottom: 12
  },
  focusAreasContainer: {
    backgroundColor: '#FFF',
    borderRadius: 10,
    padding: 16
  },
  focusAreaItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0'
  },
  focusAreaText: {
    fontSize: 14,
    color: '#3B7253',
    flex: 1
  },
  focusAreaHours: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1B5E20',
    backgroundColor: '#E8F5E9',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10
  },
  dayCard: {
    backgroundColor: '#FFF',
    borderRadius: 10,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2
  },
  dayHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    paddingBottom: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0'
  },
  dayTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#3C896D'
  },
  dayTotal: {
    fontSize: 14,
    color: '#4FB286',
    fontWeight: '600'
  },
  sessionCard: {
    backgroundColor: '#FFF',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E0E0E0'
  },
  completedSession: {
    backgroundColor: '#f8f8f8',
    borderColor: '#E0E0E0'
  },
  sessionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6
  },
  sessionSubject: {
    fontSize: 16,
    fontWeight: '600',
    color: '#3498db'
  },
  sessionTime: {
    fontSize: 14,
    fontWeight: '600',
    color: '#e74c3c'
  },
  sessionTopic: {
    fontSize: 14,
    color: '#2c3e50',
    marginBottom: 8
  },
  tipsContainer: {
    marginLeft: 8,
    marginBottom: 8
  },
  tipText: {
    fontSize: 13,
    color: '#34495e',
    marginBottom: 4
  },
  resourcesText: {
    fontSize: 12,
    color: '#7f8c8d',
    fontStyle: 'italic',
    marginBottom: 8
  },
  completionButton: {
    backgroundColor: '#4FB286',
    padding: 8,
    borderRadius: 6,
    alignItems: 'center'
  },
  completedButton: {
    backgroundColor: '#95a5a6'
  },
  completionButtonText: {
    color: '#FFF',
    fontWeight: '600'
  },
  retryButton: {
    backgroundColor: '#3C896D',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    width: '60%'
  },
  continueButton: {
    backgroundColor: '#3C896D',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginVertical: 16
  },
  buttonText: {
    color: '#FFF',
    fontWeight: 'bold',
    fontSize: 16
  }
});