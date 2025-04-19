// ================== TYPE DEFINITIONS ================== //
type SubjectName = 'Physics' | 'Chemistry' | 'Biology';
type PhysicsTopic = keyof typeof MAHARASHTRA_SCIENCE.Physics;
type ChemistryTopic = keyof typeof MAHARASHTRA_SCIENCE.Chemistry;
type BiologyTopic = keyof typeof MAHARASHTRA_SCIENCE.Biology;
type ScienceTopic = PhysicsTopic | ChemistryTopic | BiologyTopic;

type TopicScore = {
  topic: ScienceTopic;
  normalizedScore: number;
  questionCount: number;
  subtopics?: {
    name: string;
    score: number;
  }[];
};

type SubjectAnalysis = {
  subject: SubjectName;
  weakTopics: TopicScore[];
  strongTopics: TopicScore[];
  overallScore: number;
  priority: number;
};

type StudySession = {
  subject: SubjectName;
  topic: ScienceTopic;
  subtopic?: string;
  duration: number;
  tasks: string[];
  resources: string[];
};

type StudyPlan = {
  day: number;
  sessions: StudySession[];
}[];

type EvaluationMetrics = {
  // Accuracy metrics
  precision: number;
  recall: number;
  f1Score: number;
  
  // Effectiveness metrics
  improvementRate: number;
  retentionRate: number;
  
  // User experience
  satisfaction: number;
  engagementScore: number;
  
  // Diagnostic info
  truePositives: number;
  falsePositives: number;
  falseNegatives: number;
  trueNegatives: number;
  recommendationCoverage: number;
};

type UserPerformanceData = {
  preTestScores: Record<string, number>;
  postTestScores: Record<string, number>;
  sessionCompletion: {
    day: number;
    completed: boolean;
    timeSpent: number;
  }[];
  feedback?: {
    rating: number;
    comments: string;
  };
};

// ================== MAHARASHTRA BOARD SYLLABUS ================== //
const MAHARASHTRA_SCIENCE = {
  Physics: {
    'Measurement of Matter': ['Units and Measurements', 'Significant Figures', 'Dimensional Analysis'],
    'Motion': ['Scalar vs Vector', 'Equations of Motion', 'Graphical Analysis'],
    'Force and Laws of Motion': ['Newton\'s Laws', 'Momentum', 'Conservation'],
    'Work and Energy': ['Work Calculation', 'Energy Types', 'Power'],
    'Sound': ['Wave Properties', 'Sound Propagation', 'Applications'],
    'Gravitation': ['Universal Law', 'Free Fall', 'Kepler\'s Laws'],
    'Light': ['Reflection', 'Refraction', 'Lens Formula'],
    'Electricity': ['Ohm\'s Law', 'Circuits', 'Household Wiring'],
    'Magnetism': ['Magnetic Field', 'EM Induction', 'Applications']
  },
  Chemistry: {
    'Matter in Our Surroundings': ['States of Matter', 'Changes', 'Latent Heat'],
    'Is Matter Around Us Pure': ['Mixtures', 'Solutions', 'Colloids'],
    'Atoms and Molecules': ['Atomic Theory', 'Mole Concept', 'Formulas'],
    'Structure of Atom': ['Atomic Models', 'Valency', 'Isotopes'],
    'Chemical Reactions': ['Types', 'Balancing', 'Redox'],
    'Acids, Bases and Salts': ['pH Scale', 'Neutralization', 'Salts'],
    'Metals and Non-metals': ['Properties', 'Reactivity', 'Alloys'],
    'Carbon Compounds': ['Bonding', 'Functional Groups', 'Nomenclature']
  },
  Biology: {
    'Cell: Structure and Function': ['Organelles', 'Division', 'Transport'],
    'Tissues': ['Plant Tissues', 'Animal Tissues', 'Meristematic'],
    'Diversity in Living Organisms': ['Classification', 'Kingdoms', 'Nomenclature'],
    'Life Processes': ['Nutrition', 'Respiration', 'Transportation'],
    'Control and Coordination': ['Nervous System', 'Hormones', 'Reflexes'],
    'Reproduction': ['Asexual', 'Sexual', 'Human Reproductive'],
    'Heredity and Evolution': ['Mendel\'s Laws', 'DNA', 'Natural Selection']
  }
} as const;

