# Exam Management Components

This directory contains React components specific to the exam management feature.

## Available Components

* **exam-selector.tsx**: Dropdown for selecting exam type
* **section-filter.tsx**: Tabs or buttons for filtering by section
* **tag-selector.tsx**: Multi-select for filtering by tags
* **difficulty-badge.tsx**: Visual indicator of question difficulty
* **exam-config-panel.tsx**: Admin panel for configuring exams

## Component Details

### exam-selector.tsx

Dropdown component for selecting exam types:

```tsx
interface ExamSelectorProps {
  selectedExam: string;
  onExamChange: (examId: string) => void;
}

function ExamSelector({ selectedExam, onExamChange }: ExamSelectorProps) {
  const [examTypes, setExamTypes] = useState<ExamType[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchExams = async () => {
      setLoading(true);
      try {
        const data = await examService.fetchExamTypes();
        setExamTypes(data);
      } catch (error) {
        console.error('Error fetching exam types:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchExams();
  }, []);
  
  return (
    <div className="exam-selector">
      <label htmlFor="exam-select">Select Exam</label>
      <select 
        id="exam-select"
        value={selectedExam}
        onChange={(e) => onExamChange(e.target.value)}
        disabled={loading}
      >
        {loading ? (
          <option>Loading...</option>
        ) : (
          examTypes.map(exam => (
            <option key={exam.id} value={exam.id}>
              {exam.name}
            </option>
          ))
        )}
      </select>
    </div>
  );
}
```

### section-filter.tsx

Tab component for filtering by exam sections:

```tsx
interface SectionFilterProps {
  examId: string;
  selectedSection: string;
  onSectionChange: (sectionId: string) => void;
}

function SectionFilter({ examId, selectedSection, onSectionChange }: SectionFilterProps) {
  const [sections, setSections] = useState<Section[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchSections = async () => {
      setLoading(true);
      try {
        const data = await examService.fetchSections(examId);
        setSections(data);
        // Select first section by default if none selected
        if (!selectedSection && data.length > 0) {
          onSectionChange(data[0].id);
        }
      } catch (error) {
        console.error('Error fetching sections:', error);
      } finally {
        setLoading(false);
      }
    };
    
    if (examId) {
      fetchSections();
    }
  }, [examId, selectedSection, onSectionChange]);
  
  return (
    <div className="section-filter">
      {loading ? (
        <div className="loading-indicator">Loading sections...</div>
      ) : (
        <div className="section-tabs">
          {sections.map(section => (
            <button
              key={section.id}
              className={`section-tab ${selectedSection === section.id ? 'active' : ''}`}
              onClick={() => onSectionChange(section.id)}
            >
              {section.name}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
```

### tag-selector.tsx

Multi-select component for filtering by tags:

```tsx
interface TagSelectorProps {
  examId: string;
  sectionId: string;
  selectedTags: string[];
  onTagsChange: (tags: string[]) => void;
}

function TagSelector({ examId, sectionId, selectedTags, onTagsChange }: TagSelectorProps) {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  
  useEffect(() => {
    const fetchTags = async () => {
      setLoading(true);
      try {
        const data = await examService.fetchTags(examId, sectionId);
        setTags(data);
      } catch (error) {
        console.error('Error fetching tags:', error);
      } finally {
        setLoading(false);
      }
    };
    
    if (examId && sectionId) {
      fetchTags();
    }
  }, [examId, sectionId]);
  
  const filteredTags = tags.filter(tag => 
    tag.name.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  const toggleTag = (tagId: string) => {
    if (selectedTags.includes(tagId)) {
      onTagsChange(selectedTags.filter(id => id !== tagId));
    } else {
      onTagsChange([...selectedTags, tagId]);
    }
  };
  
  return (
    <div className="tag-selector">
      <div className="tag-search">
        <input
          type="text"
          placeholder="Search tags..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>
      
      {loading ? (
        <div className="loading-indicator">Loading tags...</div>
      ) : (
        <div className="tag-list">
          {filteredTags.map(tag => (
            <div
              key={tag.id}
              className={`tag-item ${selectedTags.includes(tag.id) ? 'selected' : ''}`}
              onClick={() => toggleTag(tag.id)}
            >
              <span className="tag-name">{tag.name}</span>
              <span className="tag-count">({tag.count})</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

## Integration with Hooks

These components use hooks from the exam-management feature to:
- Manage exam selection state
- Handle section filtering
- Process tag selection

## Integration with Services

These components use services from the exam-management feature to:
- Fetch exam types and sections
- Retrieve and filter tags
- Save user preferences

## Usage Example

```tsx
import { ExamSelector } from '@/features/exam-management/components/exam-selector';
import { SectionFilter } from '@/features/exam-management/components/section-filter';
import { TagSelector } from '@/features/exam-management/components/tag-selector';
import { useExamSelection } from '@/features/exam-management/hooks/use-exam-selection';

function ExamFilters() {
  const { 
    selectedExam, 
    selectedSection, 
    selectedTags,
    setExam,
    setSection,
    setTags
  } = useExamSelection();
  
  return (
    <div className="exam-filters">
      <ExamSelector 
        selectedExam={selectedExam} 
        onExamChange={setExam} 
      />
      
      <SectionFilter 
        examId={selectedExam}
        selectedSection={selectedSection}
        onSectionChange={setSection}
      />
      
      <TagSelector 
        examId={selectedExam}
        sectionId={selectedSection}
        selectedTags={selectedTags}
        onTagsChange={setTags}
      />
    </div>
  );
}
```