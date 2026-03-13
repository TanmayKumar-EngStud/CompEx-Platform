# Question Solving Hooks

This directory contains React hooks specific to the question-solving feature.

## Available Hooks

* **use-question-navigation.ts**: Manages navigation between questions
* **use-answer-submission.ts**: Handles answer submission logic
* **use-solution-display.ts**: Controls when to show solutions
* **fetchProblems.tsx**: Fetches problems with filtering
* **use-question-timer.ts**: Tracks time spent on questions

## Hook Details

### use-question-navigation.ts

Manages navigation between questions in a set:

```typescript
function useQuestionNavigation(questions: Question[]) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const currentQuestion = questions[currentIndex];
  
  const goToNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };
  
  const goToPrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };
  
  const goToQuestion = (index: number) => {
    if (index >= 0 && index < questions.length) {
      setCurrentIndex(index);
    }
  };
  
  return {
    currentQuestion,
    currentIndex,
    goToNext,
    goToPrevious,
    goToQuestion,
    isFirst: currentIndex === 0,
    isLast: currentIndex === questions.length - 1,
    totalQuestions: questions.length
  };
}
```

### use-answer-submission.ts

Handles the logic for submitting answers:

```typescript
function useAnswerSubmission(questionId: string) {
  const [answer, setAnswer] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<SubmissionResult | null>(null);
  
  const submitAnswer = async () => {
    setIsSubmitting(true);
    try {
      const timeSpent = getTimeSpent(); // From timer hook
      const response = await answerService.submitAnswer(questionId, answer, timeSpent);
      setResult(response);
    } catch (error) {
      console.error('Error submitting answer:', error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return {
    answer,
    setAnswer,
    submitAnswer,
    isSubmitting,
    result
  };
}
```

### fetchProblems.tsx

Fetches problems with filtering:

```typescript
function useFetchProblems(examName: string, sectionName: string, tags: string[]) {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const data = await fetchProblems_and_ProblemsSet(userId, examName, sectionName, tags);
        setProblems(data.problems);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [examName, sectionName, tags]);
  
  return { problems, loading, error };
}
```

## Integration with Components

These hooks are used by question-solving components to:
- Navigate through question sets
- Submit and validate answers
- Display solutions at appropriate times
- Track time spent on questions

## Integration with Services

These hooks use services from the question-solving feature to:
- Fetch question data
- Submit answers
- Format solutions
- Calculate progress metrics

## Usage Example

```tsx
import { useQuestionNavigation } from '@/features/question-solving/hooks/use-question-navigation';
import { useAnswerSubmission } from '@/features/question-solving/hooks/use-answer-submission';

function QuestionSolver({ questions }) {
  const { 
    currentQuestion, 
    goToNext, 
    goToPrevious 
  } = useQuestionNavigation(questions);
  
  const { 
    answer, 
    setAnswer, 
    submitAnswer, 
    result 
  } = useAnswerSubmission(currentQuestion.id);
  
  return (
    <div>
      <QuestionDisplay question={currentQuestion} />
      <AnswerInput value={answer} onChange={setAnswer} />
      <Button onClick={submitAnswer}>Submit</Button>
      {result && <SolutionDisplay solution={result.solution} />}
      <NavigationButtons 
        onNext={goToNext} 
        onPrevious={goToPrevious} 
      />
    </div>
  );
}
```