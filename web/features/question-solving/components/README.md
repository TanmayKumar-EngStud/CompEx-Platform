# Question Solving Components

This directory contains React components specific to the question-solving feature.

## Available Components

* **question-display.tsx**: Renders a question with options
* **answer-options.tsx**: Displays answer choices for multiple-choice questions
* **solution-viewer.tsx**: Shows the solution after submission
* **progress-tracker.tsx**: Displays progress through a set of questions
* **question-navigation.tsx**: Navigation controls between questions
* **timer-display.tsx**: Shows time spent on current question

## Component Details

### question-display.tsx

Renders a question with its content and options:

```tsx
interface QuestionDisplayProps {
  question: Question;
  showSolution?: boolean;
}

function QuestionDisplay({ question, showSolution = false }: QuestionDisplayProps) {
  // Renders question content with LaTeX support
  // Displays question metadata (difficulty, tags)
  // Conditionally shows solution if showSolution is true
  
  return (
    <div className="question-container">
      <h3 className="question-title">{question.title}</h3>
      <div className="question-content">
        {/* Render content with LaTeX support */}
      </div>
      {/* Render options or input based on question type */}
      {showSolution && <SolutionViewer solution={question.solution} />}
    </div>
  );
}
```

### answer-options.tsx

Displays answer choices for multiple-choice questions:

```tsx
interface AnswerOptionsProps {
  options: Option[];
  selectedOption: string | null;
  onSelect: (optionId: string) => void;
  disabled?: boolean;
}

function AnswerOptions({ options, selectedOption, onSelect, disabled = false }: AnswerOptionsProps) {
  // Renders multiple choice options
  // Highlights selected option
  // Disables selection after submission
  
  return (
    <div className="answer-options">
      {options.map(option => (
        <div 
          key={option.id}
          className={`option ${selectedOption === option.id ? 'selected' : ''}`}
          onClick={() => !disabled && onSelect(option.id)}
        >
          <span className="option-label">{option.label}</span>
          <span className="option-content">{option.content}</span>
        </div>
      ))}
    </div>
  );
}
```

### solution-viewer.tsx

Shows the solution after submission:

```tsx
interface SolutionViewerProps {
  solution: string;
  isCorrect?: boolean;
}

function SolutionViewer({ solution, isCorrect }: SolutionViewerProps) {
  // Renders formatted solution with LaTeX support
  // Shows visual indicator of correctness
  // Displays step-by-step explanation
  
  return (
    <div className={`solution-container ${isCorrect ? 'correct' : 'incorrect'}`}>
      <h4 className="solution-header">
        {isCorrect ? 'Correct!' : 'Incorrect'} - Solution Explanation
      </h4>
      <div className="solution-content">
        {/* Render solution with LaTeX support */}
      </div>
    </div>
  );
}
```

## Templates

The `templates` subfolder contains specialized renderers for different question types:

* **data-sufficiency.tsx**: For data sufficiency questions
* **reading-comprehension.tsx**: For reading comprehension questions
* **numeric-entry.tsx**: For numeric entry questions
* **quantitative-comparison.tsx**: For quantitative comparison questions

## Integration with Hooks

These components use hooks from the question-solving feature to:
- Fetch question data
- Handle answer submission
- Navigate between questions
- Track time spent

## Integration with Services

These components use services from the question-solving feature to:
- Format question content
- Validate answers
- Format solutions
- Calculate progress

## Usage Example

```tsx
import { QuestionDisplay } from '@/features/question-solving/components/question-display';
import { AnswerOptions } from '@/features/question-solving/components/answer-options';
import { SolutionViewer } from '@/features/question-solving/components/solution-viewer';
import { useAnswerSubmission } from '@/features/question-solving/hooks/use-answer-submission';

function QuestionPage({ question }) {
  const { 
    selectedOption, 
    setSelectedOption, 
    submitAnswer, 
    result,
    isSubmitted 
  } = useAnswerSubmission(question.id);
  
  return (
    <div className="question-page">
      <QuestionDisplay question={question} />
      <AnswerOptions 
        options={question.options}
        selectedOption={selectedOption}
        onSelect={setSelectedOption}
        disabled={isSubmitted}
      />
      <Button 
        onClick={submitAnswer} 
        disabled={!selectedOption || isSubmitted}
      >
        Submit Answer
      </Button>
      {result && (
        <SolutionViewer 
          solution={question.solution} 
          isCorrect={result.isCorrect} 
        />
      )}
    </div>
  );
}
```