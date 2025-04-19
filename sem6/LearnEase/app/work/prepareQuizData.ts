type SubjectName = 'Physics' | 'Chemistry' | 'Biology';
type PhysicsTopic = keyof typeof MAHARASHTRA_SCIENCE.Physics;
type ChemistryTopic = keyof typeof MAHARASHTRA_SCIENCE.Chemistry;
type BiologyTopic = keyof typeof MAHARASHTRA_SCIENCE.Biology;
type ScienceTopic = PhysicsTopic | ChemistryTopic | BiologyTopic;

interface QuizQuestion {
  text: string;
  subject: SubjectName;
  topic: ScienceTopic;
  subtopic?: string;
  difficulty: 'easy' | 'medium' | 'hard';
}

interface QuizAnswer {
  questionIndex: number;
  isCorrect: boolean;
  timeSpent: number;
}

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

const TOPIC_KEYWORDS = {
  Physics: {
    'Measurement of Matter': ['measure', 'unit', 'dimension', 'significant', 'accuracy', 'precision'],
    'Motion': ['motion', 'speed', 'velocity', 'acceleration', 'displacement', 'graph'],
    'Force and Laws of Motion': ['force', 'newton', 'momentum', 'inertia', 'action', 'reaction'],
    'Work and Energy': ['work', 'energy', 'power', 'joule', 'kinetic', 'potential'],
    'Sound': ['sound', 'wave', 'frequency', 'echo', 'ultrasound', 'pitch'],
    'Gravitation': ['gravity', 'gravitation', 'free fall', 'weight', 'kepler', 'satellite'],
    'Light': ['light', 'reflection', 'refraction', 'lens', 'mirror', 'prism'],
    'Electricity': ['electric', 'current', 'ohm', 'circuit', 'resistance', 'power'],
    'Magnetism': ['magnet', 'magnetic', 'induction', 'motor', 'generator', 'field']
  },
  Chemistry: {
    'Matter in Our Surroundings': ['matter', 'state', 'solid', 'liquid', 'gas', 'sublimation'],
    'Is Matter Around Us Pure': ['pure', 'mixture', 'solution', 'colloid', 'suspension', 'alloy'],
    'Atoms and Molecules': ['atom', 'molecule', 'atomic', 'molar', 'mass', 'avogadro'],
    'Structure of Atom': ['electron', 'proton', 'neutron', 'shell', 'orbital', 'valency'],
    'Chemical Reactions': ['reaction', 'equation', 'balance', 'redox', 'combination', 'decomposition'],
    'Acids, Bases and Salts': ['acid', 'base', 'salt', 'ph', 'neutralization', 'indicator'],
    'Metals and Non-metals': ['metal', 'non-metal', 'reactivity', 'alloy', 'corrosion', 'ductile'],
    'Carbon Compounds': ['carbon', 'organic', 'hydrocarbon', 'functional', 'iupac', 'isomer']
  },
  Biology: {
    'Cell: Structure and Function': ['cell', 'organelle', 'nucleus', 'membrane', 'mitochondria', 'cytoplasm'],
    'Tissues': ['tissue', 'epithelial', 'muscular', 'nervous', 'meristematic', 'xylem'],
    'Diversity in Living Organisms': ['diversity', 'classification', 'kingdom', 'species', 'binomial', 'taxonomy'],
    'Life Processes': ['nutrition', 'respiration', 'transportation', 'excretion', 'photosynthesis', 'digestion'],
    'Control and Coordination': ['neuron', 'nervous', 'hormone', 'reflex', 'brain', 'spinal'],
    'Reproduction': ['reproduction', 'asexual', 'sexual', 'gamete', 'zygote', 'menstruation'],
    'Heredity and Evolution': ['heredity', 'gene', 'dna', 'mutation', 'evolution', 'natural selection']
  }
};

const DIFFICULTY_KEYWORDS = {
  easy: ['define', 'what is', 'name', 'list', 'identify', 'recall'],
  medium: ['explain', 'describe', 'compare', 'relate', 'summarize', 'interpret'],
  hard: ['calculate', 'derive', 'analyze', 'evaluate', 'prove', 'design']
};

export const prepareQuizData = (
  questions: Array<string | { text: string }>,
  selectedOptions: string[],
  correctOptions: string[]
) => {
  return {
    questions: questions.map((question, index) => {
      const questionText = typeof question === 'string' ? question : question.text;
      return {
        text: questionText,
        subject: detectSubject(questionText),
        topic: detectTopic(questionText),
        subtopic: detectSubtopic(questionText),
        difficulty: detectDifficulty(questionText),
        index
      };
    }),
    answers: selectedOptions.map((selected, index) => ({
      questionIndex: index,
      isCorrect: selected === correctOptions[index],
      timeSpent: 30
    }))
  };
};

function detectSubject(questionText: string): SubjectName {
  const lowerQuestion = questionText.toLowerCase();
  const subjectCounts = {
    Physics: countKeywords(lowerQuestion, TOPIC_KEYWORDS.Physics),
    Chemistry: countKeywords(lowerQuestion, TOPIC_KEYWORDS.Chemistry),
    Biology: countKeywords(lowerQuestion, TOPIC_KEYWORDS.Biology)
  };
  const maxSubject = Object.entries(subjectCounts).reduce(
    (max, [subject, count]) => count > max.count ? { subject, count } : max,
    { subject: 'Physics', count: 0 }
  );
  return maxSubject.subject as SubjectName;
}

function detectTopic(questionText: string): ScienceTopic {
  const lowerQuestion = questionText.toLowerCase();
  const subject = detectSubject(questionText);
  const topics = Object.keys(TOPIC_KEYWORDS[subject]) as ScienceTopic[];
  const detectedTopic = topics.reduce(
    (maxTopic, topic) => {
      const count = TOPIC_KEYWORDS[subject][topic].filter(keyword => 
        lowerQuestion.includes(keyword)
      ).length;
      return count > maxTopic.count ? { topic, count } : maxTopic;
    },
    { topic: topics[0], count: 0 }
  );
  return detectedTopic.topic;
}

function detectSubtopic(questionText: string): string | undefined {
  const lowerQuestion = questionText.toLowerCase();
  const subject = detectSubject(questionText);
  const topic = detectTopic(questionText);
  const subtopics = MAHARASHTRA_SCIENCE[subject][topic];
  for (const subtopic of subtopics) {
    if (lowerQuestion.includes(subtopic.toLowerCase())) {
      return subtopic;
    }
  }
  return undefined;
}

function detectDifficulty(questionText: string): 'easy' | 'medium' | 'hard' {
  const lowerQuestion = questionText.toLowerCase();
  for (const [level, keywords] of Object.entries(DIFFICULTY_KEYWORDS)) {
    if (keywords.some(keyword => lowerQuestion.includes(keyword))) {
      return level as 'easy' | 'medium' | 'hard';
    }
  }
  return 'medium';
}

function countKeywords(text: string, subjectKeywords: Record<string, string[]>): number {
  return Object.values(subjectKeywords).flat().filter(keyword => 
    text.includes(keyword)
  ).length;
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