// ================== TOPIC DEPENDENCIES ================== //
const TOPIC_DEPENDENCIES: Record<string, ScienceTopic[]> = {
  'Force and Laws of Motion': ['Motion'],
  'Work and Energy': ['Motion'],
  'Gravitation': ['Motion'],
  'Electricity': ['Motion'],
  'Structure of Atom': ['Atoms and Molecules'],
  'Chemical Reactions': ['Atoms and Molecules'],
  'Carbon Compounds': ['Chemical Reactions'],
  'Tissues': ['Cell: Structure and Function'],
  'Life Processes': ['Cell: Structure and Function'],
  'Heredity and Evolution': ['Reproduction']
};

// ================== UTILITY FUNCTIONS ================== //
function getSubjectTopics(subject: SubjectName): ScienceTopic[] {
  return Object.keys(MAHARASHTRA_SCIENCE[subject]) as ScienceTopic[];
}

function getSubtopicList(subject: SubjectName, topic: ScienceTopic): string[] {
  switch (subject) {
    case 'Physics':
      return isPhysicsTopic(topic) ? [...MAHARASHTRA_SCIENCE.Physics[topic]] : [];
    case 'Chemistry':
      return isChemistryTopic(topic) ? [...MAHARASHTRA_SCIENCE.Chemistry[topic]] : [];
    case 'Biology':
      return isBiologyTopic(topic) ? [...MAHARASHTRA_SCIENCE.Biology[topic]] : [];
    default:
      return [];
  }
}

function isPhysicsTopic(topic: ScienceTopic): topic is PhysicsTopic {
  return topic in MAHARASHTRA_SCIENCE.Physics;
}

function isChemistryTopic(topic: ScienceTopic): topic is ChemistryTopic {
  return topic in MAHARASHTRA_SCIENCE.Chemistry;
}

function isBiologyTopic(topic: ScienceTopic): topic is BiologyTopic {
  return topic in MAHARASHTRA_SCIENCE.Biology;
}

// ================== ANALYSIS ENGINE ================== //
export function analyzeMaharashtraQuiz(
  questions: {
    text: string;
    subject: SubjectName;
    topic: ScienceTopic;
    subtopic?: string;
    difficulty: 'easy' | 'medium' | 'hard';
  }[],
  answers: {
    questionIndex: number;
    isCorrect: boolean;
    timeSpent: number;
  }[]
): SubjectAnalysis[] {
  const analyses: Record<SubjectName, SubjectAnalysis> = {
    Physics: initSubjectAnalysis('Physics'),
    Chemistry: initSubjectAnalysis('Chemistry'),
    Biology: initSubjectAnalysis('Biology')
  };

  questions.forEach((q, index) => {
    const answer = answers.find(a => a.questionIndex === index);
    if (!answer) return;

    const subjectAnalysis = analyses[q.subject];
    const difficultyWeight = q.difficulty === 'easy' ? 1 : q.difficulty === 'medium' ? 2 : 3;

    updateTopicScore(
      subjectAnalysis,
      q.topic,
      answer.isCorrect,
      difficultyWeight,
      q.subtopic
    );
  });

  return finalizeAnalyses(analyses);
}

function initSubjectAnalysis(subject: SubjectName): SubjectAnalysis {
  return {
    subject,
    weakTopics: getSubjectTopics(subject).map(topic => ({
      topic,
      normalizedScore: 0,
      questionCount: 0,
      subtopics: getSubtopicList(subject, topic).map(name => ({
        name,
        score: 0
      }))
    })),
    strongTopics: [],
    overallScore: 0,
    priority: 0
  };
}

