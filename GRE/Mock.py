from Mock.Verbal import Verbal

mock_difficulty = 5
verbal = Verbal(mock_difficulty)
verbal_prompts = verbal.generate_question_prompts()

for section in verbal_prompts:
    print(f"Section {verbal_prompts.index(section) + 1}")
    for prompt in section:
        print(prompt)
    print("-"*50)