function updateTopicScore(
  analysis: SubjectAnalysis,
  topic: ScienceTopic,
  isCorrect: boolean,
  weight: number,
  subtopic?: string
): void {
  let topicEntry = [...analysis.weakTopics, ...analysis.strongTopics]
    .find(t => t.topic === topic);

  if (!topicEntry) {
    topicEntry = {
      topic,
      normalizedScore: 0,
      questionCount: 0,
      subtopics: getSubtopicList(analysis.subject, topic).map(name => ({
        name,
        score: 0
      }))
    };
    analysis.weakTopics.push(topicEntry);
  }

  topicEntry.normalizedScore += isCorrect ? weight : 0;
  topicEntry.questionCount += weight;

  if (subtopic && topicEntry.subtopics) {
    const sub = topicEntry.subtopics.find(s => s.name === subtopic);
    if (sub) {
      sub.score += isCorrect ? weight : 0;
    }
  }
}

function finalizeAnalyses(analyses: Record<SubjectName, SubjectAnalysis>): SubjectAnalysis[] {
  return Object.values(analyses).map(analysis => {
    analysis.weakTopics.forEach(topic => {
      topic.normalizedScore = topic.questionCount > 0 
        ? topic.normalizedScore / topic.questionCount 
        : 0;
      
      if (topic.subtopics) {
        topic.subtopics.forEach(sub => {
          sub.score = sub.score / topic.questionCount;
        });
      }
    });

    analysis.strongTopics = analysis.weakTopics.filter(t => t.normalizedScore >= 0.7);
    analysis.weakTopics = analysis.weakTopics.filter(t => t.normalizedScore < 0.7);
    analysis.weakTopics.sort((a, b) => a.normalizedScore - b.normalizedScore);

    const totalQuestions = [...analysis.weakTopics, ...analysis.strongTopics]
      .reduce((sum, t) => sum + t.questionCount, 0);
    const correctAnswers = [...analysis.weakTopics, ...analysis.strongTopics]
      .reduce((sum, t) => sum + (t.normalizedScore * t.questionCount), 0);
    
    analysis.overallScore = totalQuestions > 0 ? correctAnswers / totalQuestions : 0;
    analysis.priority = calculatePriority(analysis);

    return analysis;
  }).sort((a, b) => b.priority - a.priority);
}

function calculatePriority(analysis: SubjectAnalysis): number {
  const weakness = 1 - analysis.overallScore;
  const importance = getSubjectImportance(analysis.subject);
  const foundationalValue = analysis.weakTopics.some(t => 
    Object.keys(TOPIC_DEPENDENCIES).some(dep => 
      TOPIC_DEPENDENCIES[dep].includes(t.topic))
  ) ? 1.5 : 1;

  return weakness * importance * foundationalValue;
}

function getSubjectImportance(subject: SubjectName): number {
  const weights = { Physics: 1.2, Chemistry: 1.1, Biology: 1.0 };
  return weights[subject];
}

// ================== EVALUATION METRICS ================== //
export function calculateEvaluationMetrics(
  recommendations: TopicScore[],
  actualPerformance: {
    topic: ScienceTopic;
    subject: SubjectName;
    correctAnswers: number;
    totalQuestions: number;
  }[],
  userData: UserPerformanceData
): EvaluationMetrics {
  // Calculate true positives, false positives, and false negatives
  let truePositives = 0;
  let falsePositives = 0;
  let falseNegatives = 0;
  let trueNegatives = 0;

  // Get all unique topics across subjects
  const allTopics = new Set<ScienceTopic>();
  Object.values(MAHARASHTRA_SCIENCE).forEach(subject => {
    Object.keys(subject).forEach(topic => allTopics.add(topic as ScienceTopic));
  });

  allTopics.forEach(topic => {
    const isRecommended = recommendations.some(r => r.topic === topic);
    const performance = actualPerformance.find(p => p.topic === topic);
    const isActuallyWeak = performance ? 
      (performance.correctAnswers / performance.totalQuestions) < 0.7 : false;

    if (isRecommended && isActuallyWeak) truePositives++;
    else if (isRecommended && !isActuallyWeak) falsePositives++;
    else if (!isRecommended && isActuallyWeak) falseNegatives++;
    else trueNegatives++;
  });

  // Calculate precision, recall, and F1 score
  const precision = truePositives / (truePositives + falsePositives) || 0;
  const recall = truePositives / (truePositives + falseNegatives) || 0;
  const f1Score = 2 * (precision * recall) / (precision + recall) || 0;

  // Calculate improvement rate
  let improvementRate = 0;
  if (userData.preTestScores && userData.postTestScores) {
    const preTestTotal = Object.values(userData.preTestScores).reduce((a, b) => a + b, 0);
    const postTestTotal = Object.values(userData.postTestScores).reduce((a, b) => a + b, 0);
    improvementRate = ((postTestTotal - preTestTotal) / preTestTotal) * 100;
  }

  // Calculate retention rate (based on session completion)
  let retentionRate = 0;
  if (userData.sessionCompletion?.length > 0) {
    const completedSessions = userData.sessionCompletion.filter(s => s.completed).length;
    retentionRate = (completedSessions / userData.sessionCompletion.length) * 100;
  }

  // Calculate recommendation coverage
  const totalWeakTopics = actualPerformance.filter(p => 
    (p.correctAnswers / p.totalQuestions) < 0.7
  ).length;
  const recommendationCoverage = totalWeakTopics > 0 ?
    (recommendations.length / totalWeakTopics) * 100 : 0;

  return {
    precision: parseFloat(precision.toFixed(3)),
    recall: parseFloat(recall.toFixed(3)),
    f1Score: parseFloat(f1Score.toFixed(3)),
    improvementRate: parseFloat(improvementRate.toFixed(1)),
    retentionRate: parseFloat(retentionRate.toFixed(1)),
    satisfaction: userData.feedback?.rating || 0,
    engagementScore: calculateEngagementScore(userData),
    truePositives,
    falsePositives,
    falseNegatives,
    trueNegatives,
    recommendationCoverage: parseFloat(recommendationCoverage.toFixed(1))
  };
}

function calculateEngagementScore(userData: UserPerformanceData): number {
  if (!userData.sessionCompletion?.length) return 0;

  const totalTimePlanned = userData.sessionCompletion.length * 60; // Assuming 60min per session
  const totalTimeSpent = userData.sessionCompletion.reduce((sum, s) => sum + s.timeSpent, 0);
  
  // Score out of 100 based on time spent and completion rate
  const completionRate = userData.sessionCompletion.filter(s => s.completed).length / 
    userData.sessionCompletion.length;
  
  const timeRatio = totalTimeSpent / totalTimePlanned;
  
  return parseFloat(((completionRate * 50) + (timeRatio * 50)).toFixed(1));
}

// ================== STUDY PLAN GENERATION ================== //
export function generateStudyPlan(
  analyses: SubjectAnalysis[],
  availableHours: number,
  days: number = 7
): StudyPlan {
  const safeHours = Math.max(1, Math.min(10, availableHours || 2));
  const safeDays = Math.max(1, Math.min(14, days || 7));
  
  const dailyMinutes = safeHours * 60;
  const plan: StudyPlan = [];

  const weakTopics = analyses.flatMap(analysis => 
    analysis.weakTopics.map(topic => ({
      ...topic,
      subject: analysis.subject,
      priorityScore: (1 - topic.normalizedScore) * analysis.priority
    }))
  ).filter(t => t.priorityScore > 0);

  weakTopics.sort((a, b) => b.priorityScore - a.priorityScore);

  const totalPriority = weakTopics.reduce((sum, t) => sum + t.priorityScore, 0);

  for (let day = 1; day <= safeDays; day++) {
    let remainingTime = dailyMinutes;
    const dailySessions: StudySession[] = [];

    for (const topic of weakTopics) {
      if (remainingTime <= 0) break;

      const timeAllocation = Math.min(
        Math.max(30, Math.round((topic.priorityScore / totalPriority) * dailyMinutes * 1.2)),
        remainingTime
      );

      if (timeAllocation < 20) continue;

      const session = createSession(topic.subject, topic, timeAllocation);
      dailySessions.push(session);
      remainingTime -= session.duration;
    }

    if (remainingTime > 20) {
      const strongTopics = analyses.flatMap(a => 
        a.strongTopics.map(t => ({
          ...t,
          subject: a.subject
        }))
      );
      
      if (strongTopics.length > 0) {
        const reviewDuration = Math.min(remainingTime, 45);
        dailySessions.push({
          subject: strongTopics[0].subject,
          topic: strongTopics[0].topic,
          duration: reviewDuration,
          tasks: ["Review key concepts", "Solve practice questions"],
          resources: getMaharashtraResources(strongTopics[0].subject, strongTopics[0].topic)
        });
      }
    }

    plan.push({
      day,
      sessions: dailySessions
    });
  }

  return plan;
}

function createSession(
  subject: SubjectName,
  topic: TopicScore,
  duration: number
): StudySession {
  const weakestSubtopic = topic.subtopics?.reduce((weakest, current) => 
    current.score < weakest.score ? current : weakest
  );

  return {
    subject,
    topic: topic.topic,
    subtopic: weakestSubtopic?.name,
    duration,
    tasks: generateTasks(subject, topic.topic, weakestSubtopic?.name),
    resources: getMaharashtraResources(subject, topic.topic)
  };
}

function generateTasks(
  subject: SubjectName,
  topic: ScienceTopic,
  subtopic?: string
): string[] {
  const tasks: Record<SubjectName, string[]> = {
    Physics: [
      `Solve 5 numerical problems from ${subtopic || topic}`,
      `Derive all relevant formulas`,
      `Create concept map`
    ],
    Chemistry: [
      `Practice 3 chemical equations`,
      `Make comparative charts`,
      `Write definitions`
    ],
    Biology: [
      `Draw labeled diagram`,
      `Explain process step-by-step`,
      `Create flashcards`
    ]
  };

  return tasks[subject] || [
    `Review NCERT chapter`,
    `Solve previous year questions`,
    `Summarize key points`
  ];
}

function getMaharashtraResources(
  subject: SubjectName,
  topic: ScienceTopic
): string[] {
  const DEFAULT_RESOURCES = [
    'Maharashtra State Board Textbook',
    'NCERT Exemplar Problems',
    'Previous Year Question Papers'
  ];
  
  const resources: Record<SubjectName, Partial<Record<ScienceTopic, string[]>>> = {
    Physics: {
      'Measurement of Matter': [
        'Maharashtra Board Class 9 Science Part 1 Chapter 1',
        'Navneet Practice Papers - Measurement',
        'Target Publications Question Bank Chapter 1'
      ],
      'Motion': [
        'Maharashtra Board Class 9 Science Part 1 Chapter 2',
        'Motion Concepts - PhysicsWallah YouTube Series',
        'Motion Numerical Problems - Target Publications'
      ],
      // ... (other physics topics)
    },
    Chemistry: {
      'Matter in Our Surroundings': [
        'Maharashtra Board Class 9 Science Part 1 Chapter 1',
        'State Changes - PW Animation Series',
        'Target Matter Question Bank'
      ],
      // ... (other chemistry topics)
    },
    Biology: {
      'Cell: Structure and Function': [
        'Maharashtra Board Class 9 Science Part 2 Chapter 1',
        'Cell Biology - PW Detailed Series',
        'Target Cell Question Bank'
      ],
      // ... (other biology topics)
    }
  };
  
  const subjectResources = resources[subject];
  const topicResources = subjectResources?.[topic];

  return topicResources || DEFAULT_RESOURCES;
}

// ================== TRACKING FUNCTIONS ================== //
export function trackUserProgress(
  userId: string,
  sessionData: {
    day: number;
    completed: boolean;
    timeSpent: number;
  },
  feedback?: {
    rating: number;
    comments: string;
  }
): void {
  // In a real implementation, this would store data in your database
  console.log(`Tracking progress for user ${userId}:`, {
    sessionData,
    feedback
  });
}

export function recordTestScores(
  userId: string,
  testType: 'pre' | 'post',
  scores: Record<string, number>
): void {
  // In a real implementation, this would update your database
  console.log(`Recording ${testType}-test scores for user ${userId}:`, scores);
}